import asyncio
import json
import shutil
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from book_ai.config import (
    PROJECTS_DIR, SUPPORTED_LANGUAGES, PROCESSING_GOALS, ProjectSettings
)
from book_ai.security.files import (
    sanitize_filename, validate_magic_bytes, verify_safe_path, FileSecurityError
)
from book_ai.security.secrets import secret_manager
from book_ai.storage.database import db
from book_ai.formats.epub_handler import EpubHandler
from book_ai.formats.pdf_handler import PdfHandler
from book_ai.formats.mobi_handler import MobiHandler
from book_ai.providers.adapters import MODEL_CATALOG, UnifiedAIProvider, ProviderError
from book_ai.jobs.engine import engine

app = FastAPI(
    title="Book AI Local Server",
    description="מערכת מקצועית לתרגום, עריכה ועיבוד ספרים דיגיטליים באמצעות מודלי AI",
    version="1.0.0"
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.on_event("startup")
async def on_startup():
    db.recover_interrupted_projects()

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self';"
    )
    return response

@app.exception_handler(FileSecurityError)
async def file_security_exception_handler(request: Request, exc: FileSecurityError):
    return JSONResponse(status_code=400, content={"error": "FILE_SECURITY_ERROR", "message": str(exc)})

@app.exception_handler(ProviderError)
async def provider_exception_handler(request: Request, exc: ProviderError):
    return JSONResponse(status_code=502, content={"error": "PROVIDER_ERROR", "message": str(exc)})

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")

@app.get("/api/info")
async def get_app_info():
    return {
        "name": "Book AI",
        "version": "1.0.0",
        "languages": SUPPORTED_LANGUAGES,
        "goals": PROCESSING_GOALS,
        "models": MODEL_CATALOG,
        "secrets_status": secret_manager.get_status(),
        "default_settings": ProjectSettings().model_dump()
    }

class SecretInput(BaseModel):
    provider: str
    api_key: str

@app.post("/api/secrets")
async def save_secret(payload: SecretInput):
    if not payload.api_key.strip():
        raise HTTPException(status_code=400, detail="מפתח ה-API אינו יכול להיות ריק.")
    secret_manager.save_key(payload.provider, payload.api_key)
    return {"status": "saved", "secrets_status": secret_manager.get_status()}

@app.delete("/api/secrets/{provider}")
async def delete_secret(provider: str):
    secret_manager.delete_key(provider)
    return {"status": "deleted", "secrets_status": secret_manager.get_status()}

class ConnectionTestInput(BaseModel):
    provider: str
    model: str
    base_url: Optional[str] = ""
    temp_api_key: Optional[str] = None

@app.post("/api/providers/test")
async def test_provider_connection(payload: ConnectionTestInput):
    test_messages = [
        {"role": "system", "content": 'Return strictly JSON: {"units": [{"id": "u1", "unit_type": "p", "text": "OK"}]}'},
        {"role": "user", "content": 'INPUT DATA PAYLOAD:\n{"target_units_to_process": [{"id": "u1", "unit_type": "p", "text": "Ping"}]}'}
    ]
    res = await UnifiedAIProvider.complete(
        payload.provider,
        payload.model,
        test_messages,
        {"base_url": payload.base_url, "timeout": 25, "max_output_tokens": 128},
        temp_api_key=payload.temp_api_key
    )
    return {"status": "ok", "model": res["model"], "elapsed_sec": round(res["elapsed"], 2)}

@app.get("/api/projects")
async def list_projects():
    return {"projects": db.list_projects()}

