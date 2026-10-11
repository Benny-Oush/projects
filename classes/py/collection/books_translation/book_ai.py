#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
book_ai.py - עיבוד ספרים באמצעות מודלי בינה מלאכותית (אפליקציה מקומית בקובץ יחיד).

הפעלה:        python book_ai.py            (פותח את הממשק בכתובת http://127.0.0.1:8765)
בדיקות:       python book_ai.py test
דוגמאות:      python book_ai.py samples    (יוצר קבצי EPUB / PDF / MOBI לדוגמה)

עיקרון על: שימור מבנה הספר חשוב יותר משימור הטקסט. הפלט נוצר בהחלפה נקודתית
של טקסט בתוך עותק של הקובץ המקורי (ראו EpubPackage.write_output).
"""
from __future__ import annotations

import base64
import copy
import datetime
import errno
import hashlib
import hmac
import html as htmlmod
import http.client
import io
import json
import math
import os
import posixpath
import random
import re
import select
import shutil
import signal
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from html.entities import name2codepoint
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple

from lxml import etree

APP_VERSION = "1.0"

# ======================================================================
# הגדרות מומלצות לפי מודל
# ======================================================================
# כל רשומה:
#   match     - ביטוי רגולרי על מזהה המודל באותיות קטנות. הרשומה הראשונה שמתאימה מנצחת, לכן הספציפיות קודם.
#   providers - (לא חובה) הרשומה חלה רק על הספקים האלה.
#   settings  - הערכים שיוצעו בטופס. temperature=None משמעו "לא לשלוח טמפרטורה" (ברירת המחדל של הספק).
#   extra     - הנחיות נוספות למודל. מוצעות רק כששדה ההנחיות ריק, ולעולם לא דורסות טקסט של המשתמש. ריק = אין המלצה.
#   notes     - הנימוק להמלצה, מוצג למשתמש.
#   status    - current / legacy (מודל ישן שייתכן שהוסר מהספק).  verified - מתי נבדקו המגבלות מול תיעוד הספק (ריק = לא נבדק).
# מגבלות הקשר והפלט לקוחות מתיעוד הספקים. chunk_chars הוא כלל אצבע ולא תוצאת מדידה: בערך 45% מתקרת הפלט, בהערכה
# שמרנית של 0.7 טוקנים לתו בעברית, ובתקרה של 6000-8000 תווים כדי לשמור על איכות ועקביות. אלה המלצות התחלתיות.
# כדי לתמוך במודל חדש מוסיפים כאן רשומה. מודל שאין לו רשומה פשוט לא יקבל הצעה.
MODEL_PROFILES: List[Dict[str, Any]] = [
    {"id": "claude-5", "label": "Claude 5 (Fable / Opus / Sonnet / Haiku)", "status": "current", "verified": "2026-10",
     "match": r"claude[-_.]?(fable|opus|sonnet|haiku)[-_.]?5|claude[-_.]?5",
     "settings": {"temperature": None, "chunk_chars": 6000, "overlap": 2, "max_output_tokens": 16000, "context_tokens": 1000000,
                  "concurrency": 2},
     "extra": "",
     "notes": ["טמפרטורה לא נשלחת: לפי התיעוד של Anthropic ל-Sonnet 5.5, ערך שאינו ברירת המחדל מחזיר שגיאת 400 (לא נבדק בנפרד ליתר המודלים במשפחה).",
               "הקשר של מיליון טוקנים ופלט עד 128K, כך שגודל המקטע נקבע לפי איכות ועקביות ולא לפי מגבלה טכנית.",
               "חשיבה אדפטיבית צורכת טוקנים מתקרת הפלט, ולכן התקרה 16,000 גדולה בהרבה מגודל המקטע."],
     "source": "platform.claude.com/docs/en/models/overview"},
    {"id": "claude-3-5-sonnet", "label": "Claude 3.5 Sonnet", "status": "legacy", "verified": "",
     "match": r"claude[-_.]?3[-_.]?5[-_.]?sonnet|claude[-_.]?sonnet[-_.]?3[-_.]?5",
     "settings": {"temperature": 0.3, "chunk_chars": 5000, "overlap": 2, "max_output_tokens": 8192, "context_tokens": 200000,
                  "concurrency": 2},
     "extra": "",
     "notes": ["תקרת הפלט היא 8,192 טוקנים, ולכן המקטע מוגבל ל-5,000 תווים (כ-45% מהתקרה) כדי להשאיר מקום לתגיות ולמבנה התשובה.",
               "טמפרטורה נמוכה לעקביות מונחים בתרגום.",
               "מודל ישן: ייתכן שהוסר מה-API אצל הספק."],
     "source": "תיעוד Anthropic (היסטורי)"},
    {"id": "gpt-4o-mini", "label": "GPT-4o mini", "status": "legacy", "verified": "2026-10",
     "match": r"gpt-4o-mini",
     "settings": {"temperature": 0.3, "chunk_chars": 6000, "overlap": 2, "max_output_tokens": 16384, "context_tokens": 128000,
                  "concurrency": 2},
     "extra": "",
     "notes": ["הקשר 128K ופלט עד 16,384 טוקנים.", "מודל קטן יותר: מקטע מתון (6,000 תווים) מקטין סיכון לאובדן הנחיות בטקסט ארוך."],
     "source": "developers.openai.com/api/docs/models"},
    {"id": "gpt-4o", "label": "GPT-4o", "status": "legacy", "verified": "2026-10",
     "match": r"gpt-4o",
     "settings": {"temperature": 0.3, "chunk_chars": 8000, "overlap": 2, "max_output_tokens": 16384, "context_tokens": 128000,
                  "concurrency": 2},
     "extra": "",
     "notes": ["הקשר 128K ופלט עד 16,384 טוקנים: 8,000 תווים מניבים בהערכה כ-5,600 טוקנים, כשליש מהתקרה.",
               "ייתכן שהמודל כבר הוצא משימוש אצל הספק."],
     "source": "developers.openai.com/api/docs/models"},
    {"id": "gpt-4.1", "label": "GPT-4.1", "status": "current", "verified": "",
     "match": r"gpt-4\.1",
     "settings": {"temperature": 0.3, "chunk_chars": 8000, "overlap": 2, "max_output_tokens": 16384, "context_tokens": 1000000,
                  "concurrency": 2},
     "extra": "",
     "notes": ["הקשר של כמיליון טוקנים ופלט עד 32,768; מוגדרת תקרה זהירה של 16,384."],
     "source": "מקורות משניים (לא נבדק מול תיעוד OpenAI)"},
    {"id": "gemini-3", "label": "Gemini 3 (Pro / Flash)", "status": "current", "verified": "2026-10",
     "match": r"gemini-3",
     "settings": {"temperature": None, "chunk_chars": 8000, "overlap": 2, "max_output_tokens": 32768, "context_tokens": 1048576,
                  "concurrency": 2},
     "extra": "",
     "notes": ["טמפרטורה לא נשלחת: Google ממליצה להשאיר אותה על 1.0 ב-Gemini 3, וערך נמוך ממנה עלול לגרום ללולאות או לפגיעה באיכות.",
               "חשיבה דינמית צורכת טוקנים מתקרת הפלט (65,536), ולכן התקרה בהגדרה היא 32,768."],
     "source": "ai.google.dev/gemini-api/docs/gemini-3"},
    {"id": "gemini-2-5", "label": "Gemini 2.5 (Pro / Flash)", "status": "current", "verified": "2026-10",
     "match": r"gemini-2\.5",
     "settings": {"temperature": 0.3, "chunk_chars": 8000, "overlap": 2, "max_output_tokens": 32768, "context_tokens": 1048576,
                  "concurrency": 2},
     "extra": "",
     "notes": ["קלט עד 1,048,576 טוקנים ופלט עד 65,536.", "בדגמי 2.5 טוקני החשיבה נספרים בתקרת הפלט, ולכן התקרה 32,768."],
     "source": "ai.google.dev/gemini-api/docs/models"},
    {"id": "gemini-1-5", "label": "Gemini 1.5 (Pro / Flash)", "status": "legacy", "verified": "",
     "match": r"gemini-1\.5",
     "settings": {"temperature": 0.3, "chunk_chars": 5000, "overlap": 2, "max_output_tokens": 8192, "context_tokens": 1000000,
                  "concurrency": 2},
     "extra": "",
     "notes": ["תקרת פלט של 8,192 טוקנים, ולכן מקטע של 5,000 תווים.", "מודל ישן: ייתכן שהוסר מהספק."],
     "source": "תיעוד Google (היסטורי)"},
    {"id": "local", "label": "מודל מקומי (Ollama)", "status": "current", "verified": "", "providers": ["ollama"],
     "match": r".*",
     "settings": {"temperature": 0.2, "chunk_chars": 2500, "overlap": 1, "max_output_tokens": 4096, "context_tokens": 0,
                  "concurrency": 1},
     "extra": "החזר רק את התרגום, בלי הסברים, הערות או הקדמות. שמור כל תגית בדיוק כפי שהיא במקור.",
     "notes": ["חלון ההקשר של מודל מקומי תלוי בהגדרת השרת (לרוב מאות עד אלפי טוקנים בודדים כברירת מחדל), ולכן מקטע קטן וחפיפה מצומצמת.",
               "מודלים קטנים נוטים להוסיף הערות מסביב לתרגום, ולכן מוצעת הנחיה מפורשת.",
               "מקביליות 1: שרת מקומי בדרך כלל מעבד בקשה אחת בכל פעם."],
     "source": "כלל אצבע (לא נמדד)"},
]


def match_model_profile(provider: str, model: str) -> Optional[Dict[str, Any]]:
    """מחזיר את הרשומה המתאימה למודל, או None אם אין."""
    lowered = (model or "").strip().lower()
    if lowered == "":
        return None
    for profile in MODEL_PROFILES:
        allowed = profile.get("providers")
        if allowed and provider not in allowed:
            continue
        if re.search(profile["match"], lowered) is not None:
            return profile
    return None


def public_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": profile["id"], "label": profile["label"], "status": profile["status"], "verified": profile["verified"],
            "settings": dict(profile["settings"]), "extra": profile.get("extra", ""), "notes": list(profile["notes"]),
            "source": profile.get("source", "")}
APP_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.environ.get("BOOK_AI_HOME") or os.path.join(APP_DIR, "data")
PROJECTS_DIR = os.path.join(HOME_DIR, "projects")
SECRETS_DIR = os.environ.get("BOOK_AI_SECRETS") or os.path.join(os.path.expanduser("~"), ".book_ai")
MAX_UPLOAD_BYTES = int(os.environ.get("BOOK_AI_MAX_UPLOAD_MB", "300")) * 1024 * 1024


# ======================================================================
# 0. טעינת .env
# ======================================================================
def load_dotenv(path: str) -> int:
    """קורא קובץ .env פשוט (KEY=VALUE). לא דורס משתני סביבה קיימים."""
    loaded = 0
    if not os.path.isfile(path):
        return loaded
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line == "" or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            if key != "" and key not in os.environ and value != "":
                os.environ[key] = value
                loaded = loaded + 1
    return loaded


# ======================================================================
# 1. הסתרת מפתחות, שגיאות, כתיבה אטומית, יומן
# ======================================================================
class Redactor:
    """מסיר מפתחות מכל טקסט שנכנס ליומן, להודעות שגיאה או לקבצי מצב."""
    _lock = threading.Lock()
    _secrets: set = set()
    _patterns = [
        re.compile(r"sk-[A-Za-z0-9_\-]{10,}"),
        re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
        re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{10,}"),
        re.compile(r"(?i)((?:api[-_]?key|x-api-key|authorization)[\"']?\s*[:=]\s*[\"']?)[^\s\"',}&]{6,}"),
    ]

    @classmethod
    def register(cls, secret: Optional[str]) -> None:
        if secret is not None and len(secret) >= 6:
            with cls._lock:
                cls._secrets.add(secret)

    @classmethod
    def clean(cls, text: Any) -> str:
        value = text if isinstance(text, str) else str(text)
        with cls._lock:
            known = sorted(cls._secrets, key=len, reverse=True)
        for secret in known:
            value = value.replace(secret, "***")
        for pattern in cls._patterns:
            if pattern.groups >= 1:
                value = pattern.sub(lambda m: m.group(1) + "***", value)
            else:
                value = pattern.sub("***", value)
        return value


ERROR_LABELS = {
    "rate_limit": "מגבלת קצב",
    "timeout": "פסק זמן",
    "api_error": "שגיאת ספק",
    "invalid_key": "מפתח לא תקין",
    "model_unavailable": "מודל לא זמין",
    "context_too_large": "הקשר גדול מדי",
    "bad_response": "תשובה לא תקינה",
    "parse_failure": "כשל בפענוח",
    "corrupt_epub": "EPUB פגום",
    "pdf_no_text": "PDF ללא שכבת טקסט",
    "conversion_failure": "כשל בהמרה",
    "network": "שגיאת רשת",
    "bad_upload": "קובץ לא תקין",
    "internal": "שגיאה פנימית",
}
ERROR_HINTS = {
    "rate_limit": "המתן או הקטן את מספר הבקשות המקבילות; אפשר להגדיר מגבלת בקשות לדקה.",
    "timeout": "הגדל את ה-timeout בהגדרות המתקדמות או הקטן את גודל המקטע.",
    "api_error": "שגיאה זמנית אצל הספק. המערכת תנסה שוב אוטומטית.",
    "invalid_key": "בדוק את המפתח בהגדרות (או בקובץ .env) ולחץ על 'המשך'.",
    "model_unavailable": "בחר מודל אחר מהרשימה או הזן שם מודל ידנית, ובצע בדיקת חיבור.",
    "context_too_large": "המקטע גדול מדי למודל. המערכת תפצל אותו אוטומטית.",
    "bad_response": "המודל החזיר תשובה שלא עומדת בפרוטוקול. נוסה שוב עם הודעת תיקון.",
    "parse_failure": "לא ניתן היה לפענח את תשובת המודל. נסה פורמט אחר (JSON/רשימה) בהגדרות מתקדמות.",
    "corrupt_epub": "הקובץ פגום או אינו EPUB תקין. נסה לתקן אותו (למשל ב-Calibre) והעלה שוב.",
    "pdf_no_text": "ה-PDF סרוק ואין בו שכבת טקסט. OCR אינו נתמך; הפעל OCR חיצוני והעלה שוב.",
    "conversion_failure": "ההמרה נכשלה. התקן Calibre (calibre-ebook.com) כך ש-ebook-convert יהיה ב-PATH.",
    "network": "בדוק את החיבור לרשת ואת כתובת נקודת הקצה.",
    "bad_upload": "העלה קובץ EPUB, PDF או MOBI תקין בגודל מתאים.",
    "internal": "שגיאה בלתי צפויה. ראה לוג להרחבה.",
}


class BookError(Exception):
    """שגיאה מסווגת. kind הוא אחד ממפתחות ERROR_LABELS."""

    def __init__(self, kind: str, message: str, retryable: bool = False,
                 retry_after: Optional[float] = None, http: Optional[int] = None,
                 hint: str = "") -> None:
        super().__init__(Redactor.clean(message))
        self.kind = kind
        self.message = Redactor.clean(message)
        self.retryable = retryable
        self.retry_after = retry_after
        self.http = http
        self.hint = hint if hint != "" else ERROR_HINTS.get(kind, "")


def atomic_write_bytes(path: str, data: bytes) -> None:
    """כתיבה אטומית: קובץ זמני באותה תיקייה, fsync, ואז os.replace."""
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    handle, temp_path = tempfile.mkstemp(prefix=".tmp_", dir=directory)
    try:
        with os.fdopen(handle, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp_path, path)
    except BaseException:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def atomic_write_json(path: str, obj: Any) -> None:
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    atomic_write_bytes(path, Redactor.clean(text).encode("utf-8"))


def read_json(path: str, default: Any = None) -> Any:
    if not os.path.isfile(path):
        return default
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def now_iso() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


class LogBuffer:
    """יומן בזמן אמת, בטוח לשרשורים, עם כתיבה לקובץ jsonl. כל שורה עוברת הסרת מפתחות."""

    def __init__(self, file_path: Optional[str] = None, limit: int = 4000) -> None:
        self.lock = threading.Lock()
        self.entries: List[Dict[str, Any]] = []
        self.counter = 0
        self.limit = limit
        self.file_path = file_path

    def add(self, level: str, message: str, **ctx: Any) -> None:
        clean_ctx: Dict[str, Any] = {}
        for key, value in ctx.items():
            if value is not None and value != "":
                clean_ctx[key] = Redactor.clean(value) if isinstance(value, str) else value
        with self.lock:
            self.counter = self.counter + 1
            entry = {"id": self.counter, "ts": now_iso(), "level": level,
                     "msg": Redactor.clean(message), "ctx": clean_ctx}
            self.entries.append(entry)
            if len(self.entries) > self.limit:
                self.entries = self.entries[len(self.entries) - self.limit:]
            if self.file_path:
                try:
                    os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                    with open(self.file_path, "a", encoding="utf-8") as handle:
                        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
                except OSError:
                    pass

    def since(self, last_id: int) -> List[Dict[str, Any]]:
        with self.lock:
            result = []
            for entry in self.entries:
                if entry["id"] > last_id:
                    result.append(entry)
            return result


# ======================================================================
# 2. אבטחת קבצי ZIP והעלאות
# ======================================================================
MAX_ZIP_ENTRIES = 30000
MAX_ZIP_TOTAL = 2_000_000_000
MAX_ZIP_RATIO = 250


def safe_zip_name(name: str) -> bool:
    """דוחה נתיבים אבסולוטיים, '..' וכוננים (הגנת Zip Slip)."""
    if name == "" or "\x00" in name:
        return False
    if name.startswith("/") or name.startswith("\\") or re.match(r"^[A-Za-z]:", name):
        return False
    parts = name.replace("\\", "/").split("/")
    for part in parts:
        if part == "..":
            return False
    return True


def check_zip(zf: zipfile.ZipFile) -> None:
    infos = zf.infolist()
    if len(infos) > MAX_ZIP_ENTRIES:
        raise BookError("corrupt_epub", "ארכיב עם מספר קבצים חריג (%d)" % len(infos))
    total = 0
    for info in infos:
        if not safe_zip_name(info.filename):
            raise BookError("corrupt_epub", "נתיב חשוד בתוך הארכיב: %r" % info.filename)
        total = total + info.file_size
        if info.file_size > 5 * 1024 * 1024 and info.compress_size > 0:
            ratio = info.file_size / float(info.compress_size)
            if ratio > MAX_ZIP_RATIO:
                raise BookError("corrupt_epub", "יחס דחיסה חשוד (פצצת דחיסה): %s" % info.filename)
        if total > MAX_ZIP_TOTAL:
            raise BookError("corrupt_epub", "גודל כולל לא דחוס חורג מהמותר")


def sniff_format(path: str, filename: str) -> str:
    """מזהה פורמט לפי תוכן (ולא רק לפי סיומת). מחזיר epub / pdf / mobi, או זורק שגיאה."""
    with open(path, "rb") as handle:
        head = handle.read(80)
    extension = os.path.splitext(filename)[1].lower()
    if head[:5] == b"%PDF-":
        return "pdf"
    if head[:4] == b"PK\x03\x04":
        if extension not in (".epub", ""):
            raise BookError("bad_upload", "הסיומת %s אינה תואמת לתוכן ZIP/EPUB" % extension)
        return "epub"
    if len(head) >= 68 and head[60:68] in (b"BOOKMOBI", b"TEXtREAd"):
        return "mobi"
    raise BookError("bad_upload", "סוג הקובץ לא מזוהה (נתמכים: EPUB, PDF, MOBI)")


# ======================================================================
# 3. שפות, כיווניות וזיהוי שפה
# ======================================================================
# (קוד, שם באנגלית, שם בעברית, האם RTL)
LANGUAGES = [
    ("he", "Hebrew", "עברית", True), ("en", "English", "אנגלית", False),
    ("ar", "Arabic", "ערבית", True), ("fa", "Persian", "פרסית", True),
    ("ur", "Urdu", "אורדו", True), ("yi", "Yiddish", "יידיש", True),
    ("ru", "Russian", "רוסית", False), ("uk", "Ukrainian", "אוקראינית", False),
    ("fr", "French", "צרפתית", False), ("de", "German", "גרמנית", False),
    ("es", "Spanish", "ספרדית", False), ("it", "Italian", "איטלקית", False),
    ("pt", "Portuguese", "פורטוגזית", False), ("nl", "Dutch", "הולנדית", False),
    ("pl", "Polish", "פולנית", False), ("cs", "Czech", "צ'כית", False),
    ("sv", "Swedish", "שוודית", False), ("no", "Norwegian", "נורווגית", False),
    ("da", "Danish", "דנית", False), ("fi", "Finnish", "פינית", False),
    ("el", "Greek", "יוונית", False), ("tr", "Turkish", "טורקית", False),
    ("hu", "Hungarian", "הונגרית", False), ("ro", "Romanian", "רומנית", False),
    ("bg", "Bulgarian", "בולגרית", False), ("hr", "Croatian", "קרואטית", False),
    ("sr", "Serbian", "סרבית", False), ("la", "Latin", "לטינית", False),
    ("ja", "Japanese", "יפנית", False), ("zh", "Chinese", "סינית", False),
    ("ko", "Korean", "קוריאנית", False), ("hi", "Hindi", "הינדית", False),
    ("th", "Thai", "תאית", False), ("vi", "Vietnamese", "וייטנאמית", False),
    ("id", "Indonesian", "אינדונזית", False), ("am", "Amharic", "אמהרית", False),
]
RTL_CODES = set(["he", "ar", "fa", "ur", "yi", "ps", "sd", "ug", "dv", "ckb", "iw"])


def resolve_language(value: str) -> Tuple[str, str, bool]:
    """מקבל קוד, שם באנגלית או בעברית, או טקסט חופשי. מחזיר (קוד, שם להצגה, RTL)."""
    text = (value or "").strip()
    lowered = text.lower()
    for code, english, hebrew, rtl in LANGUAGES:
        if lowered == code or lowered == english.lower() or text == hebrew:
            return code, english, rtl
    match = re.match(r"^([a-z]{2,3})(?:[-_][A-Za-z0-9]+)*$", text)
    if match is not None:
        base = match.group(1)
        return text.replace("_", "-"), text, base in RTL_CODES
    for code, english, hebrew, rtl in LANGUAGES:
        if english.lower() in lowered or hebrew in text:
            return code, english, rtl
    return "und", text if text != "" else "unknown", False


def dir_of(code: str) -> str:
    base = (code or "").split("-")[0].lower()
    return "rtl" if base in RTL_CODES else "ltr"


STOPWORDS = {
    "en": "the and of to in is that it was for with as his he she her they you on at by this have from or an be not but are which had were their".split(),
    "fr": "le la les des et en un une est que qui dans pour pas sur au avec il elle ce se ne ses son nous vous".split(),
    "de": "der die das und ist nicht ein eine zu den mit von sie auf für dem sich auch es im ich er wir".split(),
    "es": "el la los las de que y en un una es por con no se para su al lo como más pero sus le ya".split(),
    "it": "il lo la gli le di che e un una è per con non si su al come più ma suo sua da nel".split(),
    "pt": "os as de que e do da em um uma é para com não se por mais mas seu sua ao como".split(),
    "nl": "de het een en van ik te dat die in is niet zijn op aan met als voor had er maar om hij".split(),
}


def detect_language(text: str, hint: str = "") -> str:
    """זיהוי שפה פשוט: לפי כתב, ובכתב לטיני לפי מילות עצירה. hint = מטא־דאטה מהספר."""
    sample = text[:40000]
    counts = {"he": 0, "ar": 0, "ru": 0, "el": 0, "zh": 0, "ja": 0, "ko": 0, "hi": 0, "th": 0, "latin": 0}
    for ch in sample:
        if not ch.isalpha():
            continue
        code = ord(ch)
        if 0x0590 <= code <= 0x05FF:
            counts["he"] = counts["he"] + 1
        elif 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F or 0xFB50 <= code <= 0xFEFF:
            counts["ar"] = counts["ar"] + 1
        elif 0x0400 <= code <= 0x04FF:
            counts["ru"] = counts["ru"] + 1
        elif 0x0370 <= code <= 0x03FF:
            counts["el"] = counts["el"] + 1
        elif 0x3040 <= code <= 0x30FF:
            counts["ja"] = counts["ja"] + 1
        elif 0x4E00 <= code <= 0x9FFF:
            counts["zh"] = counts["zh"] + 1
        elif 0xAC00 <= code <= 0xD7AF:
            counts["ko"] = counts["ko"] + 1
        elif 0x0900 <= code <= 0x097F:
            counts["hi"] = counts["hi"] + 1
        elif 0x0E00 <= code <= 0x0E7F:
            counts["th"] = counts["th"] + 1
        elif code < 0x250:
            counts["latin"] = counts["latin"] + 1
    best = max(counts, key=lambda k: counts[k])
    if counts[best] == 0:
        return (hint.split("-")[0].lower() if hint else "und")
    if best == "ja" or (counts["ja"] > 0 and counts["zh"] > 0):
        return "ja"
    if best == "ar":
        if re.search("[پچژگ]", sample):
            return "fa"
        return "ar"
    if best == "ru":
        return "uk" if re.search("[їєґі]", sample) else "ru"
    if best != "latin":
        return best
    words = re.findall(r"[^\W\d_]+", sample.lower())
    if len(words) == 0:
        return "und"
    best_lang = "en"
    best_score = -1.0
    for lang, stop in STOPWORDS.items():
        stop_set = set(stop)
        hits = 0
        for word in words:
            if word in stop_set:
                hits = hits + 1
        score = hits / float(len(words))
        if score > best_score:
            best_score = score
            best_lang = lang
    if best_score < 0.04 and hint:
        return hint.split("-")[0].lower()
    return best_lang


# ======================================================================
# 4. כלי טקסט
# ======================================================================
WS_RE = re.compile(r"[ \t\r\n\f]+")
TAG_RE = re.compile(r"<(/?)([a-z]{1,2})(\d+)(/?)>")
FOREIGN_MARKUP_RE = re.compile(r"</?[A-Za-z][^<>]*>")
ENTITY_RE = re.compile(r"&(lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);")


def escape_text(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unescape_text(text: str) -> str:
    def replace(match: "re.Match[str]") -> str:
        name = match.group(1)
        if name == "lt":
            return "<"
        if name == "gt":
            return ">"
        if name == "amp":
            return "&"
        if name == "quot":
            return '"'
        if name == "apos":
            return "'"
        try:
            if name.startswith("#x"):
                return chr(int(name[2:], 16))
            return chr(int(name[1:]))
        except (ValueError, OverflowError):
            return match.group(0)
    return ENTITY_RE.sub(replace, text)


def strip_tags(tagged: str) -> str:
    """מסיר תגיות עיצוב זמניות ומחזיר טקסט רגיל (לספירה ולתצוגה)."""
    return unescape_text(TAG_RE.sub("", tagged))


def count_words(text: str) -> int:
    return len(text.split())


def normalize_digits(text: str) -> str:
    out = []
    for ch in text:
        if ch.isdigit() and not ("0" <= ch <= "9"):
            try:
                out.append(str(unicodedata.digit(ch)))
                continue
            except ValueError:
                pass
        out.append(ch)
    return "".join(out)


def number_signature(text: str) -> List[str]:
    found = re.findall(r"\d+(?:[.,]\d+)*", normalize_digits(text))
    found.sort()
    return found


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


# ======================================================================
# 5. קידוד עיצוב פנימי: החלפת רכיבי עיצוב בתגיות ממוספרות ושחזורם
# ======================================================================
EPUB_NS = "http://www.idpf.org/2007/ops"
XHTML_NS = "http://www.w3.org/1999/xhtml"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
EPUB_TYPE = "{%s}type" % EPUB_NS

BLOCK_TAGS = set(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol", "blockquote",
                  "table", "thead", "tbody", "tfoot", "tr", "td", "th", "section", "article", "aside",
                  "figure", "figcaption", "caption", "pre", "dl", "dt", "dd", "header", "footer",
                  "nav", "hr", "body", "main", "address", "details", "summary", "center", "form",
                  "fieldset", "hgroup"])
SKIP_TAGS = set(["script", "style", "svg", "math", "pre", "textarea", "head", "object", "iframe", "audio",
                 "video", "canvas"])
ATOM_KINDS = set(["n", "br", "m"])
WRAP_KIND_BY_TAG = {
    "b": "b", "strong": "b", "i": "i", "em": "i", "cite": "i", "dfn": "i", "var": "i",
    "a": "a", "sup": "u", "sub": "d",
    "span": "s", "small": "s", "big": "s", "abbr": "s", "code": "s", "kbd": "s", "samp": "s",
    "mark": "s", "u": "s", "s": "s", "strike": "s", "del": "s", "ins": "s", "q": "s", "font": "s",
    "bdi": "s", "bdo": "s", "time": "s", "tt": "s", "label": "s", "data": "s",
}


def local_name(tag: Any) -> str:
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1].lower()


def epub_type_of(el: Any) -> str:
    return (el.get(EPUB_TYPE) or el.get("epub:type") or el.get("role") or "").lower()


def has_block_descendant(el: Any) -> bool:
    for desc in el.iterdescendants():
        if local_name(desc.tag) in BLOCK_TAGS:
            return True
    return False


def is_block_like(el: Any) -> bool:
    name = local_name(el.tag)
    if name in BLOCK_TAGS or name in SKIP_TAGS:
        return True
    if not isinstance(el.tag, str):
        return False
    if len(el) > 0 and has_block_descendant(el):
        return True
    return False


def inline_kind(el: Any) -> str:
    if not isinstance(el.tag, str):
        return "m"
    name = local_name(el.tag)
    if name == "br":
        return "br"
    if name == "a":
        etype = epub_type_of(el)
        if "noteref" in etype:
            return "n"
        return "a"
    kind = WRAP_KIND_BY_TAG.get(name)
    if kind is not None:
        return kind
    return "m"


def element_items(el: Any) -> List[Tuple[str, Any]]:
    """מפרק אלמנט לרשימת פריטים: ('t', טקסט) או ('e', צאצא)."""
    items: List[Tuple[str, Any]] = []
    if el.text:
        items.append(("t", el.text))
    for child in el:
        items.append(("e", child))
        if child.tail:
            items.append(("t", child.tail))
    return items


def split_runs(items: List[Tuple[str, Any]]) -> List[Tuple[int, int]]:
    """מחלק לרצפים רציפים של תוכן שורה (ללא צאצאי בלוק). מחזיר טווחים [start, end)."""
    runs: List[Tuple[int, int]] = []
    start = -1
    index = 0
    while index < len(items):
        kind, obj = items[index]
        breaker = kind == "e" and is_block_like(obj)
        if breaker:
            if start >= 0:
                runs.append((start, index))
                start = -1
        else:
            if start < 0:
                start = index
        index = index + 1
    if start >= 0:
        runs.append((start, len(items)))
    return runs


def run_has_text(run_items: List[Tuple[str, Any]]) -> bool:
    for kind, obj in run_items:
        if kind == "t":
            if obj.strip() != "":
                return True
        else:
            if isinstance(obj.tag, str) and local_name(obj.tag) not in SKIP_TAGS:
                if "".join(obj.itertext()).strip() != "":
                    return True
    return False


def encode_run(run_items: List[Tuple[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """מקודד רצף תוכן למחרוזת עם תגיות ממוספרות. מחזיר (טקסט_מתויג, רשימת_תגיות).
    כל תגית נשמרת בצד עם התכונות המקוריות; למודל נשלחת רק התגית הממוספרת."""
    tags: List[Dict[str, Any]] = []
    counter = [0]

    def walk(el: Any) -> str:
        counter[0] = counter[0] + 1
        number = counter[0]
        kind = inline_kind(el)
        if kind in ATOM_KINDS:
            xml_text = etree.tostring(el, encoding="unicode", with_tail=False)
            tags.append({"n": number, "k": kind, "t": None, "a": None, "x": xml_text})
            return "<%s%d/>" % (kind, number)
        entry = {"n": number, "k": kind, "t": el.tag, "a": dict(el.attrib), "x": None}
        tags.append(entry)
        inner = escape_text(el.text or "")
        for child in el:
            inner = inner + walk(child) + escape_text(child.tail or "")
        return "<%s%d>%s</%s%d>" % (kind, number, inner, kind, number)

    pieces: List[str] = []
    for kind, obj in run_items:
        if kind == "t":
            pieces.append(escape_text(obj))
        else:
            pieces.append(walk(obj))
    joined = "".join(pieces)
    joined = WS_RE.sub(" ", joined).strip()
    return joined, tags


def tokenize_tagged(text: str) -> List[Tuple[str, Any]]:
    """מפרק מחרוזת מתויגת לאסימונים: ('text', s) | ('open', kind, n) | ('close', kind, n) | ('atom', kind, n)."""
    tokens: List[Tuple[str, Any]] = []
    position = 0
    for match in TAG_RE.finditer(text):
        if match.start() > position:
            tokens.append(("text", text[position:match.start()]))
        closing = match.group(1) == "/"
        selfclose = match.group(4) == "/"
        kind = match.group(2)
        number = int(match.group(3))
        if selfclose:
            tokens.append(("atom", kind, number))
        elif closing:
            tokens.append(("close", kind, number))
        else:
            tokens.append(("open", kind, number))
        position = match.end()
    if position < len(text):
        tokens.append(("text", text[position:]))
    return tokens


def validate_tags(source_tagged: str, out_tagged: str, tags: List[Dict[str, Any]]) -> List[str]:
    """בדיקת תגיות: כולן חזרו, בדיוק פעם אחת, מקוננות תקין, ללא תגיות חדשות."""
    errors: List[str] = []
    by_number: Dict[int, Dict[str, Any]] = {}
    for entry in tags:
        by_number[entry["n"]] = entry
    found_foreign: List[str] = []
    for candidate in FOREIGN_MARKUP_RE.findall(out_tagged):
        if TAG_RE.fullmatch(candidate) is None:
            found_foreign.append(candidate)
    if len(found_foreign) > 0:
        errors.append("נמצאה תגית זרה בפלט: %s" % found_foreign[0])
    seen_open: Dict[int, int] = {}
    seen_close: Dict[int, int] = {}
    seen_atom: Dict[int, int] = {}
    stack: List[int] = []
    for token in tokenize_tagged(out_tagged):
        if token[0] == "text":
            continue
        kind = token[1]
        number = token[2]
        entry = by_number.get(number)
        if entry is None or entry["k"] != kind:
            errors.append("תגית שלא קיימת במקור: %s%d" % (kind, number))
            continue
        if token[0] == "atom":
            if entry["k"] not in ATOM_KINDS:
                errors.append("תגית עוטפת הוחזרה כתגית סגורה: %s%d" % (kind, number))
            seen_atom[number] = seen_atom.get(number, 0) + 1
        elif token[0] == "open":
            if entry["k"] in ATOM_KINDS:
                errors.append("תגית יחידה הוחזרה כעוטפת: %s%d" % (kind, number))
            seen_open[number] = seen_open.get(number, 0) + 1
            stack.append(number)
        else:
            seen_close[number] = seen_close.get(number, 0) + 1
            if len(stack) == 0 or stack[-1] != number:
                errors.append("קינון שגוי סביב %s%d" % (kind, number))
                if number in stack:
                    while len(stack) > 0 and stack[-1] != number:
                        stack.pop()
                    if len(stack) > 0:
                        stack.pop()
            else:
                stack.pop()
    if len(stack) > 0:
        errors.append("תגית שלא נסגרה: %d" % stack[-1])
    for entry in tags:
        number = entry["n"]
        label = "%s%d" % (entry["k"], number)
        if entry["k"] in ATOM_KINDS:
            if seen_atom.get(number, 0) != 1:
                errors.append("התגית %s חסרה או כפולה" % label)
        else:
            if seen_open.get(number, 0) != 1 or seen_close.get(number, 0) != 1:
                errors.append("התגית %s חסרה או כפולה" % label)
    deduped: List[str] = []
    for message in errors:
        if message not in deduped:
            deduped.append(message)
    return deduped[:6]


LTR_RUN_RE = re.compile(r"(?<![\w])([A-Za-z0-9][A-Za-z0-9'’.,:;!?\-]*(?:[ ]+[A-Za-z0-9][A-Za-z0-9'’.,:;!?\-]*)+)")


def isolate_ltr_text(text: str) -> List[Tuple[str, Any]]:
    """בטקסט RTL: עוטף רצפי מילים לועזיות (שתיים ומעלה) ב-bdi כדי לשמור על סדרן."""
    result: List[Tuple[str, Any]] = []
    position = 0
    for match in LTR_RUN_RE.finditer(text):
        piece = match.group(1)
        trimmed = piece.rstrip(".,:;!?-'’")
        if len(trimmed.split()) < 2:
            continue
        if match.start(1) > position:
            result.append(("t", text[position:match.start(1)]))
        bdi = etree.Element("{%s}bdi" % XHTML_NS)
        bdi.set("dir", "ltr")
        bdi.text = trimmed
        result.append(("e", bdi))
        position = match.start(1) + len(trimmed)
    if position < len(text):
        result.append(("t", text[position:]))
    return result


def decode_run(out_tagged: str, tags: List[Dict[str, Any]], rtl_isolate: bool = False) -> List[Tuple[str, Any]]:
    """בונה מחדש פריטי תוכן (טקסט ואלמנטים) מהמחרוזת המתויגת, עם התכונות המקוריות."""
    by_number: Dict[int, Dict[str, Any]] = {}
    for entry in tags:
        by_number[entry["n"]] = entry
    root_items: List[Tuple[str, Any]] = []
    stack: List[Any] = []

    def add_text(value: str) -> None:
        if value == "":
            return
        text = unescape_text(value)
        if len(stack) == 0:
            if rtl_isolate:
                for item in isolate_ltr_text(text):
                    root_items.append(item)
            else:
                root_items.append(("t", text))
            return
        parent = stack[-1]
        if len(parent) == 0:
            parent.text = (parent.text or "") + text
        else:
            last = parent[-1]
            last.tail = (last.tail or "") + text

    def add_element(el: Any) -> None:
        if len(stack) == 0:
            root_items.append(("e", el))
        else:
            stack[-1].append(el)

    for token in tokenize_tagged(out_tagged):
        kind = token[0]
        if kind == "text":
            add_text(token[1])
        elif kind == "atom":
            entry = by_number[token[2]]
            add_element(etree.fromstring(entry["x"].encode("utf-8")))
        elif kind == "open":
            entry = by_number[token[2]]
            el = etree.Element(entry["t"], entry["a"] or {})
            stack.append(el)
        else:
            el = stack.pop()
            add_element(el)
    return root_items


def rebuild_block(block: Any, items: List[Tuple[str, Any]]) -> None:
    """מרכיב מחדש את תוכן הבלוק מרשימת פריטים. צאצאי בלוק שלא נגענו בהם נשמרים כפי שהם."""
    for child in list(block):
        block.remove(child)
    block.text = None
    last = None
    for kind, obj in items:
        if kind == "t":
            if last is None:
                block.text = (block.text or "") + obj
            else:
                last.tail = (last.tail or "") + obj
        else:
            obj.tail = None
            block.append(obj)
            last = obj


# ======================================================================
# 6. חבילת EPUB: קריאה, מודל פנימי עם הפניה למקור, החלפה נקודתית וכתיבה
# ======================================================================
DOC_MEDIA_TYPES = set(["application/xhtml+xml", "text/html"])
TEXT_UNIT_TYPES = set(["PARAGRAPH", "QUOTE", "LIST_ITEM", "FOOTNOTE", "TABLE_CELL", "CAPTION"])
OK_STATUSES = set(["done", "manual"])


def fix_html_entities(data: bytes) -> bytes:
    """ממיר ישויות HTML בשם (למשל &nbsp;) לישויות מספריות, כדי שמפענח XML לא יאבד אותן."""
    def replace(match: "re.Match[bytes]") -> bytes:
        name = match.group(1).decode("ascii")
        if name in ("lt", "gt", "amp", "quot", "apos"):
            return match.group(0)
        code = name2codepoint.get(name)
        if code is None:
            return match.group(0)
        return ("&#%d;" % code).encode("ascii")
    return re.sub(rb"&([A-Za-z][A-Za-z0-9]*);", replace, data)


def parse_xml(data: bytes) -> Any:
    """מפענח XML/XHTML בצורה בטוחה (ללא ישויות חיצוניות וללא רשת)."""
    import io
    parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True,
                             load_dtd=False, huge_tree=True, remove_blank_text=False)
    try:
        tree = etree.parse(io.BytesIO(fix_html_entities(data)), parser)
    except etree.XMLSyntaxError as exc:
        raise BookError("corrupt_epub", "קובץ XML פגום: %s" % exc)
    if tree.getroot() is None:
        raise BookError("corrupt_epub", "קובץ XML ריק או פגום")
    return tree


def serialize_xml(tree: Any) -> bytes:
    return etree.tostring(tree, xml_declaration=True, encoding="UTF-8")


def path_of(el: Any) -> str:
    parts: List[int] = []
    node = el
    while node.getparent() is not None:
        parent = node.getparent()
        index = 0
        for sibling in parent:
            if isinstance(sibling.tag, str):
                index = index + 1
                if sibling is node:
                    break
        parts.append(index)
        node = parent
    result = ""
    position = len(parts) - 1
    while position >= 0:
        result = result + "/*[%d]" % parts[position]
        position = position - 1
    return result


def build_path_map(root: Any) -> Dict[str, Any]:
    mapping: Dict[str, Any] = {"": root}
    stack: List[Tuple[str, Any]] = [("", root)]
    while len(stack) > 0:
        path, el = stack.pop()
        index = 0
        for child in el:
            if isinstance(child.tag, str):
                index = index + 1
                child_path = path + "/*[%d]" % index
                mapping[child_path] = child
                stack.append((child_path, child))
    return mapping


def unit_kind_for(name: str, in_quote: bool, in_footnote: bool, in_nav: bool) -> Tuple[str, int]:
    if len(name) == 2 and name[0] == "h" and name[1] in "123456":
        return "HEADING", int(name[1])
    if in_nav:
        return "TOC_ENTRY", 0
    if in_footnote:
        return "FOOTNOTE", 0
    if name == "li":
        return "LIST_ITEM", 0
    if name in ("td", "th"):
        return "TABLE_CELL", 0
    if name in ("figcaption", "caption"):
        return "CAPTION", 0
    if in_quote or name == "blockquote":
        return "QUOTE", 0
    return "PARAGRAPH", 0


def extract_units_from_tree(root: Any, file_path: str, chapter_no: int, is_nav_doc: bool) -> Tuple[List[Dict[str, Any]], str, int]:
    """מחלץ רכיבי טקסט מעץ XHTML. מחזיר (יחידות, כותרת פרק, מספר תמונות)."""
    units: List[Dict[str, Any]] = []
    counter = [0]
    images = 0
    for el in root.iter():
        if local_name(el.tag) in ("img", "image"):
            images = images + 1

    def walk(el: Any, path: str, in_quote: bool, in_footnote: bool, in_nav: bool) -> None:
        name = local_name(el.tag)
        if name in SKIP_TAGS:
            return
        if name == "blockquote":
            in_quote = True
        etype = epub_type_of(el)
        if "footnote" in etype or "endnote" in etype or "rearnote" in etype:
            in_footnote = True
        if name == "nav":
            in_nav = True
        if name != "html":
            items = element_items(el)
            runs = split_runs(items)
            run_index = 0
            for start, end in runs:
                run_items = items[start:end]
                if run_has_text(run_items):
                    tagged, tags = encode_run(run_items)
                    if tagged != "":
                        counter[0] = counter[0] + 1
                        kind, level = unit_kind_for(name, in_quote, in_footnote, in_nav)
                        units.append({
                            "id": "c%02d_e%03d" % (chapter_no, counter[0]),
                            "ch": chapter_no, "o": counter[0], "type": kind, "level": level,
                            "file": file_path, "xpath": path, "run": run_index,
                            "tagged": tagged, "tags": tags, "words": count_words(strip_tags(tagged)),
                            "scope": "toc" if (is_nav_doc or in_nav) else "content",
                            "status": "pending", "out": None, "warn": [], "err": None,
                            "att": 0, "chunk": None,
                        })
                run_index = run_index + 1
        child_index = 0
        for child in el:
            if not isinstance(child.tag, str):
                continue
            child_index = child_index + 1
            if name == "html" or is_block_like(child):
                walk(child, path + "/*[%d]" % child_index, in_quote, in_footnote, in_nav)

    walk(root, "", False, False, False)
    title = ""
    for unit in units:
        if unit["type"] == "HEADING":
            title = strip_tags(unit["tagged"])
            break
    if title == "":
        for el in root.iter():
            if local_name(el.tag) == "title" and el.text and el.text.strip() != "":
                title = el.text.strip()
                break
    return units, title, images


ANCHOR_SKIP_TAGS = set(["table", "tbody", "thead", "tfoot", "tr", "ul", "ol", "dl", "select", "colgroup"])


class EpubPackage:
    """קורא חבילת EPUB: קובץ החבילה (OPF), מניפסט, שדרה, ניווט ומטא־דאטה."""

    def __init__(self, path: str) -> None:
        import io
        self.path = path
        try:
            self.zf = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            raise BookError("corrupt_epub", "הקובץ אינו ארכיב ZIP תקין")
        check_zip(self.zf)
        self.infos = self.zf.infolist()
        self.names = set()
        for info in self.infos:
            self.names.add(info.filename)
        if "META-INF/container.xml" not in self.names:
            raise BookError("corrupt_epub", "חסר META-INF/container.xml")
        container = parse_xml(self.read("META-INF/container.xml")).getroot()
        self.opf_path = ""
        for el in container.iter():
            if local_name(el.tag) == "rootfile" and el.get("full-path"):
                self.opf_path = el.get("full-path")
                break
        if self.opf_path == "" or self.opf_path not in self.names:
            raise BookError("corrupt_epub", "קובץ החבילה (OPF) לא נמצא")
        self.opf_dir = posixpath.dirname(self.opf_path)
        self.opf_tree = parse_xml(self.read(self.opf_path))
        self.manifest: Dict[str, Dict[str, Any]] = {}
        self.manifest_by_path: Dict[str, Dict[str, Any]] = {}
        self.spine: List[str] = []
        self.spine_toc = ""
        self.title = ""
        self.creator = ""
        self.language = ""
        self.identifier = ""
        self._parse_opf()

    def read(self, name: str) -> bytes:
        return self.zf.read(name)

    def close(self) -> None:
        self.zf.close()

    def resolve(self, base_file: str, href: str) -> str:
        clean = urllib.parse.unquote(href.split("#")[0])
        return posixpath.normpath(posixpath.join(posixpath.dirname(base_file), clean))

    def _parse_opf(self) -> None:
        root = self.opf_tree.getroot()
        for el in root.iter():
            name = local_name(el.tag)
            if name == "item" and el.get("id") and el.get("href"):
                full = self.resolve(self.opf_path, el.get("href"))
                entry = {"id": el.get("id"), "href": el.get("href"), "path": full,
                         "type": (el.get("media-type") or "").lower(),
                         "props": (el.get("properties") or "").split()}
                self.manifest[entry["id"]] = entry
                self.manifest_by_path[full] = entry
            elif name == "itemref" and el.get("idref"):
                self.spine.append(el.get("idref"))
            elif name == "spine":
                self.spine_toc = el.get("toc") or ""
            elif name == "title" and self.title == "" and el.text:
                self.title = el.text.strip()
            elif name == "creator" and self.creator == "" and el.text:
                self.creator = el.text.strip()
            elif name == "language" and self.language == "" and el.text:
                self.language = el.text.strip()
            elif name == "identifier" and self.identifier == "" and el.text:
                self.identifier = el.text.strip()

    def nav_path(self) -> str:
        for entry in self.manifest.values():
            if "nav" in entry["props"]:
                return entry["path"]
        return ""

    def ncx_path(self) -> str:
        if self.spine_toc != "" and self.spine_toc in self.manifest:
            return self.manifest[self.spine_toc]["path"]
        for entry in self.manifest.values():
            if entry["type"] == "application/x-dtbncx+xml":
                return entry["path"]
        return ""

    def document_files(self) -> List[Tuple[str, str]]:
        """קבצי המסמך לפי סדר השדרה: (נתיב, תפקיד). תפקיד: content / nav."""
        result: List[Tuple[str, str]] = []
        seen = set()
        nav = self.nav_path()
        for idref in self.spine:
            entry = self.manifest.get(idref)
            if entry is None or entry["type"] not in DOC_MEDIA_TYPES:
                continue
            if entry["path"] not in self.names or entry["path"] in seen:
                continue
            seen.add(entry["path"])
            result.append((entry["path"], "nav" if entry["path"] == nav else "content"))
        if nav != "" and nav not in seen and nav in self.names:
            result.append((nav, "nav"))
        return result

    # ---------------- חילוץ מודל פנימי ----------------
    def extract_model(self) -> Dict[str, Any]:
        chapters: List[Dict[str, Any]] = []
        units: List[Dict[str, Any]] = []
        images = 0
        # פרק 0: מטא־דאטה (כותרת הספר)
        meta_units: List[Dict[str, Any]] = []
        for el in self.opf_tree.getroot().iter():
            if local_name(el.tag) == "title" and el.text and el.text.strip() != "":
                meta_units.append({
                    "id": "c00_e001", "ch": 0, "o": 1, "type": "META", "level": 0, "file": self.opf_path,
                    "xpath": path_of(el), "run": 0, "tagged": escape_text(el.text.strip()), "tags": [],
                    "words": count_words(el.text), "scope": "meta", "status": "pending", "out": None,
                    "warn": [], "err": None, "att": 0, "chunk": None})
                break
        chapters.append({"index": 0, "title": "מטא־דאטה", "file": self.opf_path, "kind": "meta", "count": len(meta_units)})
        units.extend(meta_units)
        chapter_no = 0
        for path, role in self.document_files():
            chapter_no = chapter_no + 1
            tree = parse_xml(self.read(path))
            file_units, title, file_images = extract_units_from_tree(tree.getroot(), path, chapter_no, role == "nav")
            images = images + file_images
            chapters.append({"index": chapter_no, "title": title or posixpath.basename(path), "file": path,
                             "kind": role, "count": len(file_units)})
            units.extend(file_units)
        ncx = self.ncx_path()
        if ncx != "" and ncx in self.names:
            chapter_no = chapter_no + 1
            tree = parse_xml(self.read(ncx))
            ncx_units: List[Dict[str, Any]] = []
            order = 0
            for el in tree.getroot().iter():
                if local_name(el.tag) == "text" and el.getparent() is not None \
                        and local_name(el.getparent().tag) in ("navlabel", "doctitle", "docauthor") \
                        and el.text and el.text.strip() != "":
                    order = order + 1
                    ncx_units.append({
                        "id": "c%02d_e%03d" % (chapter_no, order), "ch": chapter_no, "o": order,
                        "type": "TOC_ENTRY", "level": 0, "file": ncx, "xpath": path_of(el), "run": 0,
                        "tagged": escape_text(el.text.strip()), "tags": [], "words": count_words(el.text),
                        "scope": "toc", "status": "pending", "out": None, "warn": [], "err": None,
                        "att": 0, "chunk": None})
            chapters.append({"index": chapter_no, "title": "תוכן עניינים (NCX)", "file": ncx, "kind": "ncx", "count": len(ncx_units)})
            units.extend(ncx_units)
        image_files = 0
        for entry in self.manifest.values():
            if entry["type"].startswith("image/"):
                image_files = image_files + 1
        paragraphs = 0
        headings = 0
        words = 0
        for unit in units:
            if unit["scope"] != "content":
                continue
            words = words + unit["words"]
            if unit["type"] == "HEADING":
                headings = headings + 1
            elif unit["type"] in TEXT_UNIT_TYPES:
                paragraphs = paragraphs + 1
        sample_parts: List[str] = []
        sample_len = 0
        for unit in units:
            if unit["scope"] == "content" and unit["type"] != "HEADING":
                sample_parts.append(strip_tags(unit["tagged"]))
                sample_len = sample_len + len(sample_parts[-1])
                if sample_len > 30000:
                    break
        language = detect_language(" ".join(sample_parts), self.language)
        stats = {
            "chapters": chapter_no - (1 if ncx != "" and ncx in self.names else 0),
            "documents": len(self.document_files()), "headings": headings, "paragraphs": paragraphs,
            "words": words, "images": max(images, image_files), "language": language,
            "declared_language": self.language, "title": self.title, "author": self.creator,
        }
        return {"chapters": chapters, "units": units, "stats": stats}

    # ---------------- כתיבה חזרה ----------------
    def write_output(self, out_path: str, units: List[Dict[str, Any]], opts: Dict[str, Any]) -> Dict[str, Any]:
        """יוצר עותק של הקובץ המקורי ומחליף נקודתית רק את הטקסט של יחידות שעובדו.
        opts: mode (replace|bilingual), src_lang, tgt_lang, flip_dir, set_lang, layout, rtl_isolate."""
        mode = opts.get("mode", "replace")
        src_lang = opts.get("src_lang", "und")
        tgt_lang = opts.get("tgt_lang", "und")
        tgt_dir = dir_of(tgt_lang)
        src_dir = dir_of(src_lang)
        flip = bool(opts.get("flip_dir", False)) and mode == "replace"
        layout = opts.get("layout")
        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for unit in units:
            if unit["status"] in OK_STATUSES and unit.get("out"):
                by_file.setdefault(unit["file"], []).append(unit)
        modified: Dict[str, bytes] = {}
        extra: Dict[str, bytes] = {}
        applied = 0
        css_path = posixpath.join(self.opf_dir, "bai-style.css")
        docs = self.document_files()
        doc_paths = []
        for path, role in docs:
            doc_paths.append(path)
        process_files = set(by_file.keys())
        if flip or layout:
            for path in doc_paths:
                process_files.add(path)
        for path in sorted(process_files):
            if path == self.opf_path:
                continue
            tree, count = self.render_document(path, by_file.get(path, []), opts)
            applied = applied + count
            modified[path] = serialize_xml(tree)
        ncx = self.ncx_path()
        if ncx in by_file and ncx not in modified:
            tree = parse_xml(self.read(ncx))
            path_map = build_path_map(tree.getroot())
            for unit in by_file[ncx]:
                block = path_map[unit["xpath"]]
                applied = applied + self._apply_block(block, [unit], dict(opts, mode="replace"), src_dir, tgt_dir, src_lang, tgt_lang)
            modified[ncx] = serialize_xml(tree)
        # קובץ החבילה (OPF)
        opf_tree = parse_xml(self.read(self.opf_path))
        opf_root = opf_tree.getroot()
        for unit in by_file.get(self.opf_path, []):
            block = build_path_map(opf_root).get(unit["xpath"])
            if block is not None:
                applied = applied + self._apply_block(block, [unit], dict(opts, mode="replace"), src_dir, tgt_dir, src_lang, tgt_lang)
        if flip:
            for el in opf_root.iter():
                if local_name(el.tag) == "spine":
                    el.set("page-progression-direction", tgt_dir)
        if opts.get("set_lang") and tgt_lang != "und":
            done = False
            for el in opf_root.iter():
                if local_name(el.tag) == "language":
                    el.text = tgt_lang
                    done = True
                    break
            if not done:
                for el in opf_root.iter():
                    if local_name(el.tag) == "metadata":
                        lang_el = etree.SubElement(el, "{http://purl.org/dc/elements/1.1/}language")
                        lang_el.text = tgt_lang
                        break
        if layout:
            for el in opf_root.iter():
                if local_name(el.tag) == "manifest":
                    ns = etree.QName(el.tag).namespace
                    tag = "{%s}item" % ns if ns else "item"
                    item = etree.SubElement(el, tag)
                    item.set("id", "bai-style-css")
                    item.set("href", posixpath.relpath(css_path, self.opf_dir) if self.opf_dir else css_path)
                    item.set("media-type", "text/css")
                    break
            extra[css_path] = build_layout_css(layout, tgt_dir == "rtl").encode("utf-8")
        modified[self.opf_path] = serialize_xml(opf_tree)
        if flip:
            for entry in self.manifest.values():
                if entry["type"] == "text/css" and entry["path"] in self.names:
                    text = self.read(entry["path"]).decode("utf-8", errors="replace")
                    modified[entry["path"]] = mirror_css(text).encode("utf-8")
        self._write_zip(out_path, modified, extra)
        return {"applied": applied, "modified_files": len(modified)}

    def render_document(self, path: str, units: List[Dict[str, Any]], opts: Dict[str, Any], anchors: bool = False,
                        all_units: Optional[List[Dict[str, Any]]] = None) -> Tuple[Any, int]:
        """מעבד מסמך אחד בדיוק כמו write_output (החלפת טקסט, היפוך כיוון, פריסה) ומחזיר (עץ, מספר החלפות) בלי לכתוב ארכיון.
        anchors=True (לתצוגה חיה בלבד) מוסיף לכל יחידה של המסמך עוגן ריק עם המזהה bai-u-<id>, כדי שאפשר יהיה לגלול אליה."""
        src_lang = opts.get("src_lang", "und")
        tgt_lang = opts.get("tgt_lang", "und")
        tgt_dir = dir_of(tgt_lang)
        src_dir = dir_of(src_lang)
        flip = bool(opts.get("flip_dir", False)) and opts.get("mode", "replace") == "replace"
        layout = opts.get("layout")
        css_path = posixpath.join(self.opf_dir, "bai-style.css")
        doc_paths = []
        for doc_path, role in self.document_files():
            doc_paths.append(doc_path)
        tree = parse_xml(self.read(path))
        root = tree.getroot()
        path_map = build_path_map(root)
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for unit in units:
            if unit["file"] == path and unit["status"] in OK_STATUSES and unit.get("out"):
                groups.setdefault(unit["xpath"], []).append(unit)
        applied = 0
        for xpath, group in groups.items():
            block = path_map.get(xpath)
            if block is None:
                raise BookError("internal", "הפניה למקור לא נמצאה: %s %s" % (path, xpath))
            applied = applied + self._apply_block(block, group, opts, src_dir, tgt_dir, src_lang, tgt_lang)
        if path in doc_paths:
            if flip:
                root.set("dir", tgt_dir)
                if tgt_lang != "und":
                    root.set("lang", tgt_lang)
                    root.set(XML_LANG, tgt_lang)
                for el in root.iter():
                    style = el.get("style") if isinstance(el.tag, str) else None
                    if style:
                        el.set("style", mirror_css(style))
                    if local_name(el.tag) == "style" and el.text:
                        el.text = mirror_css(el.text)
            if layout:
                self._apply_layout_to_doc(root, path, css_path, layout)
        if anchors:
            seen = set()
            for unit in (all_units if all_units is not None else units):
                if unit["file"] != path or unit["id"] in seen:
                    continue
                seen.add(unit["id"])
                block = path_map.get(unit["xpath"])
                if block is not None:
                    self._insert_anchor(block, unit["id"])
        return tree, applied

    def _insert_anchor(self, block: Any, unit_id: str) -> None:
        if not isinstance(block.tag, str) or local_name(block.tag) in ANCHOR_SKIP_TAGS:
            return
        ns = etree.QName(block.tag).namespace
        span = etree.Element("{%s}span" % ns if ns else "span")
        span.set("id", "bai-u-" + unit_id)
        span.set("class", "bai-anchor")
        span.tail = block.text
        block.text = None
        block.insert(0, span)

    def _apply_block(self, block: Any, group: List[Dict[str, Any]], opts: Dict[str, Any],
                     src_dir: str, tgt_dir: str, src_lang: str, tgt_lang: str) -> int:
        mode = opts.get("mode", "replace")
        isolate = bool(opts.get("rtl_isolate", False)) and tgt_dir == "rtl"
        items = element_items(block)
        runs = split_runs(items)
        count = 0
        content_group = group[0]["scope"] == "content"
        if mode == "bilingual" and content_group:
            plain_block = True
            for kind, obj in items:
                if kind == "e" and is_block_like(obj):
                    plain_block = False
            if plain_block and len(runs) == 1 and len(group) == 1:
                unit = group[0]
                clone = copy.deepcopy(block)
                clone_items = element_items(clone)
                clone_runs = split_runs(clone_items)
                start, end = clone_runs[0]
                new_items = decode_run(unit["out"], unit["tags"], isolate)
                clone_items[start:end] = new_items
                rebuild_block(clone, clone_items)
                for el in clone.iter():
                    if isinstance(el.tag, str) and "id" in el.attrib:
                        del el.attrib["id"]
                existing = clone.get("class")
                clone.set("class", (existing + " " if existing else "") + "bai-tr")
                if tgt_lang != "und":
                    clone.set("lang", tgt_lang)
                    clone.set(XML_LANG, tgt_lang)
                clone.set("dir", tgt_dir)
                if src_dir != tgt_dir:
                    block.set("dir", src_dir)
                block.addnext(clone)
                return 1
            for unit in sorted(group, key=lambda u: u["run"], reverse=True):
                start, end = runs[unit["run"]]
                ns = etree.QName(block.tag).namespace if isinstance(block.tag, str) else None
                span = etree.Element("{%s}span" % ns if ns else "span")
                span.set("class", "bai-tr")
                span.set("dir", tgt_dir)
                if tgt_lang != "und":
                    span.set("lang", tgt_lang)
                inner = decode_run(unit["out"], unit["tags"], isolate)
                for kind, obj in inner:
                    if kind == "t":
                        if len(span) == 0:
                            span.text = (span.text or "") + obj
                        else:
                            span[-1].tail = (span[-1].tail or "") + obj
                    else:
                        span.append(obj)
                br = etree.Element("{%s}br" % ns if ns else "br")
                items[end:end] = [("e", br), ("e", span)]
                count = count + 1
            rebuild_block(block, items)
            return count
        for unit in sorted(group, key=lambda u: u["run"], reverse=True):
            start, end = runs[unit["run"]]
            items[start:end] = decode_run(unit["out"], unit["tags"], isolate and unit["scope"] == "content")
            count = count + 1
        rebuild_block(block, items)
        return count

    def _apply_layout_to_doc(self, root: Any, path: str, css_path: str, layout: Dict[str, Any]) -> None:
        head = None
        for el in root.iter():
            if local_name(el.tag) == "head":
                head = el
                break
        if head is None:
            return
        if layout.get("strip_inline_styles"):
            for el in root.iter():
                if isinstance(el.tag, str) and "style" in el.attrib:
                    del el.attrib["style"]
        if layout.get("drop_original_css"):
            for el in list(head):
                name = local_name(el.tag)
                if name == "style" or (name == "link" and "stylesheet" in (el.get("rel") or "").lower()):
                    head.remove(el)
        ns = etree.QName(root.tag).namespace
        link = etree.SubElement(head, "{%s}link" % ns if ns else "link")
        link.set("rel", "stylesheet")
        link.set("type", "text/css")
        link.set("href", posixpath.relpath(css_path, posixpath.dirname(path) or "."))

    def _write_zip(self, out_path: str, modified: Dict[str, bytes], extra: Dict[str, bytes]) -> None:
        directory = os.path.dirname(out_path)
        if directory != "":
            os.makedirs(directory, exist_ok=True)
        temp_path = out_path + ".tmp"
        ordered = list(self.infos)
        for i in range(len(ordered)):
            if ordered[i].filename == "mimetype" and i != 0:
                ordered.insert(0, ordered.pop(i))
                break
        with zipfile.ZipFile(temp_path, "w") as out:
            for info in ordered:
                name = info.filename
                if name.endswith("/"):
                    continue
                data = modified[name] if name in modified else self.read(name)
                new_info = zipfile.ZipInfo(name, date_time=info.date_time)
                new_info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
                new_info.external_attr = info.external_attr
                out.writestr(new_info, data)
            for name, data in extra.items():
                out.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
        os.replace(temp_path, out_path)


# ======================================================================
# 7. כיווניות ו-CSS
# ======================================================================
_SWAP_PROPS = re.compile(
    r"(?<![\w-])(margin-left|margin-right|padding-left|padding-right|border-left(?:-[a-z]+)?|"
    r"border-right(?:-[a-z]+)?|left|right)(\s*:)")
_SWAP_VALUES = re.compile(r"(?<![\w-])(text-align|float|clear)(\s*:\s*)(left|right)(?![\w-])", re.I)
_SWAP_SHORT = re.compile(r"(?<![\w-])(margin|padding)(\s*:\s*)([^;}{]+)", re.I)


def mirror_css(css: str) -> str:
    """הופך רק תכונות תלויות כיוון (יישור, שוליים, ריפוד, ציפה, מיקום). שאר העיצוב נשאר."""
    def swap_prop(match: "re.Match[str]") -> str:
        name = match.group(1).lower()
        if "left" in name:
            name = name.replace("left", "right")
        else:
            name = name.replace("right", "left")
        return name + match.group(2)

    def swap_value(match: "re.Match[str]") -> str:
        value = "right" if match.group(3).lower() == "left" else "left"
        return match.group(1) + match.group(2) + value

    def swap_short(match: "re.Match[str]") -> str:
        raw = match.group(3)
        if "(" in raw or "!" in raw:
            return match.group(0)
        parts = raw.split()
        if len(parts) == 4:
            temp = parts[1]
            parts[1] = parts[3]
            parts[3] = temp
            return match.group(1) + match.group(2) + " ".join(parts)
        return match.group(0)

    result = _SWAP_PROPS.sub(swap_prop, css)
    result = _SWAP_VALUES.sub(swap_value, result)
    result = _SWAP_SHORT.sub(swap_short, result)
    return result


THEMES = {
    "white": ("#ffffff", "#111111", "#0b57d0"),
    "sepia": ("#f4ecd8", "#3b2f1e", "#7a4a12"),
    "dark": ("#14161a", "#d9dce1", "#8ab4f8"),
}


def build_layout_css(layout: Dict[str, Any], rtl: bool) -> str:
    """CSS לדריסת עימוד/עיצוב (מטרות 7 ו-8). נוגע רק בשכבת התצוגה."""
    rules: List[str] = []
    body_props: List[str] = []
    family = (layout.get("font_family") or "").strip()
    if family != "":
        body_props.append("font-family:%s !important" % family)
    size = str(layout.get("font_size") or "").strip()
    if size != "":
        body_props.append("font-size:%s%% !important" % size)
    line = str(layout.get("line_height") or "").strip()
    if line != "":
        body_props.append("line-height:%s !important" % line)
    margin = str(layout.get("margin") or "").strip()
    if margin != "":
        body_props.append("margin-left:%s%% !important" % margin)
        body_props.append("margin-right:%s%% !important" % margin)
    max_width = str(layout.get("max_width") or "").strip()
    if max_width != "":
        body_props.append("max-width:%sem !important" % max_width)
        body_props.append("margin-left:auto !important")
        body_props.append("margin-right:auto !important")
    theme = layout.get("theme") or "keep"
    if theme in THEMES:
        background, color, link = THEMES[theme]
        body_props.append("background:%s !important" % background)
        body_props.append("color:%s !important" % color)
        rules.append("a{color:%s !important}" % link)
    if len(body_props) > 0:
        rules.insert(0, "html,body{%s}" % ";".join(body_props))
    align = layout.get("text_align") or "keep"
    para_style = layout.get("para_style") or "keep"
    para_props: List[str] = []
    if align == "justify":
        para_props.append("text-align:justify !important")
    elif align == "start":
        para_props.append("text-align:start !important")
    if layout.get("hyphenate"):
        para_props.append("hyphens:auto !important")
        para_props.append("-webkit-hyphens:auto !important")
    if para_style == "indent":
        para_props.append("margin-top:0 !important")
        para_props.append("margin-bottom:0 !important")
        para_props.append("text-indent:1.4em !important")
        rules.append("h1+p,h2+p,h3+p,hr+p,blockquote+p,.bai-first{text-indent:0 !important}")
    elif para_style == "spacing":
        para_props.append("margin-top:0 !important")
        para_props.append("margin-bottom:.9em !important")
        para_props.append("text-indent:0 !important")
    if len(para_props) > 0:
        rules.append("p{%s}" % ";".join(para_props))
    heading_align = layout.get("heading_align") or "keep"
    heading_props: List[str] = ["page-break-after:avoid", "break-after:avoid"]
    if heading_align == "center":
        heading_props.append("text-align:center !important")
    elif heading_align == "start":
        heading_props.append("text-align:start !important")
    hfamily = (layout.get("heading_font") or "").strip()
    if hfamily != "":
        heading_props.append("font-family:%s !important" % hfamily)
    rules.append("h1,h2,h3,h4,h5,h6{%s}" % ";".join(heading_props))
    extra = (layout.get("custom_css") or "").strip()
    if extra != "":
        rules.append(extra)
    return "\n".join(rules) + "\n"


# ======================================================================
# 8. אימות פלט EPUB
# ======================================================================
def find_epubcheck() -> Optional[List[str]]:
    exe = shutil.which("epubcheck")
    if exe:
        return [exe]
    jar = os.environ.get("EPUBCHECK_JAR", "")
    if jar != "" and os.path.isfile(jar) and shutil.which("java"):
        return ["java", "-jar", jar]
    return None


def collect_ids(data: bytes) -> set:
    found = set()
    for match in re.finditer(rb"""\b(?:id|name)\s*=\s*["']([^"']+)["']""", data):
        found.add(match.group(1).decode("utf-8", errors="replace"))
    return found


def broken_links(pkg: EpubPackage) -> Tuple[int, int, List[str]]:
    """סופר קישורים פנימיים ומחזיר (סה"כ, שבורים, דוגמאות לשבורים)."""
    total = 0
    broken = 0
    samples: List[str] = []
    ids_cache: Dict[str, set] = {}
    sources: List[Tuple[str, str]] = []
    for path, role in pkg.document_files():
        sources.append((path, "xhtml"))
    ncx = pkg.ncx_path()
    if ncx != "" and ncx in pkg.names:
        sources.append((ncx, "ncx"))
    for path, kind in sources:
        tree = parse_xml(pkg.read(path))
        for el in tree.getroot().iter():
            name = local_name(el.tag)
            href = None
            if kind == "xhtml" and name == "a":
                href = el.get("href")
            elif kind == "ncx" and name == "content":
                href = el.get("src")
            if href is None or href == "" or re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:", href):
                continue
            total = total + 1
            target = path if href.startswith("#") else pkg.resolve(path, href)
            fragment = urllib.parse.unquote(href.split("#", 1)[1]) if "#" in href else ""
            problem = ""
            if target not in pkg.names:
                problem = "קובץ חסר"
            elif fragment != "":
                if target not in ids_cache:
                    ids_cache[target] = collect_ids(pkg.read(target))
                if fragment not in ids_cache[target]:
                    problem = "עוגן חסר"
            if problem != "":
                broken = broken + 1
                if len(samples) < 5:
                    samples.append("%s -> %s (%s)" % (path, href, problem))
    return total, broken, samples


def structure_signature(model: Dict[str, Any]) -> Dict[str, List[Tuple[str, int]]]:
    signature: Dict[str, List[Tuple[str, int]]] = {}
    for unit in model["units"]:
        if unit["scope"] == "meta":
            continue
        signature.setdefault(unit["file"], []).append((unit["type"], unit["level"]))
    return signature


def verify_epub(src: EpubPackage, out_path: str, mode: str, expect_lang: str = "",
                structure_may_change: bool = False, log: Optional[LogBuffer] = None) -> Dict[str, Any]:
    """בדיקות לאחר העיבוד (סעיף 15): חבילה, מבנה, תמונות, קישורים, תוכן עניינים, CSS, מטא־דאטה."""
    checks: List[Dict[str, Any]] = []

    def check(name: str, ok: Optional[bool], detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    try:
        out = EpubPackage(out_path)
    except BookError as exc:
        check("פתיחת חבילת הפלט", False, exc.message)
        return {"checks": checks, "table": [], "epubcheck": "", "ok": False}
    bad = out.zf.testzip()
    check("שלמות ארכיב ה-ZIP", bad is None, "" if bad is None else "קובץ פגום: %s" % bad)
    first = out.infos[0].filename if len(out.infos) > 0 else ""
    mimetype_ok = first == "mimetype" and out.infos[0].compress_type == zipfile.ZIP_STORED
    if "mimetype" in src.names:
        check("mimetype ראשון ולא דחוס", mimetype_ok)
    missing = []
    for name in src.names:
        if not name.endswith("/") and name not in out.names:
            missing.append(name)
    check("כל קבצי המקור קיימים בפלט (CSS, גופנים, תמונות, כריכה)", len(missing) == 0,
          "חסרים: %s" % ", ".join(missing[:5]) if missing else "")
    manifest_missing = []
    for entry in out.manifest.values():
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:", entry["href"]) and entry["path"] not in out.names:
            manifest_missing.append(entry["href"])
    check("כל פריטי המניפסט קיימים", len(manifest_missing) == 0, ", ".join(manifest_missing[:5]))
    xml_bad = []
    for path, role in out.document_files():
        try:
            etree.fromstring(out.read(path), etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=True))
        except etree.XMLSyntaxError as exc:
            xml_bad.append("%s: %s" % (path, exc))
    check("כל קובצי ה-XHTML מפוענחים כ-XML תקין", len(xml_bad) == 0, "; ".join(xml_bad[:2]))
    src_model = src.extract_model()
    out_model = out.extract_model()
    table: List[Dict[str, Any]] = []

    def row(label: str, source_value: Any, out_value: Any) -> None:
        table.append({"label": label, "src": source_value, "out": out_value})

    src_stats = src_model["stats"]
    out_stats = out_model["stats"]
    row("פרקים (קבצי מסמך)", src_stats["documents"], out_stats["documents"])
    row("כותרות", src_stats["headings"], out_stats["headings"])
    row("פסקאות ורכיבי טקסט", src_stats["paragraphs"], out_stats["paragraphs"])
    row("מילים", src_stats["words"], out_stats["words"])
    row("תמונות", src_stats["images"], out_stats["images"])
    row("קבצי CSS", sum(1 for e in src.manifest.values() if e["type"] == "text/css"),
        sum(1 for e in out.manifest.values() if e["type"] == "text/css"))
    row("גופנים", sum(1 for e in src.manifest.values() if "font" in e["type"] or e["path"].lower().endswith((".ttf", ".otf", ".woff", ".woff2"))),
        sum(1 for e in out.manifest.values() if "font" in e["type"] or e["path"].lower().endswith((".ttf", ".otf", ".woff", ".woff2"))))
    src_toc = sum(1 for u in src_model["units"] if u["scope"] == "toc")
    out_toc = sum(1 for u in out_model["units"] if u["scope"] == "toc")
    row("רשומות בתוכן העניינים", src_toc, out_toc)
    src_total, src_broken, _ = broken_links(src)
    out_total, out_broken, samples = broken_links(out)
    row("קישורים פנימיים והערות", src_total, out_total)
    row("קישורים פנימיים שבורים", src_broken, out_broken)
    if structure_may_change:
        check("מבנה (מטרה שמשנה מבנה)", None, "דולג: המטרה מותרת לשנות מבנה")
    elif mode == "bilingual":
        ok = out_stats["headings"] >= src_stats["headings"] and out_stats["paragraphs"] >= src_stats["paragraphs"]
        check("כל הכותרות והפסקאות קיימות (מצב דו־לשוני: מותר להכפיל)", ok)
    else:
        src_sig = structure_signature(src_model)
        out_sig = structure_signature(out_model)
        diffs = []
        for file_name, sequence in src_sig.items():
            if out_sig.get(file_name) != sequence:
                diffs.append(file_name)
        check("סדר, סוגים ורמות כותרות זהים לכל הרכיבים בכל פרק", len(diffs) == 0, ", ".join(diffs[:3]))
        check("מספר הפסקאות והכותרות זהה למקור",
              src_stats["headings"] == out_stats["headings"] and src_stats["paragraphs"] == out_stats["paragraphs"])
    images_ok = src_stats["images"] == out_stats["images"] or (mode == "bilingual" and out_stats["images"] >= src_stats["images"])
    check("תמונות וכריכה קיימות", images_ok and len(missing) == 0,
          "במצב דו־לשוני תמונות בתוך פסקאות מועתקות יחד עם הפסקה" if mode == "bilingual" else "")
    check("אין קישורים פנימיים שבורים חדשים", out_broken <= src_broken, "; ".join(samples[:2]))
    check("תוכן העניינים שלם", src_toc == out_toc)
    check("מטא־דאטה: מזהה ומחבר נשמרו", src.identifier == out.identifier and src.creator == out.creator)
    if expect_lang != "":
        check("שפת הספר עודכנה במטא־דאטה", out.language.split("-")[0] == expect_lang.split("-")[0],
              "נמצא: %s" % out.language)
    epubcheck_note = ""
    runner = find_epubcheck()
    if runner is None:
        check("EPUBCheck", None, "לא זמין (הגדר EPUBCHECK_JAR או התקן epubcheck); בוצעו בדיקות פנימיות בלבד")
        epubcheck_note = "EPUBCheck לא זמין"
    else:
        try:
            completed = subprocess.run(runner + [out_path], capture_output=True, text=True, timeout=240)
            output = (completed.stdout + completed.stderr).strip()
            check("EPUBCheck", completed.returncode == 0, output[-400:])
            epubcheck_note = output[-1500:]
        except (OSError, subprocess.SubprocessError) as exc:
            check("EPUBCheck", None, "הרצה נכשלה: %s" % exc)
    out.close()
    all_ok = True
    for item in checks:
        if item["ok"] is False:
            all_ok = False
    return {"checks": checks, "table": table, "epubcheck": epubcheck_note, "ok": all_ok}


# ======================================================================
# 10. בונה EPUB (משמש להמרת PDF ולגיבוי המרת MOBI)
# ======================================================================
BUILDER_CSS = (
    "body{line-height:1.5;margin:0 4%}\n"
    "h1,h2,h3,h4,h5,h6{line-height:1.25;page-break-after:avoid}\n"
    "p{margin:0 0 .8em 0;text-align:start}\n"
    "p.small{font-size:.85em}\n"
    "p.img{text-align:center;text-indent:0}\nimg{max-width:100%}\n"
)


def xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class EpubBuilder:
    def __init__(self, title: str, language: str, author: str = "", identifier: str = "") -> None:
        self.title = title or "Untitled"
        self.language = language if language not in ("", "und") else "en"
        self.author = author
        self.identifier = identifier or ("urn:uuid:%s" % uuid.uuid4())
        self.chapters: List[Tuple[str, str, str]] = []
        self.images: List[Tuple[str, bytes, str]] = []

    def add_image(self, data: bytes, extension: str) -> str:
        extension = extension.lower().replace("jpeg", "jpg")
        if extension not in ("png", "jpg", "gif", "svg", "webp"):
            extension = "png"
        name = "images/img_%04d.%s" % (len(self.images) + 1, extension)
        media = {"png": "image/png", "jpg": "image/jpeg", "gif": "image/gif",
                 "svg": "image/svg+xml", "webp": "image/webp"}[extension]
        self.images.append((name, data, media))
        return name

    def add_chapter(self, title: str, body_xhtml: str) -> str:
        name = "chapter_%03d.xhtml" % (len(self.chapters) + 1)
        self.chapters.append((name, title or name, body_xhtml))
        return name

    def build(self, out_path: str) -> None:
        rtl = dir_of(self.language) == "rtl"
        direction = ' dir="rtl"' if rtl else ""
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n'
                '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
                'xml:lang="%s" lang="%s"%s><head><title>%s</title>'
                '<link rel="stylesheet" type="text/css" href="style.css"/></head><body>')
        files: Dict[str, bytes] = {}
        manifest: List[str] = []
        spine: List[str] = []
        for index, (name, title, body) in enumerate(self.chapters):
            doc = head % (self.language, self.language, direction, xml_escape(title)) + body + "</body></html>"
            files["OEBPS/" + name] = doc.encode("utf-8")
            manifest.append('<item id="ch%d" href="%s" media-type="application/xhtml+xml"/>' % (index + 1, name))
            spine.append('<itemref idref="ch%d"/>' % (index + 1))
        nav_items = "".join('<li><a href="%s">%s</a></li>' % (n, xml_escape(t)) for n, t, b in self.chapters)
        nav_doc = (head % (self.language, self.language, direction, "TOC")) + \
            '<nav epub:type="toc" id="toc"><ol>%s</ol></nav></body></html>' % nav_items
        files["OEBPS/nav.xhtml"] = nav_doc.encode("utf-8")
        points = ""
        for index, (name, title, body) in enumerate(self.chapters):
            points = points + ('<navPoint id="np%d" playOrder="%d"><navLabel><text>%s</text></navLabel>'
                               '<content src="%s"/></navPoint>') % (index + 1, index + 1, xml_escape(title), name)
        files["OEBPS/toc.ncx"] = ('<?xml version="1.0" encoding="UTF-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
                                  '<head><meta name="dtb:uid" content="%s"/></head><docTitle><text>%s</text></docTitle>'
                                  '<navMap>%s</navMap></ncx>' % (xml_escape(self.identifier), xml_escape(self.title), points)).encode("utf-8")
        files["OEBPS/style.css"] = BUILDER_CSS.encode("utf-8")
        for index, (name, data, media) in enumerate(self.images):
            files["OEBPS/" + name] = data
            manifest.append('<item id="img%d" href="%s" media-type="%s"/>' % (index + 1, name, media))
        author = '<dc:creator>%s</dc:creator>' % xml_escape(self.author) if self.author else ""
        progression = ' page-progression-direction="rtl"' if rtl else ""
        opf = ('<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">'
               '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">%s</dc:identifier>'
               '<dc:title>%s</dc:title>%s<dc:language>%s</dc:language>'
               '<meta property="dcterms:modified">%s</meta></metadata><manifest>'
               '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
               '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
               '<item id="css" href="style.css" media-type="text/css"/>%s</manifest><spine toc="ncx"%s>%s</spine></package>') % (
            xml_escape(self.identifier), xml_escape(self.title), author, self.language,
            datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "".join(manifest), progression, "".join(spine))
        files["OEBPS/content.opf"] = opf.encode("utf-8")
        with zipfile.ZipFile(out_path, "w") as out:
            out.writestr("mimetype", b"application/epub+zip", compress_type=zipfile.ZIP_STORED)
            out.writestr("META-INF/container.xml",
                         '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                         '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
                         '</rootfiles></container>', compress_type=zipfile.ZIP_DEFLATED)
            for name, data in files.items():
                out.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)


# ======================================================================
# 11. המרת MOBI -> EPUB (סעיף 3.2)
# ======================================================================
def find_ebook_convert() -> Optional[str]:
    if os.environ.get("BOOK_AI_NO_CALIBRE"):
        return None
    exe = shutil.which("ebook-convert")
    if exe:
        return exe
    for candidate in (r"C:\Program Files\Calibre2\ebook-convert.exe", r"C:\Program Files (x86)\Calibre2\ebook-convert.exe",
                      "/Applications/calibre.app/Contents/MacOS/ebook-convert"):
        if os.path.isfile(candidate):
            return candidate
    return None


MOBI_INSTALL_HELP = ("לא נמצא כלי המרה. התקן Calibre (https://calibre-ebook.com) כך שהפקודה ebook-convert תהיה ב-PATH, "
                     "או התקן ספריית גיבוי: pip install mobi")


def html_to_epub(html_path: str, out_path: str, title: str, language: str, log: LogBuffer) -> None:
    """גיבוי להמרת MOBI: בונה EPUB מקובץ HTML שחולץ (פיצול לפרקים לפי מעברי עמוד וכותרות)."""
    import lxml.html
    with open(html_path, "rb") as handle:
        raw = handle.read()
    document = lxml.html.fromstring(raw)
    base_dir = os.path.dirname(html_path)
    builder = EpubBuilder(title, language)
    body = document.find(".//body")
    if body is None:
        body = document
    for el in list(body.iter()):
        if isinstance(el.tag, str) and ":" in el.tag:
            if el.tag.endswith("pagebreak"):
                el.tag = "hr"
                el.set("class", "bai-pagebreak")
            else:
                el.tag = "div"
    chapters: List[Tuple[str, List[str]]] = []
    current_title = title
    current: List[str] = []

    def flush() -> None:
        if len(current) > 0 and "".join(current).strip() != "":
            chapters.append((current_title, list(current)))
        del current[:]

    for child in list(body):
        if not isinstance(child.tag, str):
            continue
        if child.tag == "hr" and child.get("class") == "bai-pagebreak":
            flush()
            continue
        name = child.tag.lower()
        if name in ("h1", "h2") and len(current) > 0:
            flush()
        if name in ("h1", "h2"):
            current_title = " ".join("".join(child.itertext()).split()) or current_title
        for img in child.iter("img"):
            src = img.get("src") or ""
            target = os.path.join(base_dir, urllib.parse.unquote(src))
            if src != "" and os.path.isfile(target):
                with open(target, "rb") as handle:
                    new_name = builder.add_image(handle.read(), os.path.splitext(target)[1].lstrip("."))
                for attr in list(img.attrib):
                    if attr != "alt":
                        del img.attrib[attr]
                img.set("src", new_name)
                if img.get("alt") is None:
                    img.set("alt", "")
            else:
                img.getparent().remove(img)
        for el in child.iter():
            if isinstance(el.tag, str):
                for attr in list(el.attrib):
                    if attr in ("recindex", "align", "width", "height", "hirecindex", "lorecindex") or ":" in attr:
                        del el.attrib[attr]
        current.append(etree.tostring(child, method="xml", encoding="unicode", with_tail=False))
    flush()
    if len(chapters) == 0:
        raise BookError("conversion_failure", "לא נמצא טקסט בקובץ ה-MOBI שחולץ")
    for chapter_title, parts in chapters:
        builder.add_chapter(chapter_title, "".join(parts))
    builder.build(out_path)


def convert_mobi(src: str, out_epub: str, log: LogBuffer) -> Dict[str, Any]:
    """MOBI -> EPUB תקני: Calibre (ebook-convert) אם קיים, אחרת ספריית mobi. בלי כלי: שגיאה ברורה."""
    exe = find_ebook_convert()
    if exe is not None:
        log.add("info", "ממיר MOBI ל-EPUB באמצעות Calibre", stage="convert")
        try:
            completed = subprocess.run([exe, src, out_epub], capture_output=True, text=True, timeout=900)
        except (OSError, subprocess.SubprocessError) as exc:
            raise BookError("conversion_failure", "הרצת ebook-convert נכשלה: %s" % exc)
        if completed.returncode != 0 or not os.path.isfile(out_epub):
            raise BookError("conversion_failure", "ebook-convert נכשל: %s" % (completed.stderr or completed.stdout)[-400:])
        return {"tool": "calibre", "note": "הומר באמצעות Calibre"}
    try:
        import mobi
    except ImportError:
        raise BookError("conversion_failure", MOBI_INSTALL_HELP)
    log.add("warn", "Calibre לא נמצא; משתמש בספריית mobi כגיבוי (איכות נמוכה יותר)", stage="convert")
    extract_dir = ""
    try:
        extract_dir, result_path = mobi.extract(src)
        if result_path.lower().endswith(".epub"):
            shutil.copy(result_path, out_epub)
        elif result_path.lower().endswith((".html", ".htm")):
            html_to_epub(result_path, out_epub, os.path.splitext(os.path.basename(src))[0], "und", log)
        else:
            raise BookError("conversion_failure", "הספרייה החזירה פורמט שאינו נתמך: %s" % os.path.basename(result_path))
    except BookError:
        raise
    except Exception as exc:
        raise BookError("conversion_failure", "המרת MOBI בספרייה נכשלה: %s. %s" % (exc, MOBI_INSTALL_HELP))
    finally:
        if extract_dir != "":
            shutil.rmtree(extract_dir, ignore_errors=True)
    return {"tool": "mobi-library", "note": "הומר באמצעות ספריית mobi (גיבוי); מומלץ להתקין Calibre לאיכות טובה יותר"}


# ======================================================================
# 12. המרת PDF -> EPUB (סעיף 3.3): מאמץ סביר, עם ציון ביטחון מבני
# ======================================================================
TERMINAL_CHARS = ".!?…:;\"”’»)]؟۔"
BULLET_RE = re.compile(r"^[\u2022\u25CF\u25AA\u25E6\u00B7\u2023\u2043*\-]\s+(.*)$")
ORDERED_RE = re.compile(r"^\(?(\d{1,2})[.)]\s+(.*)$")
PAGE_NUMBER_RE = re.compile(r"^\s*(?:\d{1,4}|[ivxlcdmIVXLCDM]{1,7}|[-–—]\s*\d{1,4}\s*[-–—])\s*$")


def import_pymupdf() -> Any:
    try:
        import pymupdf as module
        return module
    except ImportError:
        pass
    try:
        import fitz as module2
        return module2
    except ImportError:
        raise BookError("conversion_failure", "להמרת PDF נדרשת הספרייה PyMuPDF: pip install pymupdf")


def mode_of(values: List[float]) -> float:
    counts: Dict[float, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    best = 0.0
    best_count = -1
    for value, count in counts.items():
        if count > best_count:
            best = value
            best_count = count
    return best


def ends_sentence(text: str) -> bool:
    stripped = text.rstrip()
    return len(stripped) > 0 and stripped[-1] in TERMINAL_CHARS


def convert_pdf(src: str, out_epub: str, log: LogBuffer) -> Dict[str, Any]:
    fitz = import_pymupdf()
    try:
        document = fitz.open(src)
    except Exception as exc:
        raise BookError("corrupt_epub", "פתיחת ה-PDF נכשלה: %s" % exc)
    if document.needs_pass:
        raise BookError("conversion_failure", "ה-PDF מוגן בסיסמה")
    page_count = document.page_count
    pages: List[Dict[str, Any]] = []
    total_chars = 0
    for page_number in range(page_count):
        page = document[page_number]
        data = page.get_text("dict")
        entries: List[Dict[str, Any]] = []
        for block in data.get("blocks", []):
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    spans: List[Tuple[str, bool, bool]] = []
                    size_chars: Dict[float, int] = {}
                    bold_chars = 0
                    char_total = 0
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if text == "":
                            continue
                        font = (span.get("font") or "").lower()
                        flags = int(span.get("flags", 0))
                        is_bold = bool(flags & 16) or "bold" in font or "black" in font
                        is_italic = bool(flags & 2) or "italic" in font or "oblique" in font
                        spans.append((text, is_bold, is_italic))
                        size_key = round(float(span.get("size", 10.0)) * 2) / 2.0
                        size_chars[size_key] = size_chars.get(size_key, 0) + len(text)
                        char_total = char_total + len(text)
                        if is_bold:
                            bold_chars = bold_chars + len(text)
                    joined = "".join(s[0] for s in spans).replace("\u00a0", " ")
                    if joined.strip() == "":
                        continue
                    bbox = line["bbox"]
                    entries.append({"t": "line", "x0": bbox[0], "y0": bbox[1], "x1": bbox[2], "y1": bbox[3],
                                    "text": joined.strip(), "size": mode_of_weighted(size_chars),
                                    "bold": char_total > 0 and bold_chars / float(char_total) > 0.8,
                                    "spans": spans, "page": page_number})
                    total_chars = total_chars + len(joined)
            elif block.get("type") == 1 and block.get("image"):
                width = int(block.get("width", 0))
                height = int(block.get("height", 0))
                if width >= 40 and height >= 40:
                    entries.append({"t": "img", "data": block["image"], "ext": block.get("ext", "png"),
                                    "y0": block["bbox"][1], "page": page_number})
        pages.append({"w": page.rect.width, "h": page.rect.height, "entries": entries})
    metadata = document.metadata or {}
    document.close()
    if total_chars < max(60, page_count * 20):
        raise BookError("pdf_no_text", "ל-PDF אין שכבת טקסט (%d תווים ב-%d עמודים). זהו כנראה PDF סרוק; OCR אינו נתמך. "
                        "הפעל OCR חיצוני (למשל ocrmypdf) והעלה שוב." % (total_chars, page_count))
    # גודל גוף הטקסט
    size_samples: List[float] = []
    for page in pages:
        for entry in page["entries"]:
            if entry["t"] == "line":
                repeats = max(1, len(entry["text"]) // 10)
                for _ in range(repeats):
                    size_samples.append(entry["size"])
    body_size = mode_of(size_samples)
    # כותרות עליונות/תחתונות ומספרי עמודים
    key_pages: Dict[str, set] = {}
    for page_index, page in enumerate(pages):
        for entry in page["entries"]:
            if entry["t"] != "line":
                continue
            in_margin = entry["y1"] < page["h"] * 0.09 or entry["y0"] > page["h"] * 0.91
            entry["margin"] = in_margin
            if in_margin:
                key = re.sub(r"\d+", "#", entry["text"].lower())
                key_pages.setdefault(key, set()).add(page_index)
    repeat_threshold = max(3, int(page_count * 0.3))
    dropped = 0
    for page in pages:
        kept: List[Dict[str, Any]] = []
        for entry in page["entries"]:
            if entry["t"] == "line" and entry.get("margin"):
                key = re.sub(r"\d+", "#", entry["text"].lower())
                if len(key_pages.get(key, ())) >= repeat_threshold or PAGE_NUMBER_RE.match(entry["text"]):
                    dropped = dropped + 1
                    continue
            kept.append(entry)
        page["entries"] = kept
    margins: List[float] = []
    rights: List[float] = []
    for page in pages:
        for entry in page["entries"]:
            if entry["t"] == "line" and abs(entry["size"] - body_size) < 0.8:
                margins.append(round(entry["x0"] / 2.0) * 2.0)
                rights.append(entry["x1"])
    left_margin = mode_of(margins) if len(margins) > 0 else 0.0
    rights.sort()
    right_margin = rights[int(len(rights) * 0.9)] if len(rights) > 0 else 0.0
    # שלב א: זיהוי כותרות
    flat: List[Dict[str, Any]] = []
    for page in pages:
        for entry in page["entries"]:
            flat.append(entry)
    heading_sizes: List[float] = []
    for index, entry in enumerate(flat):
        if entry["t"] != "line":
            continue
        entry["heading"] = False
        text = entry["text"]
        if len(text) <= 2 and entry["size"] > body_size * 1.8:
            continue
        if entry["size"] >= body_size * 1.12 and not BULLET_RE.match(text):
            entry["heading"] = True
        elif entry["bold"] and len(text.split()) <= 10 and not ends_sentence(text) and not BULLET_RE.match(text):
            gap_before = 99.0
            if index > 0 and flat[index - 1]["t"] == "line" and flat[index - 1]["page"] == entry["page"]:
                gap_before = entry["y0"] - flat[index - 1]["y1"]
            if gap_before > body_size * 0.4 or index == 0:
                entry["heading"] = True
        if entry["heading"] and entry["size"] >= body_size * 1.12:
            heading_sizes.append(round(entry["size"] * 2) / 2.0)
    distinct: List[float] = []
    for size in sorted(set(heading_sizes), reverse=True):
        if len(distinct) == 0 or abs(distinct[-1] - size) > 0.6:
            distinct.append(size)

    def level_for(size: float, bold_only: bool) -> int:
        if bold_only:
            return min(6, len(distinct) + 1)
        for position, bucket in enumerate(distinct):
            if abs(bucket - size) <= 0.6:
                return min(6, position + 1)
        return min(6, len(distinct))
    # שלב ב: בניית רכיבים
    elements: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}
    seen_images: Dict[str, int] = {}
    meta_title = (metadata.get("title") or "").strip()
    if meta_title.lower() in ("", "(anonymous)", "untitled", "microsoft word"):
        meta_title = os.path.splitext(os.path.basename(src))[0]
    meta_author = (metadata.get("author") or "").strip()
    if meta_author.lower() == "(anonymous)":
        meta_author = ""
    builder = EpubBuilder(meta_title, "und", meta_author)

    def flush() -> None:
        if len(current) == 0:
            return
        elements.append(dict(current))
        current.clear()

    def merge_segments(segments: List[Tuple[str, bool, bool]]) -> List[Tuple[str, bool, bool]]:
        merged: List[Tuple[str, bool, bool]] = []
        for text, bold, italic in segments:
            if len(merged) > 0 and merged[-1][1] == bold and merged[-1][2] == italic:
                merged[-1] = (merged[-1][0] + text, bold, italic)
            else:
                merged.append((text, bold, italic))
        return merged

    def append_spans(spans: List[Tuple[str, bool, bool]]) -> None:
        segs = current["segs"]
        if len(segs) > 0 and len(spans) > 0:
            last_text, last_bold, last_italic = segs[-1]
            first_text = spans[0][0]
            stripped = last_text.rstrip()
            if stripped.endswith(("-", "\u00ad")) and len(stripped) >= 2 and stripped[-2].isalpha() and first_text[:1].islower():
                segs[-1] = (stripped[:-1], last_bold, last_italic)
            else:
                segs[-1] = (stripped + " ", last_bold, last_italic)
        for item in spans:
            segs.append(item)
        trimmed = list(spans)
        current["segs"] = merge_segments(segs)

    previous_line: Dict[str, Any] = {}
    for entry in flat:
        if entry["t"] == "img":
            flush()
            digest = hashlib.md5(entry["data"]).hexdigest()
            seen_images[digest] = seen_images.get(digest, 0) + 1
            if seen_images[digest] > 2:
                continue
            elements.append({"k": "img", "name": builder.add_image(entry["data"], entry["ext"])})
            previous_line = {}
            continue
        text = entry["text"]
        if entry["heading"]:
            level = level_for(entry["size"], entry["size"] < body_size * 1.12)
            if len(current) > 0 and current["k"] == "h" and abs(current["size"] - entry["size"]) < 0.6 \
                    and entry["page"] == previous_line.get("page") and entry["y0"] - previous_line.get("y1", 0) < entry["size"] * 1.1:
                append_spans([(" " + text, False, False)])
            else:
                flush()
                current.update({"k": "h", "level": level, "size": entry["size"], "segs": [(text, False, False)]})
            previous_line = entry
            continue
        bullet = BULLET_RE.match(text)
        ordered = ORDERED_RE.match(text)
        spans = entry["spans"]
        list_start = bullet is not None or ordered is not None
        if list_start:
            flush()
            stripped_spans = list(spans)
            first_text = stripped_spans[0][0]
            cut = bullet.group(1) if bullet else ordered.group(2)
            stripped_spans = [(cut, stripped_spans[0][1], stripped_spans[0][2])] if len(stripped_spans) == 1 else \
                [(first_text.lstrip("\u2022\u25CF\u25AA\u25E6\u00B7\u2023\u2043*- ").lstrip("0123456789.) ("), stripped_spans[0][1], stripped_spans[0][2])] + stripped_spans[1:]
            current.update({"k": "li", "ordered": ordered is not None, "size": entry["size"], "segs": merge_segments(stripped_spans)})
            previous_line = entry
            continue
        new_paragraph = False
        if len(current) == 0 or current["k"] == "h":
            new_paragraph = True
        elif abs(current["size"] - entry["size"]) > 0.8:
            new_paragraph = True
        else:
            joined_text = "".join(s[0] for s in current["segs"])
            if entry["page"] != previous_line.get("page"):
                new_paragraph = ends_sentence(joined_text) and not joined_text.rstrip().endswith("-")
            else:
                gap = entry["y0"] - previous_line.get("y1", entry["y0"])
                indent = entry["x0"] - left_margin
                short_previous = previous_line.get("x1", 0) < right_margin - 6 * entry["size"]
                if gap > max(3.0, 0.4 * entry["size"]):
                    new_paragraph = True
                elif current["k"] == "p" and indent > 0.8 * entry["size"] and ends_sentence(joined_text):
                    new_paragraph = True
                elif current["k"] == "p" and short_previous and ends_sentence(joined_text):
                    new_paragraph = True
        if new_paragraph:
            flush()
            current.update({"k": "p", "size": entry["size"], "small": entry["size"] < body_size * 0.88, "segs": list(merge_segments(spans))})
        else:
            append_spans(list(spans))
        previous_line = entry
    flush()
    return finish_pdf_conversion(elements, builder, out_epub, page_count, dropped, body_size, metadata, src, log)


def mode_of_weighted(counts: Dict[float, int]) -> float:
    best = 10.0
    best_count = -1
    for size, count in counts.items():
        if count > best_count:
            best = size
            best_count = count
    return best


def segs_to_html(segs: List[Tuple[str, bool, bool]]) -> str:
    total = 0
    bold_total = 0
    for text, bold, italic in segs:
        total = total + len(text.strip())
        if bold:
            bold_total = bold_total + len(text.strip())
    use_bold = total > 0 and bold_total / float(total) < 0.85
    pieces: List[str] = []
    for text, bold, italic in segs:
        escaped = xml_escape(text)
        if escaped.strip() == "":
            pieces.append(escaped)
            continue
        if italic:
            escaped = "<i>%s</i>" % escaped
        if bold and use_bold:
            escaped = "<b>%s</b>" % escaped
        pieces.append(escaped)
    return "".join(pieces).strip()


def finish_pdf_conversion(elements: List[Dict[str, Any]], builder: EpubBuilder, out_epub: str, page_count: int,
                          dropped: int, body_size: float, metadata: Dict[str, Any], src: str, log: LogBuffer) -> Dict[str, Any]:
    levels: Dict[int, int] = {}
    paragraphs = 0
    list_items = 0
    images = 0
    fragments = 0
    split_errors = 0
    garbled = 0
    plain_all: List[str] = []
    for element in elements:
        if element["k"] == "h":
            levels[element["level"]] = levels.get(element["level"], 0) + 1
            element["text"] = segs_to_html(element["segs"])
        elif element["k"] in ("p", "li"):
            element["text"] = segs_to_html(element["segs"])
            plain = re.sub(r"<[^>]+>", "", element["text"])
            plain_all.append(plain)
            if element["k"] == "p":
                paragraphs = paragraphs + 1
                if len(plain.split()) < 3:
                    fragments = fragments + 1
            else:
                list_items = list_items + 1
            if "\ufffd" in plain or "(cid:" in plain or re.search("[\ue000-\uf8ff]", plain):
                garbled = garbled + 1
        elif element["k"] == "img":
            images = images + 1
    previous_open = False
    for index, element in enumerate(elements):
        if element["k"] == "p" and index + 1 < len(elements) and elements[index + 1]["k"] == "p":
            plain = re.sub(r"<[^>]+>", "", element["text"]).rstrip()
            next_plain = re.sub(r"<[^>]+>", "", elements[index + 1]["text"]).lstrip()
            if plain != "" and not ends_sentence(plain) and next_plain[:1].islower():
                split_errors = split_errors + 1
    language = detect_language(" ".join(plain_all[:400]), "")
    builder.language = language if language != "und" else "en"
    heading_total = 0
    for count in levels.values():
        heading_total = heading_total + count
    split_level = 0
    for level in sorted(levels):
        if levels[level] >= 2:
            split_level = level
            break
    if split_level == 0 and len(levels) > 0:
        split_level = min(levels)
    chapter_title = builder.title
    chapter_parts: List[str] = []
    chapters_added = 0
    open_list = ""

    def close_list() -> None:
        nonlocal open_list
        if open_list != "":
            chapter_parts.append("</%s>" % open_list)
            open_list = ""

    def finish_chapter() -> None:
        nonlocal chapters_added
        close_list()
        if "".join(chapter_parts).strip() != "":
            builder.add_chapter(chapter_title, "".join(chapter_parts))
            chapters_added = chapters_added + 1
        del chapter_parts[:]

    if split_level == 0:
        group = 20
        pages_seen = 0
    for element in elements:
        kind = element["k"]
        if kind == "h":
            close_list()
            if element["level"] <= split_level and len(chapter_parts) > 0:
                finish_chapter()
            if element["level"] <= split_level:
                chapter_title = re.sub(r"<[^>]+>", "", element["text"])
            chapter_parts.append("<h%d>%s</h%d>" % (element["level"], element["text"], element["level"]))
        elif kind == "li":
            tag = "ol" if element["ordered"] else "ul"
            if open_list != tag:
                close_list()
                chapter_parts.append("<%s>" % tag)
                open_list = tag
            chapter_parts.append("<li>%s</li>" % element["text"])
        elif kind == "p":
            close_list()
            chapter_parts.append('<p%s>%s</p>' % (' class="small"' if element.get("small") else "", element["text"]))
        elif kind == "img":
            close_list()
            chapter_parts.append('<p class="img"><img src="%s" alt=""/></p>' % element["name"])
            if split_level == 0 and len("".join(chapter_parts)) > 60000:
                chapter_title = "חלק %d" % (chapters_added + 1)
                finish_chapter()
        if split_level == 0 and len("".join(chapter_parts)) > 60000:
            chapter_title = "חלק %d" % (chapters_added + 1)
            finish_chapter()
    finish_chapter()
    if chapters_added == 0:
        raise BookError("pdf_no_text", "לא זוהה תוכן טקסטואלי שניתן להמיר מה-PDF")
    penalty = 0.0
    paragraph_total = max(1, paragraphs)
    penalty = penalty + min(35.0, 120.0 * fragments / paragraph_total)
    penalty = penalty + min(35.0, 150.0 * split_errors / paragraph_total)
    penalty = penalty + min(30.0, 200.0 * garbled / max(1, paragraphs + list_items))
    if heading_total == 0:
        penalty = penalty + 15.0
    if paragraphs < 3:
        penalty = penalty + 30.0
    score = int(max(0.0, min(100.0, 100.0 - penalty)))
    label = "טובה" if score >= 80 else ("בינונית" if score >= 55 else "נמוכה")
    warnings = ["איכות המבנה ב-PDF אינה מובטחת: כותרות, פסקאות ורשימות משוחזרות בהערכה."]
    if builder.language in ("he", "ar", "fa", "ur"):
        warnings.append("PDF בשפה הנכתבת מימין לשמאל: סדר התווים שחולץ עלול להיות הפוך. בדוק את התצוגה המקדימה.")
    if split_errors > 0:
        warnings.append("%d מקומות חשודים כפיצול שגוי של פסקה." % split_errors)
    if garbled > 0:
        warnings.append("%d רכיבים עם תווים פגומים (ייתכן גופן ללא מיפוי יוניקוד)." % garbled)
    preview: List[Dict[str, Any]] = []
    sample_paragraphs = 0
    for element in elements:
        if element["k"] == "h" and len(preview) < 120:
            preview.append({"t": "h", "level": element["level"], "text": re.sub(r"<[^>]+>", "", element["text"])[:140]})
        elif element["k"] == "p" and sample_paragraphs < 6:
            sample_paragraphs = sample_paragraphs + 1
            preview.append({"t": "p", "text": re.sub(r"<[^>]+>", "", element["text"])[:200]})
    builder.build(out_epub)
    report = {"tool": "pdf-heuristics", "pages": page_count, "headings": heading_total,
              "headings_by_level": levels, "paragraphs": paragraphs, "list_items": list_items, "images": images,
              "dropped_header_footer_lines": dropped, "suspicious_fragments": fragments,
              "suspicious_splits": split_errors, "garbled": garbled, "score": score, "label": label,
              "warnings": warnings, "preview": preview, "body_font_size": body_size, "chapters_created": chapters_added,
              "note": "PDF הומר ל-EPUB לפי היוריסטיקות (ציון ביטחון מבני: %d, %s)" % (score, label)}
    log.add("info", "PDF הומר: %d עמודים, %d כותרות, %d פסקאות, ציון %d" % (page_count, heading_total, paragraphs, score), stage="convert")
    return report


# ======================================================================
# 13. מילון מונחים וזיכרון תרגום (סעיף 7.3)
# ======================================================================
def glossary_relevant(glossary: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    """מחזיר רק את הערכים (עם תרגום מאושר) שהמונח שלהם מופיע בטקסט המקטע."""
    lowered = text.lower()
    result: List[Dict[str, Any]] = []
    for entry in glossary:
        source = (entry.get("source") or "").strip()
        target = (entry.get("target") or "").strip()
        if source == "" or target == "":
            continue
        if source.lower() in lowered:
            result.append(entry)
    return result


def suggest_glossary_terms(units: List[Dict[str, Any]], minimum: int = 3, limit: int = 150) -> List[Dict[str, Any]]:
    """הצעת ערכים אוטומטית: שמות פרטיים וביטויים חוזרים (כתב לטיני). המשתמש מאשר ומשלים תרגום."""
    pattern = re.compile(r"[A-Z][A-Za-z'’\-]+(?:\s+[A-Z][A-Za-z'’\-]+)*")
    counts: Dict[str, int] = {}
    lower_counts: Dict[str, int] = {}
    stop = set()
    for words in STOPWORDS.values():
        for word in words:
            stop.add(word)
    for unit in units:
        if unit["scope"] != "content" or unit["type"] == "HEADING":
            continue
        text = strip_tags(unit["tagged"])
        for word in re.findall(r"\b[a-z][a-z'’\-]{2,}\b", text):
            lower_counts[word] = lower_counts.get(word, 0) + 1
        for match in pattern.finditer(text):
            phrase = match.group(0)
            at_start = match.start() == 0 or text[:match.start()].rstrip().endswith((".", "!", "?", "”", '"', ":"))
            words_in = phrase.split()
            if len(words_in) == 1:
                if at_start or phrase.lower() in stop or lower_counts.get(phrase.lower(), 0) > 0:
                    continue
            else:
                if words_in[0].lower() in stop and at_start:
                    phrase = " ".join(words_in[1:])
                    if phrase == "":
                        continue
            counts[phrase] = counts.get(phrase, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    result: List[Dict[str, Any]] = []
    for phrase, count in ranked:
        if count < minimum:
            break
        if lower_counts.get(phrase.lower(), 0) > count:
            continue
        result.append({"source": phrase, "target": "", "locked": False, "auto": True, "count": count})
        if len(result) >= limit:
            break
    return result


# ======================================================================
# 14. שכבת ספקים (AIProvider)
# ======================================================================
def error_message_from_body(raw: str) -> str:
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            err = parsed.get("error")
            if isinstance(err, dict) and err.get("message"):
                return str(err["message"])
            if isinstance(err, str):
                return err
            if parsed.get("message"):
                return str(parsed["message"])
    except (ValueError, TypeError):
        pass
    return raw[:300]


CONTEXT_PHRASES = ("context length", "maximum context", "too long", "too many tokens", "prompt is too long",
                   "exceeds the maximum", "context window", "input token count", "reduce the length")


def classify_http_error(status: int, raw: str, headers: Any = None) -> BookError:
    message = error_message_from_body(raw)
    lowered = (raw or "").lower()
    retry_after = None
    if headers is not None:
        value = headers.get("Retry-After")
        if value:
            try:
                retry_after = float(value)
            except ValueError:
                retry_after = None
    if status in (401, 403):
        return BookError("invalid_key", "HTTP %d: %s" % (status, message), False, http=status)
    if status == 404:
        if "model" in lowered:
            return BookError("model_unavailable", "HTTP 404: %s" % message, False, http=status)
        return BookError("api_error", "HTTP 404: %s (בדוק את כתובת נקודת הקצה)" % message, False, http=status)
    if status in (408, 504):
        return BookError("timeout", "HTTP %d: %s" % (status, message), True, http=status)
    if status == 429:
        if "insufficient_quota" in lowered:
            return BookError("api_error", "HTTP 429: המכסה נגמרה (%s)" % message, False, http=status,
                             hint="המכסה בחשבון הספק נגמרה; בדוק חיוב ומכסות.")
        return BookError("rate_limit", "HTTP 429: %s" % message, True, retry_after, status)
    if status == 529:
        return BookError("rate_limit", "HTTP 529: הספק עמוס", True, retry_after, status)
    if status == 400 or status == 413:
        for phrase in CONTEXT_PHRASES:
            if phrase in lowered:
                return BookError("context_too_large", "HTTP %d: %s" % (status, message), False, http=status)
        if "model" in lowered and ("not found" in lowered or "does not exist" in lowered or "not supported" in lowered):
            return BookError("model_unavailable", "HTTP %d: %s" % (status, message), False, http=status)
        return BookError("api_error", "HTTP %d: %s" % (status, message), False, http=status)
    if status >= 500:
        return BookError("api_error", "HTTP %d: %s" % (status, message), True, retry_after, status)
    return BookError("api_error", "HTTP %d: %s" % (status, message), False, http=status)


# ---------- כותרות מכסה (Rate limit) ----------
# ספקים שונים מחזירים מפתחות שונים: x-ratelimit-remaining-requests (OpenAI), anthropic-ratelimit-requests-remaining,
# x-ratelimit-remaining (כללי), ratelimit-remaining (טיוטת IETF) ועוד. במקום רשימה קשיחה, מסווגים כל כותרת לפי חלקי השם.
DURATION_PART_RE = re.compile(r"(\d+(?:\.\d+)?)(ms|s|m|h|d)")
DURATION_UNITS = {"ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0, "d": 86400.0}


def parse_rate_number(raw: str) -> Optional[float]:
    text = raw.split(";")[0].strip()
    try:
        value = float(text)
    except ValueError:
        return None
    if value != value or value < 0:
        return None
    if value == int(value):
        return int(value)
    return value


def parse_reset_seconds(raw: str) -> Optional[float]:
    """זמן עד איפוס, בשניות. מקבל מספר שניות, חותמת epoch, משך כמו 6m0s / 20ms / 1h2m, או תאריך RFC3339."""
    original = raw.strip()
    text = original.lower()
    if text == "":
        return None
    try:
        number = float(text)
        if number > 1000000000.0:
            number = number - time.time()
        return max(0.0, number)
    except ValueError:
        pass
    pieces = DURATION_PART_RE.findall(text)
    rebuilt = ""
    total = 0.0
    for amount, unit in pieces:
        rebuilt = rebuilt + amount + unit
        total = total + float(amount) * DURATION_UNITS[unit]
    if len(pieces) > 0 and rebuilt == text:
        return total
    try:
        stamp = datetime.datetime.fromisoformat(original.replace("Z", "+00:00").replace("z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=datetime.timezone.utc)
        delta = (stamp - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
        return max(0.0, delta)
    except ValueError:
        return None


def parse_rate_limit_headers(headers: Any) -> Dict[str, Any]:
    """מחלץ {"requests": {"limit", "remaining", "reset_s"}, "tokens": {...}} מכל מפתח כותרת שנראה כמו מכסה.
    כותרת ספציפית (מכילה requests/tokens) גוברת על כותרת כללית; כותרות של יום/שעה נחלשות מול כותרות של דקה."""
    try:
        items = list(headers.items())
    except AttributeError:
        return {}
    entries: List[Tuple[int, str, str, str]] = []
    for name, value in items:
        lowered = str(name).strip().lower().replace("_", "-")
        if "ratelimit" not in lowered and "rate-limit" not in lowered:
            continue
        if "remaining" in lowered:
            field = "remaining"
        elif "reset" in lowered:
            field = "reset"
        elif "limit" in lowered:
            field = "limit"
        else:
            continue
        rank = 0
        if "token" in lowered:
            scope = "tokens"
            rank = 1 if ("input" in lowered or "output" in lowered) else 2
        elif "request" in lowered:
            scope = "requests"
            rank = 2
        else:
            scope = "requests"
        if "day" in lowered or "hour" in lowered:
            rank = rank - 3
        entries.append((rank, scope, field, str(value)))
    entries.sort(key=lambda entry: entry[0])
    result: Dict[str, Any] = {}
    for rank, scope, field, raw in entries:
        slot = result.setdefault(scope, {})
        if field == "reset":
            seconds = parse_reset_seconds(raw)
            if seconds is not None:
                slot["reset_s"] = seconds
        else:
            number = parse_rate_number(raw)
            if number is not None:
                slot[field] = number
    cleaned: Dict[str, Any] = {}
    for scope, slot in result.items():
        if "limit" in slot or "remaining" in slot:
            cleaned[scope] = slot
    return cleaned


class Aborted(Exception):
    """נזרקת כשהמשתמש עצר את העבודה. מוגדרת כאן כי גם שכבת הרשת זורקת אותה באמצע בקשה."""


# ---------- תעבורה ניתנת להפסקה ----------
# הרעיון: urllib רגיל חוסם את השרשור בתוך recv עד לפסק הזמן המלא (עד 120 שניות ויותר). כאן כל המתנה על השקע
# מפורקת לפרוסות של POLL_SECONDS, ובין פרוסה לפרוסה נבדק אירוע הביטול. כך עצירה מתממשת בתוך שבריר שנייה,
# בלי להשאיר שרשור "זומבי" שמחכה לתשובה שאף אחד לא צריך. שאר ההתנהגות של urllib (פרוקסי, הפניות, TLS) נשמרת.
POLL_SECONDS = 0.25
MAX_RESPONSE_BYTES = 64 * 1024 * 1024
CONNECT_PENDING_CODES = set([errno.EINPROGRESS, errno.EWOULDBLOCK, errno.EALREADY, errno.EAGAIN, 10035])


def is_timeout_error(exc: BaseException) -> bool:
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return True
    if isinstance(exc, ssl.SSLError) and "timed out" in str(exc).lower():
        return True
    return False


def abortable_connect(address: Tuple[str, int], timeout: Any, source_address: Any, cancel: Optional[threading.Event]) -> socket.socket:
    """חיבור TCP בפרוסות קצרות (select), עם בדיקת ביטול בכל פרוסה. מחזיר שקע חוסם עם פסק זמן."""
    host = address[0]
    port = address[1]
    try:
        limit = float(timeout)
    except (TypeError, ValueError):
        limit = 30.0
    if limit <= 0:
        limit = 30.0
    deadline = time.monotonic() + limit
    last_error: Optional[BaseException] = None
    infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    for family, socktype, proto, canon, sockaddr in infos:
        if cancel is not None and cancel.is_set():
            raise Aborted()
        sock = socket.socket(family, socktype, proto)
        try:
            if source_address:
                sock.bind(source_address)
            sock.setblocking(False)
            code = sock.connect_ex(sockaddr)
            if code != 0 and code not in CONNECT_PENDING_CODES:
                raise OSError(code, os.strerror(code))
            while code != 0:
                if cancel is not None and cancel.is_set():
                    raise Aborted()
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise socket.timeout("timed out")
                readable, writable, failed = select.select([], [sock], [sock], min(POLL_SECONDS, remaining))
                if len(writable) > 0 or len(failed) > 0:
                    code = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    if code != 0:
                        raise OSError(code, os.strerror(code))
                    break
            sock.settimeout(limit)
            return sock
        except Aborted:
            sock.close()
            raise
        except OSError as exc:
            sock.close()
            last_error = exc
        except BaseException:
            sock.close()
            raise
    if last_error is not None:
        raise last_error
    raise OSError("getaddrinfo returned empty list")


class AbortableRaw(io.RawIOBase):
    """שכבת קריאה גולמית מעל AbortableSocket. BufferedReader יושב עליה, ולכן HTTPResponse רגיל עובד בלי שינוי."""

    def __init__(self, owner: "AbortableSocket") -> None:
        super().__init__()
        self.owner = owner

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: Any) -> int:
        return self.owner.recv_into_abortable(buffer)

    def close(self) -> None:
        if not self.closed:
            super().close()
            self.owner.release_ref()


class AbortableSocket:
    """עטיפה לשקע: קריאה וכתיבה בפרוסות קצרות, בדיקת ביטול בין פרוסות, ופסק זמן סרק מצטבר (idle_timeout)."""

    def __init__(self, sock: socket.socket, cancel: Optional[threading.Event], idle_timeout: float) -> None:
        self.inner = sock
        self.cancel = cancel
        self.idle_timeout = float(idle_timeout)
        self.refs = 0
        self.closed_flag = False
        sock.settimeout(POLL_SECONDS)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)

    def check_cancel(self) -> None:
        if self.cancel is not None and self.cancel.is_set():
            raise Aborted()

    def sendall(self, data: Any, flags: int = 0) -> None:
        view = memoryview(data).cast("B")
        deadline = time.monotonic() + self.idle_timeout
        while len(view) > 0:
            self.check_cancel()
            try:
                sent = self.inner.send(view, flags)
            except OSError as exc:
                if is_timeout_error(exc):
                    if time.monotonic() < deadline:
                        continue
                    raise socket.timeout("timed out")
                raise
            if sent > 0:
                deadline = time.monotonic() + self.idle_timeout
            view = view[sent:]

    def recv_into_abortable(self, buffer: Any) -> int:
        deadline = time.monotonic() + self.idle_timeout
        while True:
            self.check_cancel()
            try:
                return self.inner.recv_into(buffer)
            except OSError as exc:
                if is_timeout_error(exc):
                    if time.monotonic() < deadline:
                        continue
                    raise socket.timeout("timed out")
                raise

    def makefile(self, mode: str = "rb", buffering: Any = None, *args: Any, **kwargs: Any) -> Any:
        self.refs = self.refs + 1
        return io.BufferedReader(AbortableRaw(self), 65536)

    def release_ref(self) -> None:
        self.refs = self.refs - 1
        if self.closed_flag and self.refs <= 0:
            self.inner.close()

    def close(self) -> None:
        self.closed_flag = True
        if self.refs <= 0:
            self.inner.close()


class AbortableConnectionMixin:
    cancel_event: Optional[threading.Event] = None
    idle_timeout: float = 120.0

    def connect(self) -> None:
        cancel = self.cancel_event

        def create(address: Any, timeout: Any = None, source_address: Any = None, *args: Any, **kwargs: Any) -> socket.socket:
            return abortable_connect(address, timeout, source_address, cancel)

        self._create_connection = create  # type: ignore[attr-defined]
        super().connect()  # type: ignore[misc]
        self.sock = AbortableSocket(self.sock, cancel, self.idle_timeout)  # type: ignore[attr-defined]


class AbortableHTTPConnection(AbortableConnectionMixin, http.client.HTTPConnection):
    pass


class AbortableHTTPSConnection(AbortableConnectionMixin, http.client.HTTPSConnection):
    pass


_ssl_lock = threading.Lock()
_ssl_context: Optional[ssl.SSLContext] = None


def shared_ssl_context() -> ssl.SSLContext:
    global _ssl_context
    with _ssl_lock:
        if _ssl_context is None:
            _ssl_context = ssl.create_default_context()
        return _ssl_context


class AbortableHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, cancel: Optional[threading.Event], idle_timeout: float) -> None:
        super().__init__()
        self.cancel = cancel
        self.idle_timeout = idle_timeout

    def make_connection(self, host: str, **kwargs: Any) -> Any:
        conn = AbortableHTTPConnection(host, **kwargs)
        conn.cancel_event = self.cancel
        conn.idle_timeout = self.idle_timeout
        return conn

    def http_open(self, req: Any) -> Any:
        return self.do_open(self.make_connection, req)


class AbortableHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, cancel: Optional[threading.Event], idle_timeout: float) -> None:
        super().__init__(context=shared_ssl_context())
        self.cancel = cancel
        self.idle_timeout = idle_timeout

    def make_connection(self, host: str, **kwargs: Any) -> Any:
        conn = AbortableHTTPSConnection(host, **kwargs)
        conn.cancel_event = self.cancel
        conn.idle_timeout = self.idle_timeout
        return conn

    def https_open(self, req: Any) -> Any:
        return self.do_open(self.make_connection, req, context=shared_ssl_context())


def read_stream(stream: Any, cancel: Optional[threading.Event]) -> str:
    """קריאה במקטעים של 16KB. בין מקטע למקטע נבדק הביטול, ויש תקרה לגודל התשובה."""
    parts: List[bytes] = []
    total = 0
    while True:
        if cancel is not None and cancel.is_set():
            raise Aborted()
        piece = stream.read(16384)
        if not piece:
            break
        total = total + len(piece)
        if total > MAX_RESPONSE_BYTES:
            raise BookError("bad_response", "תשובת הספק גדולה מדי", False)
        parts.append(piece)
    return b"".join(parts).decode("utf-8", errors="replace")


def report_headers(sink: Optional[Callable[[Any], None]], headers: Any) -> None:
    if sink is None:
        return
    try:
        sink(headers)
    except Exception:
        pass  # כשל בניתוח כותרות מכסה לעולם לא מפיל בקשה


def http_json(method: str, url: str, headers: Dict[str, str], body: Optional[Dict[str, Any]], timeout: float,
              cancel: Optional[threading.Event] = None, on_headers: Optional[Callable[[Any], None]] = None) -> Any:
    """בקשת JSON. אם cancel מופעל, הבקשה נקטעת בתוך POLL_SECONDS ונזרקת Aborted (גם באמצע חיבור, שליחה או קריאה)."""
    if cancel is not None and cancel.is_set():
        raise Aborted()
    data = None
    all_headers = dict(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        all_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=all_headers)
    opener = urllib.request.build_opener(AbortableHTTPHandler(cancel, timeout), AbortableHTTPSHandler(cancel, timeout))
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = read_stream(response, cancel)
            report_headers(on_headers, response.headers)
    except urllib.error.HTTPError as exc:
        report_headers(on_headers, exc.headers)  # גם תשובת 429 נושאת מידע על המכסה
        try:
            raw_error = read_stream(exc, cancel)
        except Aborted:
            raise
        except Exception:
            raw_error = ""
        raise classify_http_error(exc.code, raw_error, exc.headers)
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout) or "timed out" in str(reason).lower():
            raise BookError("timeout", "פסק זמן בחיבור לספק", True)
        raise BookError("network", "שגיאת רשת: %s" % reason, True)
    except (socket.timeout, TimeoutError):
        raise BookError("timeout", "פסק זמן בקריאה מהספק", True)
    except (ConnectionError, OSError) as exc:
        if is_timeout_error(exc):
            raise BookError("timeout", "פסק זמן בקריאה מהספק", True)
        raise BookError("network", "שגיאת חיבור: %s" % exc, True)
    except http.client.HTTPException as exc:
        raise BookError("network", "תשובה חלקית או פגומה מהספק: %s" % exc, True)
    try:
        return json.loads(raw)
    except ValueError:
        raise BookError("parse_failure", "תשובת הספק אינה JSON תקין: %s" % raw[:200], True)


class AIProvider:
    id = "base"
    label = "base"
    needs_key = True
    default_base = ""
    native_json = False
    env_key = ""
    is_local = False

    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg
        self.model = cfg.get("model") or ""
        self.api_key = cfg.get("api_key") or ""
        self.base_url = (cfg.get("base_url") or self.default_base).rstrip("/")
        self.timeout = float(cfg.get("timeout") or 120)
        self.temperature = cfg.get("temperature")
        self.max_output = int(cfg.get("max_output_tokens") or 8192)
        self.cancel: Optional[threading.Event] = None  # ה-Job מציב כאן את אירוע העצירה שלו
        self.rate_info: Dict[str, Any] = {}  # תמונת המכסה האחרונה שנראתה בכותרות (מוחלפת בשלמותה, לכן קריאה בטוחה)
        Redactor.register(self.api_key)

    def call_json(self, method: str, url: str, headers: Dict[str, str], body: Optional[Dict[str, Any]]) -> Any:
        """כל קריאות הרשת של הספקים עוברות כאן, כדי שעצירה תקטע אותן מיד."""
        return http_json(method, url, headers, body, self.timeout, self.cancel, self.note_rate_headers)

    def note_rate_headers(self, headers: Any) -> None:
        parsed = parse_rate_limit_headers(headers)
        if len(parsed) > 0:
            snapshot = dict(parsed)
            snapshot["seen_at"] = time.time()
            snapshot["provider"] = self.id
            self.rate_info = snapshot

    def list_models(self) -> List[str]:
        raise BookError("api_error", "הספק אינו תומך ברשימת מודלים; הזן שם מודל ידנית")

    def complete(self, system: str, user: str, want_json: bool) -> Tuple[str, Dict[str, int]]:
        raise NotImplementedError

    def test_connection(self) -> Dict[str, Any]:
        """בדיקת חיבור וזמינות המודל. לא מניחה שהמודל זמין."""
        if self.needs_key and self.api_key == "":
            raise BookError("invalid_key", "לא הוזן מפתח עבור %s" % self.label)
        models: List[str] = []
        listing_note = ""
        try:
            models = self.list_models()
        except BookError as exc:
            if exc.kind in ("invalid_key", "network", "timeout"):
                raise
            listing_note = exc.message
        if self.model != "" and len(models) > 0:
            bare = [m.split("/")[-1] if self.id == "gemini" else m for m in models]
            if self.model not in models and self.model not in bare:
                raise BookError("model_unavailable", "המודל %s לא מופיע ברשימת הספק" % self.model)
        if self.model != "":
            text, usage = self.complete("Reply with the single word: OK", "ping", False)
            return {"ok": True, "message": "החיבור תקין והמודל זמין", "models": models[:300], "sample": text[:40]}
        return {"ok": True, "message": "החיבור תקין (לא נבחר מודל)%s" % (" - " + listing_note if listing_note else ""),
                "models": models[:300], "sample": ""}


class OpenAICompatProvider(AIProvider):
    id = "openai"
    label = "OpenAI"
    default_base = "https://api.openai.com/v1"
    native_json = True
    env_key = "OPENAI_API_KEY"

    def headers(self) -> Dict[str, str]:
        result = {"User-Agent": "book-ai/%s" % APP_VERSION}
        if self.api_key != "":
            result["Authorization"] = "Bearer " + self.api_key
        return result

    def list_models(self) -> List[str]:
        data = self.call_json("GET", self.base_url + "/models", self.headers(), None)
        names = []
        for item in data.get("data", []):
            if item.get("id"):
                names.append(item["id"])
        names.sort()
        return names

    def complete(self, system: str, user: str, want_json: bool) -> Tuple[str, Dict[str, int]]:
        body: Dict[str, Any] = {"model": self.model,
                                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if self.temperature is not None and self.temperature != "":
            body["temperature"] = float(self.temperature)
        if want_json and self.native_json:
            body["response_format"] = {"type": "json_object"}
        for _ in range(3):
            try:
                data = self.call_json("POST", self.base_url + "/chat/completions", self.headers(), body)
                break
            except BookError as exc:
                lowered = exc.message.lower()
                if exc.http == 400 and "temperature" in lowered and "temperature" in body:
                    del body["temperature"]
                    continue
                if exc.http == 400 and "response_format" in lowered and "response_format" in body:
                    del body["response_format"]
                    continue
                raise
        choices = data.get("choices") or []
        if len(choices) == 0:
            raise BookError("bad_response", "הספק לא החזיר תשובה", True)
        choice = choices[0]
        text = (choice.get("message") or {}).get("content") or ""
        if choice.get("finish_reason") == "length":
            raise BookError("context_too_large", "הפלט נחתך (הגיע למגבלת הפלט); המקטע יפוצל")
        usage = data.get("usage") or {}
        return text, {"in": int(usage.get("prompt_tokens", 0)), "out": int(usage.get("completion_tokens", 0))}


class OpenRouterProvider(OpenAICompatProvider):
    id = "openrouter"
    label = "OpenRouter"
    default_base = "https://openrouter.ai/api/v1"
    native_json = False
    env_key = "OPENROUTER_API_KEY"


class CustomProvider(OpenAICompatProvider):
    id = "custom"
    label = "מותאם אישית (תואם OpenAI)"
    default_base = "http://127.0.0.1:1234/v1"
    native_json = False
    needs_key = False
    env_key = "CUSTOM_API_KEY"

    @property
    def is_local(self) -> bool:  # type: ignore[override]
        host = urllib.parse.urlparse(self.base_url).hostname or ""
        return host in ("127.0.0.1", "localhost", "::1")


class GeminiProvider(AIProvider):
    id = "gemini"
    label = "Gemini"
    default_base = "https://generativelanguage.googleapis.com/v1beta"
    native_json = True
    env_key = "GEMINI_API_KEY"

    def headers(self) -> Dict[str, str]:
        return {"x-goog-api-key": self.api_key, "User-Agent": "book-ai/%s" % APP_VERSION}

    def list_models(self) -> List[str]:
        data = self.call_json("GET", self.base_url + "/models?pageSize=200", self.headers(), None)
        names = []
        for item in data.get("models", []):
            if "generateContent" in (item.get("supportedGenerationMethods") or []):
                names.append((item.get("name") or "").replace("models/", "", 1))
        names.sort()
        return names

    def complete(self, system: str, user: str, want_json: bool) -> Tuple[str, Dict[str, int]]:
        generation: Dict[str, Any] = {"maxOutputTokens": self.max_output}
        if self.temperature is not None and self.temperature != "":
            generation["temperature"] = float(self.temperature)
        if want_json:
            generation["responseMimeType"] = "application/json"
        body = {"systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": generation}
        url = "%s/models/%s:generateContent" % (self.base_url, urllib.parse.quote(self.model, safe=""))
        data = self.call_json("POST", url, self.headers(), body)
        feedback = data.get("promptFeedback") or {}
        if feedback.get("blockReason"):
            raise BookError("bad_response", "הבקשה נחסמה על ידי הספק: %s" % feedback.get("blockReason"))
        candidates = data.get("candidates") or []
        if len(candidates) == 0:
            raise BookError("bad_response", "הספק לא החזיר מועמדים", True)
        candidate = candidates[0]
        reason = candidate.get("finishReason", "")
        parts = (candidate.get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)
        if reason == "MAX_TOKENS":
            raise BookError("context_too_large", "הפלט נחתך (MAX_TOKENS); המקטע יפוצל")
        if reason in ("SAFETY", "PROHIBITED_CONTENT", "RECITATION") and text == "":
            raise BookError("bad_response", "המודל סירב או נחסם (%s)" % reason)
        usage = data.get("usageMetadata") or {}
        return text, {"in": int(usage.get("promptTokenCount", 0)), "out": int(usage.get("candidatesTokenCount", 0))}


class AnthropicProvider(AIProvider):
    id = "anthropic"
    label = "Anthropic"
    default_base = "https://api.anthropic.com/v1"
    env_key = "ANTHROPIC_API_KEY"

    def headers(self) -> Dict[str, str]:
        return {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "User-Agent": "book-ai/%s" % APP_VERSION}

    def list_models(self) -> List[str]:
        data = self.call_json("GET", self.base_url + "/models?limit=1000", self.headers(), None)
        names = []
        for item in data.get("data", []):
            if item.get("id"):
                names.append(item["id"])
        return names

    def complete(self, system: str, user: str, want_json: bool) -> Tuple[str, Dict[str, int]]:
        body: Dict[str, Any] = {"model": self.model, "max_tokens": self.max_output, "system": system,
                                "messages": [{"role": "user", "content": user}]}
        if self.temperature is not None and self.temperature != "":
            body["temperature"] = float(self.temperature)
        data: Dict[str, Any] = {}
        for _ in range(2):
            try:
                data = self.call_json("POST", self.base_url + "/messages", self.headers(), body)
                break
            except BookError as exc:
                # מודלים חדשים דוחים טמפרטורה שאינה ברירת המחדל (400). מסירים אותה וממשיכים, וזוכרים לשאר הבקשות.
                if exc.http == 400 and "temperature" in exc.message.lower() and "temperature" in body:
                    del body["temperature"]
                    self.temperature = None
                    continue
                raise
        text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        if data.get("stop_reason") == "max_tokens":
            raise BookError("context_too_large", "הפלט נחתך (max_tokens); המקטע יפוצל")
        usage = data.get("usage") or {}
        return text, {"in": int(usage.get("input_tokens", 0)), "out": int(usage.get("output_tokens", 0))}


class OllamaProvider(AIProvider):
    id = "ollama"
    label = "Ollama (מקומי)"
    default_base = "http://127.0.0.1:11434"
    needs_key = False
    native_json = True
    is_local = True
    env_key = ""

    def __init__(self, cfg: Dict[str, Any]) -> None:
        super().__init__(cfg)
        if cfg.get("base_url") in (None, ""):
            self.base_url = (os.environ.get("OLLAMA_HOST") or self.default_base).rstrip("/")
            if not self.base_url.startswith("http"):
                self.base_url = "http://" + self.base_url
        host = urllib.parse.urlparse(self.base_url).hostname or ""
        self.is_local = host in ("127.0.0.1", "localhost", "::1")

    def list_models(self) -> List[str]:
        data = self.call_json("GET", self.base_url + "/api/tags", {}, None)
        return sorted(item.get("name", "") for item in data.get("models", []) if item.get("name"))

    def complete(self, system: str, user: str, want_json: bool) -> Tuple[str, Dict[str, int]]:
        options: Dict[str, Any] = {}
        if self.temperature is not None and self.temperature != "":
            options["temperature"] = float(self.temperature)
        if self.cfg.get("num_ctx"):
            options["num_ctx"] = int(self.cfg["num_ctx"])
        body: Dict[str, Any] = {"model": self.model, "stream": False, "options": options,
                                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if want_json:
            body["format"] = "json"
        data = self.call_json("POST", self.base_url + "/api/chat", {}, body)
        text = (data.get("message") or {}).get("content") or ""
        if data.get("done_reason") == "length":
            raise BookError("context_too_large", "הפלט נחתך; המקטע יפוצל")
        return text, {"in": int(data.get("prompt_eval_count", 0)), "out": int(data.get("eval_count", 0))}


class MockProvider(AIProvider):
    """ספק דמה לבדיקות ולהדגמה: מחזיר את אותה רשימה עם טקסט מעובד (קידומת), ללא רשת.
    התנהגויות לבדיקה דרך cfg['mock']: prefix, fail_first, drop_first, merge_first, bad_tags_first,
    explain_first, delay, invalid_key, context_limit, retype_first, fail_on_text."""
    id = "mock"
    label = "ספק דמה (בדיקות)"
    needs_key = False
    native_json = True
    is_local = True
    lock = threading.Lock()

    def __init__(self, cfg: Dict[str, Any]) -> None:
        super().__init__(cfg)
        self.behavior = cfg.get("mock") if isinstance(cfg.get("mock"), dict) else {}
        state = self.behavior.setdefault("_state", {"calls": 0, "ids": [], "prompts": []})
        self.state = state

    def list_models(self) -> List[str]:
        return ["mock-1", "mock-2"]

    def complete(self, system: str, user: str, want_json: bool) -> Tuple[str, Dict[str, int]]:
        behavior = self.behavior
        if "=== ITEMS ===" not in user:
            return "OK", {"in": 1, "out": 1}
        with MockProvider.lock:
            self.state["calls"] = self.state["calls"] + 1
            call_number = self.state["calls"]
            self.state["prompts"].append(user)
        if behavior.get("rate_limit"):
            quota = int(behavior["rate_limit"])
            self.note_rate_headers({"x-ratelimit-limit-requests": str(quota),
                                    "x-ratelimit-remaining-requests": str(max(0, quota - call_number)),
                                    "x-ratelimit-reset-requests": "6m0s"})
        if behavior.get("delay"):
            end = time.time() + float(behavior["delay"])
            while time.time() < end:
                if self.cancel is not None and self.cancel.is_set():
                    raise Aborted()
                time.sleep(min(0.05, max(0.0, end - time.time())))
        if behavior.get("leak_key"):
            raise BookError("api_error", "HTTP 500: upstream failure with credential %s" % self.api_key, False, http=500)
        if behavior.get("invalid_key"):
            raise BookError("invalid_key", "HTTP 401: מפתח לא תקין (דמה)", False, http=401)
        if call_number <= int(behavior.get("fail_first", 0)):
            raise BookError("rate_limit", "HTTP 429: מגבלת קצב (דמה)", True, retry_after=0.01, http=429)
        marker_start = user.find("=== ITEMS ===")
        marker_end = user.find("=== END ===")
        block = user[marker_start + len("=== ITEMS ==="):marker_end].strip()
        if behavior.get("context_limit") and len(user) > int(behavior["context_limit"]):
            raise BookError("context_too_large", "HTTP 400: context length exceeded (דמה)", False, http=400)
        items: List[Dict[str, Any]] = []
        if want_json:
            parsed = json.loads(block)
            items = parsed
        else:
            parsed_items, _ = parse_list_response(block)
            items = parsed_items
        for ids in [[i["id"] for i in items]]:
            with MockProvider.lock:
                self.state["ids"].append(ids)
        prefix = behavior.get("prefix", "[T] ")
        out_items: List[Dict[str, Any]] = []
        for item in items:
            text = item["text"]
            if behavior.get("fail_on_text") and behavior["fail_on_text"] in text:
                text = "I'm sorry, but I can't help with that."
            out_items.append({"id": item["id"], "type": item["type"], "level": item.get("level"), "text": prefix + text})
        first_call = call_number == 1 + int(behavior.get("fail_first", 0))
        if first_call and behavior.get("drop_first") and len(out_items) > 1:
            out_items = out_items[:-1]
        if first_call and behavior.get("merge_first") and len(out_items) > 1:
            out_items[0]["text"] = out_items[0]["text"] + " " + out_items[1]["text"]
            out_items = [out_items[0]] + out_items[2:]
        if first_call and behavior.get("retype_first") and len(out_items) > 0:
            out_items[0]["type"] = "HEADING" if out_items[0]["type"] != "HEADING" else "PARAGRAPH"
        if behavior.get("always_bad_tags"):
            for out_item in out_items:
                out_item["text"] = TAG_RE.sub("", out_item["text"])
        if first_call and behavior.get("bad_tags_first") and len(out_items) > 0:
            for out_item in out_items:
                out_item["text"] = TAG_RE.sub("", out_item["text"])
        usage = {"in": max(1, len(user) // 4), "out": max(1, len(json.dumps(out_items)) // 4)}
        if want_json:
            return json.dumps({"items": out_items}, ensure_ascii=False), usage
        lines = []
        for out_item in out_items:
            level = " level=%s" % out_item["level"] if out_item.get("level") else ""
            lines.append("[id=%s | %s%s] %s" % (out_item["id"], out_item["type"], level, out_item["text"]))
        text_out = "\n".join(lines)
        if first_call and behavior.get("explain_first"):
            text_out = "Sure! Here is the result:\n" + text_out
        return text_out, usage


PROVIDER_CLASSES = {
    "gemini": GeminiProvider, "openai": OpenAICompatProvider, "anthropic": AnthropicProvider,
    "openrouter": OpenRouterProvider, "ollama": OllamaProvider, "custom": CustomProvider, "mock": MockProvider,
}


def make_provider(cfg: Dict[str, Any]) -> AIProvider:
    name = cfg.get("provider", "")
    cls = PROVIDER_CLASSES.get(name)
    if cls is None:
        raise BookError("api_error", "ספק לא מוכר: %s" % name)
    return cls(cfg)


def provider_is_local(cfg: Dict[str, Any]) -> bool:
    return bool(make_provider(dict(cfg, api_key="")).is_local)


def provider_host(cfg: Dict[str, Any]) -> str:
    provider = make_provider(dict(cfg, api_key=""))
    host = urllib.parse.urlparse(provider.base_url).hostname or provider.label
    return host


def env_key_for(provider_id: str) -> str:
    cls = PROVIDER_CLASSES.get(provider_id)
    if cls is None or cls.env_key == "":
        return ""
    return os.environ.get(cls.env_key, "")


# ======================================================================
# 15. מאגר סודות מוצפן (אופציונלי, רק לבקשת המשתמש)
# ======================================================================
class SecretStore:
    """שמירת מפתחות מוצפנת מחוץ לתיקיית הפרויקטים. דורש את החבילה cryptography; בלעדיה השמירה מושבתת."""

    @staticmethod
    def available() -> bool:
        try:
            import cryptography.fernet  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def _fernet() -> Any:
        from cryptography.fernet import Fernet
        os.makedirs(SECRETS_DIR, exist_ok=True)
        key_path = os.path.join(SECRETS_DIR, "master.key")
        if not os.path.isfile(key_path):
            fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as handle:
                handle.write(Fernet.generate_key())
        with open(key_path, "rb") as handle:
            return Fernet(handle.read().strip())

    @staticmethod
    def save(provider_id: str, key: str) -> None:
        if not SecretStore.available():
            raise BookError("internal", "לשמירת מפתח מוצפנת יש להתקין: pip install cryptography")
        store_path = os.path.join(SECRETS_DIR, "keys.enc")
        data = SecretStore.load_all()
        data[provider_id] = key
        token = SecretStore._fernet().encrypt(json.dumps(data).encode("utf-8"))
        atomic_write_bytes(store_path, token)
        try:
            os.chmod(store_path, 0o600)
        except OSError:
            pass

    @staticmethod
    def load_all() -> Dict[str, str]:
        store_path = os.path.join(SECRETS_DIR, "keys.enc")
        if not os.path.isfile(store_path) or not SecretStore.available():
            return {}
        try:
            with open(store_path, "rb") as handle:
                return json.loads(SecretStore._fernet().decrypt(handle.read()).decode("utf-8"))
        except Exception:
            return {}

    @staticmethod
    def forget(provider_id: str) -> None:
        data = SecretStore.load_all()
        if provider_id in data:
            del data[provider_id]
            token = SecretStore._fernet().encrypt(json.dumps(data).encode("utf-8"))
            atomic_write_bytes(os.path.join(SECRETS_DIR, "keys.enc"), token)


# ======================================================================
# 16. מטרות, הגדרות ופרומפטים
# ======================================================================
GOALS = {
    "rewrite_he": {"label": "שכתוב לעברית גבוהה", "ai": True, "translate": False},
    "proofread": {"label": "תיקון לשוני (שינוי מינימלי)", "ai": True, "translate": False},
    "literary_edit": {"label": "עריכה ספרותית", "ai": True, "translate": False},
    "polish": {"label": "שיפור ניסוח", "ai": True, "translate": False},
    "translate": {"label": "תרגום", "ai": True, "translate": True},
    "translate_edit": {"label": "תרגום ועריכה לשונית", "ai": True, "translate": True},
    "relayout": {"label": "שינוי עימוד", "ai": False, "translate": False},
    "restyle": {"label": "שינוי עיצוב", "ai": False, "translate": False},
    "custom": {"label": "עיבוד מותאם אישית", "ai": True, "translate": False},
}


def default_settings() -> Dict[str, Any]:
    return {
        "goal": "translate", "src_lang": "auto", "tgt_lang": "he", "mode": "replace", "extra": "",
        "provider": "gemini", "model": "", "base_url": "", "temperature": 0.3, "chunk_chars": 6000,
        "overlap": 2, "attempts": 3, "api_retries": 5, "concurrency": 2, "timeout": 120,
        "consistency": False, "format": "auto", "on_format_failure": "flag", "max_output_tokens": 8192,
        "context_tokens": 0, "rpm": 0, "price_in": 0.0, "price_out": 0.0, "rtl_isolate": True,
        "layout": {"font_family": "", "font_size": "", "line_height": "", "margin": "", "max_width": "",
                   "theme": "keep", "text_align": "keep", "para_style": "keep", "heading_align": "keep",
                   "heading_font": "", "hyphenate": False, "strip_inline_styles": False,
                   "drop_original_css": False, "custom_css": ""},
        "mock": {},
    }


def goal_task(settings: Dict[str, Any], src_name: str, tgt_name: str) -> str:
    goal = settings["goal"]
    if goal == "translate":
        return ("Translate the text from %s to %s. Preserve meaning, style, tone, point of view, names of characters "
                "and places, professional terminology and paragraph division. Avoid literal word-for-word translation "
                "that sounds unnatural; for fiction prefer natural literary translation." % (src_name, tgt_name))
    if goal == "translate_edit":
        return ("Translate the text from %s to %s and, in the same step, edit the result into fluent, natural, "
                "well-phrased %s. Preserve meaning, tone, names and paragraph division. Return only the final text." % (src_name, tgt_name, tgt_name))
    if goal == "rewrite_he":
        return ("Rewrite the text in polished, high-register, natural Hebrew. Preserve all meaning, facts, names, tone and "
                "the structure of every item.")
    if goal == "proofread":
        return ("Correct spelling, grammar, punctuation and typos with MINIMAL changes. Do not rephrase, restyle or "
                "improve anything that is not an error. Keep the language of the text.")
    if goal == "literary_edit":
        return ("Edit the text literarily: improve rhythm, word choice and flow in the author's voice. Preserve meaning, "
                "facts and names. Keep the language of the text.")
    if goal == "polish":
        return ("Improve the phrasing for clarity and concision. Preserve meaning, tone and facts. Keep the language of the text.")
    return "Process each item according to the user instructions given below."


def build_system_prompt(settings: Dict[str, Any], src_name: str, tgt_name: str, fmt: str) -> str:
    lines = ["You are a meticulous professional book editor and translator working inside an automated pipeline.",
             "TASK: " + goal_task(settings, src_name, tgt_name)]
    extra = (settings.get("extra") or "").strip()
    if extra != "":
        lines.append("ADDITIONAL USER INSTRUCTIONS (apply to every item): " + extra)
    lines.append(
        "PROTOCOL (strict):\n"
        "- The user message contains ITEMS, each with an id, a type and text. Return the SAME items: same ids, same types "
        "(and heading levels), same order, same count. Never merge, split, skip, reorder or add items.\n"
        "- Return only the processed text of each item: no explanations, notes, preface or markdown.\n"
        "- Inline tags such as <b1>..</b1>, <i2>..</i2>, <a3>..</a3>, <u5>..</u5>, <d6>..</d6>, <s7>..</s7> mark formatting and links; "
        "self-closing tags such as <n4/>, <br5/>, <m6/> mark footnote references, line breaks and inline objects. Keep EVERY tag "
        "exactly once with its own number. You may move tags inside the sentence to fit the target word order, but never add, delete, "
        "rename or renumber tags, and keep opening and closing tags properly nested.\n"
        "- The sequences &amp; &lt; &gt; are XML escapes: keep them as they are.\n"
        "- Items marked as context-only must not be returned.")
    if fmt == "json":
        lines.append('OUTPUT FORMAT: a single JSON object {"items":[{"id":"...","type":"...","level":<number or null>,"text":"..."}]} and nothing else.')
    else:
        lines.append("OUTPUT FORMAT: one item per line, exactly `[id=<id> | <TYPE> level=<n>] <text>` (omit ` level=<n>` for non-headings). "
                     "Keep each header verbatim and keep the text of an item on a single line.")
    return "\n".join(lines)


def format_items_list(items: List[Dict[str, Any]]) -> str:
    lines = []
    for item in items:
        level = " level=%d" % item["level"] if item.get("level") else ""
        lines.append("[id=%s | %s%s] %s" % (item["id"], item["type"], level, item["text"]))
    return "\n".join(lines)


def format_items_json(items: List[Dict[str, Any]]) -> str:
    payload = []
    for item in items:
        payload.append({"id": item["id"], "type": item["type"], "level": item.get("level") or None, "text": item["text"]})
    return json.dumps(payload, ensure_ascii=False)


def build_user_prompt(ctx: Dict[str, Any], items: List[Dict[str, Any]], fmt: str, corrections: List[str]) -> str:
    parts = ["Book: %s" % ctx.get("book", ""), "Chapter: %s" % ctx.get("chapter", "")]
    if ctx.get("section"):
        parts.append("Section: %s" % ctx["section"])
    if ctx.get("previous"):
        parts.append("Digest of the previous chapter (context only): %s" % ctx["previous"])
    if ctx.get("glossary"):
        parts.append("Glossary - use exactly these renderings:")
        for entry in ctx["glossary"]:
            parts.append("- %s => %s" % (entry["source"], entry["target"]))
    if ctx.get("overlap"):
        parts.append("Preceding text (context only - DO NOT return):")
        for line in ctx["overlap"]:
            parts.append("  > " + line)
    parts.append("=== ITEMS ===")
    parts.append(format_items_json(items) if fmt == "json" else format_items_list(items))
    parts.append("=== END ===")
    if len(corrections) > 0:
        parts.append("Your previous answer was rejected for these reasons. Fix them and return ALL items again in the required format:")
        for message in corrections[:10]:
            parts.append("- " + message)
    return "\n".join(parts)


# ======================================================================
# 17. פרוטוקול: פענוח תשובה ואימות אוטומטי
# ======================================================================
LIST_HEADER_RE = re.compile(r"^\[id=([^\s|\]]+)\s*\|\s*([A-Z_]+)(?:\s+level=(\d))?\]\s?(.*)$")
REFUSAL_RE = re.compile(r"^\s*(i'?m sorry|i am sorry|sorry,|i cannot|i can'?t|as an ai|i apologi[sz]e|מצטער|אני מצטער|לא אוכל|איני יכול)", re.I)


def strip_fences(text: str) -> str:
    result = []
    for line in text.strip().splitlines():
        if line.strip().startswith("```"):
            continue
        result.append(line)
    return "\n".join(result)


def parse_list_response(text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    items: List[Dict[str, Any]] = []
    extraneous: List[str] = []
    for line in strip_fences(text).splitlines():
        if line.strip() == "":
            continue
        match = LIST_HEADER_RE.match(line.strip())
        if match is None:
            extraneous.append(line.strip()[:120])
            continue
        items.append({"id": match.group(1), "type": match.group(2),
                      "level": int(match.group(3)) if match.group(3) else 0, "text": match.group(4)})
    return items, extraneous


def parse_json_response(text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    cleaned = strip_fences(text).strip()
    extraneous: List[str] = []
    data: Any = None
    try:
        data = json.loads(cleaned)
    except ValueError:
        starts = [i for i in (cleaned.find("{"), cleaned.find("[")) if i >= 0]
        if len(starts) == 0:
            raise BookError("parse_failure", "התשובה אינה JSON", True)
        begin = min(starts)
        end = max(cleaned.rfind("}"), cleaned.rfind("]"))
        try:
            data = json.loads(cleaned[begin:end + 1])
            extraneous.append("טקסט מחוץ ל-JSON")
        except ValueError:
            raise BookError("parse_failure", "לא ניתן לפענח JSON מהתשובה", True)
    if isinstance(data, dict):
        data = data.get("items")
    if not isinstance(data, list):
        raise BookError("parse_failure", "מבנה ה-JSON אינו רשימת פריטים", True)
    items: List[Dict[str, Any]] = []
    for raw in data:
        if not isinstance(raw, dict) or "id" not in raw or "text" not in raw:
            raise BookError("parse_failure", "פריט JSON ללא id או text", True)
        level = raw.get("level")
        items.append({"id": str(raw["id"]), "type": str(raw.get("type", "")),
                      "level": int(level) if isinstance(level, (int, float)) else 0, "text": str(raw["text"])})
    return items, extraneous


def validate_structure(expected: List[Dict[str, Any]], got: List[Dict[str, Any]], extraneous: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
    """מחזיר (שגיאות_מבניות_קריטיות, שגיאות_לפי_רכיב). קריטי: ספירה/מזהים/סדר/תוכן מחוץ למבנה."""
    fatal: List[str] = []
    per_item: Dict[str, List[str]] = {}
    if len(extraneous) > 0:
        fatal.append("הפלט כולל תוכן מחוץ למבנה המבוקש (הסברים/הקדמות): %s" % extraneous[0])
    if len(got) != len(expected):
        fatal.append("מספר הפריטים שגוי: נשלחו %d והוחזרו %d (אסור למזג, לפצל או לדלג)" % (len(expected), len(got)))
    else:
        for index in range(len(expected)):
            if expected[index]["id"] != got[index]["id"]:
                fatal.append("המזהה או הסדר שגויים במקום %d: צפוי %s והוחזר %s" % (index + 1, expected[index]["id"], got[index]["id"]))
                break
    if len(fatal) == 0:
        for index in range(len(expected)):
            want = expected[index]
            have = got[index]
            if want["type"] != have["type"] or (want["type"] == "HEADING" and int(want.get("level") or 0) != int(have.get("level") or 0)):
                per_item.setdefault(want["id"], []).append(
                    "סוג/רמה שגויים עבור %s: צפוי %s%s" % (want["id"], want["type"], " level=%d" % want["level"] if want.get("level") else ""))
    return fatal, per_item


def check_unit_output(unit: Dict[str, Any], out_text: str, settings: Dict[str, Any], glossary: List[Dict[str, Any]],
                      same_language: bool) -> Tuple[str, List[str], List[str], str]:
    """בדיקות ברמת רכיב. מחזיר (טקסט_נקי, שגיאות, אזהרות, סוג_שגיאה: tags|other|'')."""
    out = WS_RE.sub(" ", out_text).strip()
    errors: List[str] = []
    warnings: List[str] = []
    kind = ""
    source_plain = strip_tags(unit["tagged"])
    if out == "":
        return out, ["פלט ריק עבור %s" % unit["id"]], warnings, "other"
    tag_errors = validate_tags(unit["tagged"], out, unit["tags"])
    if len(tag_errors) > 0:
        for message in tag_errors:
            errors.append("%s: %s" % (unit["id"], message))
        kind = "tags"
    out_plain = strip_tags(out)
    if REFUSAL_RE.match(out_plain) and not REFUSAL_RE.match(source_plain):
        errors.append("%s: המודל החזיר הסבר/סירוב במקום תוצאה" % unit["id"])
        kind = "other"
    goal = settings["goal"]
    if len(source_plain) >= 20:
        ratio = len(out_plain) / float(len(source_plain))
        low, high = (0.2, 4.5) if GOALS[goal]["translate"] else ((0.4, 2.5) if goal != "custom" else (0.05, 12.0))
        if ratio < low or ratio > high:
            errors.append("%s: אורך חריג (יחס %.2f לעומת המקור)" % (unit["id"], ratio))
            kind = "other"
    if len(errors) == 0:
        if number_signature(source_plain) != number_signature(out_plain) and goal not in ("custom",):
            warnings.append("מספרים שונו או נעלמו")
        if GOALS[goal]["translate"]:
            for entry in glossary_relevant(glossary, source_plain):
                if entry["target"].strip().lower() not in out_plain.lower():
                    warnings.append("המונח '%s' לא הופיע כ-'%s'" % (entry["source"], entry["target"]))
            if not same_language and len(source_plain.split()) >= 4 and out_plain.strip().lower() == source_plain.strip().lower():
                warnings.append("הטקסט זהה למקור (ייתכן שלא תורגם)")
    return out, errors, warnings, kind


def split_tagged_parts(tagged: str, max_chars: int) -> List[str]:
    """פיצול פסקה ארוכה לפי משפטים, רק במקומות שבהם אין תגית פתוחה."""
    if len(tagged) <= max_chars:
        return [tagged]
    cuts: List[int] = []
    depth = 0
    position = 0
    for token in tokenize_tagged(tagged):
        if token[0] == "text":
            text = token[1]
            if depth == 0:
                for match in re.finditer(r"[.!?…؟։。][\"”’)»]*\s+", text):
                    cuts.append(position + match.end())
            position = position + len(text)
        else:
            width = len("<%s%s%d%s>" % ("/" if token[0] == "close" else "", token[1], token[2], "/" if token[0] == "atom" else ""))
            position = position + width
            if token[0] == "open":
                depth = depth + 1
            elif token[0] == "close":
                depth = depth - 1
    parts: List[str] = []
    start = 0
    last_cut = -1
    for cut in cuts:
        if cut - start > max_chars and last_cut > start:
            parts.append(tagged[start:last_cut])
            start = last_cut
        last_cut = cut
    parts.append(tagged[start:])
    return [p for p in parts if p.strip() != ""]


# ======================================================================
# 18. מאגר פרויקט ושמירת מצב מתמשכת
# ======================================================================
class Project:
    """פרויקט אחד: קובץ מקור, מודל פנימי, הגדרות, מילון, זיכרון תרגום ומצב. נשמר בדיסק בכתיבה אטומית."""

    def __init__(self, pid: str) -> None:
        self.id = pid
        self.dir = os.path.join(PROJECTS_DIR, pid)
        self.lock = threading.RLock()
        self.log = LogBuffer(os.path.join(self.dir, "log.jsonl"))
        self.meta: Dict[str, Any] = {"id": pid, "status": "created"}
        self.settings: Dict[str, Any] = default_settings()
        self.glossary: List[Dict[str, Any]] = []
        self.tm: Dict[str, str] = {}
        self.chapters: List[Dict[str, Any]] = []
        self.units: List[Dict[str, Any]] = []
        self.units_by_id: Dict[str, Dict[str, Any]] = {}
        self.dirty_chapters: set = set()
        self.dirty_meta = False
        self.dirty_tm = False
        self.rev = 0  # עולה בכל שינוי ברכיב או בהגדרות; הממשק משווה אותו כדי לדעת שהתצוגה החיה ישנה

    @property
    def work_path(self) -> str:
        return os.path.join(self.dir, "work.epub")

    @property
    def output_dir(self) -> str:
        return os.path.join(self.dir, "output")

    @staticmethod
    def create(filename: str, size: int, fmt: str) -> "Project":
        pid = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        project = Project(pid)
        os.makedirs(os.path.join(project.dir, "source"), exist_ok=True)
        project.meta = {"id": pid, "filename": os.path.basename(filename), "size": size, "format": fmt,
                        "created": datetime.datetime.now().isoformat(timespec="seconds"), "status": "analyzing",
                        "error": None, "conversion": None, "stats": {}, "pdf_report": None, "usage": {
                            "requests": 0, "tokens_in": 0, "tokens_out": 0, "elapsed": 0.0}, "outputs": [], "final": None}
        project.dirty_meta = True
        project.flush()
        return project

    def set_model(self, model: Dict[str, Any]) -> None:
        with self.lock:
            self.chapters = model["chapters"]
            self.units = model["units"]
            self.units_by_id = {}
            for unit in self.units:
                self.units_by_id[unit["id"]] = unit
            self.meta["stats"] = model["stats"]
            for chapter in self.chapters:
                self.dirty_chapters.add(chapter["index"])
            self.dirty_meta = True

    def touch(self, unit: Dict[str, Any]) -> None:
        with self.lock:
            self.rev = self.rev + 1
            self.dirty_chapters.add(unit["ch"])
            # אם כבר הופק פלט, כל שינוי ברכיב הופך אותו לישן. הממשק מציג זאת, והפקה מחדש מנקה את הדגל.
            if self.meta.get("final") is not None and not self.meta.get("outputs_stale"):
                self.meta["outputs_stale"] = True
                self.dirty_meta = True

    def set_status(self, status: str, error: Optional[Dict[str, Any]] = None) -> None:
        """כל מעבר סטטוס נשמר לדיסק מיד (לא ממתין למחזור השמירה הבא)."""
        with self.lock:
            self.meta["status"] = status
            self.meta["error"] = error
            self.dirty_meta = True
            self.flush()

    def storage_bytes(self) -> int:
        """גודל כל קבצי הפרויקט בדיסק (מקור, עבודה, יחידות, פלט, יומן)."""
        total = 0
        for root, dirs, files in os.walk(self.dir):
            for name in files:
                try:
                    total = total + os.path.getsize(os.path.join(root, name))
                except OSError:
                    pass
        return total

    def flush(self) -> None:
        """כותב לדיסק רק את מה שהשתנה. כל קובץ נכתב אטומית."""
        with self.lock:
            os.makedirs(self.dir, exist_ok=True)
            if self.dirty_meta:
                public_settings = dict(self.settings)
                public_settings.pop("api_key", None)
                mock = dict(public_settings.get("mock") or {})
                mock.pop("_state", None)
                public_settings["mock"] = mock
                atomic_write_json(os.path.join(self.dir, "project.json"), {
                    "meta": self.meta, "settings": public_settings, "glossary": self.glossary, "chapters": self.chapters})
                self.dirty_meta = False
            if self.dirty_tm:
                atomic_write_json(os.path.join(self.dir, "tm.json"), self.tm)
                self.dirty_tm = False
            if len(self.dirty_chapters) > 0:
                by_chapter: Dict[int, List[Dict[str, Any]]] = {}
                for unit in self.units:
                    if unit["ch"] in self.dirty_chapters:
                        by_chapter.setdefault(unit["ch"], []).append(unit)
                for index in list(self.dirty_chapters):
                    atomic_write_json(os.path.join(self.dir, "units", "c%02d.json" % index), by_chapter.get(index, []))
                self.dirty_chapters = set()

    @staticmethod
    def load(pid: str) -> "Project":
        project = Project(pid)
        data = read_json(os.path.join(project.dir, "project.json"))
        if data is None:
            raise BookError("internal", "קובץ המצב של הפרויקט חסר או פגום")
        project.meta = data["meta"]
        project.settings = dict(default_settings(), **data["settings"])
        project.glossary = data.get("glossary", [])
        project.chapters = data.get("chapters", [])
        project.tm = read_json(os.path.join(project.dir, "tm.json"), {})
        units: List[Dict[str, Any]] = []
        units_dir = os.path.join(project.dir, "units")
        if os.path.isdir(units_dir):
            for name in sorted(os.listdir(units_dir)):
                if name.endswith(".json"):
                    chunk = read_json(os.path.join(units_dir, name), [])
                    units.extend(chunk)
        project.units = units
        for unit in units:
            project.units_by_id[unit["id"]] = unit
        log_path = os.path.join(project.dir, "log.jsonl")
        if os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8") as handle:
                for line in handle.readlines()[-1500:]:
                    try:
                        entry = json.loads(line)
                    except ValueError:
                        continue
                    project.log.entries.append(entry)
                    project.log.counter = max(project.log.counter, int(entry.get("id", 0)))
        interrupted = project.meta.get("status")
        if interrupted in ("running", "analyzing", "building"):
            if interrupted == "running":
                project.meta["status"] = "paused"
            elif interrupted == "building":
                # כל הרכיבים כבר עובדו ורק ההפקה נקטעה; אפשר להפיק מחדש מלשונית הסיכום.
                project.meta["status"] = "stopped"
            else:
                project.meta["status"] = "error"
                project.meta["error"] = {"kind": "internal", "message": "הניתוח הופסק באמצע (סגירה/קריסה). העלה את הקובץ שוב; "
                                         "את הפרויקט הזה אפשר למחוק במפורש דרך 'ניהול ומחיקת פרויקטים'.", "hint": ""}
            project.dirty_meta = True
        return project

    def counts(self) -> Dict[str, int]:
        result = {"total": 0, "done": 0, "failed": 0, "flagged": 0, "pending": 0, "chars_total": 0, "chars_done": 0}
        for unit in self.units:
            if unit["scope"] == "meta" and not GOALS.get(self.settings["goal"], {}).get("translate"):
                continue
            result["total"] = result["total"] + 1
            size = len(unit["tagged"])
            result["chars_total"] = result["chars_total"] + size
            status = unit["status"]
            if status in OK_STATUSES:
                result["done"] = result["done"] + 1
                result["chars_done"] = result["chars_done"] + size
            elif status == "failed":
                result["failed"] = result["failed"] + 1
            elif status == "flagged":
                result["flagged"] = result["flagged"] + 1
            else:
                result["pending"] = result["pending"] + 1
        return result


# ======================================================================
# 19. חלוקה למקטעים
# ======================================================================
def effective_chunk_chars(settings: Dict[str, Any]) -> int:
    size = int(settings.get("chunk_chars") or 6000)
    context = int(settings.get("context_tokens") or 0)
    if context > 0:
        size = min(size, int(context * 0.35 * 3.0))
    return max(400, size)


def build_chunks(units: List[Dict[str, Any]], settings: Dict[str, Any], start_number: int = 1) -> List[Dict[str, Any]]:
    """מחלק יחידות ממתינות למקטעים לפי רכיבים (לא באמצע פסקה ולא מעבר לפרקים). פסקה ארוכה מפוצלת למקטעי־משנה."""
    limit = effective_chunk_chars(settings)
    max_unit = int(limit * 0.7)
    chunks: List[Dict[str, Any]] = []
    number = start_number
    current: Optional[Dict[str, Any]] = None
    size = 0
    for unit in units:
        if current is None or current["ch"] != unit["ch"] or (size + len(unit["tagged"]) > limit and len(current["groups"]) > 0):
            current = {"id": "chapter_%02d_chunk_%03d" % (unit["ch"], number), "ch": unit["ch"], "groups": []}
            number = number + 1
            size = 0
            chunks.append(current)
        parts = split_tagged_parts(unit["tagged"], max_unit)
        reqs = []
        for index, part in enumerate(parts):
            ident = unit["id"] if len(parts) == 1 else "%s#%d" % (unit["id"], index + 1)
            reqs.append({"id": ident, "type": unit["type"], "level": unit["level"], "text": part})
        current["groups"].append({"unit": unit, "reqs": reqs})
        size = size + len(unit["tagged"])
    return chunks


# ======================================================================
# 20. מנוע העיבוד: תור, ניסיונות חוזרים, פיצול, שמירת מצב
# ======================================================================
# Aborted מוגדרת בסעיף 14 (שכבת התעבורה), כי גם http_json זורק אותה.


class FatalProviderError(Exception):
    def __init__(self, error: BookError) -> None:
        super().__init__(error.message)
        self.error = error


class Job:
    def __init__(self, project: Project, provider_cfg: Dict[str, Any]) -> None:
        self.project = project
        self.provider_cfg = provider_cfg
        self.settings = project.settings
        self.log = project.log
        self.cancel = threading.Event()
        self.pause_flag = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.started_at = 0.0
        self.chars_done_run = 0
        self.current_chapter = 0
        self.current_chunk = ""
        self.chunks_total = 0
        self.chunks_done = 0
        self.rate_lock = threading.Lock()
        self.last_request = 0.0
        self.stats_lock = threading.Lock()
        self.fatal: Optional[BookError] = None
        self.single = False            # מצב שליחה מחדש של יחידה בודדת
        self.force_fresh = False       # עוקף את זיכרון התרגום (שליחה מחדש חייבת לפנות למודל)
        self.resume_status = "stopped"
        self.resume_error: Optional[Dict[str, Any]] = None
        self.backups: Dict[str, Dict[str, Any]] = {}
        self.provider = make_provider(provider_cfg)
        self.provider.cancel = self.cancel  # עצירה קוטעת גם בקשת רשת שכבר נשלחה (ראו http_json)
        self.chapter_units: Dict[int, List[Dict[str, Any]]] = {}
        for unit in project.units:
            self.chapter_units.setdefault(unit["ch"], []).append(unit)
        fmt = self.settings.get("format", "auto")
        self.fmt = ("json" if self.provider.native_json else "list") if fmt == "auto" else fmt
        code, name, rtl = resolve_language(self.settings.get("tgt_lang", "he"))
        self.tgt_code, self.tgt_name = code, name
        src_setting = self.settings.get("src_lang", "auto")
        if src_setting in ("", "auto"):
            src_setting = project.meta.get("stats", {}).get("language", "und")
        self.src_code, self.src_name, _ = resolve_language(src_setting)
        if not GOALS[self.settings["goal"]]["translate"]:
            self.tgt_code, self.tgt_name = (("he", "Hebrew") if self.settings["goal"] == "rewrite_he" else (self.src_code, self.src_name))
        self.same_language = self.src_code.split("-")[0] == self.tgt_code.split("-")[0]
        self.system_prompt = build_system_prompt(self.settings, self.src_name, self.tgt_name, self.fmt)
        goal_key = "|".join([self.settings["goal"], self.src_code, self.tgt_code, self.settings.get("extra", "")]) 
        self.tm_prefix = sha1(goal_key)[:12]

    # ---------- שליטה ----------
    def start(self, retry_units: Optional[List[Dict[str, Any]]] = None) -> None:
        self.thread = threading.Thread(target=self.run, args=(retry_units,), daemon=True, name="job-" + self.project.id)
        self.thread.start()

    def pause(self) -> None:
        """השהיה רכה: בקשה שכבר נשלחה לספק מסתיימת ותוצאתה נשמרת (היא כבר שולמה). לא נשלחות בקשות חדשות,
        וכל המתנה (נסיגה אחרי שגיאה, הגבלת קצב) נקטעת מיד. מה שלא הושלם נשאר ממתין וימשיך מאותה נקודה."""
        self.pause_flag.set()

    def stop(self) -> None:
        """עצירה קשיחה: גם בקשה תלויה מול הספק נקטעת תוך שבריר שנייה, והשרשור יוצא בלי לחכות לפסק הזמן."""
        self.pause_flag.set()
        self.cancel.set()

    def join(self, timeout: float = 10.0) -> bool:
        """ממתין לסיום השרשור. מחזיר True אם הסתיים."""
        if self.thread is None:
            return True
        self.thread.join(timeout)
        return not self.thread.is_alive()

    def checkpoint(self) -> None:
        """שמירה מיידית של כל מה שהשתנה בפרויקט. כשל בשמירה נרשם ביומן ואינו מפיל את העיבוד."""
        try:
            self.project.flush()
        except Exception as exc:
            self.log.add("error", "שמירת מצב נכשלה: %s" % exc, stage="state")

    def alive(self) -> bool:
        return self.thread is not None and self.thread.is_alive()

    def aborted(self) -> bool:
        return self.cancel.is_set()

    # ---------- ריצה ----------
    def run(self, retry_units: Optional[List[Dict[str, Any]]]) -> None:
        project = self.project
        self.started_at = time.time()
        base_elapsed = float(project.meta["usage"].get("elapsed", 0.0))
        project.set_status("running")
        saver_stop = threading.Event()

        def saver() -> None:
            while not saver_stop.wait(1.0):
                self.checkpoint()
        saver_thread = threading.Thread(target=saver, daemon=True)
        saver_thread.start()
        try:
            goal = self.settings["goal"]
            if GOALS[goal]["ai"]:
                self.process_all(retry_units)
            if self.single:
                self.finish_single()
            elif self.fatal is not None:
                project.set_status("error", {"kind": self.fatal.kind, "message": self.fatal.message, "hint": self.fatal.hint})
            elif self.cancel.is_set():
                project.set_status("stopped")
            elif self.pause_flag.is_set():
                project.set_status("paused")
            else:
                project.set_status("building")
                self.log.add("info", "העיבוד הסתיים; בונה EPUB ומריץ אימות", stage="output")
                build_outputs(project, self.log)
                # set_status שומר לדיסק מיד, כך שגם הסטטוס הסופי וגם פרטי הפלט נשמרים לפני שהשרשור יוצא.
                project.set_status("completed")
        except Aborted:
            project.set_status("stopped")
        except BookError as exc:
            self.log.add("error", exc.message, stage="run", kind=exc.kind, suggestion=exc.hint)
            project.set_status("error", {"kind": exc.kind, "message": exc.message, "hint": exc.hint})
        except Exception as exc:
            self.log.add("error", "שגיאה פנימית: %s" % exc, stage="run", kind="internal", trace=traceback.format_exc()[-800:])
            project.set_status("error", {"kind": "internal", "message": Redactor.clean(str(exc)), "hint": ERROR_HINTS["internal"]})
        finally:
            saver_stop.set()
            with project.lock:
                project.meta["usage"]["elapsed"] = base_elapsed + (time.time() - self.started_at)
                project.dirty_meta = True
            self.checkpoint()

    # ---------- שליחה מחדש של יחידה בודדת ----------
    def start_resend(self, unit: Dict[str, Any]) -> None:
        """מעבד מחדש יחידה אחת בלבד, עם אותו בניית הקשר כמו בעיבוד רגיל (כותרת קטע, פסקאות קודמות, מילון, תקציר פרק קודם).
        התרגום הקודם נשמר בצד ומשוחזר אם השליחה נכשלת, כדי שבקשה כושלת לא תמחק תרגום תקין."""
        project = self.project
        status = project.meta.get("status")
        self.resume_status = status if status in ("ready", "paused", "stopped", "completed", "error") else "stopped"
        self.resume_error = project.meta.get("error") if self.resume_status == "error" else None
        with project.lock:
            self.backups[unit["id"]] = {"out": unit.get("out"), "status": unit["status"],
                                        "warn": list(unit.get("warn") or []), "err": unit.get("err")}
            unit["status"] = "pending"
            unit["out"] = None
            unit["warn"] = []
            unit["err"] = None
            unit["att"] = 0
            project.touch(unit)
        project.flush()
        self.single = True
        self.force_fresh = True
        self.start([unit])

    def finish_single(self) -> None:
        project = self.project
        with project.lock:
            for unit_id, backup in self.backups.items():
                unit = project.units_by_id.get(unit_id)
                if unit is None:
                    continue
                if unit["status"] not in OK_STATUSES and backup["status"] in OK_STATUSES:
                    unit["out"] = backup["out"]
                    unit["status"] = backup["status"]
                    unit["warn"] = backup["warn"]
                    unit["err"] = backup["err"]
                    project.touch(unit)
                    self.log.add("warn", "%s: השליחה מחדש לא הצליחה; התרגום הקודם שוחזר" % unit_id, stage="resend", unit=unit_id)
        if self.fatal is not None:
            self.log.add("error", "השליחה מחדש נכשלה: %s" % self.fatal.message, stage="resend", kind=self.fatal.kind,
                         suggestion=self.fatal.hint)
        project.set_status(self.resume_status, self.resume_error)

    def sync_rate_limit(self) -> None:
        """מעתיק את תמונת המכסה האחרונה של הספק לפרויקט (נשמר לדיסק, ומוצג בממשק)."""
        snapshot = self.provider.rate_info
        if len(snapshot) == 0:
            return
        with self.stats_lock:
            self.project.meta["rate_limit"] = dict(snapshot)
            self.project.dirty_meta = True

    def pending_units(self) -> List[Dict[str, Any]]:
        goal_translate = GOALS[self.settings["goal"]]["translate"]
        result = []
        for unit in self.project.units:
            if unit["status"] != "pending":
                continue
            if unit["scope"] == "meta" and not goal_translate:
                continue
            result.append(unit)
        return result

    def process_all(self, retry_units: Optional[List[Dict[str, Any]]]) -> None:
        provider = self.provider
        if not self.single:  # שליחה מחדש של יחידה אחת לא מבזבזת בקשות על בדיקת חיבור
            self.log.add("info", "בודק חיבור וזמינות מודל (%s / %s)" % (provider.label, provider.model or "-"), stage="preflight",
                         provider=provider.id, model=provider.model)
            try:
                provider.test_connection()
            except Aborted:
                return
            except BookError as exc:
                self.fatal = exc
                self.log.add("error", "בדיקת החיבור נכשלה: %s" % exc.message, stage="preflight", kind=exc.kind,
                             provider=provider.id, model=provider.model, suggestion=exc.hint)
                return
        units = retry_units if retry_units is not None else self.pending_units()
        chunks = build_chunks(units, self.settings, self.next_chunk_number())
        self.chunks_total = len(chunks)
        workers = 1 if self.settings.get("consistency") else max(1, int(self.settings.get("concurrency") or 1))
        self.log.add("info", "%d מקטעים לעיבוד, %d בקשות מקבילות" % (len(chunks), workers), stage="plan")
        semaphore = threading.Semaphore(workers)
        pool = ThreadPoolExecutor(max_workers=workers)
        futures = []

        def task(chunk: Dict[str, Any]) -> None:
            try:
                self.process_chunk(chunk)
            except Aborted:
                pass
            except FatalProviderError as exc:
                self.fatal = exc.error
                self.cancel.set()
            except BookError as exc:
                self.log.add("error", exc.message, stage="chunk", chunk=chunk["id"], kind=exc.kind)
            except Exception as exc:
                self.log.add("error", "שגיאה פנימית במקטע: %s" % exc, stage="chunk", chunk=chunk["id"], kind="internal",
                             trace=traceback.format_exc()[-600:])
            finally:
                self.checkpoint()  # כל מקטע שהסתיים (או נקטע) נשמר מיד
                semaphore.release()

        for chunk in chunks:
            if self.pause_flag.is_set() or self.cancel.is_set():
                break
            semaphore.acquire()
            if self.pause_flag.is_set() or self.cancel.is_set():
                semaphore.release()
                break
            futures.append(pool.submit(task, chunk))
        pool.shutdown(wait=True)

    def next_chunk_number(self) -> int:
        highest = 0
        for unit in self.project.units:
            chunk = unit.get("chunk")
            if chunk:
                match = re.search(r"_chunk_(\d+)$", chunk)
                if match:
                    highest = max(highest, int(match.group(1)))
        return highest + 1

    # ---------- הקשר ----------
    def chapter_digest(self, chapter: int) -> str:
        texts = []
        for unit in self.chapter_units.get(chapter, []):
            if unit["scope"] == "content" and unit["type"] != "HEADING":
                texts.append(strip_tags(unit["tagged"]))
        if len(texts) == 0:
            return ""
        first = texts[0][:220]
        last = texts[-1][-160:] if len(texts) > 1 else ""
        title = ""
        for entry in self.project.chapters:
            if entry["index"] == chapter:
                title = entry["title"]
        return ("%s: %s%s" % (title, first, (" ... " + last) if last else "")).strip()

    def build_context(self, chunk: Dict[str, Any], group_units: List[Dict[str, Any]]) -> Dict[str, Any]:
        chapter_title = ""
        for entry in self.project.chapters:
            if entry["index"] == chunk["ch"]:
                chapter_title = entry["title"]
        section = ""
        first = group_units[0]
        for unit in self.chapter_units.get(chunk["ch"], []):
            if unit is first:
                break
            if unit["type"] == "HEADING":
                section = strip_tags(unit["tagged"])
        joined = " ".join(strip_tags(u["tagged"]) for u in group_units)
        glossary = glossary_relevant(self.project.glossary, joined) if GOALS[self.settings["goal"]]["translate"] else []
        overlap: List[str] = []
        count = int(self.settings.get("overlap") or 0)
        if count > 0:
            preceding: List[Dict[str, Any]] = []
            for unit in self.chapter_units.get(chunk["ch"], []):
                if unit["scope"] == first["scope"]:
                    if unit is first:
                        break
                    preceding.append(unit)
            for unit in preceding[-count:]:
                shown = unit["out"] if (unit["status"] in OK_STATUSES and unit.get("out")) else unit["tagged"]
                overlap.append(strip_tags(shown)[:300])
        previous = self.chapter_digest(chunk["ch"] - 1) if chunk["ch"] > 1 else ""
        return {"book": self.project.meta.get("stats", {}).get("title") or self.project.meta.get("filename", ""),
                "chapter": chapter_title, "section": section, "previous": previous[:420],
                "glossary": [{"source": g["source"], "target": g["target"]} for g in glossary], "overlap": overlap}

    # ---------- עיבוד מקטע ----------
    def tm_key(self, unit: Dict[str, Any]) -> str:
        return self.tm_prefix + ":" + sha1(unit["type"] + "|" + unit["tagged"])

    def process_chunk(self, chunk: Dict[str, Any]) -> None:
        if self.pause_flag.is_set() or self.cancel.is_set():
            raise Aborted()
        self.current_chapter = chunk["ch"]
        self.current_chunk = chunk["id"]
        remaining: List[Dict[str, Any]] = []
        for group in chunk["groups"]:
            unit = group["unit"]
            if unit["status"] != "pending":
                continue  # נערך ידנית (או טופל) בזמן שהמקטע חיכה בתור: לא דורסים
            unit["chunk"] = chunk["id"]
            cached = None if self.force_fresh else self.project.tm.get(self.tm_key(unit))
            if cached is not None and len(validate_tags(unit["tagged"], cached, unit["tags"])) == 0:
                self.accept(unit, cached, [], from_memory=True)
            else:
                remaining.append(group)
        if len(remaining) == 0:
            self.chunks_done = self.chunks_done + 1
            return
        ctx = self.build_context(chunk, [g["unit"] for g in remaining])
        self.log.add("info", "מעבד %s (%d רכיבים)" % (chunk["id"], len(remaining)), stage="chunk", chunk=chunk["id"], chapter=chunk["ch"],
                     provider=self.provider.id, model=self.provider.model)
        self.process_groups(remaining, ctx, chunk, int(self.settings.get("attempts") or 3), 0)
        self.chunks_done = self.chunks_done + 1

    def accept(self, unit: Dict[str, Any], out: str, warnings: List[str], from_memory: bool = False) -> None:
        with self.project.lock:
            if unit["status"] == "manual":
                return  # המשתמש ערך את היחידה ידנית בזמן שהבקשה הייתה באוויר: העריכה גוברת
            unit["out"] = out
            unit["status"] = "done"
            unit["warn"] = warnings + (["נלקח מזיכרון התרגום"] if from_memory else [])
            unit["err"] = None
            if not from_memory:
                self.project.tm[self.tm_key(unit)] = out
                self.project.dirty_tm = True
            self.project.touch(unit)
        with self.stats_lock:
            self.chars_done_run = self.chars_done_run + len(unit["tagged"])

    def fail_unit(self, unit: Dict[str, Any], kind: str, messages: List[str], chunk_id: str, tag_only: bool, last_out: str) -> None:
        with self.project.lock:
            if unit["status"] == "manual":
                return
            unit["att"] = unit.get("att", 0) + 1
            if tag_only and self.settings.get("on_format_failure") == "accept_plain" and last_out != "":
                plain = escape_text(strip_tags(last_out))
                unit["out"] = plain
                unit["status"] = "done"
                unit["warn"] = ["עיצוב פנימי (הדגשות/קישורים/הערות) אבד בפסקה זו, לפי הגדרת המשתמש"]
                unit["err"] = None
                self.log.add("warn", "%s: התגיות לא שוחזרו; נשמר טקסט ללא עיצוב" % unit["id"], stage="validate", chunk=chunk_id, unit=unit["id"])
            else:
                unit["status"] = "flagged" if tag_only else "failed"
                unit["out"] = None
                unit["err"] = {"kind": kind, "messages": messages[:4]}
                self.log.add("error", "%s: %s" % (unit["id"], "; ".join(messages[:2])), stage="validate", chunk=chunk_id, unit=unit["id"], kind=kind,
                             retryable=False, suggestion="סומן לבדיקה ידנית; הטקסט המקורי נשמר" if tag_only else "נסה שוב ידנית או החלף מודל")
            self.project.touch(unit)

    def should_abort(self) -> bool:
        return self.cancel.is_set()

    def process_groups(self, groups: List[Dict[str, Any]], ctx: Dict[str, Any], chunk: Dict[str, Any], attempts: int, depth: int) -> None:
        pending = list(groups)
        corrections: List[str] = []
        last_kind: Dict[str, str] = {}
        last_msgs: Dict[str, List[str]] = {}
        last_out: Dict[str, str] = {}
        for attempt in range(1, attempts + 1):
            if self.should_abort():
                raise Aborted()
            flat: List[Dict[str, Any]] = []
            for group in pending:
                for req in group["reqs"]:
                    flat.append(req)
            user_prompt = build_user_prompt(dict(ctx, glossary=ctx["glossary"]), flat, self.fmt, corrections)
            try:
                text, usage = self.call_model(user_prompt, chunk["id"], attempt)
            except BookError as exc:
                if exc.kind == "context_too_large":
                    self.log.add("warn", "%s: הקשר/פלט גדול מדי, מפצל את המקטע" % chunk["id"], stage="split", chunk=chunk["id"], kind=exc.kind)
                    break
                if exc.kind in ("invalid_key", "model_unavailable"):
                    raise FatalProviderError(exc)
                corrections = []
                self.log.add("error", exc.message, stage="request", chunk=chunk["id"], chapter=chunk["ch"], provider=self.provider.id,
                             model=self.provider.model, kind=exc.kind, http=exc.http, retryable=exc.retryable, tried=attempt,
                             suggestion=exc.hint, unit=(pending[0]["unit"]["id"] if len(pending) == 1 else None))
                continue
            try:
                got, extraneous = parse_json_response(text) if self.fmt == "json" else parse_list_response(text)
            except BookError as exc:
                corrections = ["התשובה לא ניתנת לפענוח בפורמט המבוקש"]
                self.log.add("warn", "%s: %s" % (chunk["id"], exc.message), stage="parse", chunk=chunk["id"], kind="parse_failure", tried=attempt)
                continue
            fatal, per_item = validate_structure(flat, got, extraneous)
            if len(fatal) > 0:
                corrections = fatal
                self.log.add("warn", "%s: אימות מבנה נכשל: %s" % (chunk["id"], fatal[0]), stage="validate", chunk=chunk["id"], kind="bad_response",
                             tried=attempt, suggestion="ניסיון חוזר עם הודעת תיקון")
                continue
            by_id = {}
            for item in got:
                by_id[item["id"]] = item
            still: List[Dict[str, Any]] = []
            corrections = []
            for group in pending:
                unit = group["unit"]
                texts = []
                item_errors: List[str] = []
                for req in group["reqs"]:
                    item_errors.extend(per_item.get(req["id"], []))
                    texts.append(by_id[req["id"]]["text"].strip())
                joined = " ".join(texts)
                last_out[unit["id"]] = joined
                if len(item_errors) > 0:
                    last_kind[unit["id"]] = "other"
                    last_msgs[unit["id"]] = item_errors
                    corrections.extend(item_errors)
                    still.append(group)
                    continue
                clean, errors, warnings, kind = check_unit_output(unit, joined, self.settings, self.project.glossary, self.same_language)
                if len(errors) > 0:
                    last_kind[unit["id"]] = kind
                    last_msgs[unit["id"]] = errors
                    corrections.extend(errors)
                    still.append(group)
                else:
                    self.accept(unit, clean, warnings)
            pending = still
            if len(pending) == 0:
                return
            self.log.add("warn", "%s: %d רכיבים לא עברו אימות (ניסיון %d/%d)" % (chunk["id"], len(pending), attempt, attempts),
                         stage="validate", chunk=chunk["id"], tried=attempt, kind="bad_response")
        if len(pending) == 0:
            return
        if len(pending) > 1:
            middle = len(pending) // 2
            self.log.add("info", "%s: מפצל ל-%d ו-%d רכיבים" % (chunk["id"], middle, len(pending) - middle), stage="split", chunk=chunk["id"])
            self.process_groups(pending[:middle], ctx, chunk, 2, depth + 1)
            self.process_groups(pending[middle:], ctx, chunk, 2, depth + 1)
            return
        group = pending[0]
        unit = group["unit"]
        kind = last_kind.get(unit["id"], "other")
        self.fail_unit(unit, "bad_response", last_msgs.get(unit["id"], ["הכשל חזר על עצמו"]), chunk["id"], kind == "tags", last_out.get(unit["id"], ""))

    # ---------- קריאה למודל עם נסיגה מעריכית ----------
    def pace(self) -> None:
        """הגבלת קצב. ההמתנה מתבצעת מחוץ לנעילה ובפרוסות קצרות, כך שעצירה או השהיה קוטעות אותה מיד."""
        rpm = int(self.settings.get("rpm") or 0)
        if rpm <= 0:
            return
        interval = 60.0 / rpm
        with self.rate_lock:
            now = time.time()
            slot = max(now, self.last_request + interval)
            self.last_request = slot
        wait = slot - now
        if wait > 0:
            self.interruptible_sleep(wait)

    def interruptible_sleep(self, seconds: float) -> None:
        end = time.time() + seconds
        while True:
            if self.cancel.is_set() or self.pause_flag.is_set():
                raise Aborted()
            remaining = end - time.time()
            if remaining <= 0:
                return
            time.sleep(min(0.2, remaining))

    def call_model(self, user_prompt: str, chunk_id: str, attempt: int) -> Tuple[str, Dict[str, int]]:
        retries = int(self.settings.get("api_retries") or 5)
        delay = 2.0
        last_error: Optional[BookError] = None
        for api_try in range(retries + 1):
            # גבול בקשות: אחרי השהיה או עצירה לא יוצאת בקשה חדשה. בקשה שכבר באוויר נקטעת רק בעצירה (provider.cancel).
            if self.cancel.is_set() or self.pause_flag.is_set():
                raise Aborted()
            self.pace()
            started = time.time()
            try:
                text, usage = self.provider.complete(self.system_prompt, user_prompt, self.fmt == "json")
                with self.stats_lock:
                    meta_usage = self.project.meta["usage"]
                    meta_usage["requests"] = meta_usage["requests"] + 1
                    meta_usage["tokens_in"] = meta_usage["tokens_in"] + usage.get("in", 0)
                    meta_usage["tokens_out"] = meta_usage["tokens_out"] + usage.get("out", 0)
                    self.project.dirty_meta = True
                self.sync_rate_limit()
                return text, usage
            except BookError as exc:
                last_error = exc
                self.sync_rate_limit()
                if not exc.retryable or exc.kind not in ("rate_limit", "timeout", "api_error", "network"):
                    raise
                if api_try >= retries:
                    raise
                wait = exc.retry_after if exc.retry_after is not None else min(60.0, delay) + random.uniform(0, 0.5)
                self.log.add("warn", "%s - מנסה שוב בעוד %.1f שניות (%d/%d)" % (exc.message, wait, api_try + 1, retries),
                             stage="request", chunk=chunk_id, provider=self.provider.id, model=self.provider.model, kind=exc.kind,
                             http=exc.http, retryable=True, tried=api_try + 1, suggestion="נסיגה מעריכית אוטומטית")
                self.interruptible_sleep(wait)
                delay = delay * 2.0
        raise last_error if last_error is not None else BookError("api_error", "כשל לא ידוע")

    def progress(self) -> Dict[str, Any]:
        counts = self.project.counts()
        elapsed = (time.time() - self.started_at) if self.started_at else 0.0
        remaining_chars = counts["chars_total"] - counts["chars_done"]
        eta = None
        if self.chars_done_run > 0 and elapsed > 0 and self.alive():
            eta = remaining_chars / (self.chars_done_run / elapsed)
        return {"counts": counts, "chapter": self.current_chapter, "chunk": self.current_chunk,
                "chunks_total": self.chunks_total, "chunks_done": self.chunks_done, "elapsed": elapsed, "eta": eta}


# ======================================================================
# 21. בניית פלט ודוח סופי
# ======================================================================
def output_options(project: Project, job_mode: str) -> Dict[str, Any]:
    """אפשרויות כתיבת הפלט (שפות, היפוך כיוון, פריסה). משותף להפקת ה-EPUB ולתצוגה החיה, כדי שהתצוגה תהיה זהה לפלט."""
    settings = project.settings
    goal = settings["goal"]
    src_setting = settings.get("src_lang", "auto")
    if src_setting in ("", "auto"):
        src_setting = project.meta.get("stats", {}).get("language", "und")
    src_code, _, _ = resolve_language(src_setting)
    if GOALS[goal]["translate"]:
        tgt_code, _, _ = resolve_language(settings.get("tgt_lang", "he"))
    elif goal == "rewrite_he":
        tgt_code = "he"
    else:
        tgt_code = src_code
    layout = settings.get("layout") if goal in ("relayout", "restyle") else None
    return {"mode": job_mode, "src_lang": src_code, "tgt_lang": tgt_code,
            "flip_dir": goal in ("translate", "translate_edit", "rewrite_he") and dir_of(src_code) != dir_of(tgt_code),
            "set_lang": goal in ("translate", "translate_edit", "rewrite_he") and job_mode == "replace" and tgt_code != src_code,
            "rtl_isolate": bool(settings.get("rtl_isolate", True)), "layout": layout}


def build_outputs(project: Project, log: LogBuffer) -> Dict[str, Any]:
    settings = project.settings
    goal = settings["goal"]
    mode = settings.get("mode", "replace")
    jobs: List[Tuple[str, str]] = []
    if not GOALS[goal]["translate"]:
        jobs = [("replace", "output")]
    elif mode == "both":
        jobs = [("replace", "translation"), ("bilingual", "bilingual")]
    else:
        jobs = [(mode, "bilingual" if mode == "bilingual" else "translation")]
    src = EpubPackage(project.work_path)
    outputs: List[Dict[str, Any]] = []
    report: Dict[str, Any] = {"files": []}
    base_name = os.path.splitext(project.meta.get("filename", "book"))[0]
    for job_mode, suffix in jobs:
        opts = output_options(project, job_mode)
        out_name = "%s.%s.%s.epub" % (base_name, goal, suffix)
        out_path = os.path.join(project.output_dir, out_name)
        write_stats = src.write_output(out_path, project.units, opts)
        expect_lang = opts["tgt_lang"] if opts["set_lang"] else ""
        verification = verify_epub(src, out_path, job_mode, expect_lang, False, log)
        outputs.append({"name": out_name, "mode": job_mode, "size": os.path.getsize(out_path), "applied": write_stats["applied"]})
        report["files"].append({"name": out_name, "verify": verification, "applied": write_stats["applied"]})
        log.add("info" if verification["ok"] else "warn", "נוצר %s (%d רכיבים הוחלפו); אימות: %s" % (
            out_name, write_stats["applied"], "תקין" if verification["ok"] else "יש כשלים"), stage="output")
    src.close()
    failed = []
    flagged = []
    warned = 0
    for unit in project.units:
        if unit["status"] == "failed":
            failed.append(unit["id"])
        elif unit["status"] == "flagged":
            flagged.append(unit["id"])
        if len(unit.get("warn") or []) > 0:
            warned = warned + 1
    report["failed"] = failed
    report["flagged"] = flagged
    report["warned"] = warned
    report["usage"] = dict(project.meta["usage"])
    with project.lock:
        project.meta["outputs"] = outputs
        project.meta["final"] = report
        project.meta["outputs_stale"] = False
        project.meta["built_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        project.dirty_meta = True
    atomic_write_json(os.path.join(project.output_dir, "report.json"), report)
    project.flush()
    return report


# ======================================================================
# 22. מצב היישום, ניתוח קבצים שהועלו
# ======================================================================
class HttpError(Exception):
    def __init__(self, status: int, code: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.extra = extra or {}


class AppState:
    def __init__(self, port: int = 8765) -> None:
        self.port = port
        self.token = uuid.uuid4().hex
        self.lock = threading.RLock()
        self.projects: Dict[str, Project] = {}
        self.jobs: Dict[str, Job] = {}
        self.session_keys: Dict[str, str] = {}
        self.pdf_confirm: Dict[str, bool] = {}

    def load_projects(self) -> None:
        if not os.path.isdir(PROJECTS_DIR):
            return
        for name in sorted(os.listdir(PROJECTS_DIR)):
            if os.path.isfile(os.path.join(PROJECTS_DIR, name, "project.json")):
                try:
                    loaded = Project.load(name)
                    loaded.flush()  # שומר מיד תיקוני סטטוס אחרי קריסה (למשל running -> paused)
                    self.projects[name] = loaded
                except Exception as exc:
                    sys.stderr.write("טעינת פרויקט %s נכשלה: %s\n" % (name, Redactor.clean(str(exc))))

    def project(self, pid: str) -> Project:
        project = self.projects.get(pid)
        if project is None:
            raise HttpError(404, "not_found", "הפרויקט לא נמצא")
        return project

    def preview_key(self, pid: str) -> str:
        """מפתח גישה לתצוגה המקדימה של פרויקט אחד (נכסים ומסמך חי). נגזר מהאסימון, ולכן משתנה בכל הפעלה."""
        return hashlib.sha256(("preview|%s|%s" % (self.token, pid)).encode("utf-8")).hexdigest()[:32]

    def delete_project(self, pid: str) -> Dict[str, Any]:
        """המחיקה היחידה במערכת. נקראת רק מנתיבי מחיקה מפורשים (DELETE עם אישור, או POST /api/projects/delete)
        ולעולם לא כתוצאה לוואי של פעולה אחרת (אישור מבנה, כשל בניתוח, עצירה וכד')."""
        with self.lock:
            project = self.project(pid)
            job = self.jobs.get(pid)
            if job is not None and job.alive():
                raise HttpError(409, "busy", "יש לעצור את העיבוד לפני מחיקה")
            if project.meta.get("status") in ("analyzing", "building"):
                raise HttpError(409, "busy", "הפרויקט בעיבוד פנימי (ניתוח או הפקה); נסה שוב בעוד רגע")
            root = os.path.realpath(PROJECTS_DIR)
            target = os.path.realpath(project.dir)
            if os.path.dirname(target) != root or os.path.basename(target) != pid:
                raise HttpError(500, "unsafe_path", "נתיב הפרויקט אינו בתוך תיקיית הפרויקטים; המחיקה נחסמה")
            size = project.storage_bytes()
            try:
                shutil.rmtree(target)
            except OSError as exc:
                raise HttpError(500, "delete_failed", "המחיקה נכשלה: %s" % Redactor.clean(str(exc)))
            self.projects.pop(pid, None)
            self.jobs.pop(pid, None)
        return {"id": pid, "freed_bytes": size}

    def resolve_key(self, provider_id: str, supplied: Optional[str]) -> str:
        if supplied:
            self.session_keys[provider_id] = supplied
            Redactor.register(supplied)
            return supplied
        if provider_id in self.session_keys:
            return self.session_keys[provider_id]
        env_value = env_key_for(provider_id)
        if env_value != "":
            Redactor.register(env_value)
            return env_value
        remembered = SecretStore.load_all().get(provider_id, "")
        if remembered != "":
            Redactor.register(remembered)
        return remembered

    def provider_cfg(self, project: Project, supplied_key: Optional[str], model_override: str = "") -> Dict[str, Any]:
        settings = project.settings
        if not GOALS[settings["goal"]]["ai"]:
            return {"provider": "mock"}
        provider_id = settings["provider"]
        cfg = {"provider": provider_id, "model": model_override or settings.get("model", ""), "base_url": settings.get("base_url", ""),
               "temperature": settings.get("temperature"), "timeout": settings.get("timeout"),
               "max_output_tokens": settings.get("max_output_tokens"), "mock": settings.get("mock") or {},
               "num_ctx": settings.get("context_tokens") or None,
               "api_key": self.resolve_key(provider_id, supplied_key)}
        return cfg


def analyze_project(state: AppState, project: Project, upload_path: str) -> None:
    """שלב הנרמול והניתוח: EPUB ישיר; MOBI -> EPUB; PDF -> EPUB עם ציון ביטחון. כל כשל מסווג."""
    log = project.log
    try:
        source_path = os.path.join(project.dir, "source", project.meta["filename"])
        shutil.move(upload_path, source_path)
        fmt = project.meta["format"]
        if fmt == "epub":
            shutil.copy(source_path, project.work_path)
        elif fmt == "mobi":
            project.meta["conversion"] = convert_mobi(source_path, project.work_path, log)
        else:
            report = convert_pdf(source_path, project.work_path, log)
            project.meta["pdf_report"] = report
            project.meta["conversion"] = {"tool": report["tool"], "note": report["note"]}
        package = EpubPackage(project.work_path)
        model = package.extract_model()
        package.close()
        project.set_model(model)
        if fmt == "pdf":
            project.set_status("awaiting_confirmation")
        else:
            project.set_status("ready")
        if fmt == "mobi":
            stats = model["stats"]
            if stats["headings"] == 0:
                project.meta["conversion"]["note"] = project.meta["conversion"]["note"] + ". לא זוהו כותרות (MOBI מאבד לעיתים סימון כותרות)"
        log.add("info", "הקובץ נותח: %d פרקים, %d פסקאות, %d כותרות" % (
            model["stats"]["chapters"], model["stats"]["paragraphs"], model["stats"]["headings"]), stage="analyze")
    except BookError as exc:
        log.add("error", exc.message, stage="analyze", kind=exc.kind, suggestion=exc.hint)
        project.set_status("error", {"kind": exc.kind, "message": exc.message, "hint": exc.hint})
    except Exception as exc:
        log.add("error", "שגיאה בניתוח: %s" % exc, stage="analyze", kind="internal", trace=traceback.format_exc()[-600:])
        project.set_status("error", {"kind": "internal", "message": Redactor.clean(str(exc)), "hint": ERROR_HINTS["internal"]})
    finally:
        project.flush()


UNIT_GROUPS = ("done", "failed", "flagged", "pending")


def unit_group(project: Project, unit: Dict[str, Any]) -> str:
    """קבוצת הסטטוס של יחידה, באותם כללים כמו Project.counts (יחידות meta מדולגות כשהמטרה אינה תרגום)."""
    if unit["scope"] == "meta" and not GOALS.get(project.settings["goal"], {}).get("translate"):
        return ""
    status = unit["status"]
    if status in OK_STATUSES:
        return "done"
    if status == "failed":
        return "failed"
    if status == "flagged":
        return "flagged"
    return "pending"


def unit_view(unit: Dict[str, Any], full: bool = False) -> Dict[str, Any]:
    view = {"id": unit["id"], "type": unit["type"], "level": unit["level"], "ch": unit["ch"], "status": unit["status"],
            "src": strip_tags(unit["tagged"]), "out": strip_tags(unit["out"]) if unit.get("out") else None,
            "warn": unit.get("warn") or [], "err": unit.get("err"), "chunk": unit.get("chunk"), "file": unit["file"]}
    if full:
        view["tagged"] = unit["tagged"]
        view["out_tagged"] = unit.get("out") or ""
    return view


# ---------- תצוגה חיה ----------
# ה-EPUB נטען ל-iframe עם sandbox="allow-same-origin" (בלי allow-scripts) וכותרת CSP שחוסמת כל סקריפט ומשאב חיצוני.
# ההרשאה לנכסים ולמסמך החי ניתנת במפתח בתוך הנתיב (נגזר מהאסימון ומזהה הפרויקט), ולא באסימון עצמו, כך שהוא נותן גישת קריאה
# לתצוגה המקדימה של פרויקט אחד בלבד, ונתיבי URL יחסיים בתוך קבצי CSS ממשיכים לעבוד בלי שכתוב.
LIVE_CSP = ("default-src 'none'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self' data:; "
            "media-src 'self'; base-uri 'self'; form-action 'none'")
LIVE_DROP_TAGS = set(["script", "iframe", "object", "embed", "applet", "frame", "frameset", "base"])
MAX_ASSET_BYTES = 64 * 1024 * 1024
ASSET_TYPES = {".css": "text/css; charset=utf-8", ".xhtml": "application/xhtml+xml", ".html": "application/xhtml+xml",
               ".htm": "application/xhtml+xml", ".xml": "application/xml", ".svg": "image/svg+xml", ".png": "image/png",
               ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
               ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf", ".otf": "font/otf",
               ".mp3": "audio/mpeg", ".mp4": "video/mp4", ".ncx": "application/x-dtbncx+xml"}


def preview_mode(project: Project, requested: str) -> str:
    """איזה מצב להציג: תרגום בלבד או דו־לשוני. כשהמצב בהגדרות הוא 'both', המשתמש בוחר."""
    settings = project.settings
    if not GOALS[settings["goal"]]["translate"]:
        return "replace"
    configured = settings.get("mode", "replace")
    if configured == "bilingual":
        return "bilingual"
    if configured == "both" and requested in ("replace", "bilingual"):
        return requested
    return "replace"


def remove_keep_tail(el: Any) -> None:
    parent = el.getparent()
    if parent is None:
        return
    tail = el.tail
    if tail:
        previous = el.getprevious()
        if previous is not None:
            previous.tail = (previous.tail or "") + tail
        else:
            parent.text = (parent.text or "") + tail
    parent.remove(el)


def decorate_live_tree(tree: Any, package: "EpubPackage", pid: str, key: str, doc_path: str, doc_set: set, mode: str) -> None:
    """מכין את המסמך המשוחזר לתצוגה: מסיר קוד פעיל, קובע בסיס לנכסים, ומפנה קישורים בין פרקים לתצוגה החיה."""
    root = tree.getroot()
    asset_root = "/api/p/%s/asset/%s/" % (pid, key)
    for el in list(root.iter()):
        if not isinstance(el.tag, str):
            continue
        name = local_name(el.tag)
        if name in LIVE_DROP_TAGS:
            remove_keep_tail(el)
        elif name == "meta" and (el.get("http-equiv") or "").lower() == "refresh":
            remove_keep_tail(el)
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in list(el.attrib):
            if attr.lower().startswith("on"):
                del el.attrib[attr]
    head = None
    for el in root.iter():
        if isinstance(el.tag, str) and local_name(el.tag) == "head":
            head = el
            break
    if head is not None:
        ns = etree.QName(head.tag).namespace
        base = etree.Element("{%s}base" % ns if ns else "base")
        doc_dir = posixpath.dirname(doc_path)
        base.set("href", asset_root + (urllib.parse.quote(doc_dir, safe="/") + "/" if doc_dir else ""))
        head.insert(0, base)
    for el in list(root.iter()):
        if not isinstance(el.tag, str):
            continue
        name = local_name(el.tag)
        href = el.get("href")
        if name == "a" and href is not None:
            stripped = href.strip()
            if stripped == "" or stripped.startswith("#"):
                continue
            parsed = urllib.parse.urlparse(stripped)
            if parsed.scheme != "" or stripped.startswith("//"):
                del el.attrib["href"]
                el.set("title", "קישור חיצוני (מושבת בתצוגה המקדימה)")
                continue
            target = package.resolve(doc_path, stripped)
            if target in doc_set:
                url = "/api/p/%s/live/%s/%s?mode=%s" % (pid, key, urllib.parse.quote(target, safe="/"), mode)
                if parsed.fragment:
                    url = url + "#" + parsed.fragment
                el.set("href", url)
        elif name == "link" and href is not None and "stylesheet" in (el.get("rel") or "").lower():
            if urllib.parse.urlparse(href).scheme != "" or href.startswith("//"):
                remove_keep_tail(el)
                continue
            target = package.resolve(doc_path, href)
            el.set("href", asset_root + urllib.parse.quote(target, safe="/") + "?final=1")


def build_live_document(project: Project, key: str, doc_path: str, requested_mode: str) -> Tuple[bytes, int]:
    """משחזר מסמך אחד מה-EPUB המקורי עם הטקסטים העדכניים (unit["out"]), לתצוגה חיה."""
    if not os.path.isfile(project.work_path):
        raise HttpError(404, "no_book", "הספר עדיין לא נותח")
    package = EpubPackage(project.work_path)
    try:
        doc_set = set()
        for path, role in package.document_files():
            doc_set.add(path)
        if doc_path not in doc_set:
            raise HttpError(404, "not_found", "המסמך לא קיים בספר")
        mode = preview_mode(project, requested_mode)
        opts = output_options(project, mode)
        with project.lock:
            file_units = [unit for unit in project.units if unit["file"] == doc_path]
        tree, applied = package.render_document(doc_path, file_units, opts, anchors=True, all_units=file_units)
        decorate_live_tree(tree, package, project.id, key, doc_path, doc_set, mode)
        return serialize_xml(tree), applied
    finally:
        package.close()


def read_asset(project: Project, raw_path: str, final: bool) -> Tuple[bytes, str]:
    """קורא קובץ (תמונה, CSS, גופן...) ישירות מארכיון ה-EPUB. final=True מחיל על CSS את אותו היפוך כיוון שיש בפלט הסופי."""
    clean = urllib.parse.unquote(raw_path)
    if clean == "" or "\x00" in clean or "\\" in clean:
        raise HttpError(400, "bad_path", "נתיב לא תקין")
    norm = posixpath.normpath(clean)
    if norm in (".", "") or norm.startswith("/") or norm == ".." or norm.startswith("../"):
        raise HttpError(403, "bad_path", "הנתיב מחוץ לארכיון הספר")
    if not os.path.isfile(project.work_path):
        raise HttpError(404, "no_book", "הספר עדיין לא נותח")
    package = EpubPackage(project.work_path)
    try:
        opts = output_options(project, "replace")
        if norm not in package.names:
            css_path = posixpath.join(package.opf_dir, "bai-style.css")
            if norm == css_path and opts.get("layout"):
                css = build_layout_css(opts["layout"], dir_of(opts["tgt_lang"]) == "rtl")
                return css.encode("utf-8"), "text/css; charset=utf-8"
            raise HttpError(404, "not_found", "הקובץ לא קיים בארכיון")
        info = package.zf.getinfo(norm)
        if info.file_size > MAX_ASSET_BYTES:
            raise HttpError(413, "too_large", "הקובץ גדול מדי לתצוגה")
        data = package.read(norm)
        extension = posixpath.splitext(norm)[1].lower()
        ctype = ASSET_TYPES.get(extension, "")
        if ctype == "":
            entry = package.manifest_by_path.get(norm)
            declared = entry["type"] if entry is not None else ""
            ctype = declared if declared.split("/")[0] in ("image", "font", "audio", "video") else "application/octet-stream"
        if final and extension == ".css" and opts["flip_dir"]:
            data = mirror_css(data.decode("utf-8", errors="replace")).encode("utf-8")
        return data, ctype
    finally:
        package.close()


def project_summary(state: AppState, project: Project, since: int = 0) -> Dict[str, Any]:
    job = state.jobs.get(project.id)
    running = job is not None and job.alive()
    progress = job.progress() if job is not None else {"counts": project.counts(), "chapter": 0, "chunk": "", "chunks_total": 0,
                                                       "chunks_done": 0, "elapsed": 0.0, "eta": None}
    usage = project.meta.get("usage", {})
    cost = (usage.get("tokens_in", 0) * float(project.settings.get("price_in") or 0) +
            usage.get("tokens_out", 0) * float(project.settings.get("price_out") or 0)) / 1000000.0
    failed_chunks: Dict[str, int] = {}
    for unit in project.units:
        if unit["status"] in ("failed", "flagged") and unit.get("chunk"):
            failed_chunks[unit["chunk"]] = failed_chunks.get(unit["chunk"], 0) + 1
    meta = dict(project.meta)
    pdf_report = meta.get("pdf_report")
    if pdf_report:
        meta["pdf_report"] = {k: v for k, v in pdf_report.items() if k != "preview"}
    return {"meta": meta, "settings": project.settings, "running": running, "progress": progress, "cost": cost,
            "chapters": project.chapters, "failed_chunks": failed_chunks, "logs": project.log.since(since),
            "glossary_count": len(project.glossary), "tm_size": len(project.tm), "rev": project.rev}


def glossary_translate_terms(state: AppState, project: Project, key: Optional[str]) -> int:
    """מבקש מהמודל להציע תרגום לערכים שאין להם עדיין תרגום. מחזיר מספר ערכים שהושלמו."""
    cfg = state.provider_cfg(project, key)
    provider = make_provider(cfg)
    code, name, rtl = resolve_language(project.settings.get("tgt_lang", "he"))
    empty = [e for e in project.glossary if not (e.get("target") or "").strip()][:80]
    if len(empty) == 0:
        return 0
    terms = [e["source"] for e in empty]
    system = ("You translate glossary terms (names, places, technical terms) from a book into %s. Return only JSON: "
              '{"translations": {"<term>": "<translation>"}}. Transliterate names naturally.' % name)
    text, _ = provider.complete(system, json.dumps(terms, ensure_ascii=False), True)
    data = json.loads(strip_fences(text))
    mapping = data.get("translations", data) if isinstance(data, dict) else {}
    count = 0
    for entry in empty:
        value = mapping.get(entry["source"])
        if isinstance(value, str) and value.strip() != "":
            entry["target"] = value.strip()
            count = count + 1
    project.dirty_meta = True
    project.flush()
    return count


# ======================================================================
# 23. שרת HTTP מקומי
# ======================================================================
class Api:
    """לוגיקת נקודות הקצה. כל מתודה מקבלת (state, params, body) ומחזירה JSON."""

    @staticmethod
    def info(state: AppState) -> Dict[str, Any]:
        providers = []
        for pid, cls in PROVIDER_CLASSES.items():
            if pid == "mock":
                continue
            probe = make_provider({"provider": pid})
            providers.append({"id": pid, "label": cls.label, "needs_key": cls.needs_key, "default_base": probe.base_url,
                              "env_key": bool(env_key_for(pid)), "remembered": bool(SecretStore.load_all().get(pid)),
                              "local": bool(probe.is_local)})
        goals = [{"id": gid, "label": g["label"], "ai": g["ai"], "translate": g["translate"]} for gid, g in GOALS.items()]
        languages = [{"code": c, "en": e, "he": h} for c, e, h, r in LANGUAGES]
        try:
            import_pymupdf()
            has_pdf = True
        except BookError:
            has_pdf = False
        try:
            import mobi  # noqa: F401
            has_mobi_lib = True
        except ImportError:
            has_mobi_lib = False
        return {"version": APP_VERSION, "providers": providers, "goals": goals, "languages": languages,
                "features": {"calibre": find_ebook_convert() is not None, "pdf": has_pdf, "mobi_lib": has_mobi_lib,
                             "crypto": SecretStore.available(), "epubcheck": find_epubcheck() is not None},
                "default_settings": default_settings(), "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024)}

    @staticmethod
    def list_projects(state: AppState, detail: bool = False) -> List[Dict[str, Any]]:
        """רשימת הפרויקטים. עם detail=True מתווספים התקדמות, גודל בדיסק ומועד עדכון (למסך הניהול)."""
        with state.lock:
            snapshot = list(state.projects.values())
        result = []
        for project in sorted(snapshot, key=lambda p: p.meta.get("created", ""), reverse=True):
            job = state.jobs.get(project.id)
            running = job is not None and job.alive()
            status = project.meta.get("status")
            row = {"id": project.id, "filename": project.meta.get("filename"), "format": project.meta.get("format"),
                   "status": status, "created": project.meta.get("created"), "running": running,
                   "busy": running or status in ("analyzing", "building"),
                   "has_output": bool(project.meta.get("outputs")), "outputs_stale": bool(project.meta.get("outputs_stale"))}
            if detail:
                counts = project.counts()
                row["done"] = counts["done"]
                row["total"] = counts["total"]
                row["size_bytes"] = project.storage_bytes()
                try:
                    row["updated"] = datetime.datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(project.dir, "project.json"))).isoformat(timespec="seconds")
                except OSError:
                    row["updated"] = None
            result.append(row)
        return result

    @staticmethod
    def delete_projects(state: AppState, body: Dict[str, Any]) -> Dict[str, Any]:
        """מחיקה מפורשת של פרויקטים לפי רשימת מזהים. נדרש confirm == "DELETE"; אין תחליפי תו כלליים או "הכול"."""
        if body.get("confirm") != "DELETE":
            raise HttpError(400, "confirmation_required", "מחיקה דורשת אישור מפורש (confirm=DELETE)")
        ids = body.get("ids")
        if not isinstance(ids, list) or len(ids) == 0 or len(ids) > 200:
            raise HttpError(400, "bad_ids", "יש לציין רשימה מפורשת של 1 עד 200 מזהי פרויקטים")
        unique: List[str] = []
        for pid in ids:
            if not isinstance(pid, str) or re.match(r"^[A-Za-z0-9\-]+$", pid) is None:
                raise HttpError(400, "bad_ids", "מזהה פרויקט לא תקין")
            if pid not in unique:
                unique.append(pid)
        deleted: List[str] = []
        failed: List[Dict[str, Any]] = []
        for pid in unique:
            try:
                state.delete_project(pid)
                deleted.append(pid)
            except HttpError as exc:
                failed.append({"id": pid, "error": exc.code, "message": exc.message})
        return {"ok": len(failed) == 0, "deleted": deleted, "failed": failed}

    @staticmethod
    def provider_test(state: AppState, body: Dict[str, Any]) -> Dict[str, Any]:
        provider_id = body.get("provider", "")
        cfg = {"provider": provider_id, "model": body.get("model", ""), "base_url": body.get("base_url", ""),
               "timeout": min(float(body.get("timeout") or 30), 60), "temperature": body.get("temperature"),
               "api_key": state.resolve_key(provider_id, body.get("key"))}
        provider = make_provider(cfg)
        try:
            result = provider.test_connection()
            result["local"] = bool(provider.is_local)
            return result
        except BookError as exc:
            return {"ok": False, "kind": exc.kind, "message": exc.message, "hint": exc.hint}

    @staticmethod
    def provider_models(state: AppState, body: Dict[str, Any]) -> Dict[str, Any]:
        provider_id = body.get("provider", "")
        cfg = {"provider": provider_id, "base_url": body.get("base_url", ""), "timeout": 30,
               "api_key": state.resolve_key(provider_id, body.get("key"))}
        provider = make_provider(cfg)
        if provider.needs_key and provider.api_key == "":
            return {"ok": False, "message": "לא הוזן מפתח", "models": []}
        try:
            return {"ok": True, "models": provider.list_models()}
        except BookError as exc:
            return {"ok": False, "kind": exc.kind, "message": exc.message, "hint": exc.hint, "models": []}

    @staticmethod
    def live_index(state: AppState, project: Project) -> Dict[str, Any]:
        """רשימת המסמכים לתצוגה חיה (לפי סדר הספר), המפתח לכתובות, והמצבים האפשריים."""
        if not os.path.isfile(project.work_path):
            raise HttpError(400, "no_book", "הספר עדיין לא נותח")
        package = EpubPackage(project.work_path)
        try:
            docs = package.document_files()
        finally:
            package.close()
        titles: Dict[str, str] = {}
        chapter_of: Dict[str, int] = {}
        for chapter in project.chapters:
            file_name = chapter.get("file")
            if chapter.get("kind") == "meta" or not file_name or file_name in titles:
                continue
            titles[file_name] = chapter.get("title") or ""
            chapter_of[file_name] = chapter.get("index")
        done: Dict[str, int] = {}
        total: Dict[str, int] = {}
        with project.lock:
            for unit in project.units:
                if unit["scope"] != "content":
                    continue
                total[unit["file"]] = total.get(unit["file"], 0) + 1
                if unit["status"] in OK_STATUSES:
                    done[unit["file"]] = done.get(unit["file"], 0) + 1
        rows = []
        for path, role in docs:
            rows.append({"path": path, "title": titles.get(path) or posixpath.basename(path), "ch": chapter_of.get(path),
                         "role": role, "done": done.get(path, 0), "total": total.get(path, 0)})
        goal = project.settings["goal"]
        if GOALS[goal]["translate"] and project.settings.get("mode", "replace") == "both":
            modes = ["replace", "bilingual"]
        else:
            modes = [preview_mode(project, "")]
        return {"key": state.preview_key(project.id), "docs": rows, "modes": modes, "mode": modes[0], "rev": project.rev}

    @staticmethod
    def prepare_cfg(state: AppState, project: Project, body: Dict[str, Any], model: str = "") -> Dict[str, Any]:
        """אימות מפתח, מודל ואישור שליחה לספק חיצוני; מחזיר הגדרת ספק. משותף להתחלה, ניסיון חוזר ושליחה מחדש."""
        settings = project.settings
        if GOALS[settings["goal"]]["ai"]:
            cfg = state.provider_cfg(project, body.get("key"), model)
            provider = make_provider(cfg)
            if provider.needs_key and provider.api_key == "":
                raise HttpError(400, "no_key", "לא הוזן מפתח עבור %s" % provider.label)
            if (cfg.get("model") or "") == "":
                raise HttpError(400, "no_model", "לא נבחר מודל")
            if not provider.is_local and not body.get("ack_external"):
                raise HttpError(400, "ack_required", "יש לאשר שהטקסט נשלח לספק חיצוני",
                                {"host": urllib.parse.urlparse(provider.base_url).hostname or provider.label, "provider": provider.label})
            if body.get("remember") and body.get("key"):
                SecretStore.save(settings["provider"], body["key"])
        else:
            cfg = {"provider": "mock"}
        if body.get("remember") is False and body.get("forget"):
            SecretStore.forget(settings["provider"])
        return cfg

    @staticmethod
    def resend_unit(state: AppState, project: Project, body: Dict[str, Any]) -> Dict[str, Any]:
        """שליחה מחדש של יחידה אחת למודל לפי ההגדרות הנוכחיות, עם הקשר מלא (ראו Job.start_resend)."""
        unit = project.units_by_id.get(body.get("id", ""))
        if unit is None:
            raise HttpError(404, "not_found", "הרכיב לא נמצא")
        existing = state.jobs.get(project.id)
        if existing is not None and existing.alive():
            raise HttpError(409, "busy", "העיבוד רץ כרגע; השהה או עצור לפני שליחה מחדש")
        if project.meta.get("status") in ("analyzing", "awaiting_confirmation", "building"):
            raise HttpError(400, "not_ready", "הפרויקט עדיין לא מוכן לעיבוד")
        goal = project.settings["goal"]
        if not GOALS[goal]["ai"]:
            raise HttpError(400, "not_ai", "המטרה הנוכחית אינה משתמשת במודל")
        if unit["scope"] == "meta" and not GOALS[goal]["translate"]:
            raise HttpError(400, "not_applicable", "רכיב זה אינו מעובד במטרה הנוכחית")
        cfg = Api.prepare_cfg(state, project, body, "")
        job = Job(project, cfg)
        state.jobs[project.id] = job
        project.log.add("info", "שליחה מחדש של %s למודל %s" % (unit["id"], cfg.get("model") or "-"), stage="resend", unit=unit["id"])
        job.start_resend(unit)
        return {"ok": True}

    @staticmethod
    def start(state: AppState, project: Project, body: Dict[str, Any], retry_ids: Optional[List[str]] = None, model: str = "") -> Dict[str, Any]:
        existing = state.jobs.get(project.id)
        if existing is not None and existing.alive():
            raise HttpError(409, "busy", "העיבוד כבר רץ")
        if project.meta.get("status") in ("analyzing", "awaiting_confirmation", "error") and not project.units:
            raise HttpError(400, "not_ready", "הפרויקט עדיין לא מוכן לעיבוד")
        if project.meta.get("status") == "awaiting_confirmation":
            raise HttpError(400, "not_ready", "יש לאשר את המבנה שזוהה לפני התחלה")
        settings = project.settings
        cfg = Api.prepare_cfg(state, project, body, model)
        retry_units = None
        if retry_ids is not None:
            retry_units = []
            for unit_id in retry_ids:
                unit = project.units_by_id[unit_id]
                unit["status"] = "pending"
                unit["err"] = None
                unit["out"] = None
                unit["warn"] = []
                project.touch(unit)
                retry_units.append(unit)
            project.flush()  # האיפוס נשמר לפני שהעיבוד מתחיל
        job = Job(project, cfg)
        state.jobs[project.id] = job
        project.log.add("info", "העיבוד התחיל (מטרה: %s)" % GOALS[settings["goal"]]["label"], stage="start")
        job.start(retry_units)
        return {"ok": True}


def make_handler(state: AppState) -> Any:
    allowed_hosts = set(["127.0.0.1:%d" % state.port, "localhost:%d" % state.port, "[::1]:%d" % state.port,
                         "127.0.0.1", "localhost"])
    ROUTE_P = re.compile(r"^/api/p/([A-Za-z0-9\-]+)(?:/(.*))?$")
    ROUTE_PREVIEW = re.compile(r"^/api/p/([A-Za-z0-9\-]+)/(asset|live)/([0-9a-f]{32})/(.+)$")

    class Handler(BaseHTTPRequestHandler):
        server_version = "BookAI/" + APP_VERSION

        def log_message(self, fmt: str, *args: Any) -> None:
            return

        # ---------- עזרים ----------
        def send_json(self, data: Any, status: int = 200) -> None:
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def read_body(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            if length > 5 * 1024 * 1024:
                raise HttpError(413, "too_large", "גוף הבקשה גדול מדי")
            if length == 0:
                return {}
            try:
                return json.loads(self.rfile.read(length).decode("utf-8"))
            except ValueError:
                raise HttpError(400, "bad_json", "גוף הבקשה אינו JSON תקין")

        def check_access(self, query: Dict[str, List[str]]) -> None:
            host = self.headers.get("Host", "")
            if host not in allowed_hosts:
                raise HttpError(403, "bad_host", "כותרת Host אינה מורשית")
            supplied = self.headers.get("X-Token") or (query.get("t") or [""])[0]
            if supplied != state.token:
                raise HttpError(403, "bad_token", "אסימון גישה שגוי")

        # ---------- ניתוב ----------
        def handle_any(self, method: str) -> None:
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            path = parsed.path
            try:
                if method == "GET" and path == "/":
                    if self.headers.get("Host", "") not in allowed_hosts:
                        raise HttpError(403, "bad_host", "כותרת Host אינה מורשית")
                    page = UI_HTML.replace("__TOKEN__", state.token).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(page)))
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Security-Policy", "default-src 'self' 'unsafe-inline'; img-src 'self' data:")
                    self.end_headers()
                    self.wfile.write(page)
                    return
                preview_match = ROUTE_PREVIEW.match(path)
                if preview_match is not None and method == "GET":
                    # תצוגה מקדימה בתוך iframe: אי אפשר לשלוח כותרת X-Token, ולכן המפתח בנתיב מחליף את האסימון (לפרויקט הזה בלבד)
                    if self.headers.get("Host", "") not in allowed_hosts:
                        raise HttpError(403, "bad_host", "כותרת Host אינה מורשית")
                    preview_pid, preview_kind, preview_key, preview_rest = preview_match.groups()
                    if hmac.compare_digest(preview_key, state.preview_key(preview_pid)):
                        self.serve_preview_resource(state.project(preview_pid), preview_kind, preview_key, preview_rest, query)
                        return
                self.check_access(query)
                if path == "/api/model-profile" and method == "GET":
                    profile = match_model_profile((query.get("provider") or [""])[0], (query.get("model") or [""])[0])
                    self.send_json({"profile": public_profile(profile) if profile is not None else None})
                    return
                if path == "/api/upload" and method == "POST":
                    self.send_json(self.upload())
                    return
                if path == "/api/info" and method == "GET":
                    self.send_json(Api.info(state))
                    return
                if path == "/api/projects" and method == "GET":
                    detail = (query.get("detail") or ["0"])[0] == "1"
                    self.send_json(Api.list_projects(state, detail))
                    return
                if path == "/api/projects/delete" and method == "POST":
                    self.send_json(Api.delete_projects(state, self.read_body()))
                    return
                if path == "/api/provider/test" and method == "POST":
                    self.send_json(Api.provider_test(state, self.read_body()))
                    return
                if path == "/api/provider/models" and method == "POST":
                    self.send_json(Api.provider_models(state, self.read_body()))
                    return
                if path == "/api/secrets/forget" and method == "POST":
                    body = self.read_body()
                    SecretStore.forget(body.get("provider", ""))
                    state.session_keys.pop(body.get("provider", ""), None)
                    self.send_json({"ok": True})
                    return
                match = ROUTE_P.match(path)
                if match is not None:
                    self.project_route(method, match.group(1), match.group(2) or "", query)
                    return
                raise HttpError(404, "not_found", "נתיב לא קיים")
            except HttpError as exc:
                self.send_json(dict({"error": exc.code, "message": exc.message}, **exc.extra), exc.status)
            except BookError as exc:
                self.send_json({"error": exc.kind, "message": exc.message, "hint": exc.hint}, 400)
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as exc:
                sys.stderr.write(Redactor.clean(traceback.format_exc()) + "\n")
                self.send_json({"error": "internal", "message": Redactor.clean(str(exc))}, 500)

        def do_GET(self) -> None:
            self.handle_any("GET")

        def do_POST(self) -> None:
            self.handle_any("POST")

        def do_DELETE(self) -> None:
            self.handle_any("DELETE")

        # ---------- העלאה ----------
        def upload(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            filename = urllib.parse.unquote(self.headers.get("X-Filename") or "book")
            filename = os.path.basename(filename.replace("\\", "/"))
            if length <= 0:
                raise BookError("bad_upload", "הקובץ ריק")
            if length > MAX_UPLOAD_BYTES:
                raise BookError("bad_upload", "הקובץ גדול מדי (מקסימום %d MB)" % (MAX_UPLOAD_BYTES // (1024 * 1024)))
            os.makedirs(HOME_DIR, exist_ok=True)
            handle, temp_path = tempfile.mkstemp(prefix="upload_", dir=HOME_DIR)
            received = 0
            try:
                with os.fdopen(handle, "wb") as out:
                    while received < length:
                        chunk = self.rfile.read(min(1024 * 1024, length - received))
                        if not chunk:
                            break
                        out.write(chunk)
                        received = received + len(chunk)
                if received != length:
                    raise BookError("bad_upload", "ההעלאה נקטעה")
                fmt = sniff_format(temp_path, filename)
            except BaseException:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
            project = Project.create(filename, length, fmt)
            state.projects[project.id] = project
            project.log.add("info", "הקובץ הועלה: %s (%d בתים, %s)" % (filename, length, fmt), stage="upload")
            threading.Thread(target=analyze_project, args=(state, project, temp_path), daemon=True).start()
            return {"id": project.id}

        # ---------- נתיבי פרויקט ----------
        def project_route(self, method: str, pid: str, rest: str, query: Dict[str, List[str]]) -> None:
            project = state.project(pid)
            if method == "DELETE" and rest == "":
                # מחיקה מפורשת בלבד: חייבים לציין ?confirm=<מזהה הפרויקט> (אותו מזהה שבנתיב).
                if (query.get("confirm") or [""])[0] != pid:
                    raise HttpError(400, "confirmation_required", "מחיקה דורשת אישור מפורש: הוסף ?confirm=<מזהה הפרויקט>")
                result = state.delete_project(pid)
                self.send_json({"ok": True, "deleted": True, "id": result["id"], "freed_bytes": result["freed_bytes"]})
                return
            if method == "GET":
                if rest == "" or rest == "status":
                    since = int((query.get("since") or ["0"])[0])
                    self.send_json(project_summary(state, project, since))
                    return
                if rest == "units":
                    chapter = int((query.get("chapter") or ["-1"])[0])
                    flt = (query.get("filter") or [""])[0]
                    offset = int((query.get("offset") or ["0"])[0])
                    limit = min(300, int((query.get("limit") or ["120"])[0]))
                    upto = (query.get("upto") or [""])[0]  # טוען עד היחידה הזו (ועוד מעט אחריה): לניווט ליחידה רחוקה
                    rows = []
                    total = 0
                    found = False
                    extra = 0
                    for unit in project.units:
                        if chapter >= 0 and unit["ch"] != chapter:
                            continue
                        if flt == "issues" and unit["status"] not in ("failed", "flagged") and not unit.get("warn"):
                            continue
                        total = total + 1
                        if total <= offset:
                            continue
                        if upto == "":
                            if len(rows) < limit:
                                rows.append(unit_view(unit, True))
                        elif len(rows) < 3000 and (not found or extra < 15):
                            rows.append(unit_view(unit, True))
                            if found:
                                extra = extra + 1
                            elif unit["id"] == upto:
                                found = True
                    self.send_json({"units": rows, "total": total, "found": found})
                    return
                if rest == "unit-index":
                    status = (query.get("status") or [""])[0]
                    chunk_id = (query.get("chunk") or [""])[0]
                    if chunk_id == "" and status not in UNIT_GROUPS:
                        raise HttpError(400, "bad_status", "סטטוס לא מוכר")
                    ids = []
                    for unit in project.units:
                        if chunk_id != "":
                            if unit.get("chunk") == chunk_id:
                                ids.append(unit["id"])
                        elif unit_group(project, unit) == status:
                            ids.append(unit["id"])
                    self.send_json({"ids": ids, "total": len(ids)})
                    return
                if rest == "live-index":
                    self.send_json(Api.live_index(state, project))
                    return
                if rest.startswith("asset/") or rest.startswith("live/"):
                    kind, _, tail = rest.partition("/")
                    self.serve_preview_resource(project, kind, state.preview_key(pid), tail, query)
                    return
                if rest == "preview":
                    report = project.meta.get("pdf_report") or {}
                    self.send_json({"preview": report.get("preview", []), "chapters": project.chapters})
                    return
                if rest == "glossary":
                    self.send_json({"entries": project.glossary})
                    return
                if rest.startswith("download/"):
                    self.download(project, urllib.parse.unquote(rest[len("download/"):]))
                    return
            if method == "POST":
                body = self.read_body()
                if rest == "settings":
                    job = state.jobs.get(pid)
                    if job is not None and job.alive():
                        raise HttpError(409, "busy", "אי אפשר לשנות הגדרות בזמן עיבוד")
                    incoming = body.get("settings", {})
                    incoming.pop("api_key", None)
                    merged = dict(project.settings)
                    for key, value in incoming.items():
                        if key in default_settings():
                            merged[key] = value
                    merged["mock"] = project.settings.get("mock") or {}
                    project.settings = merged
                    project.rev = project.rev + 1
                    project.dirty_meta = True
                    project.flush()
                    self.send_json({"ok": True})
                    return
                if rest == "confirm":
                    status = project.meta.get("status")
                    if body.get("accept"):
                        if status == "awaiting_confirmation":
                            project.set_status("ready")
                        elif status != "ready":
                            raise HttpError(409, "not_pending", "הפרויקט אינו ממתין לאישור מבנה")
                        self.send_json({"ok": True})
                    else:
                        # דחייה אינה מחיקה: הפרויקט נשאר כפי שהוא (ממתין לאישור) וניתן לחזור אליו או למחוק אותו במפורש.
                        project.log.add("info", "המבנה לא אושר כרגע; הפרויקט נשמר ולא נמחק", stage="confirm")
                        project.flush()
                        self.send_json({"ok": True, "kept": True})
                    return
                if rest in ("start", "resume"):
                    self.send_json(Api.start(state, project, body))
                    return
                if rest in ("pause", "stop"):
                    job = state.jobs.get(pid)
                    if job is None or not job.alive():
                        raise HttpError(409, "idle", "אין עיבוד פעיל")
                    job.pause() if rest == "pause" else job.stop()
                    project.log.add("info", "התקבלה פקודת %s" % ("השהיה" if rest == "pause" else "עצירה"), stage="control")
                    self.send_json({"ok": True})
                    return
                if rest == "retry-chunk":
                    ids = [u["id"] for u in project.units if u.get("chunk") == body.get("chunk") and u["status"] in ("failed", "flagged")]
                    if len(ids) == 0:
                        raise HttpError(404, "not_found", "אין רכיבים כושלים במקטע הזה")
                    self.send_json(Api.start(state, project, body, ids, body.get("model", "")))
                    return
                if rest == "retry-failed":
                    ids = [u["id"] for u in project.units if u["status"] in ("failed", "flagged")]
                    if len(ids) == 0:
                        raise HttpError(404, "not_found", "אין רכיבים כושלים")
                    self.send_json(Api.start(state, project, body, ids, body.get("model", "")))
                    return
                if rest == "unit-save":
                    unit = project.units_by_id.get(body.get("id", ""))
                    if unit is None:
                        raise HttpError(404, "not_found", "הרכיב לא נמצא")
                    text = WS_RE.sub(" ", body.get("text", "")).strip()
                    errors = validate_tags(unit["tagged"], text, unit["tags"]) if text != "" else ["הטקסט ריק"]
                    if len(errors) > 0:
                        raise HttpError(400, "bad_tags", "; ".join(errors))
                    with project.lock:
                        unit["out"] = text
                        unit["status"] = "manual"
                        unit["warn"] = []
                        unit["err"] = None
                        project.touch(unit)
                    project.flush()
                    self.send_json({"ok": True, "unit": unit_view(unit, True)})
                    return
                if rest == "unit-resend":
                    self.send_json(Api.resend_unit(state, project, body))
                    return
                if rest == "glossary":
                    entries = []
                    for raw in body.get("entries", []):
                        source = (raw.get("source") or "").strip()
                        if source != "":
                            entries.append({"source": source, "target": (raw.get("target") or "").strip(),
                                            "locked": bool(raw.get("locked")), "auto": bool(raw.get("auto"))})
                    project.glossary = entries
                    project.dirty_meta = True
                    project.flush()
                    self.send_json({"ok": True, "count": len(entries)})
                    return
                if rest == "glossary/suggest":
                    suggestions = suggest_glossary_terms(project.units)
                    known = set(e["source"].lower() for e in project.glossary)
                    fresh = [s for s in suggestions if s["source"].lower() not in known]
                    self.send_json({"entries": fresh})
                    return
                if rest == "glossary/translate":
                    count = glossary_translate_terms(state, project, body.get("key"))
                    self.send_json({"ok": True, "count": count, "entries": project.glossary})
                    return
                if rest == "build":
                    job = state.jobs.get(pid)
                    if job is not None and job.alive():
                        raise HttpError(409, "busy", "העיבוד עדיין רץ")
                    previous = project.meta.get("status")
                    previous_error = project.meta.get("error")
                    project.set_status("building")
                    try:
                        report = build_outputs(project, project.log)
                    except BaseException:
                        project.set_status(previous, previous_error)
                        raise
                    if project.counts()["pending"] == 0:
                        project.set_status("completed")
                    else:
                        # הפקה חלקית (למשל אחרי עצירה): הסטטוס חוזר להיות מה שהיה, ואפשר להמשיך לעבד.
                        resting = previous if previous in ("paused", "stopped", "error", "ready") else "stopped"
                        project.set_status(resting, previous_error if resting == "error" else None)
                    self.send_json({"ok": True, "report": report})
                    return
            raise HttpError(404, "not_found", "נתיב לא קיים")

        def serve_preview_resource(self, project: Project, kind: str, key: str, rest: str, query: Dict[str, List[str]]) -> None:
            if kind == "asset":
                data, ctype = read_asset(project, rest, (query.get("final") or [""])[0] == "1")
            else:
                data, applied = build_live_document(project, key, urllib.parse.unquote(rest), (query.get("mode") or [""])[0])
                ctype = "application/xhtml+xml; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", LIVE_CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(data)

        def download(self, project: Project, name: str) -> None:
            if name == "log":
                path = os.path.join(project.dir, "log.jsonl")
                filename = "log-%s.jsonl" % project.id
            elif name == "report":
                path = os.path.join(project.output_dir, "report.json")
                filename = "report-%s.json" % project.id
            else:
                safe = os.path.basename(name)
                path = os.path.join(project.output_dir, safe)
                filename = safe
            if not os.path.isfile(path):
                raise HttpError(404, "not_found", "הקובץ לא קיים")
            size = os.path.getsize(path)
            self.send_response(200)
            self.send_header("Content-Type", "application/epub+zip" if path.endswith(".epub") else "application/octet-stream")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''%s" % urllib.parse.quote(filename))
            self.end_headers()
            with open(path, "rb") as handle:
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)

    return Handler


def shutdown_state(state: AppState, join_seconds: float = 8.0) -> None:
    """כיבוי מסודר: עוצר עבודות (בקשות רשת נקטעות מיד), ממתין ליציאתן ושומר כל פרויקט לדיסק."""
    jobs = list(state.jobs.values())
    for job in jobs:
        if job.alive():
            job.stop()
    deadline = time.time() + join_seconds
    for job in jobs:
        job.join(max(0.0, deadline - time.time()))
    for project in list(state.projects.values()):
        try:
            project.flush()
        except Exception as exc:
            sys.stderr.write("שמירת פרויקט %s נכשלה: %s\n" % (project.id, Redactor.clean(str(exc))))


def serve(host: str, port: int, open_browser: bool) -> None:
    load_dotenv(os.path.join(APP_DIR, ".env"))
    for cls in PROVIDER_CLASSES.values():
        if cls.env_key and os.environ.get(cls.env_key):
            Redactor.register(os.environ[cls.env_key])
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    state = AppState(port)
    state.load_projects()
    server = ThreadingHTTPServer((host, port), make_handler(state))
    url = "http://127.0.0.1:%d/" % port
    print("מעבד ספרים פועל בכתובת %s (האזנה ל-%s בלבד). לעצירה: Ctrl+C" % (url, host))
    if host not in ("127.0.0.1", "localhost", "::1"):
        print("אזהרה: השרת מאזין לכתובת שאינה מקומית. האסימון והבדיקות מגינים רק חלקית.")
    if open_browser:
        try:
            import webbrowser
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        except Exception:
            pass
    def request_shutdown(signum: int, frame: Any) -> None:
        raise KeyboardInterrupt()

    try:
        signal.signal(signal.SIGTERM, request_shutdown)
    except (ValueError, OSError, AttributeError):
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nנעצר. שומר מצב...")
    finally:
        shutdown_state(state)
        server.server_close()


# ======================================================================
# 24. ממשק משתמש (דף יחיד מוטמע)
# ======================================================================
UI_HTML = r"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>מעבד ספרים</title>
<style>
:root{--paper:#e9edf1;--panel:#fff;--ink:#1b2530;--mute:#5d6b79;--line:#c9d2da;--acc:#0f5c58;--acc-soft:#dcefed;--warn:#a8641a;--warn-soft:#fbefd9;--bad:#b3261e;--bad-soft:#fbe3e1;--ok:#2e7d4f;--ok-soft:#dff2e6;--r:6px}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 "Assistant","Heebo","Segoe UI",Arial,sans-serif}
header{background:var(--ink);color:#fff;padding:12px 24px 12px 70px;display:flex;align-items:baseline;gap:16px;flex-wrap:wrap}
header h1{margin:0;font-size:20px;font-weight:700;letter-spacing:.2px}
header span{color:#aab7c4;font-size:13px}
main{display:block;padding:16px 24px;max-width:1500px;margin:0 auto}
@media(max-width:980px){main{padding:12px}}
.col{display:flex;flex-direction:column;gap:14px;min-width:0}
section.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px}
section.card>h2{margin:0 0 10px;font-size:16px;border-bottom:1px solid var(--line);padding-bottom:6px}
label{display:block;font-size:13px;color:var(--mute);margin:8px 0 3px}
input[type=text],input[type=number],input[type=password],select,textarea{width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:var(--r);background:#fff;color:var(--ink);font:inherit}
textarea{min-height:64px;resize:vertical}
input:focus,select:focus,textarea:focus,button:focus-visible,summary:focus-visible{outline:2px solid var(--acc);outline-offset:1px}
.row{display:flex;gap:8px;align-items:flex-end}
.row>*{flex:1;min-width:0}
.row>.fixed{flex:0 0 auto}
button{font:inherit;padding:7px 13px;border-radius:var(--r);border:1px solid var(--acc);background:var(--acc);color:#fff;cursor:pointer}
button.ghost{background:#fff;color:var(--acc)}
button.danger{background:#fff;color:var(--bad);border-color:var(--bad)}
button:disabled{opacity:.45;cursor:not-allowed}
.drop{border:2px dashed var(--line);border-radius:var(--r);padding:20px;text-align:center;color:var(--mute);cursor:pointer;background:#f7f9fb}
.drop.over{border-color:var(--acc);background:var(--acc-soft)}
.kv{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;font-size:14px}
.kv b{color:var(--mute);font-weight:600}
.chip{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;border:1px solid var(--line);background:#f1f4f7}
.chip.ok{background:var(--ok-soft);border-color:#a9d6b8;color:var(--ok)}
.chip.warn{background:var(--warn-soft);border-color:#e6c690;color:var(--warn)}
.chip.bad{background:var(--bad-soft);border-color:#eba9a4;color:var(--bad)}
.note{padding:8px 10px;border-radius:var(--r);font-size:13px;margin:8px 0}
.note.warn{background:var(--warn-soft);border:1px solid #e6c690}
.note.bad{background:var(--bad-soft);border:1px solid #eba9a4}
.note.ok{background:var(--ok-soft);border:1px solid #a9d6b8}
.bar{height:14px;background:#e1e7ec;border-radius:7px;overflow:hidden;margin:8px 0}
.bar>i{display:block;height:100%;background:var(--acc);width:0;transition:width .4s}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px;margin-top:8px}
.stats .stat{display:block;text-align:start;background:#f4f7f9;border:1px solid var(--line);border-radius:var(--r);padding:6px 8px;font-size:13px;color:var(--ink)}
.stats .stat b{display:block;font-size:17px}
.stats .stat small{display:block;color:var(--mute);font-size:11px}
.stats button.stat{font:inherit;font-size:13px;cursor:pointer;transition:border-color .15s,box-shadow .15s,transform .1s}
.stats button.stat:hover:not(:disabled){border-color:var(--acc);box-shadow:0 0 0 2px var(--acc-soft)}
.stats button.stat:active:not(:disabled){transform:scale(.97)}
.stats button.stat:disabled{cursor:default;opacity:.65}
.stats button.stat.on{border-color:var(--acc);background:var(--acc-soft)}
.tabs{display:flex;gap:2px;border-bottom:1px solid var(--line);margin-bottom:10px;flex-wrap:wrap}
.tabs button{background:transparent;color:var(--mute);border:0;border-bottom:3px solid transparent;border-radius:0;padding:8px 14px}
.tabs button.on{color:var(--acc);border-bottom-color:var(--acc);font-weight:700}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--line);border-radius:var(--r);margin-bottom:8px;background:#fff}
.pair>div{padding:8px 10px;min-width:0;overflow-wrap:anywhere}
.pair>div:first-child{border-inline-end:1px solid var(--line);background:#f8fafb}
.pair .meta{grid-column:1/-1;border-top:1px solid var(--line);background:#fafbfc;padding:5px 10px;font-size:12px;color:var(--mute);display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.pair.failed{border-color:var(--bad)}.pair.flagged{border-color:var(--warn)}
.src{unicode-bidi:plaintext}
ins{background:var(--ok-soft);text-decoration:none}del{background:var(--bad-soft)}
h3.hd{margin:0 0 4px;font-size:15px}
.log{font:13px/1.5 Consolas,"Courier New",monospace;max-height:460px;overflow:auto;background:#10161d;color:#d6dde4;padding:10px;border-radius:var(--r);direction:ltr;text-align:left}
.log .e{color:#ff9a92}.log .w{color:#f1c27d}.log .c{color:#7e8c99}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid var(--line);padding:5px 8px;text-align:start}th{background:#f1f4f7}
details{margin-top:10px}summary{cursor:pointer;color:var(--acc);font-weight:600}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:0 10px}
.hidden{display:none!important}
dialog{border:1px solid var(--line);border-radius:var(--r);max-width:720px;width:92%;padding:16px}
dialog::backdrop{background:rgba(16,22,29,.45)}
.small{font-size:12px;color:var(--mute)}
.check{display:flex;gap:6px;align-items:center;margin:8px 0;color:var(--ink);font-size:14px}
.check input{width:auto}
.tag{font:12px monospace;background:#eef2f5;border:1px solid var(--line);border-radius:4px;padding:0 4px}
/* ----- תפריט צד צף ----- */
#side{position:fixed;top:0;bottom:0;left:0;width:min(620px,96vw);z-index:80;overflow-y:auto;overscroll-behavior:contain;padding:14px;background:var(--paper);box-shadow:8px 0 32px rgba(16,22,29,.3);outline:none;transform:translateX(-104%);visibility:hidden;transition:transform .28s ease,visibility 0s linear .28s}
#side>*{flex:0 0 auto}
body.side-open #side{transform:none;visibility:visible;transition:transform .28s ease,visibility 0s}
#scrim{position:fixed;inset:0;z-index:70;background:rgba(16,22,29,.45);opacity:0;pointer-events:none;transition:opacity .28s}
body.side-open #scrim{opacity:1;pointer-events:auto}
.side-head{padding-left:52px;min-height:42px;display:flex;align-items:center}
.side-head h2{margin:0;font-size:18px}
.menu{position:fixed;top:10px;left:10px;z-index:90;width:44px;height:44px;padding:0;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:5px;box-shadow:0 1px 6px rgba(16,22,29,.3)}
.menu i{display:block;width:20px;height:2px;background:currentColor;border-radius:1px;transition:transform .25s,opacity .2s}
body.side-open .menu i:nth-child(1){transform:translateY(7px) rotate(45deg)}
body.side-open .menu i:nth-child(2){opacity:0}
body.side-open .menu i:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
/* ----- כותרת הרצה דביקה ----- */
#runCard{position:sticky;top:0;z-index:50;padding-left:62px;box-shadow:0 3px 10px rgba(16,22,29,.12)}
.runhead{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.runhead h2{margin:0;font-size:16px;border:0;padding:0}
.runhead #statusLine{flex:1;min-width:0}
#runCard.shrunk{padding-top:7px;padding-bottom:7px}
#runCard.shrunk .runhead{margin-bottom:2px}
#runCard.shrunk #runDetails{display:none}
#runCard.shrunk .bar{height:8px;margin:5px 0 0}
#runCard.shrunk .row{margin-top:2px!important}
@media(prefers-reduced-motion:reduce){#side,#scrim,.menu i{transition:none}}
/* ----- התראות, ניווט בין רכיבים, אנימציות יחידה ----- */
#toasts{position:fixed;right:16px;bottom:16px;z-index:100;display:flex;flex-direction:column-reverse;gap:8px;width:min(380px,calc(100vw - 32px));pointer-events:none}
.toast{pointer-events:auto;display:flex;align-items:stretch;background:#fff;border:1px solid var(--line);border-inline-start:5px solid var(--acc);border-radius:var(--r);box-shadow:0 6px 22px rgba(16,22,29,.25);animation:toastIn .22s ease-out}
.toast.error{border-inline-start-color:var(--bad)}.toast.warn{border-inline-start-color:var(--warn)}.toast.ok{border-inline-start-color:var(--ok)}
.toast .tbody{flex:1;min-width:0;text-align:start;background:transparent;color:var(--ink);border:0;border-radius:0;padding:9px 11px;font:inherit;font-size:13px;cursor:pointer}
.toast .tbody b{display:block;margin-bottom:2px}
.toast .tbody span{display:block;overflow-wrap:anywhere;color:var(--mute);max-height:4.6em;overflow:hidden}
.toast .tbody em{display:block;font-style:normal;font-size:11px;color:var(--acc);margin-top:3px}
.toast .tclose{background:transparent;color:var(--mute);border:0;border-inline-start:1px solid var(--line);border-radius:0;padding:0 12px;cursor:pointer}
.toast .tclose:hover{color:var(--bad)}
.toast.out{opacity:0;transform:translateX(24px);transition:opacity .2s,transform .2s}
@keyframes toastIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.navpop{position:fixed;left:16px;bottom:16px;z-index:60;display:flex;align-items:center;gap:6px;background:#fff;border:1px solid var(--line);border-radius:24px;padding:5px 8px 5px 12px;box-shadow:0 6px 22px rgba(16,22,29,.25);animation:toastIn .2s ease-out}
.navpop[hidden]{display:none}
.navpop .navtitle{font-weight:700;font-size:13px}
.navpop[data-group=failed] .navtitle{color:var(--bad)}.navpop[data-group=flagged] .navtitle{color:var(--warn)}.navpop[data-group=done] .navtitle{color:var(--ok)}
.navpop .navpos{font-variant-numeric:tabular-nums;color:var(--mute);min-width:3.4em;text-align:center;font-size:13px}
.navpop button{padding:2px 11px;border-radius:14px;line-height:1.5}
.pair.flash{animation:flash 1.5s ease-out}
@keyframes flash{0%{box-shadow:0 0 0 4px var(--acc);background:var(--acc-soft)}100%{box-shadow:0 0 0 0 transparent;background:#fff}}
.pair.resending{border-color:var(--acc);animation:pulse 1.1s ease-in-out infinite}
@keyframes pulse{50%{box-shadow:0 0 0 4px var(--acc-soft)}}
@media(max-width:700px){#toasts{bottom:70px}}
/* ----- תצוגה חיה ----- */
.livebar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}
.livebar select{width:auto;max-width:100%}
.livebar #live_doc{flex:1;min-width:200px}
.livebar .check{margin:0}
#liveFrame{display:block;width:100%;height:72vh;min-height:360px;border:1px solid var(--line);border-radius:var(--r);background:#fff}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
/* ----- הגדרות מומלצות לפי מודל ----- */
.profile{margin-top:8px;padding:9px 11px;border:1px solid var(--acc);border-radius:var(--r);background:var(--acc-soft);font-size:13px}
.profile .ph{display:flex;gap:8px;align-items:center;margin-bottom:4px;flex-wrap:wrap}
.profile ul{margin:4px 0;padding-inline-start:18px}
.profile li{margin:2px 0}
.profile details{margin:4px 0}
.profile .psrc{color:var(--mute);font-size:11px;margin:4px 0}
.profile .pa{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}
.profile .pa button{padding:3px 12px}
.profile .check{margin:6px 0 0;font-size:12px}
@media(prefers-reduced-motion:reduce){.toast,.navpop,.pair.flash,.pair.resending{animation:none}.toast.out{transition:none}}
</style>
</head>
<body>
<header><h1>מעבד ספרים</h1><span>EPUB, PDF ו-MOBI &#8594; EPUB תקין, בהחלפה נקודתית בתוך הקובץ המקורי</span><span id="conn"></span></header>
<button type="button" class="menu" id="menuBtn" aria-controls="side" aria-expanded="false" aria-label="פתח או סגור את תפריט הפרויקטים וההגדרות"><i></i><i></i><i></i></button>
<div id="scrim"></div>
<aside class="col" id="side" tabindex="-1" aria-label="פרויקטים והגדרות">
  <div class="side-head"><h2>פרויקטים והגדרות</h2></div>
  <section class="card">
    <h2>ספר ופרויקטים</h2>
    <div class="drop" id="drop" tabindex="0">גרור לכאן קובץ EPUB, PDF או MOBI, או לחץ לבחירה<input id="file" type="file" accept=".epub,.pdf,.mobi,.azw3" hidden></div>
    <label for="projects">פרויקטים קיימים</label>
    <div class="row"><select id="projects"></select><button class="ghost fixed" id="mgrOpen" title="ניהול ומחיקת פרויקטים">ניהול ומחיקה</button></div>
  </section>
  <section class="card" id="fileCard" hidden>
    <h2>פרטי הקובץ</h2>
    <div class="kv" id="fileInfo"></div>
    <div id="pdfBox"></div>
  </section>
  <section class="card">
    <h2>הגדרות עיבוד</h2>
    <label for="s_goal">מטרה</label><select id="s_goal"></select>
    <div id="langBox">
      <div class="grid2">
        <div><label for="s_src">שפת מקור</label><input id="s_src" type="text" list="langList" placeholder="auto = זיהוי אוטומטי"></div>
        <div><label for="s_tgt">שפת יעד</label><input id="s_tgt" type="text" list="langList" placeholder="בחר או כתוב חופשי"></div>
      </div>
      <datalist id="langList"></datalist>
      <label for="s_mode">מצב פלט</label>
      <select id="s_mode"><option value="replace">תרגום בלבד (מחליף את המקור)</option><option value="bilingual">דו־לשוני: מקור ותרגום בכל פסקה</option><option value="both">שני קבצים: תרגום בלבד + דו־לשוני</option></select>
    </div>
    <div id="aiBox">
      <label for="s_extra">הנחיות נוספות למודל</label><textarea id="s_extra" placeholder="למשל: סגנון, רמת לשון, כינויים, מונחים"></textarea>
      <label for="s_provider">ספק</label><select id="s_provider"></select>
      <label for="s_model">מודל</label>
      <div class="row"><input id="s_model" type="text" list="modelList" autocomplete="off"><button class="ghost fixed" id="loadModels">טען רשימה</button></div>
      <div id="profileBox" class="profile hidden" role="region" aria-live="polite" aria-label="הגדרות מומלצות למודל"></div>
      <datalist id="modelList"></datalist>
      <div id="baseBox"><label for="s_base">נקודת קצה (אופציונלי)</label><input id="s_base" type="text" placeholder="" dir="ltr"></div>
      <div id="keyBox">
        <label for="s_key">מפתח API (נשמר בזיכרון הסשן בלבד)</label><input id="s_key" type="password" autocomplete="off" dir="ltr">
        <div class="check"><input id="s_remember" type="checkbox"><label for="s_remember" style="margin:0;color:inherit;font-size:14px">שמור את המפתח מוצפן במחשב זה</label></div>
        <div class="small" id="keyNote"></div>
      </div>
      <div class="row" style="margin-top:8px"><button class="ghost" id="testConn">בדיקת חיבור</button><span id="connState" class="small"></span></div>
    </div>
    <div id="layoutBox" class="hidden">
      <div class="note ok">המטרה הזו משנה רק CSS ותצוגה, ללא שליחה למודל.</div>
      <div class="grid2">
        <div><label for="l_family">גופן גוף</label><input id="l_family" type="text" placeholder="Georgia, serif" dir="ltr"></div>
        <div><label for="l_hfamily">גופן כותרות</label><input id="l_hfamily" type="text" dir="ltr"></div>
        <div><label for="l_size">גודל גופן (%)</label><input id="l_size" type="number" placeholder="110"></div>
        <div><label for="l_line">גובה שורה</label><input id="l_line" type="number" step="0.1" placeholder="1.6"></div>
        <div><label for="l_margin">שוליים צדדיים (%)</label><input id="l_margin" type="number"></div>
        <div><label for="l_maxw">רוחב מרבי (em)</label><input id="l_maxw" type="number"></div>
        <div><label for="l_align">יישור פסקאות</label><select id="l_align"><option value="keep">כמו במקור</option><option value="justify">מוצדק</option><option value="start">לתחילת השורה</option></select></div>
        <div><label for="l_para">סגנון פסקה</label><select id="l_para"><option value="keep">כמו במקור</option><option value="indent">הזחה בשורה ראשונה</option><option value="spacing">רווח בין פסקאות</option></select></div>
        <div><label for="l_theme">ערכת צבעים</label><select id="l_theme"><option value="keep">כמו במקור</option><option value="white">לבן</option><option value="sepia">חום־בהיר</option><option value="dark">כהה</option></select></div>
        <div><label for="l_halign">יישור כותרות</label><select id="l_halign"><option value="keep">כמו במקור</option><option value="center">מרכז</option><option value="start">תחילת שורה</option></select></div>
      </div>
      <div class="check"><input id="l_hyph" type="checkbox"><label for="l_hyph" style="margin:0;color:inherit;font-size:14px">הטעמת מקף אוטומטית</label></div>
      <div class="check"><input id="l_strip" type="checkbox"><label for="l_strip" style="margin:0;color:inherit;font-size:14px">הסר סגנונות inline מהמסמכים</label></div>
      <div class="check"><input id="l_drop" type="checkbox"><label for="l_drop" style="margin:0;color:inherit;font-size:14px">הסר CSS מקורי מקבצי המסמך</label></div>
      <label for="l_css">CSS מותאם</label><textarea id="l_css" dir="ltr"></textarea>
    </div>
    <details>
      <summary>הגדרות מתקדמות</summary>
      <div class="grid2">
        <div><label for="s_chunk">גודל מקטע (תווים)</label><input id="s_chunk" type="number"></div>
        <div><label for="s_overlap">חפיפה להקשר (פסקאות)</label><input id="s_overlap" type="number"></div>
        <div><label for="s_temp">טמפרטורה</label><input id="s_temp" type="number" step="0.1" placeholder="ריק = ברירת מחדל של הספק"></div>
        <div><label for="s_attempts">ניסיונות חוזרים לאימות</label><input id="s_attempts" type="number"></div>
        <div><label for="s_apiretries">ניסיונות חוזרים לשגיאות ספק</label><input id="s_apiretries" type="number"></div>
        <div><label for="s_conc">בקשות מקבילות</label><select id="s_conc"><option>1</option><option>2</option><option>4</option><option>8</option></select></div>
        <div><label for="s_timeout">פסק זמן (שניות)</label><input id="s_timeout" type="number"></div>
        <div><label for="s_ctx">הקשר המודל (tokens, 0 = לא ידוע)</label><input id="s_ctx" type="number"></div>
        <div><label for="s_maxout">מקסימום פלט (tokens)</label><input id="s_maxout" type="number"></div>
        <div><label for="s_rpm">בקשות לדקה (0 = ללא הגבלה)</label><input id="s_rpm" type="number"></div>
        <div><label for="s_format">פורמט פרוטוקול</label><select id="s_format"><option value="auto">אוטומטי</option><option value="json">JSON</option><option value="list">רשימה</option></select></div>
        <div><label for="s_onfail">כשל באימות עיצוב</label><select id="s_onfail"><option value="flag">סמן לבדיקה ידנית ושמור מקור</option><option value="accept_plain">קבל טקסט ללא עיצוב</option></select></div>
        <div><label for="s_pin">מחיר ל-1M tokens קלט</label><input id="s_pin" type="number" step="0.01"></div>
        <div><label for="s_pout">מחיר ל-1M tokens פלט</label><input id="s_pout" type="number" step="0.01"></div>
      </div>
      <div class="check"><input id="s_cons" type="checkbox"><label for="s_cons" style="margin:0;color:inherit;font-size:14px">עקביות מרבית (עיבוד לפי הסדר, בקשה אחת בכל פעם)</label></div>
      <div class="check"><input id="s_bdi" type="checkbox"><label for="s_bdi" style="margin:0;color:inherit;font-size:14px">בידוד מילים לועזיות בטקסט RTL (bdi)</label></div>
    </details>
  </section>
</aside>
<main>
<div class="col" id="work">
  <section class="card" id="runCard">
    <div class="runhead"><h2>הרצה</h2><div id="statusLine"></div><button type="button" class="ghost fixed" id="runToggle" aria-expanded="true" aria-controls="runDetails" title="הרחב או צמצם את פרטי ההרצה">&#9650;</button></div>
    <div class="row" style="margin-top:8px">
      <button id="btnStart" class="fixed">התחלה</button><button id="btnPause" class="ghost fixed">השהיה</button>
      <button id="btnResume" class="ghost fixed">המשך</button><button id="btnStop" class="danger fixed">עצירה</button>
      <button id="btnRetry" class="ghost fixed">נסה שוב את הכושלים</button><span></span>
    </div>
    <div class="bar"><i id="barFill"></i></div>
    <div id="runDetails"><div id="errBox"></div><div class="stats" id="stats"></div></div>
  </section>
  <section class="card">
    <div class="tabs" role="tablist">
      <button data-tab="compare" class="on">השוואה</button><button data-tab="glossary">מילון מונחים</button>
      <button data-tab="logs">יומן</button><button data-tab="summary">סיכום ואימות</button><button data-tab="live">תצוגה חיה</button>
    </div>
    <div id="tab_compare">
      <div class="row">
        <div><label for="c_chapter">פרק</label><select id="c_chapter"></select></div>
        <button class="ghost fixed" id="c_prev">הקודם</button><button class="ghost fixed" id="c_next">הבא</button>
        <div class="check fixed" style="margin-bottom:6px"><input id="c_issues" type="checkbox"><label for="c_issues" style="margin:0;color:inherit">אזהרות וכשלים בלבד</label></div>
      </div>
      <div class="small" id="c_note" style="margin:6px 0"></div>
      <div id="c_list"></div>
      <div class="row"><button class="ghost" id="c_more">טען עוד</button></div>
    </div>
    <div id="tab_glossary" class="hidden">
      <div class="small">מונחים עם תרגום נשלחים למודל רק כשהם מופיעים במקטע. ערכים נעולים נשמרים כפי שהם.</div>
      <div class="row" style="margin:8px 0"><button class="ghost" id="g_suggest">הצע ערכים מהספר</button><button class="ghost" id="g_translate">הצע תרגום באמצעות המודל</button><button id="g_save">שמור מילון</button><button class="ghost" id="g_add">הוסף שורה</button></div>
      <table><thead><tr><th>מונח במקור</th><th>תרגום</th><th>נעול</th><th></th></tr></thead><tbody id="g_body"></tbody></table>
    </div>
    <div id="tab_logs" class="hidden">
      <div class="row" style="margin-bottom:8px"><button class="ghost" id="l_clear">נקה</button><button class="ghost" id="l_copy">העתק</button><a id="l_dl" href="#"><button class="ghost" type="button">הורד</button></a>
        <div class="check fixed"><input id="l_err" type="checkbox"><label for="l_err" style="margin:0;color:inherit">שגיאות בלבד</label></div></div>
      <div class="log" id="logBox"></div>
    </div>
    <div id="tab_summary" class="hidden"><div id="summaryBox" class="small">הסיכום יופיע בסיום העיבוד.</div></div>
    <div id="tab_live" class="hidden">
      <div class="livebar">
        <label for="live_doc" class="sr">מסמך להצגה</label><select id="live_doc"></select>
        <label for="live_mode" class="sr">מצב תצוגה</label><select id="live_mode" hidden></select>
        <button type="button" class="ghost fixed" id="live_refresh" title="טען מחדש את המסמך עם הטקסטים העדכניים">רענן</button>
        <div class="check"><input id="live_auto" type="checkbox" checked><label for="live_auto" style="margin:0;color:inherit;font-size:13px">רענון אוטומטי אחרי עריכה ושינויים</label></div>
        <span class="small" id="live_status"></span>
      </div>
      <iframe id="liveFrame" title="תצוגה חיה של הספר" sandbox="allow-same-origin"></iframe>
    </div>
  </section>
</div>
</main>
<dialog id="dlg"><div id="dlgBody"></div><div class="row" style="margin-top:12px"><span></span><button id="dlgClose" class="ghost fixed">סגור</button></div></dialog>
<dialog id="mgrDlg" style="max-width:900px">
  <h3 class="hd">ניהול ומחיקת פרויקטים</h3>
  <div class="note ok">אף פרויקט לא נמחק אוטומטית. מחיקה אפשרית רק מכאן: מסמנים פרויקטים, מקלידים את מילת האישור ולוחצים על מחיקה. אי אפשר לשחזר.</div>
  <div style="max-height:46vh;overflow:auto"><table><thead><tr><th></th><th>פרויקט</th><th>סטטוס</th><th>התקדמות</th><th>גודל בדיסק</th><th>נוצר</th><th></th></tr></thead><tbody id="mgrBody"></tbody></table></div>
  <div class="small" id="mgrEmpty" style="margin:6px 0"></div>
  <div class="row" style="margin-top:10px"><div><label for="mgrConfirm">כדי להפעיל את המחיקה הקלד: מחק</label><input id="mgrConfirm" type="text" autocomplete="off"></div><button class="danger fixed" id="mgrDelete" disabled>מחק את המסומנים</button></div>
  <div class="small" id="mgrMsg" style="margin-top:6px"></div>
  <div class="row" style="margin-top:12px"><span></span><button id="mgrClose" class="ghost fixed">סגור</button></div>
</dialog>
<div id="toasts" role="region" aria-live="polite" aria-label="התראות"></div>
<div class="navpop" id="navPop" role="group" aria-label="ניווט בין רכיבים" hidden>
  <span class="navtitle" id="navTitle"></span><span class="navpos" id="navPos"></span>
  <button type="button" class="ghost" id="navUp" aria-label="הרכיב הקודם" title="הקודם">&#9650;</button>
  <button type="button" class="ghost" id="navDown" aria-label="הרכיב הבא" title="הבא">&#9660;</button>
  <button type="button" class="ghost" id="navClose" aria-label="סגור ניווט" title="סגור">&#10005;</button>
</div>
<script>
const TOKEN="__TOKEN__";
const $=(s,r=document)=>r.querySelector(s);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const S={info:null,pid:null,sum:null,logs:[],logSince:0,chapter:-1,offset:0,rows:[],total:0,glossary:[],timer:null,tick:0,saveT:null};
async function api(path,opt){opt=opt||{};const r=await fetch(path,{method:opt.method||"GET",headers:Object.assign({"X-Token":TOKEN},opt.body?{"Content-Type":"application/json"}:{}),body:opt.body?JSON.stringify(opt.body):undefined});let j={};try{j=await r.json()}catch(e){}if(!r.ok){const e=new Error(j.message||r.statusText);e.data=j;e.status=r.status;throw e}return j}
function fmtTime(s){if(s==null)return"-";s=Math.round(s);const m=Math.floor(s/60);return m+":"+String(s%60).padStart(2,"0")}
function fmtSize(b){return b>1048576?(b/1048576).toFixed(1)+" MB":Math.round(b/1024)+" KB"}
const STATUS={created:"נוצר",analyzing:"מנתח קובץ",awaiting_confirmation:"ממתין לאישור מבנה",ready:"מוכן",running:"רץ",paused:"מושהה",stopped:"נעצר",building:"בונה פלט ומאמת",completed:"הושלם",error:"שגיאה"};

/* ---------- כותרת הרצה דביקה שמצטמצמת בגלילה ---------- */
const RUN={manual:false,ticking:false};
function setRunCollapsed(on){
  const card=$("#runCard");
  if(on===card.classList.contains("shrunk"))return;
  const before=card.offsetHeight;
  card.classList.toggle("shrunk",on);
  // הכרטיס דביק, אז כשהוא מצטמצם נשמר המקום שלו בזרימה. בלי זה התוכן שמתחתיו היה קופץ למעלה.
  card.style.marginBottom=(on&&window.scrollY>80)?(before-card.offsetHeight)+"px":"";
  const btn=$("#runToggle");
  btn.setAttribute("aria-expanded",String(!on));
  btn.innerHTML=on?"&#9660;":"&#9650;";
}
function onRunScroll(){
  if(RUN.ticking)return;
  RUN.ticking=true;
  requestAnimationFrame(()=>{
    RUN.ticking=false;
    const y=window.scrollY;
    if(y<40){RUN.manual=false;setRunCollapsed(false);return}
    if(RUN.manual)return;
    const shrunk=$("#runCard").classList.contains("shrunk");
    // שני ספים שונים (160 ו-80) מונעים הבהוב סביב נקודת המעבר
    if(!shrunk&&y>160)setRunCollapsed(true);
    else if(shrunk&&y<80)setRunCollapsed(false);
  });
}
window.addEventListener("scroll",onRunScroll,{passive:true});
$("#runToggle").onclick=()=>{RUN.manual=true;setRunCollapsed(!$("#runCard").classList.contains("shrunk"))};

/* ---------- תפריט צד (המבורגר) ---------- */
function setSidebar(open,persist){
  document.body.classList.toggle("side-open",open);
  $("#menuBtn").setAttribute("aria-expanded",String(open));
  if(open&&persist!==false)$("#side").focus({preventScroll:true});
  if(persist!==false){try{localStorage.setItem("bookai.side",open?"1":"0")}catch(e){}}
}
$("#menuBtn").onclick=()=>setSidebar(!document.body.classList.contains("side-open"));
$("#scrim").onclick=()=>setSidebar(false);
document.addEventListener("keydown",e=>{
  if(e.key==="Escape"&&document.body.classList.contains("side-open")&&!document.querySelector("dialog[open]"))setSidebar(false);
});
(function(){let saved=null;try{saved=localStorage.getItem("bookai.side")}catch(e){}setSidebar(saved===null?true:saved==="1",false)})();


/* ---------- אתחול ---------- */
async function init(){
  S.info=await api("/api/info");
  const g=$("#s_goal");S.info.goals.forEach(x=>g.add(new Option(x.label,x.id)));
  const p=$("#s_provider");S.info.providers.forEach(x=>p.add(new Option(x.label,x.id)));
  const ll=$("#langList");S.info.languages.forEach(x=>{ll.appendChild(new Option(x.he+" ("+x.en+")",x.en))});
  const f=S.info.features;
  $("#conn").textContent="Calibre: "+(f.calibre?"זמין":"לא זמין")+" | PDF: "+(f.pdf?"זמין":"חסר PyMuPDF")+" | EPUBCheck: "+(f.epubcheck?"זמין":"לא זמין");
  if(!f.crypto){$("#s_remember").disabled=true;$("#keyNote").textContent="שמירת מפתח מוצפנת דורשת: pip install cryptography"}
  fillSettings(S.info.default_settings);
  await refreshProjects();
}
async function refreshProjects(select){
  const list=await api("/api/projects");const el=$("#projects");el.innerHTML="";
  el.add(new Option(list.length?"בחר פרויקט...":"אין פרויקטים",""));
  list.forEach(x=>el.add(new Option(x.filename+" ["+x.format+"] - "+(STATUS[x.status]||x.status),x.id)));
  if(select){el.value=select;await openProject(select)}else if(S.pid){el.value=S.pid}
}
async function openProject(pid){
  S.pid=pid||null;S.logs=[];S.logSince=0;S.chapter=-1;S.offset=0;$("#logBox").innerHTML="";$("#c_list").innerHTML="";
  S.sum=null;S.resendId=null;S.shown=0;navClose();clearToasts();liveReset();PROFILE.last="";hideProfile();
  clearInterval(S.timer);
  if(!pid){$("#fileCard").hidden=true;return}
  await poll(true);S.timer=setInterval(poll,1000);
}

/* ---------- הגדרות ---------- */
function fillSettings(s){
  $("#s_goal").value=s.goal;$("#s_src").value=s.src_lang;$("#s_tgt").value=s.tgt_lang;$("#s_mode").value=s.mode;$("#s_extra").value=s.extra||"";
  $("#s_provider").value=s.provider;$("#s_model").value=s.model||"";$("#s_base").value=s.base_url||"";
  $("#s_chunk").value=s.chunk_chars;$("#s_overlap").value=s.overlap;$("#s_temp").value=s.temperature;$("#s_attempts").value=s.attempts;$("#s_apiretries").value=s.api_retries;
  $("#s_conc").value=String(s.concurrency);$("#s_timeout").value=s.timeout;$("#s_ctx").value=s.context_tokens;$("#s_maxout").value=s.max_output_tokens;$("#s_rpm").value=s.rpm;
  $("#s_format").value=s.format;$("#s_onfail").value=s.on_format_failure;$("#s_pin").value=s.price_in;$("#s_pout").value=s.price_out;$("#s_cons").checked=!!s.consistency;$("#s_bdi").checked=!!s.rtl_isolate;
  const l=s.layout||{};$("#l_family").value=l.font_family||"";$("#l_hfamily").value=l.heading_font||"";$("#l_size").value=l.font_size||"";$("#l_line").value=l.line_height||"";
  $("#l_margin").value=l.margin||"";$("#l_maxw").value=l.max_width||"";$("#l_align").value=l.text_align||"keep";$("#l_para").value=l.para_style||"keep";$("#l_theme").value=l.theme||"keep";
  $("#l_halign").value=l.heading_align||"keep";$("#l_hyph").checked=!!l.hyphenate;$("#l_strip").checked=!!l.strip_inline_styles;$("#l_drop").checked=!!l.drop_original_css;$("#l_css").value=l.custom_css||"";
  applyVisibility();
}
function tempValue(){const v=parseFloat($("#s_temp").value);return isNaN(v)?null:v}  // ריק = לא שולחים טמפרטורה
function collectSettings(){
  const n=(id,d)=>{const v=parseFloat($(id).value);return isNaN(v)?d:v};
  return {goal:$("#s_goal").value,src_lang:$("#s_src").value.trim()||"auto",tgt_lang:$("#s_tgt").value.trim()||"he",mode:$("#s_mode").value,extra:$("#s_extra").value,
    provider:$("#s_provider").value,model:$("#s_model").value.trim(),base_url:$("#s_base").value.trim(),temperature:tempValue(),chunk_chars:n("#s_chunk",6000),overlap:n("#s_overlap",2),
    attempts:n("#s_attempts",3),api_retries:n("#s_apiretries",5),concurrency:parseInt($("#s_conc").value),timeout:n("#s_timeout",120),context_tokens:n("#s_ctx",0),max_output_tokens:n("#s_maxout",8192),
    rpm:n("#s_rpm",0),format:$("#s_format").value,on_format_failure:$("#s_onfail").value,price_in:n("#s_pin",0),price_out:n("#s_pout",0),consistency:$("#s_cons").checked,rtl_isolate:$("#s_bdi").checked,
    layout:{font_family:$("#l_family").value,heading_font:$("#l_hfamily").value,font_size:$("#l_size").value,line_height:$("#l_line").value,margin:$("#l_margin").value,max_width:$("#l_maxw").value,
      text_align:$("#l_align").value,para_style:$("#l_para").value,theme:$("#l_theme").value,heading_align:$("#l_halign").value,hyphenate:$("#l_hyph").checked,strip_inline_styles:$("#l_strip").checked,
      drop_original_css:$("#l_drop").checked,custom_css:$("#l_css").value}};
}
function applyVisibility(){
  const goal=S.info.goals.find(x=>x.id===$("#s_goal").value)||{};
  $("#langBox").classList.toggle("hidden",!goal.translate);
  $("#aiBox").classList.toggle("hidden",!goal.ai);
  $("#layoutBox").classList.toggle("hidden",goal.ai);
  const pv=S.info.providers.find(x=>x.id===$("#s_provider").value)||{};
  $("#keyBox").classList.toggle("hidden",!pv.needs_key&&pv.id!=="custom");
  $("#s_base").placeholder=pv.default_base||"";
  const note=[];if(pv.env_key)note.push("נמצא מפתח במשתנה סביבה (.env) - אפשר להשאיר ריק");if(pv.remembered)note.push("יש מפתח שמור מוצפן");
  if(note.length)$("#keyNote").textContent=note.join(". ");
}
function scheduleSave(){clearTimeout(S.saveT);S.saveT=setTimeout(saveSettings,500)}
async function saveSettings(){if(!S.pid)return;try{await api("/api/p/"+S.pid+"/settings",{method:"POST",body:{settings:collectSettings()}})}catch(e){}}
document.querySelectorAll("#side input,#side select,#side textarea").forEach(el=>{el.addEventListener("change",()=>{applyVisibility();scheduleSave()});el.addEventListener("input",scheduleSave)});
$("#s_provider").addEventListener("change",()=>{$("#s_model").value="";$("#modelList").innerHTML="";$("#connState").textContent=""});

/* ---------- העלאה ופרויקטים ---------- */
const drop=$("#drop");
drop.onclick=()=>$("#file").click();
drop.ondragover=e=>{e.preventDefault();drop.classList.add("over")};drop.ondragleave=()=>drop.classList.remove("over");
drop.ondrop=e=>{e.preventDefault();drop.classList.remove("over");if(e.dataTransfer.files[0])upload(e.dataTransfer.files[0])};
$("#file").onchange=e=>{if(e.target.files[0])upload(e.target.files[0])};
async function upload(file){
  drop.textContent="מעלה "+file.name+"...";
  try{
    const r=await fetch("/api/upload",{method:"POST",headers:{"X-Token":TOKEN,"X-Filename":encodeURIComponent(file.name)},body:file});
    const j=await r.json();if(!r.ok)throw new Error(j.message||"שגיאה");
    drop.innerHTML="גרור לכאן קובץ EPUB, PDF או MOBI, או לחץ לבחירה";
    await refreshProjects(j.id);await saveSettings();
  }catch(e){drop.textContent="ההעלאה נכשלה: "+e.message}
}
$("#projects").onchange=e=>openProject(e.target.value);

/* ---------- ניהול ומחיקת פרויקטים (המקום היחיד שבו אפשר למחוק) ---------- */
const MGR={rows:[]};
const MGR_WORD="מחק";
function mgrSelected(){return Array.from(document.querySelectorAll("[data-sel]:checked")).map(x=>x.dataset.sel)}
function mgrUpdateButton(){$("#mgrDelete").disabled=mgrSelected().length===0||$("#mgrConfirm").value.trim()!==MGR_WORD}
function mgrRender(){
  const body=$("#mgrBody");
  if(!MGR.rows.length){body.innerHTML="";$("#mgrEmpty").textContent="אין פרויקטים שמורים.";mgrUpdateButton();return}
  $("#mgrEmpty").textContent="";
  body.innerHTML=MGR.rows.map(r=>{
    const prog=r.total?Math.round(100*r.done/r.total)+"% ("+r.done+"/"+r.total+")":"-";
    const note=r.busy?'<div class="small">פעיל כעת; יש לעצור לפני מחיקה</div>':(r.has_output&&r.outputs_stale?'<div class="small">נערכו רכיבים אחרי ההפקה האחרונה</div>':"");
    return '<tr><td><input type="checkbox" data-sel="'+esc(r.id)+'"'+(r.busy?" disabled":"")+'></td><td dir="auto">'+esc(r.filename)+' <span class="tag">'+esc(r.format)+'</span>'+note+'</td><td><span class="chip">'+esc(STATUS[r.status]||r.status)+'</span></td><td>'+esc(prog)+'</td><td>'+esc(fmtSize(r.size_bytes||0))+'</td><td>'+esc((r.created||"").replace("T"," "))+'</td><td><button class="ghost" data-open="'+esc(r.id)+'" style="padding:1px 8px">פתח</button></td></tr>'}).join("");
  document.querySelectorAll("[data-sel]").forEach(el=>el.onchange=mgrUpdateButton);
  document.querySelectorAll("[data-open]").forEach(b=>b.onclick=async()=>{$("#mgrDlg").close();await refreshProjects(b.dataset.open)});
  mgrUpdateButton();
}
async function mgrLoad(){MGR.rows=await api("/api/projects?detail=1");mgrRender()}
$("#mgrOpen").onclick=async()=>{try{$("#mgrMsg").textContent="";$("#mgrConfirm").value="";await mgrLoad();$("#mgrDlg").showModal()}catch(e){alert(e.message)}};
$("#mgrConfirm").oninput=mgrUpdateButton;
$("#mgrClose").onclick=()=>$("#mgrDlg").close();
$("#mgrDelete").onclick=async()=>{
  const ids=mgrSelected();if(!ids.length)return;
  if(!confirm("למחוק לצמיתות "+ids.length+" פרויקטים יחד עם קובץ המקור, התרגום והפלט שלהם? לא ניתן לשחזר."))return;
  try{
    const r=await api("/api/projects/delete",{method:"POST",body:{ids:ids,confirm:"DELETE"}});
    if(r.deleted.includes(S.pid)){clearInterval(S.timer);await openProject(null)}
    $("#mgrConfirm").value="";
    $("#mgrMsg").textContent="נמחקו "+r.deleted.length+(r.failed.length?" | לא נמחקו: "+r.failed.map(f=>f.message).join("; "):"");
    await refreshProjects();await mgrLoad();
  }catch(e){$("#mgrMsg").textContent=e.message}
};

/* ---------- סקירת מצב (polling) ---------- */
async function poll(first){
  if(!S.pid)return;
  let d;try{d=await api("/api/p/"+S.pid+"/status?since="+S.logSince)}catch(e){if(e.status===404){S.pid=null;clearInterval(S.timer);refreshProjects()}return}
  const prev=S.sum;S.sum=d;
  d.logs.forEach(l=>{S.logs.push(l);S.logSince=Math.max(S.logSince,l.id)});
  if(S.logs.length>4000)S.logs.splice(0,S.logs.length-4000);
  if(first)fillSettings(d.settings);
  renderFile(d);renderRun(d);appendLogs(d.logs);
  notifyLogs(d.logs,!!first||!prev);
  if(prev&&prev.meta.status!==d.meta.status&&d.meta.status==="error"&&d.meta.error)toast({kind:"error",title:"העיבוד נעצר בשגיאה",text:d.meta.error.message,target:{tab:"logs"}});
  navSync(d);
  liveSync(d);
  if(first||!prev||prev.meta.status!==d.meta.status){await loadChapters(d);renderSummary(d);refreshProjectsQuiet()}
  S.tick++;
  // אחרי קפיצה לעומק הרשימה (יותר מ-300 שורות) לא מרעננים אוטומטית, כדי שהגלילה לא תקפוץ; הרענון קורה בסיום הריצה
  if(d.running&&S.tick%2===0&&!$("#tab_compare").classList.contains("hidden")&&(S.shown||0)<=300)loadUnits(true);
  if(!d.running&&prev&&prev.running){loadUnits(true).then(finishResend);renderSummary(d)}
}
async function refreshProjectsQuiet(){const keep=S.pid;try{const list=await api("/api/projects");const el=$("#projects");const cur=el.value;el.innerHTML="";el.add(new Option("בחר פרויקט...",""));list.forEach(x=>el.add(new Option(x.filename+" ["+x.format+"] - "+(STATUS[x.status]||x.status),x.id)));el.value=keep||cur}catch(e){}}
function renderFile(d){
  const m=d.meta,st=m.stats||{};$("#fileCard").hidden=false;
  const rows=[["שם קובץ",m.filename],["גודל",fmtSize(m.size||0)],["פורמט",(m.format||"").toUpperCase()],["פרקים",st.chapters],["פסקאות",st.paragraphs],["כותרות",st.headings],["מילים",st.words],["תמונות",st.images],["שפה מזוהה",st.language]];
  if(m.conversion)rows.push(["המרה",m.conversion.note]);
  $("#fileInfo").innerHTML=rows.map(r=>"<b>"+esc(r[0])+"</b><span>"+esc(r[1]==null?"-":r[1])+"</span>").join("");
  let html="";
  if(m.pdf_report){const r=m.pdf_report;const cls=r.score>=80?"ok":r.score>=55?"warn":"bad";
    html+='<div class="note '+cls+'"><b>ציון ביטחון מבני: '+r.score+' ('+esc(r.label)+')</b><br>עמודים: '+r.pages+' | כותרות: '+r.headings+' | פסקאות: '+r.paragraphs+' | פריטי רשימה: '+r.list_items+' | תמונות: '+r.images+
      '<br>שורות חשודות כפיצול שגוי: '+r.suspicious_splits+' | קטעים קצרים חשודים: '+r.suspicious_fragments+' | כותרות עליונות/תחתונות שהוסרו: '+r.dropped_header_footer_lines+'</div>';
    html+=(r.warnings||[]).map(w=>'<div class="note warn">'+esc(w)+'</div>').join("");
    if(m.status==="awaiting_confirmation")html+='<div class="row"><button class="ghost" id="pdfPrev">תצוגה מקדימה של המבנה</button><button id="pdfOk">אשר והמשך</button><button class="ghost" id="pdfNo">לא עכשיו (הפרויקט נשמר)</button></div>';
  }
  $("#pdfBox").innerHTML=html;
  if($("#pdfPrev"))$("#pdfPrev").onclick=showPreview;
  if($("#pdfOk"))$("#pdfOk").onclick=()=>confirmPdf(true);
  if($("#pdfNo"))$("#pdfNo").onclick=()=>confirmPdf(false);
}
async function showPreview(){
  const d=await api("/api/p/"+S.pid+"/preview");
  $("#dlgBody").innerHTML="<h3 class='hd'>המבנה שזוהה</h3>"+d.preview.map(p=>p.t==="h"?"<div style='margin-inline-start:"+((p.level-1)*18)+"px'><span class='tag'>H"+p.level+"</span> <b>"+esc(p.text)+"</b></div>":"<div class='small' style='margin:2px 0 2px 0'>&#182; "+esc(p.text)+"</div>").join("");
  $("#dlg").showModal();
}
$("#dlgClose").onclick=()=>$("#dlg").close();
async function confirmPdf(ok){
  try{
    await api("/api/p/"+S.pid+"/confirm",{method:"POST",body:{accept:ok}});
    if(!ok){
      clearInterval(S.timer);S.pid=null;$("#fileCard").hidden=true;await refreshProjects();
      alert("הפרויקט נשמר ולא נמחק. אפשר לחזור אליו מרשימת הפרויקטים ולאשר את המבנה בהמשך, או למחוק אותו במפורש דרך 'ניהול'.");
    }else await poll(false)
  }catch(e){alert(e.message)}
}

function renderRun(d){
  const m=d.meta,c=d.progress.counts,run=d.running;
  const done=c.done+c.failed+c.flagged;const pct=c.total?Math.round(100*done/c.total):0;
  $("#barFill").style.width=pct+"%";
  const cls=m.status==="error"?"bad":m.status==="completed"?"ok":"";
  const rv=rateView(m);
  $("#statusLine").innerHTML='<span class="chip '+cls+'">'+esc(STATUS[m.status]||m.status)+'</span> '+(run?"פרק "+d.progress.chapter+" | מקטע "+esc(d.progress.chunk):"")+
    (rv.remaining!=null?' <span class="chip '+rv.level+'" title="'+esc(rv.title)+'">מכסה '+rv.remaining+(rv.limit!=null?"/"+rv.limit:"")+'</span>':"");
  $("#errBox").innerHTML=m.error?'<div class="note bad"><b>'+esc(m.error.message)+'</b><br>'+esc(m.error.hint||"")+'</div>':"";
  renderStats(d,pct);
  const st=m.status;const hasUnits=(m.stats||{}).paragraphs>0||(m.stats||{}).headings>0;
  $("#btnStart").disabled=run||!hasUnits||["awaiting_confirmation","analyzing","building"].includes(st);
  $("#btnPause").disabled=!run;$("#btnStop").disabled=!run;
  $("#btnResume").disabled=run||!["paused","stopped","error"].includes(st)||c.pending===0;
  $("#btnRetry").disabled=run||(c.failed+c.flagged)===0;
  $("#l_dl").href="/api/p/"+S.pid+"/download/log?t="+TOKEN;
  document.querySelectorAll("[data-resend]").forEach(b=>{b.disabled=run||!!S.resendId});
}

/* ---------- אריחי סטטוס (ניתנים ללחיצה) ומונה מכסה ---------- */
const STAT_DEFS=[["progress","התקדמות",""],["done","מוצלחים","done"],["failed","כושלים","failed"],["flagged","לבדיקה ידנית","flagged"],["pending","ממתינים","pending"],
  ["elapsed","זמן שחלף",""],["eta","זמן משוער",""],["rate","בקשות / מכסה זמינה",""],["tokens","tokens קלט/פלט",""],["cost","עלות משוערת",""]];
function statEl(k){return document.querySelector('#stats [data-k="'+k+'"]')}
function ensureStats(){
  const box=$("#stats");if(box.dataset.ready)return;
  STAT_DEFS.forEach(def=>{
    const group=def[2];
    const el=document.createElement(group?"button":"div");
    el.className="stat"+(group?" clickable":"");el.dataset.k=def[0];
    if(group){el.type="button";el.dataset.group=group;el.title="לחץ לניווט בין הרכיבים בסטטוס הזה";el.onclick=()=>navToggle(group)}
    el.innerHTML='<span class="sl"></span><b></b><small></small>';
    el.querySelector(".sl").textContent=def[1];
    box.appendChild(el);
  });
  box.dataset.ready="1";
}
function setStat(k,value,sub,count){
  const el=statEl(k);if(!el)return;
  const b=el.querySelector("b"),s=el.querySelector("small");
  const text=String(value);if(b.textContent!==text)b.textContent=text;
  const subText=sub||"";if(s.textContent!==subText)s.textContent=subText;
  if(el.tagName==="BUTTON")el.disabled=!(count>0);
}
function rateView(m){
  const rl=m.rate_limit;const r=rl&&rl.requests;
  if(!r||(r.remaining==null&&r.limit==null))return{remaining:null,limit:null,sub:"",title:"הספק אינו מחזיר כותרות מכסה (או שעדיין לא נשלחה בקשה)",level:""};
  const age=Date.now()/1000-(rl.seen_at||0);
  let sub=r.limit!=null?"מתוך "+r.limit:"";
  if(r.reset_s!=null){sub+=(sub?" • ":"")+"איפוס בעוד "+fmtTime(Math.max(0,Math.round(r.reset_s-age)))}
  const t=rl.tokens;if(t&&t.remaining!=null)sub+=(sub?" • ":"")+"tokens: "+t.remaining;
  let level="";
  if(r.remaining!=null){if(r.remaining===0)level="bad";else if(r.limit&&r.remaining/r.limit<0.1)level="warn"}
  return{remaining:r.remaining,limit:r.limit,sub:sub,level:level,title:"בקשות שבוצעו / מכסה זמינה לפי כותרות הספק"+(rl.provider?" ("+rl.provider+")":"")};
}
function renderStats(d,pct){
  ensureStats();
  const m=d.meta,c=d.progress.counts,run=d.running,u=m.usage||{};
  const cost=d.cost>0?"$"+d.cost.toFixed(3):"-";
  setStat("progress",pct+"%");
  setStat("done",c.done,"",c.done);setStat("failed",c.failed,"",c.failed);setStat("flagged",c.flagged,"",c.flagged);setStat("pending",c.pending,"",c.pending);
  setStat("elapsed",fmtTime((u.elapsed||0)+(run?d.progress.elapsed:0)));
  setStat("eta",run?fmtTime(d.progress.eta):"-");
  const rv=rateView(m);
  setStat("rate",(u.requests||0)+" / "+(rv.remaining==null?"\u2014":rv.remaining),rv.sub);
  statEl("rate").title=rv.title;
  setStat("tokens",(u.tokens_in||0)+" / "+(u.tokens_out||0));
  setStat("cost",cost);
  document.querySelectorAll("#stats .clickable").forEach(el=>el.classList.toggle("on",NAV.group===el.dataset.group));
}
function checkSettingsBeforeStart(){const s=collectSettings();const goal=S.info.goals.find(x=>x.id===s.goal);if(goal.ai&&!s.model){alert("בחר מודל (אפשר לטעון רשימה או להזין ידנית).");return null}return {s,goal}}
function prepareBody(chk,extra,rememberAck){
  const pv=S.info.providers.find(x=>x.id===chk.s.provider)||{};
  const body=Object.assign({key:$("#s_key").value||undefined,remember:$("#s_remember").checked,ack_external:false},extra||{});
  if(chk.goal.ai&&!pv.local){
    const ackKey=chk.s.provider+"|"+chk.s.base_url;
    S.acks=S.acks||{};
    if(!(rememberAck&&S.acks[ackKey])){
      const host=(chk.s.base_url?(()=>{try{return new URL(chk.s.base_url).host}catch(e){return chk.s.base_url}})():pv.label);
      if(!confirm("שים לב: טקסט הספר יישלח לספק חיצוני ("+host+"). להמשיך?"))return null;
      if(rememberAck)S.acks[ackKey]=true;
    }
    body.ack_external=true;
  }
  return body;
}
async function startRun(path,extra){
  const chk=checkSettingsBeforeStart();if(!chk)return;
  await saveSettings();
  const body=prepareBody(chk,extra,false);if(!body)return;
  try{await api("/api/p/"+S.pid+"/"+path,{method:"POST",body});setSidebar(false);await poll(false)}catch(e){if(e.data&&e.data.error==="ack_required"){alert("נדרש אישור לשליחה לספק חיצוני")}else alert(e.message)}
}
async function resendUnit(u,btn){
  if(!u)return;
  const chk=checkSettingsBeforeStart();if(!chk)return;
  if(!chk.goal.ai){alert("המטרה הנוכחית אינה משתמשת במודל.");return}
  if(u.status==="manual"&&!confirm("הרכיב נערך ידנית. אם השליחה תצליח, התרגום החדש יחליף את העריכה. להמשיך?"))return;
  await saveSettings();
  const body=prepareBody(chk,{id:u.id},true);if(!body)return;
  S.resendId=u.id;S.resendLogFrom=S.logSince;renderUnits();
  try{await api("/api/p/"+S.pid+"/unit-resend",{method:"POST",body});await poll(false)}
  catch(e){S.resendId=null;renderUnits();toast({kind:"error",title:"השליחה מחדש נכשלה",text:e.message})}
}
function finishResend(){
  const id=S.resendId;if(!id)return;
  S.resendId=null;
  const row=S.rows.find(x=>x.id===id);
  // כשל בשליחה מחדש משחזר את התרגום הקודם (הסטטוס נשאר תקין), ולכן מזהים אותו לפי רשומת היומן ולא לפי הסטטוס
  const restored=S.logs.some(l=>l.id>(S.resendLogFrom||0)&&l.level==="warn"&&l.ctx&&l.ctx.stage==="resend"&&l.ctx.unit===id);
  if(restored)toast({kind:"warn",title:"השליחה מחדש לא הצליחה",text:id+": התרגום הקודם נשמר ללא שינוי",target:{unit:id}});
  else if(!row||row.status==="done"||row.status==="manual")toast({kind:"ok",title:"הרכיב עודכן",text:id,target:{unit:id}});
  LIVE.focus=id;liveSync(S.sum,true);
  renderUnits();
}
$("#btnStart").onclick=()=>startRun("start");$("#btnResume").onclick=()=>startRun("resume");$("#btnRetry").onclick=()=>startRun("retry-failed");
$("#btnPause").onclick=async()=>{try{await api("/api/p/"+S.pid+"/pause",{method:"POST",body:{}})}catch(e){alert(e.message)}};
$("#btnStop").onclick=async()=>{try{await api("/api/p/"+S.pid+"/stop",{method:"POST",body:{}})}catch(e){alert(e.message)}};
$("#testConn").onclick=async()=>{
  const s=collectSettings();$("#connState").textContent="בודק...";
  try{const r=await api("/api/provider/test",{method:"POST",body:{provider:s.provider,model:s.model,base_url:s.base_url,key:$("#s_key").value||undefined,timeout:s.timeout}});
    $("#connState").innerHTML=r.ok?'<span class="chip ok">'+esc(r.message)+(r.local?" (מקומי, דבר לא נשלח החוצה)":"")+'</span>':'<span class="chip bad">'+esc(r.message)+'</span> '+esc(r.hint||"");
    if(r.ok&&r.models&&r.models.length)fillModels(r.models)}catch(e){$("#connState").innerHTML='<span class="chip bad">'+esc(e.message)+'</span>'}
};
function fillModels(list){const dl=$("#modelList");dl.innerHTML="";list.forEach(m=>dl.appendChild(new Option(m,m)))}
$("#loadModels").onclick=async()=>{const s=collectSettings();try{const r=await api("/api/provider/models",{method:"POST",body:{provider:s.provider,base_url:s.base_url,key:$("#s_key").value||undefined}});
  if(r.ok){fillModels(r.models);$("#connState").innerHTML='<span class="chip ok">נטענו '+r.models.length+' מודלים</span>'}else $("#connState").innerHTML='<span class="chip bad">'+esc(r.message)+'</span> '+esc(r.hint||"")}catch(e){$("#connState").textContent=e.message}};

/* ---------- טאבים ---------- */
document.querySelectorAll(".tabs button").forEach(b=>b.onclick=()=>{document.querySelectorAll(".tabs button").forEach(x=>x.classList.toggle("on",x===b));
  ["compare","glossary","logs","summary","live"].forEach(t=>$("#tab_"+t).classList.toggle("hidden",t!==b.dataset.tab));
  if(b.dataset.tab==="glossary")loadGlossary();if(b.dataset.tab==="compare"&&!S.silentTab)loadUnits(true);if(b.dataset.tab==="summary")renderSummary(S.sum);if(b.dataset.tab==="logs")renderLogs(true);if(b.dataset.tab==="live")liveOpen()});

/* ---------- השוואה ---------- */
async function loadChapters(d){
  const sel=$("#c_chapter");const keep=sel.value;sel.innerHTML="";sel.add(new Option("כל הספר","-1"));
  (d.chapters||[]).forEach(c=>sel.add(new Option(c.index+". "+c.title+" ("+c.count+")",String(c.index))));
  sel.value=keep||"-1";S.chapter=parseInt(sel.value);await loadUnits(true);
}
$("#c_chapter").onchange=()=>{S.chapter=parseInt($("#c_chapter").value);loadUnits(true)};
$("#c_issues").onchange=()=>loadUnits(true);
$("#c_prev").onclick=()=>{const s=$("#c_chapter");if(s.selectedIndex>0){s.selectedIndex--;s.onchange()}};
$("#c_next").onclick=()=>{const s=$("#c_chapter");if(s.selectedIndex<s.options.length-1){s.selectedIndex++;s.onchange()}};
$("#c_more").onclick=()=>loadUnits(false);
function wordDiff(a,b){
  const x=a.split(/\s+/),y=b.split(/\s+/);if(x.length>350||y.length>350)return[esc(a),esc(b)];
  const n=x.length,m=y.length,L=Array.from({length:n+1},()=>new Int32Array(m+1));
  for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)L[i][j]=x[i]===y[j]?L[i+1][j+1]+1:Math.max(L[i+1][j],L[i][j+1]);
  let i=0,j=0;const A=[],B=[];
  while(i<n&&j<m){if(x[i]===y[j]){A.push(esc(x[i]));B.push(esc(y[j]));i++;j++}else if(L[i+1][j]>=L[i][j+1]){A.push("<del>"+esc(x[i])+"</del>");i++}else{B.push("<ins>"+esc(y[j])+"</ins>");j++}}
  while(i<n)A.push("<del>"+esc(x[i++])+"</del>");while(j<m)B.push("<ins>"+esc(y[j++])+"</ins>");
  return[A.join(" "),B.join(" ")];
}
async function loadUnits(reset,upto){
  if(!S.pid)return;
  if(reset){S.offset=0;S.rows=[]}
  const issues=$("#c_issues").checked?"issues":"";
  const window_=upto?"&upto="+encodeURIComponent(upto):"&limit="+(reset?Math.min(300,Math.max(60,S.shown||120)):120);
  let d;try{d=await api("/api/p/"+S.pid+"/units?chapter="+S.chapter+"&filter="+issues+"&offset="+S.offset+window_)}catch(e){return}
  S.rows=reset?d.units:S.rows.concat(d.units);S.total=d.total;S.offset=S.rows.length;S.shown=S.rows.length;
  renderUnits();
}
function renderUnits(){
  const goal=S.sum?S.info.goals.find(x=>x.id===S.sum.settings.goal):null;const useDiff=goal&&!goal.translate&&goal.ai;
  const editing=document.activeElement&&document.activeElement.tagName==="TEXTAREA";if(editing)return;
  $("#c_note").textContent="מוצגים "+S.rows.length+" מתוך "+S.total+" רכיבים";
  $("#c_more").classList.toggle("hidden",S.rows.length>=S.total);
  $("#c_list").innerHTML=S.rows.map((u,idx)=>{
    let src=esc(u.src),out=u.out==null?'<span class="small">'+(u.status==="pending"?"ממתין לעיבוד":"הטקסט המקורי נשמר")+'</span>':esc(u.out);
    if(useDiff&&u.out!=null){const d=wordDiff(u.src,u.out);src=d[0];out=d[1]}
    const chips=[];if(u.status==="failed")chips.push('<span class="chip bad">נכשל</span>');if(u.status==="flagged")chips.push('<span class="chip warn">לבדיקה ידנית</span>');if(u.status==="manual")chips.push('<span class="chip ok">נערך ידנית</span>');
    (u.warn||[]).forEach(w=>chips.push('<span class="chip warn">'+esc(w)+'</span>'));
    if(u.err)chips.push('<span class="chip bad">'+esc((u.err.messages||[]).join("; "))+'</span>');
    const sending=S.resendId===u.id;
    const resendBtn=(goal&&goal.ai)?'<button class="ghost" style="padding:1px 8px" data-resend="'+idx+'"'+((S.sum&&S.sum.running)||S.resendId?' disabled':'')+' title="שליחה מחדש של הרכיב הזה בלבד למודל הנוכחי, עם ההקשר המלא (כותרת, פסקאות קודמות, מילון)">'+(sending?'שולח...':'שלח שוב למודל')+'</button>':"";
    // כפתור העריכה מוצג לכל רכיב, כולל כאלה שעדיין ממתינים (גם כשאין להם פלט)
    return '<div class="pair '+u.status+(sending?' resending':'')+'" data-uid="'+esc(u.id)+'"><div class="src">'+src+'</div><div class="src">'+out+'</div><div class="meta"><span class="tag">'+esc(u.id)+'</span><span class="tag">'+esc(u.type)+(u.level?" "+u.level:"")+'</span>'+chips.join("")+
      '<button class="ghost" style="padding:1px 8px" data-edit="'+idx+'">עריכה ידנית</button>'+resendBtn+'<button class="ghost" style="padding:1px 8px" data-live="'+idx+'" title="הצג את הרכיב בתצוגה החיה של הספר">תצוגה חיה</button></div></div>';
  }).join("");
  document.querySelectorAll("[data-edit]").forEach(b=>b.onclick=()=>editUnit(parseInt(b.dataset.edit),b));
  document.querySelectorAll("[data-resend]").forEach(b=>b.onclick=()=>resendUnit(S.rows[parseInt(b.dataset.resend)],b));
  document.querySelectorAll("[data-live]").forEach(b=>b.onclick=()=>liveShow(S.rows[parseInt(b.dataset.live)]));
}
function editUnit(idx,btn){
  const u=S.rows[idx];const meta=btn.parentElement;const pair=meta.parentElement;
  const wrap=document.createElement("div");wrap.style.gridColumn="1/-1";wrap.style.padding="8px 10px";
  wrap.innerHTML='<div class="small">'+(u.status==="pending"?"הרכיב עדיין לא עובד. אם תשמור עריכה, העיבוד ידלג עליו ויסמן אותו כנערך ידנית. ":"")+'שמור על התגיות <span class="tag">&lt;b1&gt;..&lt;/b1&gt;</span> <span class="tag">&lt;n2/&gt;</span> בדיוק כפי שהן במקור:</div><textarea dir="auto"></textarea><div class="small" dir="auto" style="margin:4px 0">מקור: '+esc(u.tagged)+'</div><div class="row"><button class="fixed">שמור</button><button class="ghost fixed">ביטול</button><span class="small" data-msg></span></div>';
  wrap.querySelector("textarea").value=u.out_tagged||u.tagged;pair.insertBefore(wrap,meta);
  const [save,cancel]=wrap.querySelectorAll("button");
  cancel.onclick=()=>{wrap.remove();loadUnits(true)};
  save.onclick=async()=>{try{await api("/api/p/"+S.pid+"/unit-save",{method:"POST",body:{id:u.id,text:wrap.querySelector("textarea").value}});wrap.remove();await loadUnits(true);await poll(false);LIVE.focus=u.id;liveSync(S.sum,true)}catch(e){wrap.querySelector("[data-msg]").textContent=e.message}};
}

/* ---------- ניווט ליחידה / לשונית ---------- */
function openTab(name,silent){
  const b=document.querySelector('.tabs button[data-tab="'+name+'"]');if(!b)return;
  S.silentTab=!!silent;b.click();S.silentTab=false;
}
const REDUCED=window.matchMedia("(prefers-reduced-motion: reduce)");
async function revealUnit(id){
  openTab("compare",true);
  const find=()=>document.querySelector('[data-uid="'+CSS.escape(id)+'"]');
  let el=find();
  if(!el){
    // היחידה לא בשורות שנטענו: מאפסים מסננים וטוענים מההתחלה עד אליה
    $("#c_issues").checked=false;$("#c_chapter").value="-1";S.chapter=-1;
    await loadUnits(true,id);
    el=find();
  }
  if(!el)return false;
  el.scrollIntoView({block:"center",behavior:REDUCED.matches?"auto":"smooth"});
  document.querySelectorAll(".pair.flash").forEach(x=>x.classList.remove("flash"));void el.offsetWidth;el.classList.add("flash");
  return true;
}
async function goToTarget(t){
  try{
    let id=t.unit||"";
    if(!id&&t.chunk){const r=await api("/api/p/"+S.pid+"/unit-index?chunk="+encodeURIComponent(t.chunk));id=(r.ids||[])[0]||""}
    if(id&&await revealUnit(id))return;
    if(t.chapter){
      $("#c_chapter").value=String(t.chapter);S.chapter=parseInt(t.chapter);openTab("compare",true);await loadUnits(true);
      $("#c_list").scrollIntoView({block:"start",behavior:REDUCED.matches?"auto":"smooth"});return;
    }
    if(t.errorsOnly){$("#l_err").checked=true;renderLogs()}
    openTab(t.tab||"logs");
  }catch(e){}
}

/* ---------- התראות (toast) ---------- */
const TOAST={max:4,seen:{}};
function clearToasts(){$("#toasts").textContent="";TOAST.seen={}}
function dismissToast(el){
  if(!el.parentNode)return;
  el.classList.add("out");
  if(REDUCED.matches)el.remove();else setTimeout(()=>el.remove(),220);
}
function toast(o){
  const key=(o.kind||"")+"|"+(o.title||"")+"|"+(o.text||"");
  const now=Date.now();
  if(TOAST.seen[key]&&now-TOAST.seen[key]<4000)return;
  TOAST.seen[key]=now;
  const box=$("#toasts");
  const el=document.createElement("div");
  el.className="toast "+(o.kind||"info");
  el.setAttribute("role",o.kind==="error"?"alert":"status");
  const body=document.createElement("button");body.type="button";body.className="tbody";
  const title=document.createElement("b");title.textContent=o.title||"";
  const text=document.createElement("span");text.textContent=o.text||"";
  body.appendChild(title);body.appendChild(text);
  if(o.target){const hint=document.createElement("em");hint.textContent=(o.target.unit||o.target.chunk||o.target.chapter)?"לחץ למעבר לרכיב":"לחץ לפתיחת היומן";body.appendChild(hint)}
  body.onclick=()=>{dismissToast(el);if(o.target)goToTarget(o.target)};
  const close=document.createElement("button");close.type="button";close.className="tclose";close.setAttribute("aria-label","סגור התראה");close.textContent="\u2715";
  close.onclick=e=>{e.stopPropagation();dismissToast(el)};
  el.appendChild(body);el.appendChild(close);
  box.appendChild(el);
  while(box.childElementCount>TOAST.max)box.removeChild(box.firstElementChild);
  if(o.kind!=="error")setTimeout(()=>dismissToast(el),o.kind==="warn"?9000:4500);
}
const ERR_TITLES={request:"שגיאת ספק",validate:"אימות הרכיב נכשל",parse:"כשל בפענוח התשובה",preflight:"בדיקת החיבור נכשלה",resend:"שליחה מחדש",state:"שמירת מצב נכשלה",run:"שגיאה בריצה",chunk:"שגיאה במקטע"};
function notifyLogs(logs,initial){
  if(initial)return;
  const issues=logs.filter(l=>l.level==="error"||(l.level==="warn"&&["validate","parse","resend"].includes((l.ctx||{}).stage)));
  if(!issues.length)return;
  if(issues.length>3){
    const errs=issues.filter(l=>l.level==="error").length;
    toast({kind:errs?"error":"warn",title:issues.length+" התראות חדשות",text:"לחץ לפתיחת היומן (שגיאות בלבד)",target:{tab:"logs",errorsOnly:true}});
    return;
  }
  issues.forEach(l=>{
    const c=l.ctx||{};
    toast({kind:l.level==="error"?"error":"warn",title:(ERR_TITLES[c.stage]||"שגיאה")+(c.chunk?" \u2022 "+c.chunk:""),text:l.msg,target:{unit:c.unit,chunk:c.chunk,chapter:c.chapter,tab:"logs"}});
  });
}

/* ---------- תפריט ניווט צף בין רכיבים לפי סטטוס ---------- */
const NAV={group:"",ids:[],i:-1,busy:false};
const GROUP_LABEL={done:"מוצלחים",failed:"כושלים",flagged:"לבדיקה ידנית",pending:"ממתינים"};
function navLabel(){
  $("#navPop").dataset.group=NAV.group;
  $("#navTitle").textContent=GROUP_LABEL[NAV.group]||"";
  $("#navPos").textContent=NAV.ids.length?(NAV.i+1)+" / "+NAV.ids.length:"0";
}
function navClose(){
  NAV.group="";NAV.ids=[];NAV.i=-1;
  $("#navPop").hidden=true;
  document.querySelectorAll("#stats .clickable").forEach(el=>el.classList.remove("on"));
}
async function navOpen(group){
  const r=await api("/api/p/"+S.pid+"/unit-index?status="+group);
  if(!r.ids.length){navClose();return}
  NAV.group=group;NAV.ids=r.ids;NAV.i=-1;
  $("#navPop").hidden=false;
  document.querySelectorAll("#stats .clickable").forEach(el=>el.classList.toggle("on",el.dataset.group===group));
  await navStep(1);
}
function navToggle(group){
  if(NAV.group===group){navClose();return}
  navOpen(group).catch(e=>toast({kind:"error",title:"הניווט נכשל",text:e.message}));
}
async function navStep(dir){
  if(!NAV.ids.length)return;
  const n=NAV.ids.length;
  NAV.i=NAV.i<0?(dir>0?0:n-1):(NAV.i+dir+n)%n;
  navLabel();
  await revealUnit(NAV.ids[NAV.i]);
}
async function navRefresh(){
  NAV.busy=true;
  try{
    const current=NAV.ids[NAV.i];
    const r=await api("/api/p/"+S.pid+"/unit-index?status="+NAV.group);
    if(!r.ids.length){navClose();return}
    NAV.ids=r.ids;
    const at=r.ids.indexOf(current);
    NAV.i=at>=0?at:Math.min(Math.max(NAV.i,0),r.ids.length-1);
    navLabel();
  }catch(e){}
  NAV.busy=false;
}
function navSync(d){
  if(!NAV.group||NAV.busy)return;
  if(d.progress.counts[NAV.group]!==NAV.ids.length)navRefresh();
}
$("#navUp").onclick=()=>navStep(-1);
$("#navDown").onclick=()=>navStep(1);
$("#navClose").onclick=navClose;
$("#navPop").addEventListener("keydown",e=>{
  if(e.key==="ArrowUp"){e.preventDefault();navStep(-1)}
  else if(e.key==="ArrowDown"){e.preventDefault();navStep(1)}
  else if(e.key==="Escape"){navClose()}
});

/* ---------- תצוגה חיה ---------- */
// ה-iframe נטען מכתובת של השרת (/live/...) שמשחזרת את ה-XHTML המקורי עם הטקסטים העדכניים, ושאר הנכסים (CSS, תמונות, גופנים)
// נטענים מתוך ארכיון ה-EPUB דרך /asset/... . sandbox בלי allow-scripts מונע הרצת קוד מהספר, ו-allow-same-origin מאפשר לשמור גלילה.
const LIVE={key:"",docs:[],doc:"",mode:"",loadedRev:-1,focus:"",lastLoad:0,ready:false,restore:null,pending:null,loadedAt:null};
function liveVisible(){return !$("#tab_live").classList.contains("hidden")}
function liveReset(){
  LIVE.key="";LIVE.docs=[];LIVE.doc="";LIVE.ready=false;LIVE.loadedRev=-1;LIVE.focus="";LIVE.restore=null;LIVE.pending=null;LIVE.loadedAt=null;
  $("#liveFrame").removeAttribute("src");$("#live_status").textContent="";
}
function liveUrl(){
  const path=LIVE.doc.split("/").map(encodeURIComponent).join("/");
  return "/api/p/"+S.pid+"/live/"+LIVE.key+"/"+path+"?mode="+encodeURIComponent(LIVE.mode)+"&r="+Date.now();
}
function liveStatus(stale){
  const t=LIVE.loadedAt?LIVE.loadedAt.toLocaleTimeString("he-IL"):"";
  $("#live_status").textContent=(t?"עודכן "+t:"")+(stale?" \u2022 יש שינויים חדשים, לחץ על רענן":"");
}
function liveReload(focusId,top){
  if(!LIVE.ready||!LIVE.doc)return;
  const frame=$("#liveFrame");
  let y=0;
  if(!top&&!focusId){try{y=frame.contentWindow.scrollY||0}catch(e){}}
  LIVE.restore=focusId?{focus:focusId}:{y:y};
  LIVE.loadedRev=S.sum?S.sum.rev:-1;LIVE.lastLoad=Date.now();
  $("#live_status").textContent="טוען...";
  frame.src=liveUrl();
}
async function liveOpen(){
  if(!S.pid)return;
  try{
    const d=await api("/api/p/"+S.pid+"/live-index");
    LIVE.key=d.key;LIVE.docs=d.docs;
    $("#live_doc").innerHTML=d.docs.map(x=>'<option value="'+esc(x.path)+'">'+esc(x.title)+" ("+x.done+"/"+x.total+")</option>").join("");
    const msel=$("#live_mode");
    msel.innerHTML=d.modes.map(m=>'<option value="'+m+'">'+(m==="bilingual"?"דו־לשוני":"תרגום בלבד")+"</option>").join("");
    msel.hidden=d.modes.length<2;
    if(!LIVE.mode||!d.modes.includes(LIVE.mode))LIVE.mode=d.mode;
    msel.value=LIVE.mode;
    let focus;
    if(LIVE.pending){LIVE.doc=LIVE.pending.doc;focus=LIVE.pending.focus;LIVE.pending=null}
    else if(!d.docs.some(x=>x.path===LIVE.doc)){const first=d.docs.find(x=>x.role==="content"&&x.total>0)||d.docs.find(x=>x.role==="content")||d.docs[0];LIVE.doc=first?first.path:""}
    $("#live_doc").value=LIVE.doc;
    LIVE.ready=true;
    if(LIVE.doc)liveReload(focus,!focus);else $("#live_status").textContent="אין מסמכים להצגה";
  }catch(e){$("#live_status").textContent=e.message}
}
function liveShow(u){
  if(!u)return;
  if(liveVisible()&&LIVE.ready){LIVE.doc=u.file;$("#live_doc").value=u.file;liveReload(u.id)}
  else{LIVE.pending={doc:u.file,focus:u.id};openTab("live")}
}
function liveSync(d,fromEdit){
  if(!LIVE.ready||!d||!liveVisible())return;
  const stale=d.rev!==LIVE.loadedRev;
  const now=Date.now();
  // רענון אוטומטי: מיד אחרי עריכה, ובזמן ריצה לכל היותר אחת ל-8 שניות כדי שלא יהבהב
  if(stale&&$("#live_auto").checked&&(fromEdit||!d.running||now-LIVE.lastLoad>8000)&&now-LIVE.lastLoad>400){
    const f=LIVE.focus;LIVE.focus="";liveReload(f||undefined);return;
  }
  liveStatus(stale);
}
$("#liveFrame").addEventListener("load",()=>{
  const frame=$("#liveFrame");
  let doc=null;
  try{doc=frame.contentDocument}catch(e){return}
  if(!doc||!doc.location||doc.location.href==="about:blank")return;
  const m=doc.location.pathname.match(/\/live\/[0-9a-f]{32}\/(.+)$/);
  if(m){const p=decodeURIComponent(m[1]);if(p!==LIVE.doc){LIVE.doc=p;$("#live_doc").value=p}}
  const r=LIVE.restore||{};LIVE.restore=null;
  if(r.focus){
    const el=doc.getElementById("bai-u-"+r.focus);
    if(el){
      el.scrollIntoView({block:"center"});
      const block=el.parentElement;
      if(block){
        const color=getComputedStyle(document.documentElement).getPropertyValue("--acc").trim()||"#0f6b5c";
        const old=block.style.outline;
        block.style.outline="3px solid "+color;block.style.outlineOffset="3px";
        setTimeout(()=>{block.style.outline=old;block.style.outlineOffset=""},1800);
      }
    }
  }else if(r.y){try{frame.contentWindow.scrollTo(0,r.y)}catch(e){}}
  LIVE.loadedAt=new Date();
  liveStatus(S.sum?S.sum.rev!==LIVE.loadedRev:false);
});
$("#live_refresh").onclick=()=>{const f=LIVE.focus;LIVE.focus="";liveReload(f||undefined)};
$("#live_doc").onchange=()=>{LIVE.doc=$("#live_doc").value;liveReload(undefined,true)};
$("#live_mode").onchange=()=>{LIVE.mode=$("#live_mode").value;liveReload()};

/* ---------- הגדרות מומלצות לפי מודל ---------- */
// המיפוי עצמו (MODEL_PROFILES) יושב בראש הסקריפט בצד השרת; כאן רק מבקשים התאמה ומציגים אותה.
const PROFILE={current:null,undo:null,timer:null,last:""};
const PROFILE_FIELDS=[["temperature","#s_temp","טמפרטורה"],["chunk_chars","#s_chunk","גודל מקטע (תווים)"],["overlap","#s_overlap","חפיפה להקשר (פסקאות)"],
  ["max_output_tokens","#s_maxout","מקסימום פלט (tokens)"],["context_tokens","#s_ctx","הקשר המודל (tokens)"],["concurrency","#s_conc","בקשות מקבילות"]];
function profileAuto(){try{return localStorage.getItem("bookai.autoprofile")==="1"}catch(e){return false}}
function hideProfile(){const box=$("#profileBox");box.classList.add("hidden");box.textContent="";PROFILE.current=null}
function fmtProfileValue(key,v){
  if(v===null||v===undefined||v==="")return key==="temperature"?"לא נשלחת":"ריק";
  return String(v);
}
function profileDiff(p){
  const rows=[];
  PROFILE_FIELDS.forEach(f=>{
    if(!(f[0] in p.settings))return;
    const want=p.settings[f[0]];
    const raw=$(f[1]).value.trim();
    const have=raw===""?null:parseFloat(raw);
    if(have===want)return;
    rows.push({id:f[1],label:f[2],key:f[0],from:have,to:want});
  });
  if(p.extra&&!$("#s_extra").value.trim())rows.push({id:"#s_extra",label:"הנחיות נוספות",key:"extra",from:null,to:p.extra});
  return rows;
}
function showProfile(p,rows,state){
  const box=$("#profileBox");
  box.textContent="";box.classList.remove("hidden");
  const add=(tag,text,cls)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!=null)el.textContent=text;box.appendChild(el);return el};
  const head=add("div",null,"ph");
  const title=document.createElement("b");
  title.textContent=(state==="applied"?"הוחלו הגדרות מומלצות: ":"הגדרות מומלצות: ")+p.label;head.appendChild(title);
  if(p.status==="legacy"){const tag=document.createElement("span");tag.className="chip warn";tag.textContent="מודל ישן";head.appendChild(tag)}
  if(!rows.length){add("div","ההגדרות הנוכחיות כבר תואמות להמלצה.")}
  else{
    const list=add("ul");
    rows.forEach(r=>{
      const li=document.createElement("li");
      li.textContent=r.label+": "+(r.key==="extra"?"":fmtProfileValue(r.key,r.from)+" \u2190 ")+(r.key==="extra"?r.to:fmtProfileValue(r.key,r.to));
      list.appendChild(li);
    });
  }
  const det=add("details");
  const sum=document.createElement("summary");sum.textContent="למה?";det.appendChild(sum);
  const why=document.createElement("ul");
  p.notes.forEach(t=>{const li=document.createElement("li");li.textContent=t;why.appendChild(li)});
  det.appendChild(why);
  if(p.extra&&$("#s_extra").value.trim()&&state!=="applied")add("div","שדה ההנחיות שלך אינו ריק, ולכן לא יוחלף.","psrc");
  add("div","מקור: "+p.source+" \u2022 "+(p.verified?"מגבלות נבדקו מול תיעוד הספק ("+p.verified+")":"המגבלות לא נבדקו מול תיעוד עדכני")+" \u2022 המלצה התחלתית, לא תוצאת מדידה.","psrc");
  const actions=add("div",null,"pa");
  const button=(label,cls,fn,disabled)=>{const b=document.createElement("button");b.type="button";b.textContent=label;if(cls)b.className=cls;b.disabled=!!disabled;b.onclick=fn;actions.appendChild(b)};
  const running=!!(S.sum&&S.sum.running);
  if(state==="suggest"){
    button("החל","",()=>applyProfile(p),running);
    button("התעלם","ghost",hideProfile);
    if(running)add("div","אי אפשר לשנות הגדרות בזמן עיבוד.","psrc");
  }else if(state==="applied"){
    button("בטל החלה","ghost",undoProfile);
    button("סגור","ghost",hideProfile);
  }else button("סגור","ghost",hideProfile);
  const auto=add("div",null,"check");
  const cb=document.createElement("input");cb.type="checkbox";cb.id="profileAuto";cb.checked=profileAuto();
  const lb=document.createElement("label");lb.htmlFor="profileAuto";lb.style.margin="0";lb.style.color="inherit";lb.textContent="החל אוטומטית כשבוחרים מודל מוכר";
  cb.onchange=()=>{
    try{localStorage.setItem("bookai.autoprofile",cb.checked?"1":"0")}catch(e){}
    if(cb.checked&&state==="suggest"&&!running)applyProfile(p);
  };
  auto.appendChild(cb);auto.appendChild(lb);
}
function applyProfile(p){
  const rows=profileDiff(p);
  PROFILE.undo=rows.map(r=>({id:r.id,value:$(r.id).value}));
  rows.forEach(r=>{$(r.id).value=r.to===null?"":String(r.to)});
  applyVisibility();scheduleSave();
  showProfile(p,rows,"applied");
}
function undoProfile(){
  (PROFILE.undo||[]).forEach(u=>{$(u.id).value=u.value});
  PROFILE.undo=null;applyVisibility();scheduleSave();hideProfile();
}
async function checkProfile(){
  const provider=$("#s_provider").value,model=$("#s_model").value.trim();
  const key=provider+"|"+model;
  if(!model){hideProfile();PROFILE.last="";return}
  if(key===PROFILE.last)return;
  PROFILE.last=key;
  let r;
  try{r=await api("/api/model-profile?provider="+encodeURIComponent(provider)+"&model="+encodeURIComponent(model))}catch(e){return}
  if(PROFILE.last!==key)return;
  if(!r.profile){hideProfile();return}
  PROFILE.current=r.profile;
  const rows=profileDiff(r.profile);
  const running=!!(S.sum&&S.sum.running);
  if(!rows.length){showProfile(r.profile,rows,"match");return}
  if(profileAuto()&&!running){
    applyProfile(r.profile);
    toast({kind:"ok",title:"הוחלו הגדרות מומלצות",text:r.profile.label});
    return;
  }
  showProfile(r.profile,rows,"suggest");
}
$("#s_model").addEventListener("change",()=>{clearTimeout(PROFILE.timer);checkProfile()});
$("#s_model").addEventListener("input",()=>{clearTimeout(PROFILE.timer);PROFILE.timer=setTimeout(checkProfile,800)});
$("#s_provider").addEventListener("change",()=>{hideProfile();PROFILE.last=""});

/* ---------- יומן ---------- */
const LOG_MAX_NODES=1500;
function logNode(l){
  const icon=l.level==="error"?"\u2716":l.level==="warn"?"\u26A0":"\u2139";
  const c=l.ctx||{};
  const ctx=["stage","chunk","chapter","provider","model","kind","http","retryable","tried"].filter(k=>c[k]!=null).map(k=>k+"="+c[k]).join(" ");
  const row=document.createElement("div");
  if(l.level==="error")row.className="e";else if(l.level==="warn")row.className="w";
  row.innerHTML=icon+" "+esc(l.ts)+" "+esc(l.msg)+(ctx?' <span class="c">['+esc(ctx)+']</span>':"")+(c.suggestion?' <span class="c">&rarr; '+esc(c.suggestion)+'</span>':"");
  return row;
}
function logShown(l){return !$("#l_err").checked||l.level==="error"}
function logsToEnd(){
  const box=$("#logBox");
  box.scrollTop=box.scrollHeight;
  // פעם נוספת אחרי הציור, למקרה שהפריסה הסתיימה רק עכשיו
  requestAnimationFrame(()=>{box.scrollTop=box.scrollHeight});
}
function trimLogs(){
  const box=$("#logBox");
  while(box.childElementCount>LOG_MAX_NODES)box.removeChild(box.firstElementChild);
}
function appendLogs(entries){
  if(!entries.length)return;
  const frag=document.createDocumentFragment();
  entries.forEach(l=>{if(logShown(l))frag.appendChild(logNode(l))});
  $("#logBox").appendChild(frag);
  trimLogs();
  logsToEnd();
}
function renderLogs(){
  const frag=document.createDocumentFragment();
  S.logs.forEach(l=>{if(logShown(l))frag.appendChild(logNode(l))});
  const box=$("#logBox");
  box.textContent="";
  box.appendChild(frag);
  trimLogs();
  logsToEnd();
}
$("#l_err").onchange=()=>renderLogs(true);
$("#l_clear").onclick=()=>{S.logs=[];$("#logBox").innerHTML=""};
$("#l_copy").onclick=()=>navigator.clipboard.writeText($("#logBox").innerText);

/* ---------- מילון ---------- */
async function loadGlossary(){if(!S.pid)return;const d=await api("/api/p/"+S.pid+"/glossary");S.glossary=d.entries;renderGlossary()}
function renderGlossary(){
  $("#g_body").innerHTML=S.glossary.map((e,i)=>'<tr><td><input type="text" data-g="source" data-i="'+i+'" value="'+esc(e.source)+'" dir="auto"></td><td><input type="text" data-g="target" data-i="'+i+'" value="'+esc(e.target)+'" dir="auto"></td><td><input type="checkbox" data-g="locked" data-i="'+i+'" '+(e.locked?"checked":"")+'></td><td><button class="danger" data-del="'+i+'" style="padding:1px 8px">x</button></td></tr>').join("");
  document.querySelectorAll("[data-g]").forEach(el=>el.onchange=()=>{const i=+el.dataset.i,k=el.dataset.g;S.glossary[i][k]=k==="locked"?el.checked:el.value});
  document.querySelectorAll("[data-del]").forEach(b=>b.onclick=()=>{S.glossary.splice(+b.dataset.del,1);renderGlossary()});
}
$("#g_add").onclick=()=>{S.glossary.push({source:"",target:"",locked:false});renderGlossary()};
$("#g_save").onclick=async()=>{try{const r=await api("/api/p/"+S.pid+"/glossary",{method:"POST",body:{entries:S.glossary}});$("#g_save").textContent="נשמר ("+r.count+")";setTimeout(()=>$("#g_save").textContent="שמור מילון",1500)}catch(e){alert(e.message)}};
$("#g_suggest").onclick=async()=>{const r=await api("/api/p/"+S.pid+"/glossary/suggest",{method:"POST",body:{}});S.glossary=S.glossary.concat(r.entries);renderGlossary()};
$("#g_translate").onclick=async()=>{await api("/api/p/"+S.pid+"/glossary",{method:"POST",body:{entries:S.glossary}});if(!confirm("שמות ומונחים מהספר יישלחו למודל לתרגום. להמשיך?"))return;
  try{const r=await api("/api/p/"+S.pid+"/glossary/translate",{method:"POST",body:{key:$("#s_key").value||undefined}});S.glossary=r.entries;renderGlossary()}catch(e){alert(e.message)}};

/* ---------- סיכום ---------- */
function renderSummary(d){
  if(!d)return;const box=$("#summaryBox");const f=d.meta.final;
  if(!f){
    const idle=!d.running&&["paused","stopped","error","ready"].includes(d.meta.status)&&d.progress.counts.done>0;
    box.innerHTML='<div class="small">הסיכום יופיע בסיום העיבוד.</div>'+(idle?'<div class="row" style="margin:8px 0"><button class="ghost fixed" id="rebuild">הפק EPUB מהתוצאות הנוכחיות</button><span></span></div><div class="small">רכיבים שעדיין לא עובדו יישארו בטקסט המקורי, ואפשר להמשיך לעבד אחר כך.</div>':"");
    bindRebuild();return}
  let h='<h3 class="hd">קבצי פלט</h3>'+f.files.map(x=>'<div class="row" style="margin:4px 0"><span>'+esc(x.name)+' <span class="chip '+(x.verify.ok?"ok":"bad")+'">'+(x.verify.ok?"אימות תקין":"יש כשלים באימות")+'</span></span><a class="fixed" href="/api/p/'+d.meta.id+'/download/'+encodeURIComponent(x.name)+'?t='+TOKEN+'"><button type="button">הורד EPUB</button></a></div>').join("");
  h+='<div class="row" style="margin:8px 0"><a class="fixed" href="/api/p/'+d.meta.id+'/download/report?t='+TOKEN+'"><button class="ghost" type="button">הורד דוח JSON</button></a><button class="ghost fixed" id="rebuild">הפק מחדש מהתוצאות הנוכחיות</button><span></span></div>';
  if(d.meta.outputs_stale)h='<div class="note warn">נערכו רכיבים אחרי ההפקה האחרונה, ולכן קבצי ההורדה אינם כוללים אותם. לחץ על "הפק מחדש מהתוצאות הנוכחיות".</div>'+h;
  const v=f.files[0].verify;
  h+='<h3 class="hd">בדיקות</h3><table><tbody>'+v.checks.map(c=>'<tr><td style="width:36px">'+(c.ok===true?"\u2714":c.ok===false?"\u2716":"\u2014")+'</td><td>'+esc(c.name)+(c.detail?'<div class="small">'+esc(c.detail)+'</div>':"")+'</td></tr>').join("")+'</tbody></table>';
  h+='<h3 class="hd" style="margin-top:12px">השוואה מספרית: מקור מול פלט</h3><table><thead><tr><th>מדד</th><th>מקור</th><th>פלט</th></tr></thead><tbody>'+v.table.map(r=>'<tr><td>'+esc(r.label)+'</td><td>'+r.src+'</td><td>'+r.out+'</td></tr>').join("")+'</tbody></table>';
  h+='<h3 class="hd" style="margin-top:12px">אזהרות ומקטעים שנכשלו</h3><div class="small">רכיבים עם אזהרות: '+f.warned+' | נכשלו: '+f.failed.length+' | לבדיקה ידנית: '+f.flagged.length+'</div>';
  const fc=Object.entries(d.failed_chunks||{});
  if(fc.length)h+='<table style="margin-top:6px"><thead><tr><th>מקטע</th><th>רכיבים</th><th></th></tr></thead><tbody>'+fc.map(([k,n])=>'<tr><td>'+esc(k)+'</td><td>'+n+'</td><td><button class="ghost" data-retry="'+esc(k)+'">נסה שוב</button></td></tr>').join("")+'</tbody></table><div class="small">אפשר להחליף מודל בהגדרות לפני הניסיון החוזר, או לערוך ידנית בלשונית ההשוואה (אזהרות וכשלים בלבד) ואז להפיק מחדש.</div>';
  box.innerHTML=h;
  document.querySelectorAll("[data-retry]").forEach(b=>b.onclick=()=>startRun("retry-chunk",{chunk:b.dataset.retry,model:$("#s_model").value}));
  bindRebuild();
}
function bindRebuild(){
  const rb=$("#rebuild");if(rb)rb.onclick=async()=>{rb.disabled=true;try{await api("/api/p/"+S.pid+"/build",{method:"POST",body:{}});await poll(false);renderSummary(S.sum)}catch(e){alert(e.message)}rb.disabled=false};
}
init().catch(e=>{document.body.insertAdjacentHTML("afterbegin",'<div class="note bad">שגיאת טעינה: '+esc(e.message)+'</div>')});
</script>
</body>
</html>
"""


# ======================================================================
# 9. מחולל קבצי דוגמה (טקסט מקורי, ללא תוכן מוגן בזכויות יוצרים)
# ======================================================================
def png_bytes(width: int, height: int, rgb: Tuple[int, int, int]) -> bytes:
    import struct
    import zlib
    row = b"\x00" + bytes(rgb) * width
    raw = row * height

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


SAMPLE_CHAPTERS = [
    ("The Harbor at Dawn", [
        "Elena Marlowe arrived in Port Lantern before the fishing boats had left the quay. The town was quiet, and the air smelled of salt and cold iron. She carried one suitcase and a letter that she had read so many times the folds were turning soft.",
        "The letter was from her uncle, who owned the old lighthouse on Harbor Street. He had written that the lamp would not light, that the keeper had gone, and that he needed someone who could read the ledgers. Nobody in the family had expected her to say yes.",
        "At the gate she met a man named Tobias Reed, who repaired nets and knew every rumor in the harbor. He studied her for a long moment and then said that the lighthouse had not been lit for nineteen winters.",
        "She climbed the stairs slowly. Each landing held a window, and each window showed the same gray water in a slightly different light. By the last landing her legs were trembling, but she did not stop.",
        "In the lamp room she found a brass wheel, a stack of dusty ledgers and a small wooden box. Inside the box was a key, and under the key a note that read only: begin with the third ledger.",
    ]),
    ("The Third Ledger", [
        "The third ledger was different from the others. Its pages were not filled with tide tables but with names, dates and short remarks written in a careful hand. Elena counted forty-two entries before the light failed.",
        "Tobias Reed brought her soup that evening and did not ask what she had found. He only said that the harbor remembered everything, and that some of its memories were better left on the shelf.",
        "She read until midnight. One name appeared again and again: Captain Isidore Vance, who had sailed out of Port Lantern in the spring of 1911 and never returned. Every remark beside his name ended with the same three words.",
        "By morning she had made her decision. She would light the lamp, and she would find out why nobody in Port Lantern wanted it lit.",
    ]),
    ("What the Lamp Showed", [
        "On the nineteenth night the lamp caught. A pale beam swept across the harbor, touched the breakwater, and rested on a boat that had been drifting there unnoticed for as long as anyone could remember.",
        "The boat carried a single lantern and a locked chest. Elena rowed out with Tobias, and together they hauled the chest ashore while the whole town watched from the quay in silence.",
        "Inside the chest lay Captain Vance's last log. It told of a storm, a promise, and a debt that Port Lantern had agreed to forget. When Elena finished reading aloud, the harbor bell began to ring by itself.",
    ]),
]


def sample_list_items() -> List[str]:
    return ["Check the tide tables each morning.", "Trim the wick before sunset.", "Keep the ledgers dry."]


def make_sample_epub(path: str, with_rtl_book: bool = False) -> str:
    """יוצר EPUB 3 לדוגמה: כותרות, פסקאות, הדגשות, קישורים, הערות שוליים, רשימות, ציטוט,
    תמונות, CSS עם יישור שמאלי, גופן, תוכן עניינים (nav + ncx) וכריכה."""
    ns = 'xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"'

    def page(title: str, body: str, lang: str = "en") -> str:
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n<html %s xml:lang="%s" lang="%s">'
                '<head><title>%s</title><link rel="stylesheet" type="text/css" href="styles/style.css"/></head>'
                '<body>%s</body></html>') % (ns, lang, lang, title, body)

    files: Dict[str, bytes] = {}
    chapter_html: List[Tuple[str, str, str]] = []
    for index, (title, paragraphs) in enumerate(SAMPLE_CHAPTERS):
        number = index + 1
        parts = ['<h1 id="ch%d">%s</h1>' % (number, title)]
        for p_index, text in enumerate(paragraphs):
            marked = text
            if number == 1 and p_index == 0:
                marked = text.replace("Port Lantern", "<b>Port Lantern</b>", 1).replace("a letter", "<i>a letter</i>", 1)
                marked = marked + '<a epub:type="noteref" href="notes.xhtml#n1" id="r1"><sup>1</sup></a>'
            if number == 1 and p_index == 1:
                marked = marked.replace("the ledgers", '<a href="ch02.xhtml#third">the ledgers</a>', 1)
            if number == 2 and p_index == 0:
                parts.append('<h2 id="third">Notes on the ledger</h2>')
            if number == 1 and p_index == 3:
                marked = marked.replace("Each landing", "Each landing<br/>").replace("gray water", "gray <i>water</i>")
            parts.append("<p>%s</p>" % marked)
        if number == 1:
            parts.append("<blockquote><p>The harbor remembers everything, and forgives very little.</p></blockquote>")
            parts.append("<ul>" + "".join("<li>%s</li>" % t for t in sample_list_items()) +
                         "<li>Nested rules:<ul><li>Never leave the lamp room unlocked.</li></ul></li></ul>")
            parts.append('<figure><img src="images/pic.png" alt="Lamp"/><figcaption>The lamp room at dusk.</figcaption></figure>')
            parts.append("<hr/>")
        if number == 3:
            parts.append("<p>Price of the chest: 1,250 coins, 3 keys.</p>")
        name = "ch%02d.xhtml" % number
        chapter_html.append((name, title, page(title, "".join(parts))))
    for name, title, content in chapter_html:
        files["OEBPS/" + name] = content.encode("utf-8")
    notes_body = ('<h2>Notes</h2><aside epub:type="footnote" id="n1"><p>The old quay was rebuilt in 1923. '
                  '<a href="ch01.xhtml#r1">Back</a></p></aside>')
    files["OEBPS/notes.xhtml"] = page("Notes", notes_body).encode("utf-8")
    cover = '<div class="cover"><img src="images/cover.png" alt="Cover"/></div>'
    files["OEBPS/cover.xhtml"] = page("Cover", cover).encode("utf-8")
    nav_items = "".join('<li><a href="%s">%s</a></li>' % (n, t) for n, t, c in chapter_html)
    nav = ('<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>%s</ol></nav>' % nav_items)
    files["OEBPS/nav.xhtml"] = page("Contents", nav).encode("utf-8")
    ncx_points = ""
    for i, (n, t, c) in enumerate(chapter_html):
        ncx_points = ncx_points + ('<navPoint id="np%d" playOrder="%d"><navLabel><text>%s</text></navLabel>'
                                   '<content src="%s"/></navPoint>') % (i + 1, i + 1, t, n)
    files["OEBPS/toc.ncx"] = ('<?xml version="1.0" encoding="UTF-8"?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
                              '<head><meta name="dtb:uid" content="urn:uuid:sample-0001"/></head>'
                              '<docTitle><text>The Lamp of Port Lantern</text></docTitle><navMap>%s</navMap></ncx>' % ncx_points).encode("utf-8")
    files["OEBPS/styles/style.css"] = (
        "body{margin-left:5%;margin-right:5%;font-family:Georgia,serif}\n"
        "p{text-align:left;margin:0 0 0 0;text-indent:1.2em;margin-left:0.5em}\n"
        "h1{text-align:center;font-size:1.6em}\nblockquote{margin:1em 2em 1em 3em;border-left:3px solid #999;padding-left:1em}\n"
        ".cover{text-align:center}\n").encode("utf-8")
    files["OEBPS/images/cover.png"] = png_bytes(60, 90, (30, 60, 120))
    files["OEBPS/images/pic.png"] = png_bytes(80, 50, (200, 160, 40))
    files["OEBPS/fonts/dummy.woff2"] = b"wOF2" + bytes(range(64))
    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
                '<item id="css" href="styles/style.css" media-type="text/css"/>',
                '<item id="cover-img" href="images/cover.png" media-type="image/png" properties="cover-image"/>',
                '<item id="pic" href="images/pic.png" media-type="image/png"/>',
                '<item id="font" href="fonts/dummy.woff2" media-type="font/woff2"/>',
                '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
                '<item id="notes" href="notes.xhtml" media-type="application/xhtml+xml"/>']
    spine = ['<itemref idref="cover"/>']
    for i, (n, t, c) in enumerate(chapter_html):
        manifest.append('<item id="c%d" href="%s" media-type="application/xhtml+xml"/>' % (i + 1, n))
        spine.append('<itemref idref="c%d"/>' % (i + 1))
    spine.append('<itemref idref="notes"/>')
    opf = ('<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:uuid:sample-0001</dc:identifier>'
           '<dc:title>The Lamp of Port Lantern</dc:title><dc:creator>A. Sample</dc:creator><dc:language>en</dc:language>'
           '<meta property="dcterms:modified">2024-01-01T00:00:00Z</meta><meta name="cover" content="cover-img"/></metadata>'
           '<manifest>%s</manifest><spine toc="ncx">%s</spine></package>') % ("".join(manifest), "".join(spine))
    files["OEBPS/content.opf"] = opf.encode("utf-8")
    files["META-INF/container.xml"] = ('<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                                       '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
                                       '</rootfiles></container>').encode("utf-8")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with zipfile.ZipFile(path, "w") as out:
        out.writestr("mimetype", b"application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name, data in files.items():
            out.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
    return path


def make_sample_pdf(path: str) -> str:
    """PDF עם שכבת טקסט: כותרות בגדלים שונים, פסקאות, רשימה, כותרת עליונה ומספרי עמודים."""
    from reportlab.lib.pagesizes import A5
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    title_style = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=26, leading=32, spaceAfter=20)
    h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18, leading=22, spaceBefore=6, spaceAfter=12)
    body = ParagraphStyle("b", fontName="Times-Roman", fontSize=11, leading=15, spaceAfter=6, firstLineIndent=0)
    bullet = ParagraphStyle("l", fontName="Times-Roman", fontSize=11, leading=15, leftIndent=18)
    story: List[Any] = [Paragraph("The Lamp of Port Lantern", title_style), Paragraph("A short sample novel", body), PageBreak()]
    for chapter_index, (title, paragraphs) in enumerate(SAMPLE_CHAPTERS):
        story.append(Paragraph(title, h1))
        for text in paragraphs:
            story.append(Paragraph(text + " " + text.split(". ")[0] + ".", body))
        if chapter_index == 0:
            for item in sample_list_items():
                story.append(Paragraph("\u2022 " + item, bullet))
        story.append(PageBreak())

    def decorate(canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(36, A5[1] - 24, "The Lamp of Port Lantern")
        canvas.drawCentredString(A5[0] / 2.0, 20, str(doc.page))
        canvas.restoreState()
    doc = SimpleDocTemplate(path, pagesize=A5, leftMargin=36, rightMargin=36, topMargin=48, bottomMargin=48)
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return path


def make_scanned_pdf(path: str) -> str:
    """PDF ללא שכבת טקסט (תמונה בלבד) לבדיקת הודעת השגיאה."""
    fitz = import_pymupdf()
    document = fitz.open()
    for _ in range(2):
        page = document.new_page()
        page.insert_image(fitz.Rect(50, 50, 300, 300), stream=png_bytes(40, 40, (90, 90, 90)))
    document.save(path)
    document.close()
    return path


def make_sample_mobi(epub_path: str, mobi_path: str) -> str:
    exe = find_ebook_convert()
    if exe is None:
        raise BookError("conversion_failure", "Calibre לא זמין ליצירת MOBI לדוגמה")
    completed = subprocess.run([exe, epub_path, mobi_path], capture_output=True, text=True, timeout=600)
    if completed.returncode != 0 or not os.path.isfile(mobi_path):
        raise BookError("conversion_failure", "יצירת MOBI נכשלה: %s" % completed.stderr[-300:])
    return mobi_path


# ======================================================================
# 25. בדיקות אוטומטיות (python book_ai.py test)
# ======================================================================
def run_tests(verbose: bool = False) -> int:
    import http.client
    import unittest

    sandbox = tempfile.mkdtemp(prefix="book_ai_test_")
    globals()["HOME_DIR"] = sandbox
    globals()["PROJECTS_DIR"] = os.path.join(sandbox, "projects")
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    samples = os.path.join(sandbox, "samples")
    os.makedirs(samples, exist_ok=True)
    epub_path = make_sample_epub(os.path.join(samples, "sample.epub"))
    has_pdf = True
    try:
        import_pymupdf()
        import reportlab  # noqa: F401
    except (BookError, ImportError):
        has_pdf = False
    pdf_path = make_sample_pdf(os.path.join(samples, "sample.pdf")) if has_pdf else ""
    scanned_path = make_scanned_pdf(os.path.join(samples, "scanned.pdf")) if has_pdf else ""
    mobi_path = ""
    if find_ebook_convert() is not None:
        mobi_path = make_sample_mobi(epub_path, os.path.join(samples, "sample.mobi"))

    def new_project(path: str, **overrides: Any) -> Tuple[AppState, Project]:
        state = AppState()
        name = os.path.basename(path)
        fmt = sniff_format(path, name)
        project = Project.create(name, os.path.getsize(path), fmt)
        state.projects[project.id] = project
        temp = os.path.join(sandbox, "up_" + uuid.uuid4().hex)
        shutil.copy(path, temp)
        analyze_project(state, project, temp)
        settings = dict(default_settings())
        settings.update({"provider": "mock", "model": "mock-1", "chunk_chars": 800, "concurrency": 2, "tgt_lang": "he"})
        settings.update(overrides)
        project.settings = settings
        return state, project

    def run_job(project: Project, key: str = "", wait: float = 120.0) -> Job:
        project.set_status("ready")
        job = Job(project, dict(project.settings, api_key=key))
        job.start()
        job.thread.join(wait)
        return job

    class Tests(unittest.TestCase):
        # ---- הלוך־חזור ----
        def test_roundtrip_identity(self) -> None:
            pkg = EpubPackage(epub_path)
            model = pkg.extract_model()
            for unit in model["units"]:
                unit["status"] = "done"
                unit["out"] = unit["tagged"]
            out_path = os.path.join(sandbox, "identity.epub")
            pkg.write_output(out_path, model["units"], {"mode": "replace", "src_lang": "en", "tgt_lang": "en"})
            out = EpubPackage(out_path)
            out_model = out.extract_model()
            self.assertEqual([(u["type"], u["level"], u["tagged"]) for u in model["units"]],
                             [(u["type"], u["level"], u["tagged"]) for u in out_model["units"]])
            report = verify_epub(pkg, out_path, "replace")
            self.assertTrue(report["ok"], report["checks"])
            for name in pkg.names:
                if name.endswith((".png", ".woff2", ".css")):
                    self.assertEqual(pkg.read(name), out.read(name))

        # ---- תגיות עיצוב ----
        def test_inline_tags_survive_reordering(self) -> None:
            xml = ('<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">Hello <b>big <i>old</i></b> '
                   '<a href="x.html#t" class="k">link</a> world<a epub:type="noteref" href="n.xhtml#1"><sup>1</sup></a><br/>end &amp; more</p>')
            root = etree.fromstring(xml.encode("utf-8"))
            items = element_items(root)
            runs = split_runs(items)
            tagged, tags = encode_run(items[runs[0][0]:runs[0][1]])
            self.assertIn("<b1>", tagged)
            self.assertNotIn("href", tagged)
            reordered = "סוף &amp; עוד<br5/> <a3>קישור</a3> <b1><i2>ישן</i2> גדול</b1> עולם<n4/>"
            self.assertEqual(validate_tags(tagged, reordered, tags), [])
            new_items = decode_run(reordered, tags)
            rebuild_block(root, new_items)
            text = etree.tostring(root, encoding="unicode")
            self.assertIn('href="x.html#t"', text)
            self.assertIn('class="k"', text)
            self.assertIn('epub:type="noteref"', text)
            self.assertIn("<sup>1</sup>", text)
            self.assertIn("<br/>", text)
            self.assertIn("<i>ישן</i>", text)
            self.assertIn("&amp;", text)

        def test_tag_validation_rejects_damage(self) -> None:
            root = etree.fromstring(b"<p>a <b>b</b> c<br/></p>")
            tagged, tags = encode_run(element_items(root))
            self.assertEqual(tagged, "a <b1>b</b1> c<br2/>")
            self.assertTrue(len(validate_tags(tagged, "א ב ג<br2/>", tags)) > 0)
            self.assertTrue(len(validate_tags(tagged, "א <b1>ב</b1> ג<br2/><br2/>", tags)) > 0)
            self.assertTrue(len(validate_tags(tagged, "א </b1>ב<b1> ג<br2/>", tags)) > 0)
            self.assertTrue(len(validate_tags(tagged, "א <b>ב</b> ג<br2/>", tags)) > 0)
            self.assertTrue(len(validate_tags(tagged, "א <b1>ב</b1> <i9>x</i9> ג<br2/>", tags)) > 0)
            self.assertEqual(validate_tags(tagged, "א <b1>ב</b1> ג<br2/>", tags), [])

        # ---- פרוטוקול ----
        def test_structure_rejection(self) -> None:
            expected = [{"id": "a", "type": "HEADING", "level": 2, "text": "x"}, {"id": "b", "type": "PARAGRAPH", "level": 0, "text": "y"},
                        {"id": "c", "type": "PARAGRAPH", "level": 0, "text": "z"}]
            good = [dict(e) for e in expected]
            self.assertEqual(validate_structure(expected, good, []), ([], {}))
            merged = [good[0], dict(good[1], text="y z")]
            self.assertTrue(len(validate_structure(expected, merged, [])[0]) > 0)
            split = good + [{"id": "c2", "type": "PARAGRAPH", "level": 0, "text": "extra"}]
            self.assertTrue(len(validate_structure(expected, split, [])[0]) > 0)
            skipped = [good[0], good[2]]
            self.assertTrue(len(validate_structure(expected, skipped, [])[0]) > 0)
            reordered = [good[1], good[0], good[2]]
            self.assertTrue(len(validate_structure(expected, reordered, [])[0]) > 0)
            retyped = [dict(good[0], type="PARAGRAPH"), good[1], good[2]]
            fatal, per_item = validate_structure(expected, retyped, [])
            self.assertEqual(fatal, [])
            self.assertIn("a", per_item)
            relevel = [dict(good[0], level=3), good[1], good[2]]
            self.assertIn("a", validate_structure(expected, relevel, [])[1])
            self.assertTrue(len(validate_structure(expected, good, ["Sure! here you go"])[0]) > 0)

        def test_response_parsers(self) -> None:
            items, extra = parse_list_response("```\n[id=c1_e1 | HEADING level=2] כותרת\n[id=c1_e2 | PARAGRAPH] טקסט <b1>ב</b1>\n```")
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]["level"], 2)
            self.assertEqual(extra, [])
            items, extra = parse_json_response('```json\n{"items":[{"id":"x","type":"PARAGRAPH","level":null,"text":"t"}]}\n```')
            self.assertEqual(items[0]["id"], "x")
            with self.assertRaises(BookError):
                parse_json_response("not json at all")

        # ---- חלוקה למקטעים ----
        def test_chunking_order_and_integrity(self) -> None:
            pkg = EpubPackage(epub_path)
            model = pkg.extract_model()
            units = [u for u in model["units"] if u["scope"] == "content"]
            chunks = build_chunks(units, dict(default_settings(), chunk_chars=500))
            order = []
            for chunk in chunks:
                chapters = set(g["unit"]["ch"] for g in chunk["groups"])
                self.assertEqual(len(chapters), 1)
                for group in chunk["groups"]:
                    order.append(group["unit"]["id"])
            self.assertEqual(order, [u["id"] for u in units])
            long_unit = dict(units[0], id="c99_e001", tagged="; ".join(["Sentence number %d is here." % i for i in range(120)]), tags=[])
            long_unit["tagged"] = " ".join("Sentence number %d is here." % i for i in range(120))
            parts = split_tagged_parts(long_unit["tagged"], 700)
            self.assertTrue(len(parts) > 3)
            self.assertEqual(" ".join(p.strip() for p in parts), long_unit["tagged"])
            tagged = "<b1>" + " ".join("Bold sentence %d." % i for i in range(80)) + "</b1> tail. Another one."
            for part in split_tagged_parts(tagged, 300):
                depth = 0
                for token in tokenize_tagged(part):
                    if token[0] == "open":
                        depth = depth + 1
                    elif token[0] == "close":
                        depth = depth - 1
                self.assertIn(depth, (0,))
                self.assertFalse(part.startswith("</b1>") and "<b1>" not in part and depth != 0)

        # ---- נסיגה מעריכית, שחזור והמשך ----
        def test_backoff_then_success(self) -> None:
            state, project = new_project(epub_path, mock={"fail_first": 2, "prefix": "[T] "})
            job = run_job(project)
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            retries = [e for e in project.log.entries if "מנסה שוב" in e["msg"]]
            self.assertTrue(len(retries) >= 2)
            self.assertEqual(project.counts()["pending"], 0)

        def test_resume_does_not_resend_completed(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"delay": 0.15})
            project.set_status("ready")
            job = Job(project, dict(project.settings, api_key=""))
            job.start()
            deadline = time.time() + 30
            while time.time() < deadline and project.counts()["done"] < 5:
                time.sleep(0.05)
            job.stop()
            job.thread.join(30)
            self.assertEqual(project.meta["status"], "stopped")
            counts = project.counts()
            self.assertTrue(0 < counts["done"] < counts["total"])
            done_before = set(u["id"] for u in project.units if u["status"] in OK_STATUSES)
            # סימולציית קריסה: טעינה מחדש מהדיסק
            project.flush()
            reloaded = Project.load(project.id)
            self.assertEqual(set(u["id"] for u in reloaded.units if u["status"] in OK_STATUSES), done_before)
            reloaded.settings = dict(project.settings, mock={"delay": 0.0})
            job2 = run_job(reloaded)
            self.assertEqual(reloaded.meta["status"], "completed", reloaded.meta.get("error"))
            resent = set()
            for ids in reloaded.settings["mock"]["_state"]["ids"]:
                for ident in ids:
                    resent.add(ident.split("#")[0])
            self.assertTrue(resent.isdisjoint(done_before), resent & done_before)

        def test_crash_recovery_status(self) -> None:
            state, project = new_project(epub_path)
            project.set_status("running")
            project.flush()
            self.assertEqual(Project.load(project.id).meta["status"], "paused")

        # ---- תיקון אוטומטי ----
        def test_self_healing_failures(self) -> None:
            for behavior in ("drop_first", "merge_first", "retype_first", "bad_tags_first", "explain_first"):
                state, project = new_project(epub_path, concurrency=1, mock={behavior: True})
                run_job(project)
                self.assertEqual(project.meta["status"], "completed", (behavior, project.meta.get("error")))
                counts = project.counts()
                self.assertEqual(counts["failed"] + counts["flagged"], 0, behavior)

        def test_persistent_tag_loss_flags_and_keeps_original(self) -> None:
            state, project = new_project(epub_path, mock={"always_bad_tags": True})
            run_job(project)
            flagged = [u for u in project.units if u["status"] == "flagged"]
            self.assertTrue(len(flagged) > 0)
            for unit in flagged:
                self.assertIsNone(unit["out"])
            out_path = os.path.join(project.output_dir, project.meta["outputs"][0]["name"])
            out = EpubPackage(out_path)
            text = b"".join(out.read(p) for p, r in out.document_files()).decode("utf-8")
            self.assertIn("Elena Marlowe arrived in", text)
            state2, project2 = new_project(epub_path, mock={"always_bad_tags": True}, on_format_failure="accept_plain")
            run_job(project2)
            warned = [u for u in project2.units if any("אבד" in w for w in u["warn"])]
            self.assertTrue(len(warned) > 0)

        def test_manual_unit_save_validates_tags(self) -> None:
            state, project = new_project(epub_path, mock={"always_bad_tags": True})
            run_job(project)
            unit = [u for u in project.units if u["status"] == "flagged"][0]
            self.assertTrue(len(validate_tags(unit["tagged"], strip_tags(unit["tagged"]), unit["tags"])) > 0)
            self.assertEqual(validate_tags(unit["tagged"], "[ידני] " + unit["tagged"], unit["tags"]), [])

        # ---- מילון וזיכרון ----
        def test_glossary_and_memory(self) -> None:
            state, project = new_project(epub_path, concurrency=1)
            project.glossary = [{"source": "Elena Marlowe", "target": "אלנה מרלו", "locked": True},
                                {"source": "Zebra Unrelated", "target": "זברה", "locked": False}]
            run_job(project)
            prompts = " ".join(project.settings["mock"]["_state"]["prompts"])
            self.assertIn("Elena Marlowe => אלנה מרלו", prompts)
            self.assertNotIn("Zebra Unrelated", prompts)
            calls = project.settings["mock"]["_state"]["calls"]
            for unit in project.units:
                unit["status"] = "pending"
                unit["out"] = None
            job = run_job(project)
            self.assertEqual(project.settings["mock"]["_state"]["calls"], calls)
            self.assertTrue(all("זיכרון" in " ".join(u["warn"]) for u in project.units))
            suggested = suggest_glossary_terms(EpubPackage(epub_path).extract_model()["units"], minimum=2)
            names = [s["source"] for s in suggested]
            self.assertIn("Tobias Reed", names)

        # ---- סודות ----
        def test_keys_never_leak(self) -> None:
            key = "sk-TESTSECRETKEY1234567890abcdef"
            state, project = new_project(epub_path, provider="mock", mock={"leak_key": True}, api_retries=0)
            project.set_status("ready")
            job = Job(project, dict(project.settings, api_key=key))
            job.start()
            job.thread.join(60)
            project.flush()
            self.assertTrue(len(project.log.entries) > 0)
            blob = json.dumps(project.log.entries, ensure_ascii=False)
            for root, dirs, files in os.walk(project.dir):
                for name in files:
                    with open(os.path.join(root, name), "rb") as handle:
                        blob = blob + handle.read().decode("utf-8", errors="ignore")
            self.assertNotIn(key, blob)
            self.assertNotIn("TESTSECRETKEY", blob)
            self.assertIn("***", blob)

        def test_atomic_write_survives_crash(self) -> None:
            path = os.path.join(sandbox, "state.json")
            atomic_write_json(path, {"v": 1})
            original_replace = os.replace

            def boom(src: str, dst: str) -> None:
                raise OSError("simulated crash")
            os.replace = boom  # type: ignore[assignment]
            try:
                with self.assertRaises(OSError):
                    atomic_write_json(path, {"v": 2})
            finally:
                os.replace = original_replace  # type: ignore[assignment]
            self.assertEqual(read_json(path), {"v": 1})
            self.assertEqual([n for n in os.listdir(sandbox) if n.startswith(".tmp_")], [])

        # ---- אבטחת קבצים ----
        def test_zip_slip_and_bomb_rejected(self) -> None:
            evil = os.path.join(sandbox, "evil.epub")
            with zipfile.ZipFile(evil, "w") as z:
                z.writestr("mimetype", "application/epub+zip")
                z.writestr("../evil.txt", "x")
            with self.assertRaises(BookError):
                EpubPackage(evil)
            bomb = os.path.join(sandbox, "bomb.epub")
            with zipfile.ZipFile(bomb, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr("mimetype", "application/epub+zip")
                z.writestr("big.txt", b"\0" * (8 * 1024 * 1024))
            with self.assertRaises(BookError):
                EpubPackage(bomb)
            junk = os.path.join(sandbox, "junk.bin")
            with open(junk, "wb") as handle:
                handle.write(b"hello world" * 20)
            with self.assertRaises(BookError):
                sniff_format(junk, "junk.epub")

        # ---- זרימות מלאות לשלושת הפורמטים ----
        def check_full_translation(self, project: Project, bilingual: bool = False) -> None:
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            final = project.meta["final"]
            for entry in final["files"]:
                failing = [c for c in entry["verify"]["checks"] if c["ok"] is False]
                self.assertEqual(failing, [], failing)

        def test_full_flow_epub_rtl(self) -> None:
            state, project = new_project(epub_path, mode="replace")
            run_job(project)
            self.check_full_translation(project)
            out = EpubPackage(os.path.join(project.output_dir, project.meta["outputs"][0]["name"]))
            opf = out.read(out.opf_path).decode("utf-8")
            self.assertIn('page-progression-direction="rtl"', opf)
            self.assertEqual(out.language, "he")
            first = out.read(out.document_files()[1][0]).decode("utf-8")
            self.assertIn('dir="rtl"', first)
            self.assertIn('lang="he"', first)
            css = out.read("OEBPS/styles/style.css").decode("utf-8")
            self.assertIn("text-align:right", css)
            self.assertIn("text-align:center", css)
            self.assertEqual(out.title, "[T] The Lamp of Port Lantern")
            self.assertIn("[T] ", first)

        def test_bilingual_unique_ids_and_dirs(self) -> None:
            state, project = new_project(epub_path, mode="both")
            run_job(project)
            self.check_full_translation(project)
            names = [o["name"] for o in project.meta["outputs"]]
            self.assertEqual(len(names), 2)
            bilingual = EpubPackage(os.path.join(project.output_dir, [n for n in names if "bilingual" in n][0]))
            for path, role in bilingual.document_files():
                ids = re.findall(r'\bid="([^"]+)"', bilingual.read(path).decode("utf-8"))
                self.assertEqual(len(ids), len(set(ids)), path)
            text = bilingual.read("OEBPS/ch01.xhtml").decode("utf-8")
            self.assertIn('class="bai-tr"', text)
            self.assertIn('dir="rtl"', text)

        def test_full_flow_pdf(self) -> None:
            if not has_pdf:
                self.skipTest("PyMuPDF/reportlab לא זמינים")
            state, project = new_project(pdf_path)
            self.assertEqual(project.meta["status"], "awaiting_confirmation", project.meta.get("error"))
            report = project.meta["pdf_report"]
            self.assertTrue(report["headings"] >= 3 and report["paragraphs"] >= 10)
            self.assertTrue(report["score"] >= 70, report["score"])
            self.assertTrue(len(report["warnings"]) > 0)
            run_job(project)
            self.check_full_translation(project)

        def test_scanned_pdf_error(self) -> None:
            if not has_pdf:
                self.skipTest("PyMuPDF לא זמין")
            state, project = new_project(scanned_path)
            self.assertEqual(project.meta["status"], "error")
            self.assertEqual(project.meta["error"]["kind"], "pdf_no_text")

        def test_full_flow_mobi(self) -> None:
            if mobi_path == "":
                self.skipTest("Calibre לא זמין ליצירת MOBI לדוגמה")
            state, project = new_project(mobi_path)
            self.assertEqual(project.meta["status"], "ready", project.meta.get("error"))
            run_job(project)
            self.check_full_translation(project)

        def test_mobi_library_fallback(self) -> None:
            if mobi_path == "":
                self.skipTest("אין MOBI לדוגמה")
            os.environ["BOOK_AI_NO_CALIBRE"] = "1"
            try:
                state, project = new_project(mobi_path)
                self.assertEqual(project.meta["status"], "ready", project.meta.get("error"))
                self.assertEqual(project.meta["conversion"]["tool"], "mobi-library")
                run_job(project)
                self.check_full_translation(project)
            finally:
                del os.environ["BOOK_AI_NO_CALIBRE"]

        def test_mobi_without_any_tool_gives_clear_error(self) -> None:
            if mobi_path == "":
                self.skipTest("אין MOBI לדוגמה")
            import builtins
            real_import = builtins.__import__

            def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
                if name == "mobi":
                    raise ImportError("blocked")
                return real_import(name, *args, **kwargs)
            os.environ["BOOK_AI_NO_CALIBRE"] = "1"
            builtins.__import__ = fake_import
            try:
                state, project = new_project(mobi_path)
            finally:
                builtins.__import__ = real_import
                del os.environ["BOOK_AI_NO_CALIBRE"]
            self.assertEqual(project.meta["status"], "error")
            self.assertEqual(project.meta["error"]["kind"], "conversion_failure")
            self.assertIn("Calibre", project.meta["error"]["message"])

        # ---- עימוד ועיצוב (ללא מודל) ----
        def test_relayout_without_model(self) -> None:
            layout = dict(default_settings()["layout"], font_size="120", para_style="spacing", text_align="justify", theme="sepia")
            state, project = new_project(epub_path, goal="relayout", layout=layout, provider="gemini")
            job = run_job(project)
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            out = EpubPackage(os.path.join(project.output_dir, project.meta["outputs"][0]["name"]))
            self.assertIn("OEBPS/bai-style.css", out.names)
            self.assertIn("bai-style.css", out.read("OEBPS/ch01.xhtml").decode("utf-8"))
            self.assertIn("120%", out.read("OEBPS/bai-style.css").decode("utf-8"))
            self.assertEqual(project.meta["usage"]["requests"], 0)

        def test_css_mirror(self) -> None:
            css = "p{text-align:left;margin-left:2em;padding:1px 2px 3px 4px;float:right}div{border-left:1px solid;left:0}h1{text-align:center}"
            mirrored = mirror_css(css)
            self.assertIn("text-align:right", mirrored)
            self.assertIn("margin-right:2em", mirrored)
            self.assertIn("padding:1px 4px 3px 2px", mirrored)
            self.assertIn("float:left", mirrored)
            self.assertIn("border-right:1px solid", mirrored)
            self.assertIn("text-align:center", mirrored)
            self.assertEqual(mirror_css(mirrored), css)


        # ---- שכבת הספקים מול שרת מזויף (צורת הבקשות והתשובות של כל ספק) ----
        def test_provider_wire_formats_with_fake_server(self) -> None:
            from http.server import BaseHTTPRequestHandler as BH
            seen: List[Dict[str, Any]] = []
            counters = {"throttle": 0}
            engine = MockProvider({"mock": {"prefix": "[W] "}})

            class Fake(BH):
                def log_message(self, *a: Any) -> None:
                    return

                def reply(self, status: int, body: Dict[str, Any], extra: Optional[Dict[str, str]] = None) -> None:
                    data = json.dumps(body).encode()
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(data)))
                    for k, v in (extra or {}).items():
                        self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(data)

                def do_GET(self) -> None:
                    seen.append({"path": self.path, "headers": dict(self.headers)})
                    if "/v1/models" in self.path and "anthropic-version" in self.headers:
                        return self.reply(200, {"data": [{"id": "claude-x"}]})
                    if self.path.startswith("/v1/models") or self.path.startswith("/oa/models"):
                        auth = self.headers.get("Authorization", "")
                        if auth != "Bearer goodkey":
                            return self.reply(401, {"error": {"message": "bad key"}})
                        return self.reply(200, {"data": [{"id": "gpt-x"}, {"id": "gpt-y"}]})
                    if self.path.startswith("/v1beta/models"):
                        return self.reply(200, {"models": [{"name": "models/gem-x", "supportedGenerationMethods": ["generateContent"]}]})
                    if self.path.startswith("/api/tags"):
                        return self.reply(200, {"models": [{"name": "llama-x"}]})
                    self.reply(404, {"error": {"message": "nope"}})

                def do_POST(self) -> None:
                    length = int(self.headers.get("Content-Length") or 0)
                    body = json.loads(self.rfile.read(length).decode())
                    seen.append({"path": self.path, "headers": dict(self.headers), "body": body})
                    if "/chat/completions" in self.path:
                        if self.headers.get("Authorization") != "Bearer goodkey":
                            return self.reply(401, {"error": {"message": "bad key"}})
                        counters["throttle"] = counters["throttle"] + 1
                        if counters["throttle"] == 2:
                            return self.reply(429, {"error": {"message": "slow down"}}, {"Retry-After": "0"})
                        system = body["messages"][0]["content"]
                        user = body["messages"][1]["content"]
                        text, usage = engine.complete(system, user, "single JSON object" in system)
                        return self.reply(200, {"choices": [{"message": {"content": text}, "finish_reason": "stop"}],
                                                "usage": {"prompt_tokens": usage["in"], "completion_tokens": usage["out"]}})
                    if self.path.endswith("/messages"):
                        text, usage = engine.complete(body["system"], body["messages"][0]["content"], False)
                        return self.reply(200, {"content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
                                                "usage": {"input_tokens": usage["in"], "output_tokens": usage["out"]}})
                    if ":generateContent" in self.path:
                        text, usage = engine.complete(body["systemInstruction"]["parts"][0]["text"], body["contents"][0]["parts"][0]["text"],
                                                      body["generationConfig"].get("responseMimeType") == "application/json")
                        return self.reply(200, {"candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": "STOP"}],
                                                "usageMetadata": {"promptTokenCount": usage["in"], "candidatesTokenCount": usage["out"]}})
                    if self.path.endswith("/api/chat"):
                        text, usage = engine.complete(body["messages"][0]["content"], body["messages"][1]["content"], body.get("format") == "json")
                        return self.reply(200, {"message": {"content": text}, "done_reason": "stop", "prompt_eval_count": usage["in"], "eval_count": usage["out"]})
                    self.reply(404, {"error": {"message": "nope"}})

            fake = ThreadingHTTPServer(("127.0.0.1", 0), Fake)
            base = "http://127.0.0.1:%d" % fake.server_address[1]
            threading.Thread(target=fake.serve_forever, daemon=True).start()
            try:
                bad = make_provider({"provider": "custom", "base_url": base + "/v1", "api_key": "wrongkey", "model": "gpt-x"})
                with self.assertRaises(BookError) as caught:
                    bad.list_models()
                self.assertEqual(caught.exception.kind, "invalid_key")
                cases = [("custom", base + "/v1", "goodkey", "gpt-x"), ("openai", base + "/v1", "goodkey", "gpt-x"),
                         ("openrouter", base + "/v1", "goodkey", "gpt-x"), ("anthropic", base + "/v1", "ant-key-12345", "claude-x"),
                         ("gemini", base + "/v1beta", "gem-key-12345", "gem-x"), ("ollama", base, "", "llama-x")]
                for provider_id, base_url, key, model in cases:
                    counters["throttle"] = 0
                    state, project = new_project(epub_path, provider=provider_id, model=model, base_url=base_url, concurrency=1, mock={})
                    job = run_job(project, key=key)
                    self.assertEqual(project.meta["status"], "completed", (provider_id, project.meta.get("error"), [e["msg"] for e in project.log.entries][-4:]))
                    self.assertEqual(project.counts()["pending"], 0, provider_id)
                    self.assertEqual(project.counts()["failed"] + project.counts()["flagged"], 0, provider_id)
                    self.assertTrue(project.meta["usage"]["tokens_in"] > 0, provider_id)
                posts = [s for s in seen if "body" in s]
                gem = [s for s in posts if ":generateContent" in s["path"]][0]
                self.assertIn("x-goog-api-key", {k.lower() for k in gem["headers"]})
                self.assertNotIn("gem-key", gem["path"])
                ant = [s for s in posts if s["path"].endswith("/messages")][0]
                self.assertEqual({k.lower(): v for k, v in ant["headers"].items()}.get("anthropic-version"), "2023-06-01")
                self.assertIn("x-api-key", {k.lower() for k in ant["headers"]})
                self.assertTrue(len(make_provider({"provider": "ollama", "base_url": base, "model": "llama-x"}).list_models()) == 1)
            finally:
                fake.shutdown()
                fake.server_close()

        # ---- שרת מקומי ----
        def test_http_security_and_upload(self) -> None:
            state = AppState(0)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
            port = server.server_address[1]
            state.port = port
            server.RequestHandlerClass = make_handler(state)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                def call(method: str, path: str, headers: Optional[Dict[str, str]] = None, body: Optional[bytes] = None, host: Optional[str] = None) -> Tuple[int, bytes]:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
                    hdrs = dict(headers or {})
                    conn.putrequest(method, path, skip_host=True)
                    conn.putheader("Host", host or "127.0.0.1:%d" % port)
                    for k, v in hdrs.items():
                        conn.putheader(k, v)
                    if body is not None:
                        conn.putheader("Content-Length", str(len(body)))
                    conn.endheaders(body)
                    response = conn.getresponse()
                    data = response.read()
                    conn.close()
                    return response.status, data
                self.assertEqual(call("GET", "/api/info")[0], 403)
                self.assertEqual(call("GET", "/api/info", {"X-Token": "wrong"})[0], 403)
                self.assertEqual(call("GET", "/api/info", {"X-Token": state.token}, host="evil.example:80")[0], 403)
                status, data = call("GET", "/")
                self.assertEqual(status, 200)
                self.assertIn(state.token.encode(), data)
                status, data = call("GET", "/api/info", {"X-Token": state.token})
                self.assertEqual(status, 200)
                self.assertTrue(json.loads(data)["providers"])
                with open(epub_path, "rb") as handle:
                    payload = handle.read()
                status, data = call("POST", "/api/upload", {"X-Token": state.token, "X-Filename": "sample.epub"}, payload)
                self.assertEqual(status, 200, data)
                pid = json.loads(data)["id"]
                for _ in range(100):
                    status, data = call("GET", "/api/p/%s/status" % pid, {"X-Token": state.token})
                    if json.loads(data)["meta"]["status"] == "ready":
                        break
                    time.sleep(0.1)
                self.assertEqual(json.loads(data)["meta"]["status"], "ready")
                status, data = call("POST", "/api/p/%s/start" % pid, {"X-Token": state.token, "Content-Type": "application/json"},
                                    json.dumps({}).encode())
                self.assertEqual(status, 400)
                self.assertEqual(json.loads(data)["error"], "no_key")
                status, data = call("POST", "/api/upload", {"X-Token": state.token, "X-Filename": "x.epub"}, b"not a book" * 10)
                self.assertEqual(status, 400)
                project = state.projects[pid]
                state.project(pid).settings.update({"provider": "gemini", "model": "gemini-x"})
                status, data = call("POST", "/api/p/%s/start" % pid, {"X-Token": state.token, "Content-Type": "application/json"},
                                    json.dumps({"key": "AIza-fake-key-for-test-1234567890"}).encode())
                self.assertEqual(status, 400)
                self.assertEqual(json.loads(data)["error"], "ack_required")
            finally:
                server.shutdown()
                server.server_close()

        # ---- עצירה מיידית של בקשת רשת תלויה ----
        def test_http_json_cancel_is_immediate(self) -> None:
            silent = socket.socket()
            silent.bind(("127.0.0.1", 0))
            silent.listen(5)
            port = silent.getsockname()[1]
            try:
                cancel = threading.Event()
                threading.Timer(0.3, cancel.set).start()
                started = time.time()
                with self.assertRaises(Aborted):
                    http_json("POST", "http://127.0.0.1:%d/x" % port, {}, {"a": 1}, 60.0, cancel)
                self.assertTrue(time.time() - started < 2.0, time.time() - started)
                # פסק זמן סרק רגיל (בלי ביטול) עדיין מסווג כ-timeout
                with self.assertRaises(BookError) as caught:
                    http_json("GET", "http://127.0.0.1:%d/x" % port, {}, None, 0.6, None)
                self.assertEqual(caught.exception.kind, "timeout")
                # ביטול שכבר הופעל לפני הקריאה
                early = threading.Event()
                early.set()
                with self.assertRaises(Aborted):
                    http_json("GET", "http://127.0.0.1:%d/x" % port, {}, None, 5.0, early)
            finally:
                silent.close()

        def test_stop_aborts_inflight_request(self) -> None:
            release = threading.Event()
            counters = {"items": 0}

            class Slow(BaseHTTPRequestHandler):
                def log_message(self, fmt: str, *args: Any) -> None:
                    return

                def reply(self, payload: Dict[str, Any]) -> None:
                    raw = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)

                def do_GET(self) -> None:
                    self.reply({"data": [{"id": "gpt-x"}]})

                def do_POST(self) -> None:
                    length = int(self.headers.get("Content-Length") or 0)
                    body = json.loads(self.rfile.read(length).decode("utf-8"))
                    if "=== ITEMS ===" in body["messages"][1]["content"]:
                        counters["items"] = counters["items"] + 1
                        release.wait(60)  # השרת "תקוע": אין תשובה עד שהבדיקה משחררת
                        return
                    self.reply({"choices": [{"message": {"content": "OK"}, "finish_reason": "stop"}],
                                "usage": {"prompt_tokens": 1, "completion_tokens": 1}})

            fake = ThreadingHTTPServer(("127.0.0.1", 0), Slow)
            threading.Thread(target=fake.serve_forever, daemon=True).start()
            base = "http://127.0.0.1:%d/v1" % fake.server_address[1]
            try:
                state, project = new_project(epub_path, provider="custom", model="gpt-x", base_url=base, concurrency=2, mock={}, timeout=60)
                project.set_status("ready")
                job = Job(project, dict(project.settings, api_key=""))
                job.start()
                deadline = time.time() + 20
                while time.time() < deadline and counters["items"] < 1:
                    time.sleep(0.05)
                self.assertTrue(counters["items"] >= 1, "הבקשה לא הגיעה לשרת")
                started = time.time()
                job.stop()
                finished = job.join(5.0)
                took = time.time() - started
                self.assertTrue(finished, "השרשור נשאר חי אחרי עצירה")
                self.assertTrue(took < 2.5, took)
                self.assertEqual(project.meta["status"], "stopped")
                self.assertEqual(project.counts()["done"], 0)
                self.assertFalse(project.dirty_meta)
            finally:
                release.set()
                fake.shutdown()
                fake.server_close()

        def test_pause_then_resume(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"delay": 0.1})
            project.set_status("ready")
            job = Job(project, dict(project.settings, api_key=""))
            job.start()
            deadline = time.time() + 30
            while time.time() < deadline and project.counts()["done"] < 3:
                time.sleep(0.05)
            job.pause()
            self.assertTrue(job.join(10.0))
            self.assertEqual(project.meta["status"], "paused")
            counts = project.counts()
            self.assertTrue(0 < counts["done"] < counts["total"], counts)
            # ההשהיה נשמרה לדיסק: טעינה מחדש רואה את אותו מצב
            reloaded = Project.load(project.id)
            self.assertEqual(reloaded.meta["status"], "paused")
            self.assertEqual(reloaded.counts()["done"], counts["done"])
            reloaded.settings = dict(project.settings, mock={"delay": 0.0})
            run_job(reloaded)
            self.assertEqual(reloaded.meta["status"], "completed", reloaded.meta.get("error"))

        # ---- שמירת מצב ושחזור ----
        def test_state_persisted_after_final_build(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={})
            run_job(project)
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            self.assertFalse(project.dirty_meta)
            self.assertEqual(len(project.dirty_chapters), 0)
            reloaded = Project.load(project.id)
            self.assertEqual(reloaded.meta["status"], "completed")
            self.assertTrue(reloaded.meta["final"] is not None)
            self.assertTrue(len(reloaded.meta["outputs"]) > 0)
            self.assertFalse(reloaded.meta.get("outputs_stale"))
            self.assertEqual(reloaded.counts()["pending"], 0)
            # עריכה אחרי ההפקה נשמרת ומסמנת שהפלט ישן
            target = None
            for candidate in reloaded.units:
                if candidate["status"] == "done" and candidate["scope"] == "content":
                    target = candidate
                    break
            self.assertTrue(target is not None)
            reloaded.touch(target)
            reloaded.flush()
            self.assertTrue(Project.load(project.id).meta.get("outputs_stale"))
            build_outputs(reloaded, reloaded.log)
            self.assertFalse(Project.load(project.id).meta.get("outputs_stale"))

        def test_crash_during_build_is_recoverable(self) -> None:
            state, project = new_project(epub_path)
            project.set_status("building")
            self.assertEqual(Project.load(project.id).meta["status"], "stopped")

        # ---- מחיקה מפורשת בלבד ----
        def test_deletion_is_explicit_only(self) -> None:
            state = AppState(0)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
            port = server.server_address[1]
            state.port = port
            server.RequestHandlerClass = make_handler(state)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                def call(method: str, path: str, body: Optional[Dict[str, Any]] = None, raw: Optional[bytes] = None,
                         extra: Optional[Dict[str, str]] = None) -> Tuple[int, Any]:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
                    headers = {"X-Token": state.token}
                    headers.update(extra or {})
                    payload = raw
                    if body is not None:
                        payload = json.dumps(body).encode("utf-8")
                        headers["Content-Type"] = "application/json"
                    conn.request(method, path, body=payload, headers=headers)
                    response = conn.getresponse()
                    data = response.read()
                    conn.close()
                    return response.status, (json.loads(data) if data else {})

                with open(epub_path, "rb") as handle:
                    payload = handle.read()
                status, data = call("POST", "/api/upload", raw=payload, extra={"X-Filename": "sample.epub"})
                self.assertEqual(status, 200, data)
                pid = data["id"]
                for _ in range(100):
                    status, data = call("GET", "/api/p/%s/status" % pid)
                    if data["meta"]["status"] == "ready":
                        break
                    time.sleep(0.1)
                project = state.projects[pid]
                project_dir = project.dir

                # 1. דחיית אישור מבנה אינה מוחקת
                project.set_status("awaiting_confirmation")
                status, data = call("POST", "/api/p/%s/confirm" % pid, body={"accept": False})
                self.assertEqual(status, 200, data)
                self.assertTrue(data.get("kept"))
                self.assertFalse(data.get("deleted"))
                self.assertTrue(pid in state.projects)
                self.assertTrue(os.path.isdir(project_dir))
                self.assertEqual(project.meta["status"], "awaiting_confirmation")
                status, data = call("POST", "/api/p/%s/confirm" % pid, body={"accept": True})
                self.assertEqual(status, 200, data)
                self.assertEqual(project.meta["status"], "ready")
                status, data = call("POST", "/api/p/%s/confirm" % pid, body={"accept": True})
                self.assertEqual(status, 200, data)  # אישור כפול אינו שגיאה

                # 2. מחיקה בלי אישור מפורש נדחית
                status, data = call("DELETE", "/api/p/%s" % pid)
                self.assertEqual(status, 400)
                self.assertEqual(data["error"], "confirmation_required")
                status, data = call("DELETE", "/api/p/%s?confirm=wrong" % pid)
                self.assertEqual(status, 400)
                status, data = call("POST", "/api/projects/delete", body={"ids": [pid]})
                self.assertEqual(status, 400)
                status, data = call("POST", "/api/projects/delete", body={"ids": [pid], "confirm": "yes"})
                self.assertEqual(status, 400)
                status, data = call("POST", "/api/projects/delete", body={"ids": [], "confirm": "DELETE"})
                self.assertEqual(status, 400)
                status, data = call("POST", "/api/projects/delete", body={"ids": ["../etc"], "confirm": "DELETE"})
                self.assertEqual(status, 400)
                self.assertTrue(pid in state.projects)
                self.assertTrue(os.path.isdir(project_dir))

                # 3. פרטי ניהול
                status, rows = call("GET", "/api/projects?detail=1")
                self.assertEqual(status, 200)
                self.assertEqual(len(rows), 1)
                self.assertTrue(rows[0]["size_bytes"] > 0)
                self.assertTrue("total" in rows[0] and "busy" in rows[0])

                # 4. אי אפשר למחוק פרויקט שרץ
                project.settings.update({"provider": "mock", "model": "mock-1", "chunk_chars": 800, "concurrency": 1, "mock": {"delay": 0.3}})
                job = Job(project, dict(project.settings, api_key=""))
                state.jobs[pid] = job
                job.start()
                time.sleep(0.3)
                status, data = call("DELETE", "/api/p/%s?confirm=%s" % (pid, pid))
                self.assertEqual(status, 409, data)
                status, data = call("POST", "/api/projects/delete", body={"ids": [pid], "confirm": "DELETE"})
                self.assertEqual(status, 200)
                self.assertEqual(data["deleted"], [])
                self.assertEqual(data["failed"][0]["error"], "busy")
                self.assertTrue(os.path.isdir(project_dir))
                job.stop()
                self.assertTrue(job.join(10.0))

                # 5. מחיקה מפורשת עובדת
                status, data = call("POST", "/api/projects/delete", body={"ids": [pid], "confirm": "DELETE"})
                self.assertEqual(status, 200, data)
                self.assertEqual(data["deleted"], [pid])
                self.assertFalse(os.path.exists(project_dir))
                self.assertFalse(pid in state.projects)
                status, rows = call("GET", "/api/projects")
                self.assertEqual(rows, [])
            finally:
                server.shutdown()
                server.server_close()

        def test_single_delete_with_confirm(self) -> None:
            state, project = new_project(epub_path)
            server_state = AppState(0)
            server_state.projects[project.id] = project
            result = server_state.delete_project(project.id)
            self.assertEqual(result["id"], project.id)
            self.assertFalse(os.path.exists(project.dir))
            with self.assertRaises(HttpError):
                server_state.delete_project(project.id)

        # ---- כותרות מכסה ----
        def test_rate_limit_header_variants(self) -> None:
            openai = parse_rate_limit_headers({
                "x-ratelimit-limit-requests": "500", "x-ratelimit-remaining-requests": "498", "x-ratelimit-reset-requests": "6m0s",
                "x-ratelimit-limit-tokens": "30000", "x-ratelimit-remaining-tokens": "29000", "x-ratelimit-reset-tokens": "20ms"})
            self.assertEqual(openai["requests"], {"limit": 500, "remaining": 498, "reset_s": 360.0})
            self.assertEqual(openai["tokens"]["remaining"], 29000)
            self.assertTrue(abs(openai["tokens"]["reset_s"] - 0.02) < 1e-9)

            generic = parse_rate_limit_headers({"X-RateLimit-Limit": "60", "X-RateLimit-Remaining": "59", "X-RateLimit-Reset": "30"})
            self.assertEqual(generic["requests"], {"limit": 60, "remaining": 59, "reset_s": 30.0})

            ietf = parse_rate_limit_headers({"RateLimit-Limit": "10", "RateLimit-Remaining": "7", "RateLimit-Reset": "12"})
            self.assertEqual(ietf["requests"]["remaining"], 7)

            future = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=90)).isoformat()
            anthropic = parse_rate_limit_headers({
                "anthropic-ratelimit-requests-limit": "50", "anthropic-ratelimit-requests-remaining": "49",
                "anthropic-ratelimit-requests-reset": future,
                "anthropic-ratelimit-input-tokens-remaining": "1000", "anthropic-ratelimit-tokens-remaining": "2000"})
            self.assertEqual(anthropic["requests"]["remaining"], 49)
            self.assertTrue(80 < anthropic["requests"]["reset_s"] < 91, anthropic["requests"]["reset_s"])
            self.assertEqual(anthropic["tokens"]["remaining"], 2000)  # הכותרת הכללית של tokens גוברת על input-tokens

            # כותרת ספציפית גוברת על כללית, בכל סדר הגעה
            first = parse_rate_limit_headers({"x-ratelimit-remaining": "5", "x-ratelimit-remaining-requests": "9"})
            second = parse_rate_limit_headers({"x-ratelimit-remaining-requests": "9", "x-ratelimit-remaining": "5"})
            self.assertEqual(first["requests"]["remaining"], 9)
            self.assertEqual(second["requests"]["remaining"], 9)
            # מכסה יומית נחלשת מול מכסת דקה
            mixed = parse_rate_limit_headers({"x-ratelimit-remaining-requests-day": "900", "x-ratelimit-remaining-requests": "40"})
            self.assertEqual(mixed["requests"]["remaining"], 40)

            self.assertEqual(parse_rate_limit_headers({}), {})
            self.assertEqual(parse_rate_limit_headers({"content-type": "application/json"}), {})
            self.assertEqual(parse_rate_limit_headers({"x-ratelimit-remaining": "abc"}), {})

            self.assertEqual(parse_reset_seconds("1m30.5s"), 90.5)
            self.assertEqual(parse_reset_seconds("2h"), 7200.0)
            self.assertEqual(parse_reset_seconds("45"), 45.0)
            self.assertTrue(abs(parse_reset_seconds(str(time.time() + 100)) - 100) < 2)
            self.assertTrue(parse_reset_seconds("garbage") is None)

        def test_http_json_reports_rate_headers(self) -> None:
            class Limited(BaseHTTPRequestHandler):
                def log_message(self, fmt: str, *args: Any) -> None:
                    return

                def do_POST(self) -> None:
                    length = int(self.headers.get("Content-Length") or 0)
                    self.rfile.read(length)
                    code = 429 if self.path.endswith("/limited") else 200
                    raw = json.dumps({"ok": code == 200}).encode("utf-8")
                    self.send_response(code)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("x-ratelimit-limit-requests", "10")
                    self.send_header("x-ratelimit-remaining-requests", "3")
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)

            fake = ThreadingHTTPServer(("127.0.0.1", 0), Limited)
            threading.Thread(target=fake.serve_forever, daemon=True).start()
            base = "http://127.0.0.1:%d" % fake.server_address[1]
            try:
                seen: List[Dict[str, Any]] = []
                data = http_json("POST", base + "/ok", {}, {}, 5.0, None, lambda h: seen.append(parse_rate_limit_headers(h)))
                self.assertEqual(data, {"ok": True})
                self.assertEqual(seen[0]["requests"]["remaining"], 3)
                self.assertEqual(seen[0]["requests"]["limit"], 10)
                # גם תשובת 429 מדווחת על המכסה
                with self.assertRaises(BookError):
                    http_json("POST", base + "/limited", {}, {}, 5.0, None, lambda h: seen.append(parse_rate_limit_headers(h)))
                self.assertEqual(len(seen), 2)
                self.assertEqual(seen[1]["requests"]["remaining"], 3)

                def broken(headers: Any) -> None:
                    raise RuntimeError("boom")
                # כשל ביוצר הדיווח אינו מפיל את הבקשה
                self.assertEqual(http_json("POST", base + "/ok", {}, {}, 5.0, None, broken), {"ok": True})
            finally:
                fake.shutdown()
                fake.server_close()

        def test_rate_limit_snapshot_is_persisted(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"rate_limit": 400})
            run_job(project)
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            requests = project.meta["usage"]["requests"]
            snapshot = project.meta["rate_limit"]
            self.assertEqual(snapshot["requests"]["limit"], 400)
            self.assertEqual(snapshot["requests"]["remaining"], 400 - requests)
            self.assertTrue(snapshot["seen_at"] > 0)
            reloaded = Project.load(project.id)
            self.assertEqual(reloaded.meta["rate_limit"]["requests"], snapshot["requests"])

        # ---- שליחה מחדש של יחידה בודדת ----
        def pick_context_unit(self, project: Project) -> Dict[str, Any]:
            per_chapter: Dict[int, int] = {}
            heading_seen: Dict[int, bool] = {}
            fallback = None
            for unit in project.units:
                if unit["scope"] != "content":
                    continue
                chapter = unit["ch"]
                if unit["type"] == "HEADING":
                    heading_seen[chapter] = True
                elif unit["type"] == "PARAGRAPH" and per_chapter.get(chapter, 0) >= 2:
                    if heading_seen.get(chapter):
                        return unit
                    if fallback is None:
                        fallback = unit
                per_chapter[chapter] = per_chapter.get(chapter, 0) + 1
            self.assertTrue(fallback is not None, "אין בדוגמה רכיב עם פסקאות קודמות")
            return fallback  # type: ignore[return-value]

        def test_resend_unit_keeps_context_and_bypasses_memory(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"prefix": "[T] "})
            run_job(project)
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            target = self.pick_context_unit(project)
            others = {}
            for unit in project.units:
                if unit["id"] != target["id"]:
                    others[unit["id"]] = unit.get("out")
            words = sorted(strip_tags(target["tagged"]).split(), key=len, reverse=True)
            project.glossary = [{"source": words[0], "target": "ZZTERM"}]
            mock_state = project.settings["mock"]["_state"]
            calls_before = mock_state["calls"]
            project.settings["mock"]["prefix"] = "[R] "
            job = Job(project, dict(project.settings, api_key=""))
            job.start_resend(target)
            self.assertTrue(job.join(30.0))
            # בקשה אחת בדיוק, ושהמודל באמת נשאל (זיכרון התרגום לא עקף אותה)
            self.assertEqual(mock_state["calls"], calls_before + 1)
            self.assertTrue(target["out"].startswith("[R] "), target["out"])
            self.assertEqual(target["status"], "done")
            self.assertEqual(project.meta["status"], "completed")
            self.assertTrue(project.meta.get("outputs_stale"))
            prompt = mock_state["prompts"][-1]
            self.assertTrue("Chapter:" in prompt)
            self.assertTrue("ZZTERM" in prompt, "מונחי המילון לא הועברו")
            self.assertTrue("Preceding text" in prompt, "הפסקאות הקודמות לא הועברו")
            self.assertTrue("[T] " in prompt.split("Preceding text")[1], "ההקשר הקודם צריך להיות התרגום הקיים")
            # יחידות אחרות לא השתנו, והכול נשמר לדיסק
            for unit in project.units:
                if unit["id"] != target["id"]:
                    self.assertEqual(unit.get("out"), others[unit["id"]])
            self.assertFalse(project.dirty_meta)
            reloaded = Project.load(project.id)
            self.assertTrue(reloaded.units_by_id[target["id"]]["out"].startswith("[R] "))

            # שליחה כושלת משחזרת את התרגום הקודם במקום למחוק אותו
            good_out = target["out"]
            project.settings["mock"]["fail_on_text"] = target["tagged"][:12]
            failing = Job(project, dict(project.settings, api_key=""))
            failing.start_resend(target)
            self.assertTrue(failing.join(30.0))
            self.assertEqual(target["out"], good_out)
            self.assertEqual(target["status"], "done")
            self.assertEqual(project.meta["status"], "completed")
            warnings = [entry["msg"] for entry in project.log.since(0) if "שוחזר" in entry["msg"]]
            self.assertTrue(len(warnings) >= 1)

        def test_manual_edit_wins_over_inflight_result(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"delay": 0.4})
            project.set_status("ready")
            job = Job(project, dict(project.settings, api_key=""))
            job.start()
            mock_state = project.settings["mock"]["_state"]
            deadline = time.time() + 20
            while time.time() < deadline and len(mock_state["prompts"]) < 1:
                time.sleep(0.02)
            victim = project.units[0]
            with project.lock:
                victim["status"] = "manual"
                victim["out"] = "EDITED BY HAND"
                project.touch(victim)
            self.assertTrue(job.join(60.0))
            self.assertEqual(victim["status"], "manual")
            self.assertEqual(victim["out"], "EDITED BY HAND")

        # ---- אינדקס יחידות, טעינה עד יחידה, ושליחה מחדש דרך HTTP ----
        def test_unit_index_upto_and_resend_endpoints(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"prefix": "[T] "})
            run_job(project)
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
            port = server.server_address[1]
            state.port = port
            server.RequestHandlerClass = make_handler(state)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                def call(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
                    headers = {"X-Token": state.token}
                    payload = None
                    if body is not None:
                        payload = json.dumps(body).encode("utf-8")
                        headers["Content-Type"] = "application/json"
                    conn.request(method, path, body=payload, headers=headers)
                    response = conn.getresponse()
                    data = response.read()
                    conn.close()
                    return response.status, (json.loads(data) if data else {})

                pid = project.id
                content = []
                for unit in project.units:
                    if unit["scope"] == "content":
                        content.append(unit)
                self.assertTrue(len(content) >= 5)
                with project.lock:
                    content[1]["status"] = "failed"
                    content[3]["status"] = "failed"
                    content[2]["status"] = "flagged"
                    content[4]["status"] = "pending"
                counts = project.counts()
                status, data = call("GET", "/api/p/%s/unit-index?status=failed" % pid)
                self.assertEqual(status, 200)
                self.assertEqual(data["ids"], [content[1]["id"], content[3]["id"]])  # לפי סדר הספר
                for group in ("done", "failed", "flagged", "pending"):
                    status, data = call("GET", "/api/p/%s/unit-index?status=%s" % (pid, group))
                    self.assertEqual(len(data["ids"]), counts[group], group)
                status, data = call("GET", "/api/p/%s/unit-index?status=bogus" % pid)
                self.assertEqual(status, 400)
                chunk_id = content[0].get("chunk")
                self.assertTrue(chunk_id)
                status, data = call("GET", "/api/p/%s/unit-index?chunk=%s" % (pid, chunk_id))
                self.assertTrue(content[0]["id"] in data["ids"])

                last = project.units[-1]["id"]
                status, data = call("GET", "/api/p/%s/units?chapter=-1&filter=&offset=0&upto=%s" % (pid, last))
                self.assertEqual(status, 200)
                self.assertTrue(data["found"])
                self.assertEqual(data["units"][-1]["id"], last)
                status, data = call("GET", "/api/p/%s/units?chapter=-1&filter=&offset=0&limit=2" % pid)
                self.assertEqual(len(data["units"]), 2)
                self.assertFalse(data["found"])

                # שליחה מחדש דרך ה-API
                status, data = call("POST", "/api/p/%s/unit-resend" % pid, {"id": "no-such-unit"})
                self.assertEqual(status, 404)
                project.settings["mock"]["prefix"] = "[R] "
                target = content[1]
                status, data = call("POST", "/api/p/%s/unit-resend" % pid, {"id": target["id"]})
                self.assertEqual(status, 200, data)
                job = state.jobs[pid]
                self.assertTrue(job.join(30.0))
                self.assertTrue(target["out"].startswith("[R] "), target["out"])
                self.assertEqual(target["status"], "done")
                self.assertEqual(project.meta["status"], "completed")
            finally:
                server.shutdown()
                server.server_close()

        # ---- תצוגה חיה ----
        def test_live_preview_documents_assets_and_sync(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"prefix": "[T] "})
            run_job(project)
            self.assertEqual(project.meta["status"], "completed", project.meta.get("error"))
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
            port = server.server_address[1]
            state.port = port
            server.RequestHandlerClass = make_handler(state)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                def call(method: str, path: str, body: Optional[Dict[str, Any]] = None, token: bool = True) -> Tuple[int, Any, Dict[str, str], bytes]:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
                    headers = {}
                    if token:
                        headers["X-Token"] = state.token
                    payload = None
                    if body is not None:
                        payload = json.dumps(body).encode("utf-8")
                        headers["Content-Type"] = "application/json"
                    conn.request(method, path, body=payload, headers=headers)
                    response = conn.getresponse()
                    data = response.read()
                    got = dict((k.lower(), v) for k, v in response.getheaders())
                    conn.close()
                    parsed: Any = None
                    if got.get("content-type", "").startswith("application/json") and data:
                        parsed = json.loads(data)
                    return response.status, parsed, got, data

                pid = project.id
                status, index, headers, raw = call("GET", "/api/p/%s/live-index" % pid)
                self.assertEqual(status, 200, index)
                key = index["key"]
                self.assertEqual(len(key), 32)
                self.assertTrue(len(index["docs"]) >= 3)
                content_docs = [d for d in index["docs"] if d["role"] == "content" and d["total"] > 0]
                self.assertTrue(len(content_docs) >= 1)
                doc = content_docs[0]["path"]

                # המסמך החי נטען במפתח בנתיב, בלי כותרת אסימון (כמו ש-iframe טוען אותו)
                status, parsed, headers, raw = call("GET", "/api/p/%s/live/%s/%s" % (pid, key, doc), token=False)
                self.assertEqual(status, 200)
                self.assertTrue(headers["content-type"].startswith("application/xhtml+xml"))
                self.assertTrue("default-src 'none'" in headers["content-security-policy"])
                self.assertEqual(headers["x-content-type-options"], "nosniff")
                text = raw.decode("utf-8")
                self.assertTrue("[T] " in text)
                self.assertTrue('<base href="/api/p/%s/asset/%s/OEBPS/"' % (pid, key) in text)
                self.assertTrue('id="bai-u-' in text)
                self.assertFalse("<script" in text)

                # זהות לפלט הסופי: אותם טקסטים מתורגמים כמו במסמך שנכתב ל-EPUB המוגמר
                with zipfile.ZipFile(os.path.join(project.output_dir, project.meta["outputs"][0]["name"])) as built:
                    final_text = built.read(doc).decode("utf-8")
                self.assertEqual(text.count("[T] "), final_text.count("[T] "))

                # נכסים מתוך הארכיון: CSS, תמונה, גופן
                status, parsed, headers, raw = call("GET", "/api/p/%s/asset/%s/OEBPS/styles/style.css" % (pid, key), token=False)
                self.assertEqual(status, 200)
                self.assertTrue(headers["content-type"].startswith("text/css"))
                with zipfile.ZipFile(project.work_path) as source:
                    original_css = source.read("OEBPS/styles/style.css")
                    original_png = source.read("OEBPS/images/pic.png")
                self.assertEqual(raw, original_css)
                status, parsed, headers, raw = call("GET", "/api/p/%s/asset/%s/OEBPS/images/pic.png" % (pid, key), token=False)
                self.assertEqual((status, headers["content-type"], raw), (200, "image/png", original_png))
                # היפוך כיוון (אנגלית לעברית) חל על ה-CSS רק בבקשה לגרסה הסופית
                status, parsed, headers, final_css = call("GET", "/api/p/%s/asset/%s/OEBPS/styles/style.css?final=1" % (pid, key), token=False)
                self.assertEqual(final_css, mirror_css(original_css.decode("utf-8")).encode("utf-8"))
                # גם הצורה עם אסימון בכותרת עובדת (/asset/<path> ללא מפתח)
                status, parsed, headers, raw = call("GET", "/api/p/%s/asset/OEBPS/images/pic.png" % pid)
                self.assertEqual((status, raw), (200, original_png))

                # אבטחה: מפתח שגוי, חציית תיקיות, קובץ שלא קיים
                status, parsed, headers, raw = call("GET", "/api/p/%s/asset/%s/OEBPS/images/pic.png" % (pid, "0" * 32), token=False)
                self.assertEqual(status, 403)
                for evil in ("../../../etc/passwd", "%2e%2e/%2e%2e/etc/passwd", "OEBPS/../../x", "..%5cwin.ini"):
                    status, parsed, headers, raw = call("GET", "/api/p/%s/asset/%s/%s" % (pid, key, evil), token=False)
                    self.assertTrue(status in (400, 403, 404), (evil, status))
                status, parsed, headers, raw = call("GET", "/api/p/%s/asset/%s/OEBPS/nope.png" % (pid, key), token=False)
                self.assertEqual(status, 404)
                status, parsed, headers, raw = call("GET", "/api/p/%s/live/%s/META-INF/container.xml" % (pid, key), token=False)
                self.assertEqual(status, 404)  # רק מסמכי הספר, לא כל קובץ
                # מפתח של פרויקט אחד לא פותח פרויקט אחר
                self.assertNotEqual(state.preview_key(pid), state.preview_key("other-project"))

                # סנכרון עם עריכות: עריכה ידנית משנה את המסמך החי ואת מונה הגרסה
                target = None
                for unit in project.units:
                    if unit["file"] == doc and unit["scope"] == "content" and unit["type"] == "PARAGRAPH" and not unit["tags"]:
                        target = unit
                        break
                self.assertTrue(target is not None)
                rev_before = project.rev
                status, parsed, headers, raw = call("POST", "/api/p/%s/unit-save" % pid, {"id": target["id"], "text": "EDITED-LIVE-TEXT"})
                self.assertEqual(status, 200, parsed)
                self.assertTrue(project.rev > rev_before)
                status, summary, headers, raw = call("GET", "/api/p/%s/status" % pid)
                self.assertEqual(summary["rev"], project.rev)
                status, parsed, headers, raw = call("GET", "/api/p/%s/live/%s/%s" % (pid, key, doc), token=False)
                self.assertTrue("EDITED-LIVE-TEXT" in raw.decode("utf-8"))
                self.assertTrue('id="bai-u-%s"' % target["id"] in raw.decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()

        def test_live_tree_sanitizing_and_links(self) -> None:
            state, project = new_project(epub_path)
            package = EpubPackage(project.work_path)
            try:
                doc_set = set()
                for path, role in package.document_files():
                    doc_set.add(path)
                xhtml = (b'<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>t</title>'
                         b'<base href="http://evil.example/"/><meta http-equiv="refresh" content="0;url=/api/projects"/>'
                         b'<link rel="stylesheet" href="styles/style.css"/><link rel="stylesheet" href="http://evil.example/x.css"/>'
                         b'<script>alert(1)</script></head><body onload="x()"><p onclick="y()">hi'
                         b'<a href="ch02.xhtml#sec">next</a><a href="http://evil.example/">out</a><a href="#local">here</a>'
                         b'<a href="images/pic.png">img</a></p><iframe src="/api/projects"></iframe></body></html>')
                tree = parse_xml(xhtml)
                decorate_live_tree(tree, package, "pid1", "k" * 32, "OEBPS/ch01.xhtml", doc_set, "replace")
                out = serialize_xml(tree).decode("utf-8")
                self.assertFalse("<script" in out)
                self.assertFalse("<iframe" in out)
                self.assertFalse("evil.example/\"" in out)
                self.assertFalse("refresh" in out)
                self.assertFalse("onclick" in out)
                self.assertFalse("onload" in out)
                self.assertTrue('<base href="/api/p/pid1/asset/%s/OEBPS/"' % ("k" * 32) in out)
                self.assertTrue('href="/api/p/pid1/asset/%s/OEBPS/styles/style.css?final=1"' % ("k" * 32) in out)
                self.assertTrue('href="/api/p/pid1/live/%s/OEBPS/ch02.xhtml?mode=replace#sec"' % ("k" * 32) in out)
                self.assertTrue('href="#local"' in out)
                self.assertTrue('href="images/pic.png"' in out)  # נכס רגיל נפתר דרך ה-base
                self.assertFalse("evil.example/x.css" in out)
            finally:
                package.close()

        def test_render_document_matches_write_output(self) -> None:
            state, project = new_project(epub_path, concurrency=1, mock={"prefix": "[T] "})
            run_job(project)
            package = EpubPackage(project.work_path)
            try:
                opts = output_options(project, "replace")
                built = os.path.join(project.output_dir, "x.epub")
                package.write_output(built, project.units, opts)
                with zipfile.ZipFile(built) as archive:
                    for path, role in package.document_files():
                        tree, count = package.render_document(path, project.units, opts)
                        self.assertEqual(serialize_xml(tree), archive.read(path), path)
            finally:
                package.close()

        # ---- הגדרות מומלצות לפי מודל ----
        def test_model_profiles_matching(self) -> None:
            cases = [("anthropic", "claude-sonnet-5-5", "claude-5"), ("anthropic", "claude-opus-5-5", "claude-5"),
                     ("openrouter", "anthropic/claude-fable-5.1", "claude-5"), ("anthropic", "claude-3-5-sonnet-20241022", "claude-3-5-sonnet"),
                     ("anthropic", "claude-3-5-sonnet-latest", "claude-3-5-sonnet"), ("openai", "gpt-4o", "gpt-4o"),
                     ("openai", "gpt-4o-2024-08-06", "gpt-4o"), ("openai", "gpt-4o-mini", "gpt-4o-mini"), ("openai", "gpt-4.1-mini", "gpt-4.1"),
                     ("gemini", "gemini-1.5-pro", "gemini-1-5"), ("gemini", "gemini-1.5-pro-002", "gemini-1-5"),
                     ("gemini", "gemini-2.5-flash", "gemini-2-5"), ("gemini", "gemini-3.1-pro-preview", "gemini-3"),
                     ("ollama", "llama3.1:8b", "local")]
            for provider, model, expected in cases:
                profile = match_model_profile(provider, model)
                self.assertTrue(profile is not None, (provider, model))
                self.assertEqual(profile["id"], expected, (provider, model))
            # אין התאמה: מודל לא מוכר, מודל ריק, ומודל מקומי שמוגדר תחת ספק אחר
            self.assertTrue(match_model_profile("openai", "some-unknown-model") is None)
            self.assertTrue(match_model_profile("openai", "") is None)
            self.assertTrue(match_model_profile("custom", "llama3.1:8b") is None)
            # שלמות הרשומות: כל המפתחות שהממשק מחיל קיימים בטופס ובהגדרות ברירת המחדל
            allowed = set(["temperature", "chunk_chars", "overlap", "max_output_tokens", "context_tokens", "concurrency"])
            defaults = default_settings()
            for profile in MODEL_PROFILES:
                re.compile(profile["match"])
                self.assertTrue(set(profile["settings"].keys()).issubset(allowed), profile["id"])
                for key in profile["settings"]:
                    self.assertTrue(key in defaults)
                self.assertTrue(profile["status"] in ("current", "legacy"))
                self.assertTrue(len(profile["notes"]) >= 1)
                # מקטע שמוצע לא חורג מהכלל: כ-45% מתקרת הפלט לפי 0.7 טוקנים לתו, עד 8000 תווים
                chunk = profile["settings"]["chunk_chars"]
                limit = profile["settings"]["max_output_tokens"]
                self.assertTrue(chunk <= 8000)
                self.assertTrue(chunk * 0.7 <= limit * 0.75, profile["id"])
            # דגמים שדוחים או לא מומלץ להם טמפרטורה לא מקבלים אחת
            self.assertTrue(match_model_profile("anthropic", "claude-sonnet-5-5")["settings"]["temperature"] is None)
            self.assertTrue(match_model_profile("gemini", "gemini-3-pro")["settings"]["temperature"] is None)

        def test_model_profile_endpoint_and_blank_temperature(self) -> None:
            state = AppState(0)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
            port = server.server_address[1]
            state.port = port
            server.RequestHandlerClass = make_handler(state)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
                conn.request("GET", "/api/model-profile?provider=gemini&model=gemini-1.5-pro", headers={"X-Token": state.token})
                response = conn.getresponse()
                data = json.loads(response.read())
                self.assertEqual(response.status, 200)
                self.assertEqual(data["profile"]["id"], "gemini-1-5")
                self.assertFalse("match" in data["profile"])
                self.assertEqual(data["profile"]["settings"]["chunk_chars"], 5000)
                conn.request("GET", "/api/model-profile?provider=openai&model=nothing", headers={"X-Token": state.token})
                self.assertTrue(json.loads(conn.getresponse().read())["profile"] is None)
                conn.request("GET", "/api/model-profile?provider=openai&model=gpt-4o")
                self.assertEqual(conn.getresponse().status, 403)  # נדרש אסימון
                conn.close()
            finally:
                server.shutdown()
                server.server_close()
            # טמפרטורה ריקה אינה נשלחת, ושגיאת 400 על טמפרטורה ב-Anthropic מסירה אותה וממשיכה
            seen_bodies: List[Dict[str, Any]] = []

            class FakeAnthropic(AnthropicProvider):
                def call_json(self, method: str, url: str, headers: Dict[str, str], body: Optional[Dict[str, Any]]) -> Any:
                    seen_bodies.append(dict(body or {}))
                    if body is not None and "temperature" in body:
                        raise BookError("api_error", "temperature may only be set to default", True, http=400)
                    return {"content": [{"type": "text", "text": "ok"}], "usage": {"input_tokens": 1, "output_tokens": 1}}

            provider = FakeAnthropic({"provider": "anthropic", "model": "claude-sonnet-5-5", "api_key": "k", "temperature": 0.3})
            text, usage = provider.complete("s", "u", False)
            self.assertEqual(text, "ok")
            self.assertTrue("temperature" in seen_bodies[0])
            self.assertFalse("temperature" in seen_bodies[1])
            provider.complete("s", "u", False)
            self.assertFalse("temperature" in seen_bodies[2])  # נזכר: לא שולחים שוב
            blank = FakeAnthropic({"provider": "anthropic", "model": "m", "api_key": "k", "temperature": None})
            seen_bodies.clear()
            blank.complete("s", "u", False)
            self.assertFalse("temperature" in seen_bodies[0])

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result = unittest.TextTestRunner(verbosity=2 if verbose else 1).run(suite)
    shutil.rmtree(sandbox, ignore_errors=True)
    return 0 if result.wasSuccessful() else 1


# ======================================================================
# 26. נקודת כניסה
# ======================================================================
ENV_EXAMPLE = """# העתק לקובץ .env והחלף בערכים אמיתיים. אל תוסיף את .env לבקרת גרסאות.
GEMINI_API_KEY=your-gemini-key-here
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
OPENROUTER_API_KEY=your-openrouter-key-here
CUSTOM_API_KEY=
OLLAMA_HOST=http://127.0.0.1:11434
# EPUBCHECK_JAR=/path/to/epubcheck.jar
# BOOK_AI_HOME=./data
# BOOK_AI_MAX_UPLOAD_MB=300
"""
GITIGNORE = ".env\ndata/\nprojects/\n*.state.json\n__pycache__/\n.book_ai/\nsamples/\n"


def main(argv: List[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="מעבד ספרים באמצעות מודלי בינה מלאכותית")
    parser.add_argument("command", nargs="?", default="serve", choices=["serve", "test", "samples", "init"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--out", default=os.path.join(APP_DIR, "samples"))
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "test":
        return run_tests(args.verbose)
    if args.command == "init":
        for name, content in ((".env.example", ENV_EXAMPLE), (".gitignore", GITIGNORE)):
            target = os.path.join(APP_DIR, name)
            if os.path.exists(target):
                print("קיים, לא נדרס:", name)
            else:
                with open(target, "w", encoding="utf-8") as handle:
                    handle.write(content)
                print("נוצר:", name)
        return 0
    if args.command == "samples":
        os.makedirs(args.out, exist_ok=True)
        epub = make_sample_epub(os.path.join(args.out, "sample.epub"))
        print("נוצר", epub)
        try:
            print("נוצר", make_sample_pdf(os.path.join(args.out, "sample.pdf")))
        except ImportError:
            print("דילוג על PDF (נדרש reportlab ליצירת דוגמה)")
        try:
            print("נוצר", make_sample_mobi(epub, os.path.join(args.out, "sample.mobi")))
        except BookError as exc:
            print("דילוג על MOBI:", exc.message)
        return 0
    serve(args.host, args.port, not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
