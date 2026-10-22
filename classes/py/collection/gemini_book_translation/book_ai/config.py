import os
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("BOOK_AI_DATA_DIR", BASE_DIR / "data")).resolve()
PROJECTS_DIR = DATA_DIR / "projects"
SECRETS_DIR = DATA_DIR / "secrets"
DB_PATH = DATA_DIR / "book_ai.sqlite3"

for d in (DATA_DIR, PROJECTS_DIR, SECRETS_DIR):
    d.mkdir(parents=True, exist_ok=True)

SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "auto": {"name": "זיהוי אוטומטי", "dir": "ltr"},
    "he": {"name": "עברית", "dir": "rtl"},
    "en": {"name": "אנגלית", "dir": "ltr"},
    "ar": {"name": "ערבית", "dir": "rtl"},
    "fa": {"name": "פרסית", "dir": "rtl"},
    "ur": {"name": "אורדו", "dir": "rtl"},
    "yi": {"name": "יידיש", "dir": "rtl"},
    "ru": {"name": "רוסית", "dir": "ltr"},
    "uk": {"name": "אוקראינית", "dir": "ltr"},
    "fr": {"name": "צרפתית", "dir": "ltr"},
    "de": {"name": "גרמנית", "dir": "ltr"},
    "es": {"name": "ספרדית", "dir": "ltr"},
    "it": {"name": "איטלקית", "dir": "ltr"},
    "pt": {"name": "פורטוגזית", "dir": "ltr"},
    "nl": {"name": "הולנדית", "dir": "ltr"},
    "pl": {"name": "פולנית", "dir": "ltr"},
    "cs": {"name": "צ'כית", "dir": "ltr"},
    "sv": {"name": "שוודית", "dir": "ltr"},
    "no": {"name": "נורווגית", "dir": "ltr"},
    "da": {"name": "דנית", "dir": "ltr"},
    "fi": {"name": "פינית", "dir": "ltr"},
    "el": {"name": "יוונית", "dir": "ltr"},
    "tr": {"name": "טורקית", "dir": "ltr"},
    "hu": {"name": "הונגרית", "dir": "ltr"},
    "ro": {"name": "רומנית", "dir": "ltr"},
    "bg": {"name": "בולגרית", "dir": "ltr"},
    "hr": {"name": "קרואטית", "dir": "ltr"},
    "sr": {"name": "סרבית", "dir": "ltr"},
    "la": {"name": "לטינית", "dir": "ltr"},
    "ja": {"name": "יפנית", "dir": "ltr"},
    "zh": {"name": "סינית", "dir": "ltr"},
    "ko": {"name": "קוריאנית", "dir": "ltr"},
    "hi": {"name": "הינדי", "dir": "ltr"},
    "th": {"name": "תאית", "dir": "ltr"},
    "vi": {"name": "וייטנאמית", "dir": "ltr"},
    "id": {"name": "אינדונזית", "dir": "ltr"},
    "am": {"name": "אמהרית", "dir": "ltr"},
}

PROCESSING_GOALS = {
    "translate": "תרגום מדויק",
    "translate_edit": "תרגום ועריכה לשונית",
    "rewrite_he": "שכתוב לעברית טבעית",
    "proofread": "הגהה ותיקון שגיאות מינימלי",
    "literary_edit": "עריכה ספרותית",
    "polish": "ליטוש ובהירות",
    "custom": "הוראות מותאמות אישית",
}

class LayoutSettings(BaseModel):
    preserve_original: bool = True
    font_family: str = ""
    font_size: str = ""
    line_height: str = ""
    margins: str = ""
    max_width: str = ""
    theme: str = "default"
    text_align: str = ""
    paragraph_spacing: str = ""
    heading_align: str = ""
    heading_font: str = ""
    hyphens: str = "auto"
    strip_inline_styles: bool = False
    strip_original_css: bool = False
    custom_css: str = ""
    force_direction: str = "auto"

class ProjectSettings(BaseModel):
    goal: str = "translate_edit"
    src_lang: str = "auto"
    tgt_lang: str = "he"
    mode: str = "standard"
    extra: str = ""
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"
    base_url: str = ""
    temperature: Optional[float] = 0.3
    chunk_chars: int = Field(default=6000, ge=500, le=100000)
    overlap: int = Field(default=2, ge=0, le=10)
    attempts: int = Field(default=3, ge=1, le=10)
    api_retries: int = Field(default=5, ge=1, le=20)
    concurrency: int = Field(default=2, ge=1, le=20)
    timeout: int = Field(default=120, ge=10, le=600)
    consistency: bool = True
    format: str = "auto"
    on_format_failure: str = "flag"
    max_output_tokens: int = Field(default=8192, ge=256, le=65536)
    context_tokens: int = Field(default=128000, ge=2048, le=2000000)
    rpm: int = Field(default=30, ge=1, le=1000)
    price_in: float = Field(default=0.15, ge=0.0)
    price_out: float = Field(default=0.60, ge=0.0)
    rtl_isolate: bool = True
    layout: LayoutSettings = Field(default_factory=LayoutSettings)
    mock: bool = False

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v: str) -> str:
        if v not in PROCESSING_GOALS:
            raise ValueError(f"מטרת עיבוד לא חוקית: {v}")
        return v