@app.post("/api/projects")
async def create_project(
    file: UploadFile = File(...),
    name: str = Form(""),
    settings_json: str = Form("{}")
):
    proj_id = f"proj_{uuid.uuid4().hex[:10]}"
    proj_dir = verify_safe_path(PROJECTS_DIR, PROJECTS_DIR / proj_id)
    src_dir = proj_dir / "source"
    work_dir = proj_dir / "work"
    out_dir = proj_dir / "output"
    for d in (src_dir, work_dir, out_dir):
        d.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(file.filename or "book.epub")
    src_file = src_dir / safe_name

    try:
        content = await file.read()
        src_file.write_bytes(content)
        fmt = validate_magic_bytes(src_file)

        extraction_report = None
        if fmt == "epub":
            working_epub = src_file
        elif fmt == "pdf":
            working_epub, extraction_report = PdfHandler.convert_pdf_to_epub(src_file, work_dir)
        elif fmt == "mobi":
            working_epub = MobiHandler.convert_mobi_to_epub(src_file, work_dir)
        else:
            raise FileSecurityError("פורמט אינו נתמך.")

        metadata, chapters, units = EpubHandler.ingest_epub(working_epub, work_dir)
        if extraction_report:
            metadata["extraction_report"] = extraction_report

        raw_settings = json.loads(settings_json) if settings_json else {}
        validated_settings = ProjectSettings(**raw_settings).model_dump()
        if validated_settings["src_lang"] == "auto" and metadata.get("language"):
            lang_code = metadata["language"].split("-")[0].lower()
            if lang_code in SUPPORTED_LANGUAGES:
                validated_settings["src_lang"] = lang_code

        proj_record = {
            "id": proj_id,
            "name": name.strip() or metadata.get("title") or safe_name,
            "original_filename": safe_name,
            "source_format": fmt.upper(),
            "source_path": str(src_file),
            "work_dir": str(work_dir),
            "output_path": None,
            "metadata": metadata,
            "settings": validated_settings,
            "status": "ready"
        }
        db.create_project(proj_record, chapters, units)
        db.log(proj_id, "INFO", "ingest", f"פרויקט נוצר בהצלחה ({len(chapters)} פרקים, {len(units)} יחידות).")
        return db.get_project(proj_id)
    except Exception as e:
        shutil.rmtree(proj_dir, ignore_errors=True)
        if isinstance(e, FileSecurityError):
            raise e
        raise HTTPException(status_code=400, detail=f"שגיאה בקליטת הספר: {e}")

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: str):
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא.")
    return {
        "project": proj,
        "chapters": db.get_chapters(project_id),
        "live": engine.get_live_state(project_id)
    }

@app.put("/api/projects/{project_id}/settings")
async def update_settings(project_id: str, settings: ProjectSettings):
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא.")
    updated = db.update_project_settings(project_id, settings.model_dump())
    db.log(project_id, "INFO", "settings", "הגדרות הפרויקט עודכנו.")
    return updated

class RenameInput(BaseModel):
    name: str

@app.patch("/api/projects/{project_id}/rename")
async def rename_project(project_id: str, payload: RenameInput):
    db.rename_project(project_id, payload.name)
    return db.get_project(project_id)

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, mode: str = Query("full", enum=["full", "output_only"])):
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא.")
    await engine.stop(project_id)

    proj_dir = verify_safe_path(PROJECTS_DIR, Path(proj["work_dir"]).parent)
    if mode == "output_only":
        if proj.get("output_path"):
            out_p = verify_safe_path(proj_dir, Path(proj["output_path"]))
            if out_p.exists():
                out_p.unlink()
        db.update_project_status(project_id, proj["status"], output_path="")
        return {"status": "output_deleted"}
    else:
        shutil.rmtree(proj_dir, ignore_errors=True)
        db.delete_project_record(project_id)
        return {"status": "project_deleted"}

class ControlInput(BaseModel):
    action: str
    unit_id: Optional[str] = None
    force_manual_override: bool = False

