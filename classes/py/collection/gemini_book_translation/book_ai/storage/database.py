import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from book_ai.config import DB_PATH, ProjectSettings

VALID_UNIT_STATUSES = {"pending", "processing", "done", "failed", "flagged", "manual"}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._local = threading.local()
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            self._local.conn = conn
        return self._local.conn

    def _init_schema(self) -> None:
        conn = self._get_conn()
        with conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS global_settings (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    source_format TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    work_dir TEXT NOT NULL,
                    output_path TEXT,
                    metadata_json TEXT NOT NULL,
                    settings_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ready',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    stats_json TEXT NOT NULL,
                    usage_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chapters (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    ord INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    doc_path TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS units (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    chapter_id TEXT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
                    ord INTEGER NOT NULL,
                    unit_type TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    result_text TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    error_msg TEXT,
                    protected_json TEXT NOT NULL,
                    history_json TEXT NOT NULL DEFAULT '[]',
                    is_manual INTEGER NOT NULL DEFAULT 0,
                    validation_ok INTEGER NOT NULL DEFAULT 0,
                    settings_version INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_units_project_ord ON units(project_id, ord);
                CREATE INDEX IF NOT EXISTS idx_units_status ON units(project_id, status);

                CREATE TABLE IF NOT EXISTS glossary (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    source_term TEXT NOT NULL,
                    target_term TEXT NOT NULL,
                    term_type TEXT NOT NULL DEFAULT 'general',
                    notes TEXT DEFAULT '',
                    approved INTEGER NOT NULL DEFAULT 1,
                    case_sensitive INTEGER NOT NULL DEFAULT 0,
                    match_rule TEXT NOT NULL DEFAULT 'exact'
                );

                CREATE TABLE IF NOT EXISTS translation_memory (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    source_text TEXT NOT NULL,
                    target_text TEXT NOT NULL,
                    src_lang TEXT NOT NULL,
                    tgt_lang TEXT NOT NULL,
                    context TEXT DEFAULT '',
                    approved INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    progress_json TEXT NOT NULL,
                    errors_json TEXT NOT NULL DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    unit_id TEXT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    message TEXT NOT NULL,
                    provider TEXT,
                    model TEXT,
                    attempt INTEGER DEFAULT 0
                );
            """)

    def recover_interrupted_projects(self) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("UPDATE units SET status='pending' WHERE status='processing'")
            conn.execute("UPDATE projects SET status='paused', updated_at=? WHERE status='running'", (now_iso(),))
            conn.execute("UPDATE jobs SET status='interrupted', ended_at=? WHERE status='running'", (now_iso(),))

    def create_project(self, proj: Dict[str, Any], chapters: List[Dict[str, Any]], units: List[Dict[str, Any]]) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO projects (
                    id, name, original_filename, source_format, source_path, work_dir,
                    output_path, metadata_json, settings_json, status, created_at,
                    updated_at, version, stats_json, usage_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proj["id"], proj["name"], proj["original_filename"], proj["source_format"],
                proj["source_path"], proj["work_dir"], proj.get("output_path"),
                json.dumps(proj["metadata"], ensure_ascii=False),
                json.dumps(proj["settings"], ensure_ascii=False),
                proj.get("status", "ready"), now_iso(), now_iso(), 1,
                json.dumps(proj.get("stats", {}), ensure_ascii=False),
                json.dumps({
                    "input_tokens": 0, "output_tokens": 0, "requests": 0,
                    "retries": 0, "estimated_cost": 0.0, "elapsed_sec": 0.0
                })
            ))
            for ch in chapters:
                conn.execute("""
                    INSERT INTO chapters (id, project_id, ord, title, doc_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (ch["id"], proj["id"], ch["ord"], ch["title"], ch["doc_path"]))

            for u in units:
                conn.execute("""
                    INSERT INTO units (
                        id, project_id, chapter_id, ord, unit_type, source_text,
                        result_text, status, attempts, error_msg, protected_json,
                        history_json, is_manual, validation_ok, settings_version, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', 0, NULL, ?, '[]', 0, 0, 1, ?)
                """, (
                    u["id"], proj["id"], u["chapter_id"], u["ord"], u["unit_type"],
                    u["source_text"], None, json.dumps(u["protected"], ensure_ascii=False), now_iso()
                ))
        self.refresh_project_stats(proj["id"])

    def refresh_project_stats(self, project_id: str) -> Dict[str, Any]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT status, COUNT(*) as cnt FROM units WHERE project_id=? GROUP BY status
        """, (project_id,)).fetchall()
        counts = {r["status"]: r["cnt"] for r in rows}
        total = sum(counts.values())
        done = counts.get("done", 0) + counts.get("manual", 0)
        failed = counts.get("failed", 0)
        flagged = counts.get("flagged", 0)
        pending = counts.get("pending", 0)
        processing = counts.get("processing", 0)
        pct = round((done / total) * 100.0, 1) if total > 0 else 0.0

        stats = {
            "total": total, "done": done, "failed": failed,
            "flagged": flagged, "pending": pending, "processing": processing,
            "progress_pct": pct
        }
        with conn:
            conn.execute("UPDATE projects SET stats_json=?, updated_at=? WHERE id=?",
                         (json.dumps(stats), now_iso(), project_id))
        return stats

    def list_projects(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        return [self._deserialize_project(r) for r in rows]

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
        return self._deserialize_project(row) if row else None

    def _deserialize_project(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        d["metadata"] = json.loads(d.pop("metadata_json"))
        d["settings"] = json.loads(d.pop("settings_json"))
        d["stats"] = json.loads(d.pop("stats_json"))
        d["usage"] = json.loads(d.pop("usage_json"))
        return d

    def update_project_settings(self, project_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        validated = ProjectSettings(**settings).model_dump()
        conn = self._get_conn()
        with conn:
            conn.execute("""
                UPDATE projects
                SET settings_json=?, version=version+1, updated_at=?
                WHERE id=?
            """, (json.dumps(validated, ensure_ascii=False), now_iso(), project_id))
        return self.get_project(project_id)

    def update_project_status(self, project_id: str, status: str, output_path: Optional[str] = None) -> None:
        conn = self._get_conn()
        with conn:
            if output_path is not None:
                conn.execute("UPDATE projects SET status=?, output_path=?, updated_at=? WHERE id=?",
                             (status, output_path, now_iso(), project_id))
            else:
                conn.execute("UPDATE projects SET status=?, updated_at=? WHERE id=?",
                             (status, now_iso(), project_id))

    def rename_project(self, project_id: str, new_name: str) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("UPDATE projects SET name=?, updated_at=? WHERE id=?", (new_name.strip(), now_iso(), project_id))

    def delete_project_record(self, project_id: str) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM projects WHERE id=?", (project_id,))

    def add_usage(self, project_id: str, in_tok: int, out_tok: int, retries: int, cost: float, elapsed: float) -> None:
        conn = self._get_conn()
        with conn:
            row = conn.execute("SELECT usage_json FROM projects WHERE id=?", (project_id,)).fetchone()
            if not row:
                return
            u = json.loads(row["usage_json"])
            u["input_tokens"] = u.get("input_tokens", 0) + in_tok
            u["output_tokens"] = u.get("output_tokens", 0) + out_tok
            u["requests"] = u.get("requests", 0) + 1
            u["retries"] = u.get("retries", 0) + retries
            u["estimated_cost"] = round(u.get("estimated_cost", 0.0) + cost, 6)
            u["elapsed_sec"] = round(u.get("elapsed_sec", 0.0) + elapsed, 2)
            conn.execute("UPDATE projects SET usage_json=?, updated_at=? WHERE id=?",
                         (json.dumps(u), now_iso(), project_id))

    def get_chapters(self, project_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM chapters WHERE project_id=? ORDER BY ord ASC", (project_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_units(self, project_id: str, status: Optional[str] = None,
                  chapter_id: Optional[str] = None, unit_type: Optional[str] = None,
                  search: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        query = "SELECT * FROM units WHERE project_id=?"
        params: List[Any] = [project_id]
        if status:
            query += " AND status=?"
            params.append(status)
        if chapter_id:
            query += " AND chapter_id=?"
            params.append(chapter_id)
        if unit_type:
            query += " AND unit_type=?"
            params.append(unit_type)
        if search:
            query += " AND (source_text LIKE ? OR result_text LIKE ? OR id LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like, like])
        query += " ORDER BY ord ASC"
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["protected"] = json.loads(d.pop("protected_json"))
            d["history"] = json.loads(d.pop("history_json"))
            d["is_manual"] = bool(d["is_manual"])
            d["validation_ok"] = bool(d["validation_ok"])
            result.append(d)
        return result

    def get_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        r = conn.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["protected"] = json.loads(d.pop("protected_json"))
        d["history"] = json.loads(d.pop("history_json"))
        d["is_manual"] = bool(d["is_manual"])
        d["validation_ok"] = bool(d["validation_ok"])
        return d

    def update_unit_atomic(self, unit_id: str, status: str, result_text: Optional[str],
                           error_msg: Optional[str], validation_ok: bool,
                           increment_attempt: bool = False, is_manual: bool = False,
                           settings_version: int = 1) -> None:
        if status not in VALID_UNIT_STATUSES:
            raise ValueError(f"סטטוס יחידה לא חוקי: {status}")
        if status in ("done", "manual") and (result_text is None or not result_text.strip()):
            raise ValueError("אין לסמן יחידה כמושלמת ללא תוצאה תקינה.")

        conn = self._get_conn()
        with conn:
            cur = conn.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
            if not cur:
                return
            history = json.loads(cur["history_json"])
            prev_res = cur["result_text"]
            if prev_res and prev_res != result_text:
                history.append({
                    "timestamp": now_iso(),
                    "previous_text": prev_res,
                    "previous_status": cur["status"],
                    "was_manual": bool(cur["is_manual"])
                })
                history = history[-10:]

            attempts = cur["attempts"] + (1 if increment_attempt else 0)
            final_res = result_text if result_text is not None else prev_res

            conn.execute("""
                UPDATE units
                SET status=?, result_text=?, error_msg=?, validation_ok=?,
                    attempts=?, is_manual=?, history_json=?, settings_version=?, updated_at=?
                WHERE id=?
            """, (
                status, final_res, error_msg, 1 if validation_ok else 0,
                attempts, 1 if is_manual else int(cur["is_manual"] and status != "done"),
                json.dumps(history, ensure_ascii=False), settings_version, now_iso(), unit_id
            ))
            self.refresh_project_stats(cur["project_id"])

    def revert_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        with conn:
            cur = conn.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
            if not cur:
                return None
            history = json.loads(cur["history_json"])
            if not history:
                return self.get_unit(unit_id)
            last_entry = history.pop()
            conn.execute("""
                UPDATE units
                SET result_text=?, status=?, is_manual=?, history_json=?, updated_at=?
                WHERE id=?
            """, (
                last_entry["previous_text"], last_entry["previous_status"],
                1 if last_entry.get("was_manual") else 0,
                json.dumps(history, ensure_ascii=False), now_iso(), unit_id
            ))
            self.refresh_project_stats(cur["project_id"])
        return self.get_unit(unit_id)

    def log(self, project_id: str, level: str, stage: str, message: str,
            unit_id: Optional[str] = None, provider: Optional[str] = None,
            model: Optional[str] = None, attempt: int = 0) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO logs (project_id, unit_id, timestamp, level, stage, message, provider, model, attempt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, unit_id, now_iso(), level, stage, message, provider, model, attempt))

    def get_logs(self, project_id: str, level: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        q = "SELECT * FROM logs WHERE project_id=?"
        params: List[Any] = [project_id]
        if level:
            q += " AND level=?"
            params.append(level)
        if search:
            q += " AND message LIKE ?"
            params.append(f"%{search}%")
        q += " ORDER BY id DESC LIMIT 1000"
        return [dict(r) for r in conn.execute(q, params).fetchall()]

    def clear_logs(self, project_id: str) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM logs WHERE project_id=?", (project_id,))

    def list_glossary(self, project_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM glossary WHERE project_id=? ORDER BY source_term ASC", (project_id,)).fetchall()
        return [dict(r) for r in rows]

    def upsert_glossary(self, entry: Dict[str, Any]) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO glossary (id, project_id, source_term, target_term, term_type, notes, approved, case_sensitive, match_rule)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_term=excluded.source_term, target_term=excluded.target_term,
                    term_type=excluded.term_type, notes=excluded.notes,
                    approved=excluded.approved, case_sensitive=excluded.case_sensitive,
                    match_rule=excluded.match_rule
            """, (
                entry["id"], entry["project_id"], entry["source_term"], entry["target_term"],
                entry.get("term_type", "general"), entry.get("notes", ""),
                1 if entry.get("approved", True) else 0,
                1 if entry.get("case_sensitive", False) else 0,
                entry.get("match_rule", "exact")
            ))

    def delete_glossary(self, entry_id: str) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM glossary WHERE id=?", (entry_id,))

    def list_tm(self, project_id: str, search: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        q = "SELECT * FROM translation_memory WHERE project_id=?"
        params: List[Any] = [project_id]
        if search:
            q += " AND (source_text LIKE ? OR target_text LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        q += " ORDER BY updated_at DESC"
        return [dict(r) for r in conn.execute(q, params).fetchall()]

    def upsert_tm(self, entry: Dict[str, Any]) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO translation_memory (id, project_id, source_text, target_text, src_lang, tgt_lang, context, approved, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_text=excluded.source_text, target_text=excluded.target_text,
                    approved=excluded.approved, updated_at=excluded.updated_at
            """, (
                entry["id"], entry["project_id"], entry["source_text"], entry["target_text"],
                entry.get("src_lang", "auto"), entry.get("tgt_lang", "he"),
                entry.get("context", ""), 1 if entry.get("approved", True) else 0, now_iso()
            ))

    def clear_tm(self, project_id: str) -> None:
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM translation_memory WHERE project_id=?", (project_id,))

db = Database()
