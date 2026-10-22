import asyncio
import random
import time
from typing import Dict, Any, List, Optional, Set
from book_ai.storage.database import db
from book_ai.core.chunker import Chunker
from book_ai.core.prompts import build_processing_messages
from book_ai.core.tag_protector import validate_and_restore_placeholders
from book_ai.providers.adapters import UnifiedAIProvider, ProviderError

class ProjectJobController:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.pause_event = asyncio.Event()
        self.pause_event.set()
        self.stop_requested = False
        self.cancelled_units: Set[str] = set()
        self.active_units: int = 0
        self.current_chapter_title: str = ""
        self.current_unit_id: str = ""
        self.started_at: float = time.time()
        self.completed_in_session: int = 0
        self.task: Optional[asyncio.Task] = None

class ProcessingEngine:
    def __init__(self):
        self._controllers: Dict[str, ProjectJobController] = {}
        self._lock = asyncio.Lock()

    def get_live_state(self, project_id: str) -> Dict[str, Any]:
        proj = db.get_project(project_id)
        if not proj:
            return {}
        stats = proj["stats"]
        usage = proj["usage"]
        ctrl = self._controllers.get(project_id)

        elapsed = usage.get("elapsed_sec", 0.0)
        eta_seconds: Optional[int] = None
        if ctrl and proj["status"] == "running":
            session_elapsed = max(1.0, time.time() - ctrl.started_at)
            if ctrl.completed_in_session >= 2:
                rate = ctrl.completed_in_session / session_elapsed
                remaining = stats.get("pending", 0) + stats.get("processing", 0)
                eta_seconds = int(remaining / rate) if rate > 0 else None

        return {
            "project_id": project_id,
            "status": proj["status"],
            "stats": stats,
            "usage": usage,
            "active_units": ctrl.active_units if ctrl else 0,
            "current_chapter": ctrl.current_chapter_title if ctrl else "",
            "current_unit": ctrl.current_unit_id if ctrl else "",
            "elapsed_sec": round(elapsed, 1),
            "eta_seconds": eta_seconds,
            "eta_reliable": eta_seconds is not None
        }

    async def start_or_resume(self, project_id: str, mode: str = "resume",
                              specific_unit_id: Optional[str] = None,
                              force_manual_override: bool = False) -> Dict[str, Any]:
        async with self._lock:
            existing = self._controllers.get(project_id)
            if existing and existing.task and not existing.task.done():
                existing.pause_event.set()
                db.update_project_status(project_id, "running")
                return {"status": "resumed"}

            ctrl = ProjectJobController(project_id)
            self._controllers[project_id] = ctrl
            db.update_project_status(project_id, "running")
            ctrl.task = asyncio.create_task(
                self._run_pipeline(ctrl, mode=mode, specific_unit_id=specific_unit_id, force_manual_override=force_manual_override)
            )
            return {"status": "started"}

    async def pause(self, project_id: str) -> None:
        ctrl = self._controllers.get(project_id)
        if ctrl:
            ctrl.pause_event.clear()
        db.update_project_status(project_id, "paused")
        db.log(project_id, "INFO", "control", "העיבוד הושהה באופן מבוקר על ידי המשתמש.")

    async def stop(self, project_id: str) -> None:
        ctrl = self._controllers.get(project_id)
        if ctrl:
            ctrl.stop_requested = True
            ctrl.pause_event.set()
        db.update_project_status(project_id, "stopped")
        db.log(project_id, "WARN", "control", "בקשת עצירה התקבלה. שומר תוצאות שהושלמו ומפסיק משימות חדשות.")

    async def cancel_unit(self, project_id: str, unit_id: str) -> None:
        ctrl = self._controllers.get(project_id)
        if ctrl:
            ctrl.cancelled_units.add(unit_id)
        u = db.get_unit(unit_id)
        if u and u["status"] in ("pending", "processing"):
            db.update_unit_atomic(unit_id, "pending", u.get("result_text"), "הפעולה בוטלה על ידי המשתמש", False)

    async def _run_pipeline(self, ctrl: ProjectJobController, mode: str,
                            specific_unit_id: Optional[str], force_manual_override: bool) -> None:
        project_id = ctrl.project_id
        try:
            proj = db.get_project(project_id)
            if not proj:
                return
            settings = proj["settings"]
            version = proj["version"]
            chapters = {c["id"]: c for c in db.get_chapters(project_id)}
            all_units = db.get_units(project_id)
            glossary = db.list_glossary(project_id)
            tm_list = db.list_tm(project_id)

            target_ids: Set[str] = set()
            for u in all_units:
                if specific_unit_id:
                    if u["id"] == specific_unit_id:
                        if u["is_manual"] and not force_manual_override:
                            db.log(project_id, "WARN", "manual_guard", f"היחידה {u['id']} נערכה ידנית ומוגנת מפני דריסה ללא אישור.", unit_id=u["id"])
                            continue
                        target_ids.add(u["id"])
                elif mode == "retry_failed":
                    if u["status"] == "failed":
                        target_ids.add(u["id"])
                elif mode == "retry_flagged":
                    if u["status"] == "flagged":
                        target_ids.add(u["id"])
                else:
                    if u["status"] in ("pending", "failed"):
                        target_ids.add(u["id"])

            if not target_ids:
                db.update_project_status(project_id, "completed")
                db.log(project_id, "INFO", "engine", "אין יחידות הממתינות לעיבוד.")
                return

            units_by_chapter: Dict[str, List[Dict[str, Any]]] = {}
            for u in all_units:
                units_by_chapter.setdefault(u["chapter_id"], []).append(u)

            chunks: List[Dict[str, Any]] = []
            for ch_id, ch_units in units_by_chapter.items():
                ch_chunks = Chunker.build_chunks(
                    ch_units,
                    target_ids,
                    chunk_chars=int(settings.get("chunk_chars", 6000)),
                    overlap_units=int(settings.get("overlap", 2))
                )
                chunks.extend(ch_chunks)

            concurrency = max(1, int(settings.get("concurrency", 2)))
            rpm = max(1, int(settings.get("rpm", 30)))
            min_interval = 60.0 / rpm
            last_req_time = [0.0]
            rate_lock = asyncio.Lock()
            sem = asyncio.Semaphore(concurrency)

            async def _process_chunk(chunk: Dict[str, Any]):
                await ctrl.pause_event.wait()
                if ctrl.stop_requested:
                    return

                async with sem:
                    await ctrl.pause_event.wait()
                    if ctrl.stop_requested:
                        return

                    async with rate_lock:
                        now = time.perf_counter()
                        wait_s = min_interval - (now - last_req_time[0])
                        if wait_s > 0:
                            await asyncio.sleep(wait_s)
                        last_req_time[0] = time.perf_counter()

                    t_units = [u for u in chunk["target_units"] if u["id"] not in ctrl.cancelled_units]
                    if not t_units:
                        return

                    ctrl.active_units += len(t_units)
                    ch_obj = chapters.get(chunk["chapter_id"], {})
                    ctrl.current_chapter_title = ch_obj.get("title", "")
                    ctrl.current_unit_id = t_units[0]["id"]

                    for u in t_units:
                        db.update_unit_atomic(u["id"], "processing", u.get("result_text"), None, False, settings_version=version)

                    try:
                        await self._execute_chunk_with_retries(ctrl, proj, t_units, chunk["context_units"], glossary, tm_list)
                    finally:
                        ctrl.active_units = max(0, ctrl.active_units - len(t_units))

            await asyncio.gather(*(_process_chunk(c) for c in chunks))

            stats = db.refresh_project_stats(project_id)
            if ctrl.stop_requested:
                db.update_project_status(project_id, "stopped")
            elif stats["failed"] > 0 or stats["flagged"] > 0:
                db.update_project_status(project_id, "needs_review")
            else:
                db.update_project_status(project_id, "completed")

            db.log(project_id, "INFO", "engine", f"סבב העיבוד הסתיים. הושלמו: {stats['done']}/{stats['total']}.")
        except Exception as e:
            db.update_project_status(project_id, "error")
            db.log(project_id, "ERROR", "engine", f"שגיאה קריטית במנוע העיבוד: {e}")

    async def _execute_chunk_with_retries(
        self,
        ctrl: ProjectJobController,
        proj: Dict[str, Any],
        target_units: List[Dict[str, Any]],
        context_units: List[Dict[str, Any]],
        glossary: List[Dict[str, Any]],
        tm_list: List[Dict[str, Any]]
    ) -> None:
        project_id = proj["id"]
        settings = proj["settings"]
        version = proj["version"]
        max_content_attempts = max(1, int(settings.get("attempts", 3)))
        max_api_retries = max(1, int(settings.get("api_retries", 5)))
        provider = settings.get("provider", "gemini")
        model = settings.get("model", "gemini-2.5-flash")
        on_format_failure = settings.get("on_format_failure", "flag")

        messages = build_processing_messages(settings, target_units, context_units, glossary, tm_list)

        for content_attempt in range(1, max_content_attempts + 1):
            if ctrl.stop_requested:
                for u in target_units:
                    db.update_unit_atomic(u["id"], "pending", u.get("result_text"), None, False)
                return

            api_response = None
            last_err = ""
            for api_try in range(1, max_api_retries + 1):
                try:
                    api_response = await UnifiedAIProvider.complete(provider, model, messages, settings)
                    break
                except ProviderError as pe:
                    last_err = str(pe)
                    db.log(project_id, "WARN" if pe.retryable else "ERROR", "api", last_err,
                           unit_id=target_units[0]["id"], provider=provider, model=model, attempt=api_try)
                    if not pe.retryable or api_try == max_api_retries:
                        break
                    backoff = pe.retry_after if pe.retry_after > 0 else min(30.0, (2 ** (api_try - 1)) + random.uniform(0.1, 0.9))
                    await asyncio.sleep(backoff)
                except Exception as ex:
                    last_err = f"שגיאת פענוח/תקשורת: {ex}"
                    if api_try == max_api_retries:
                        break
                    await asyncio.sleep(1.5 * api_try)

            if not api_response:
                if content_attempt == max_content_attempts:
                    for u in target_units:
                        prev = u.get("result_text")
                        status = "done" if prev else "failed"
                        db.update_unit_atomic(u["id"], status, prev, last_err, bool(prev), increment_attempt=True, settings_version=version)
                    return
                continue

            in_tok = api_response["input_tokens"]
            out_tok = api_response["output_tokens"]
            cost = (in_tok * float(settings.get("price_in", 0.0)) + out_tok * float(settings.get("price_out", 0.0))) / 1_000_000.0
            db.add_usage(project_id, in_tok, out_tok, content_attempt - 1, cost, api_response["elapsed"])

            parsed_units = api_response.get("parsed", {}).get("units", [])
            if not isinstance(parsed_units, list) or len(parsed_units) != len(target_units):
                last_err = f"חוסר התאמה במספר היחידות שהוחזרו ({len(parsed_units)} במקום {len(target_units)})."
                db.log(project_id, "WARN", "validation", last_err, unit_id=target_units[0]["id"], provider=provider, model=model, attempt=content_attempt)
                if content_attempt < max_content_attempts:
                    continue
                if len(target_units) > 1:
                    for single_u in target_units:
                        await self._execute_chunk_with_retries(ctrl, proj, [single_u], context_units, glossary, tm_list)
                    return
                for u in target_units:
                    db.update_unit_atomic(u["id"], "failed", u.get("result_text"), last_err, False, increment_attempt=True)
                return

            all_valid = True
            for orig_u, ret_u in zip(target_units, parsed_units):
                if orig_u["id"] in ctrl.cancelled_units:
                    continue
                ret_id = ret_u.get("id")
                ret_text = (ret_u.get("text") or "").strip()

                if ret_id != orig_u["id"] or not ret_text:
                    all_valid = False
                    last_err = f"מזהה יחידה שגוי או טקסט ריק עבור {orig_u['id']}."
                    break

                allow_repair = on_format_failure in ("repair", "flag")
                ok, _, tag_errors = validate_and_restore_placeholders(ret_text, orig_u["protected"], attempt_repair=allow_repair)

                if ok:
                    db.update_unit_atomic(orig_u["id"], "done", ret_text, None, True, increment_attempt=True, settings_version=version)
                    ctrl.completed_in_session += 1
                    db.upsert_tm({
                        "id": f"tm_{orig_u['id']}",
                        "project_id": project_id,
                        "source_text": orig_u["source_text"],
                        "target_text": ret_text,
                        "src_lang": settings["src_lang"],
                        "tgt_lang": settings["tgt_lang"],
                        "context": orig_u["chapter_id"],
                        "approved": True
                    })
                else:
                    err_str = "; ".join(tag_errors)
                    if content_attempt < max_content_attempts and on_format_failure == "retry":
                        all_valid = False
                        last_err = err_str
                        break
                    final_status = "flagged" if on_format_failure in ("flag", "repair") else "failed"
                    db.update_unit_atomic(orig_u["id"], final_status, ret_text, err_str, False, increment_attempt=True, settings_version=version)
                    db.log(project_id, "WARN", "tag_validation", f"יחידה {orig_u['id']} סומנה ({final_status}): {err_str}", unit_id=orig_u["id"])

            if all_valid:
                return

engine = ProcessingEngine()