@app.post("/api/projects/{project_id}/control")
async def control_processing(project_id: str, payload: ControlInput):
    act = payload.action
    if act in ("start", "resume"):
        return await engine.start_or_resume(project_id, mode="resume")
    elif act == "retry_failed":
        return await engine.start_or_resume(project_id, mode="retry_failed")
    elif act == "retry_flagged":
        return await engine.start_or_resume(project_id, mode="retry_flagged")
    elif act == "resend_unit":
        if not payload.unit_id:
            raise HTTPException(status_code=400, detail="חסר מזהה יחידה לשליחה מחדש.")
        u = db.get_unit(payload.unit_id)
        if u and u["is_manual"] and not payload.force_manual_override:
            return JSONResponse(status_code=409, content={
                "error": "MANUAL_EDIT_PROTECTED",
                "message": "יחידה זו נערכה ידנית. שליחה מחדש תדרוס את העריכה הידנית שלך. האם אתה בטוח?",
                "current_text": u["result_text"]
            })
        return await engine.start_or_resume(
            project_id, mode="single", specific_unit_id=payload.unit_id,
            force_manual_override=payload.force_manual_override
        )
    elif act == "pause":
        await engine.pause(project_id)
        return {"status": "paused"}
    elif act == "stop":
        await engine.stop(project_id)
        return {"status": "stopped"}
    elif act == "cancel_unit" and payload.unit_id:
        await engine.cancel_unit(project_id, payload.unit_id)
        return {"status": "unit_cancelled"}
    raise HTTPException(status_code=400, detail=f"פעולת בקרה לא מוכרת: {act}")

@app.get("/api/projects/{project_id}/events")
async def project_events_sse(project_id: str, request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            state = engine.get_live_state(project_id)
            yield f"data: {json.dumps(state, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1.0)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/projects/{project_id}/units")
async def list_project_units(
    project_id: str,
    status: Optional[str] = None,
    chapter_id: Optional[str] = None,
    unit_type: Optional[str] = None,
    search: Optional[str] = None
):
    return {"units": db.get_units(project_id, status=status, chapter_id=chapter_id, unit_type=unit_type, search=search)}

class ManualEditInput(BaseModel):
    result_text: str

@app.put("/api/units/{unit_id}")
async def manual_edit_unit(unit_id: str, payload: ManualEditInput):
    u = db.get_unit(unit_id)
    if not u:
        raise HTTPException(status_code=404, detail="היחידה לא נמצאה.")
    from book_ai.core.tag_protector import validate_and_restore_placeholders
    ok, _, errors = validate_and_restore_placeholders(payload.result_text, u["protected"], attempt_repair=True)
    db.update_unit_atomic(
        unit_id, "manual", payload.result_text,
        "; ".join(errors) if not ok else None, ok, is_manual=True
    )
    db.log(u["project_id"], "INFO", "manual_edit", f"היחידה {unit_id} נערכה ונשמרה ידנית.", unit_id=unit_id)
    return db.get_unit(unit_id)

@app.post("/api/units/{unit_id}/revert")
async def revert_unit_history(unit_id: str):
    reverted = db.revert_unit(unit_id)
    if not reverted:
        raise HTTPException(status_code=404, detail="היחידה לא נמצאה.")
    return reverted

@app.get("/api/projects/{project_id}/glossary")
async def get_glossary(project_id: str):
    return {"entries": db.list_glossary(project_id)}

class GlossaryInput(BaseModel):
    id: Optional[str] = None
    source_term: str
    target_term: str
    term_type: str = "general"
    notes: str = ""
    approved: bool = True
    case_sensitive: bool = False
    match_rule: str = "exact"

@app.post("/api/projects/{project_id}/glossary")
async def save_glossary_entry(project_id: str, payload: GlossaryInput):
    entry = payload.model_dump()
    entry["id"] = entry.get("id") or f"gl_{uuid.uuid4().hex[:8]}"
    entry["project_id"] = project_id
    db.upsert_glossary(entry)
    return {"entries": db.list_glossary(project_id)}

@app.delete("/api/projects/{project_id}/glossary/{entry_id}")
async def remove_glossary_entry(project_id: str, entry_id: str):
    db.delete_glossary(entry_id)
    return {"entries": db.list_glossary(project_id)}

@app.get("/api/projects/{project_id}/tm")
async def get_tm(project_id: str, search: Optional[str] = None):
    return {"entries": db.list_tm(project_id, search=search)}

@app.delete("/api/projects/{project_id}/tm")
async def clear_project_tm(project_id: str):
    db.clear_tm(project_id)
    return {"entries": []}

@app.get("/api/projects/{project_id}/logs")
async def get_project_logs(project_id: str, level: Optional[str] = None, search: Optional[str] = None):
    return {"logs": db.get_logs(project_id, level=level, search=search)}

@app.delete("/api/projects/{project_id}/logs")
async def clear_project_logs(project_id: str):
    db.clear_logs(project_id)
    return {"status": "cleared"}

@app.get("/api/projects/{project_id}/preview")
async def preview_chapter(project_id: str, chapter_id: Optional[str] = None):
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא.")
    chapters = db.get_chapters(project_id)
    if not chapters:
        return {"html": "<p>אין פרקים להצגה.</p>"}
    target_ch = next((c for c in chapters if c["id"] == chapter_id), chapters[0])
    units = db.get_units(project_id, chapter_id=target_ch["id"])
    tgt_dir = SUPPORTED_LANGUAGES.get(proj["settings"]["tgt_lang"], {}).get("dir", "rtl")

    rows_html = []
    for u in units:
        from book_ai.core.tag_protector import validate_and_restore_placeholders
        _, src_html, _ = validate_and_restore_placeholders(u["source_text"], u["protected"], attempt_repair=True)
        res_raw = u["result_text"] or "<em style='color:#888'>[טרם עובד]</em>"
        if u["result_text"]:
            _, res_html, _ = validate_and_restore_placeholders(u["result_text"], u["protected"], attempt_repair=True)
        else:
            res_html = res_raw
        rows_html.append(f"""
        <div class="preview-pair">
            <div class="preview-src" dir="auto"><small>{u['id']} ({u['unit_type']})</small><div>{src_html}</div></div>
            <div class="preview-tgt" dir="{tgt_dir}"><small>{u['status']}</small><div>{res_html}</div></div>
        </div>
        """)
    return {"chapter": target_ch, "html": "\n".join(rows_html)}

@app.post("/api/projects/{project_id}/build")
async def build_final_epub(project_id: str):
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא.")
    chapters = db.get_chapters(project_id)
    units = db.get_units(project_id)
    proj_dir = verify_safe_path(PROJECTS_DIR, Path(proj["work_dir"]).parent)
    out_dir = proj_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{sanitize_filename(proj['name'])}_{proj['settings']['tgt_lang']}.epub"

    report = EpubHandler.build_and_verify_epub(proj, chapters, units, out_file)
    if report["valid"]:
        db.update_project_status(project_id, proj["status"], output_path=str(out_file))
        db.log(project_id, "INFO", "build", f"קובץ ה-EPUB הופק ואומת בהצלחה: {out_file.name}")
    else:
        db.log(project_id, "ERROR", "build", f"בדיקת הפלט נכשלה: {'; '.join(report['errors'])}")
    return {"report": report, "output_ready": report["valid"]}

@app.get("/api/projects/{project_id}/download")
async def download_final_epub(project_id: str):
    proj = db.get_project(project_id)
    if not proj or not proj.get("output_path"):
        raise HTTPException(status_code=404, detail="טרם הופק קובץ סופי תקין לפרויקט זה.")
    proj_dir = verify_safe_path(PROJECTS_DIR, Path(proj["work_dir"]).parent)
    out_p = verify_safe_path(proj_dir, Path(proj["output_path"]))
    if not out_p.exists():
        raise HTTPException(status_code=404, detail="קובץ הפלט לא נמצא בכונן.")
    return FileResponse(str(out_p), media_type="application/epub+zip", filename=out_p.name)

@app.get("/api/projects/{project_id}/report")
async def export_project_report(project_id: str):
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא.")
    units = db.get_units(project_id)
    failed_units = [{"id": u["id"], "status": u["status"], "error": u["error_msg"]} for u in units if u["status"] in ("failed", "flagged")]
    return {
        "project_id": proj["id"],
        "name": proj["name"],
        "source_format": proj["source_format"],
        "metadata": proj["metadata"],
        "stats": proj["stats"],
        "usage": proj["usage"],
        "issues": failed_units
    }
