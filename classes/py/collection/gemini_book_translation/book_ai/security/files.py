import os
import re
import zipfile
from pathlib import Path
from lxml import etree

MAX_UPLOAD_SIZE_BYTES = 150 * 1024 * 1024  # 150 MB
MAX_ARCHIVE_ENTRIES = 10000
MAX_UNCOMPRESSED_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_COMPRESSION_RATIO = 100.0

class FileSecurityError(Exception):
    pass

def sanitize_filename(filename: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9א-ת_\-\.]', '_', Path(filename).name)
    clean = clean.lstrip('.')
    return clean or "book_file"

def verify_safe_path(base_dir: Path, target_path: Path) -> Path:
    base_resolved = base_dir.resolve()
    target_resolved = target_path.resolve()
    if not str(target_resolved).startswith(str(base_resolved) + os.sep) and target_resolved != base_resolved:
        raise FileSecurityError(f"ניסיון חציית תיקיות (Path Traversal) נחסם: {target_path}")
    return target_resolved

def validate_magic_bytes(file_path: Path) -> str:
    if not file_path.exists() or file_path.stat().st_size == 0:
        raise FileSecurityError("הקובץ ריק או אינו קיים.")
    if file_path.stat().st_size > MAX_UPLOAD_SIZE_BYTES:
        raise FileSecurityError("הקובץ חורג ממגבלת הגודל המותרת (150MB).")

    with open(file_path, "rb") as f:
        header = f.read(100)

    if header.startswith(b"PK\x03\x04"):
        return "epub"
    if header.startswith(b"%PDF-"):
        return "pdf"
    if len(header) >= 68 and header[60:68] in (b"BOOKMOBI", b"TEXtREAd"):
        return "mobi"
    if file_path.suffix.lower() == ".mobi" and len(header) > 16:
        return "mobi"

    raise FileSecurityError("תוכן הקובץ אינו תואם לפורמט נתמך (EPUB, PDF, MOBI).")

def safe_extract_zip(zip_path: Path, extract_to: Path) -> None:
    extract_to = extract_to.resolve()
    extract_to.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            infos = zf.infolist()
            if len(infos) > MAX_ARCHIVE_ENTRIES:
                raise FileSecurityError(f"הארכיון מכיל יותר מדי רשומות ({len(infos)} > {MAX_ARCHIVE_ENTRIES}).")

            total_uncompressed = 0
            for info in infos:
                if info.filename.startswith("/") or info.filename.startswith("\\") or ".." in Path(info.filename).parts:
                    raise FileSecurityError(f"זוהה נתיב זדוני בארכיון (Zip Slip): {info.filename}")

                target_file = (extract_to / info.filename).resolve()
                verify_safe_path(extract_to, target_file)

                total_uncompressed += info.file_size
                if total_uncompressed > MAX_UNCOMPRESSED_SIZE:
                    raise FileSecurityError("הגודל הכולל של הארכיון לאחר פתיחה חורג מהמותר (Zip Bomb).")

                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > MAX_COMPRESSION_RATIO and info.file_size > 10 * 1024 * 1024:
                        raise FileSecurityError(f"יחס דחיסה חריג זוהה ברשומה {info.filename}.")

            for info in infos:
                target_file = (extract_to / info.filename).resolve()
                if info.is_dir():
                    target_file.mkdir(parents=True, exist_ok=True)
                else:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(info, "r") as src, open(target_file, "wb") as dst:
                        dst.write(src.read())
    except zipfile.BadZipFile as e:
        raise FileSecurityError(f"ארכיון ה-EPUB פגום: {e}")

def safe_parse_xml(xml_bytes: bytes) -> etree._Element:
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        dtd_validation=False,
        load_dtd=False,
        recover=True,
        huge_tree=False
    )
    try:
        return etree.fromstring(xml_bytes, parser=parser)
    except Exception as e:
        raise FileSecurityError(f"שגיאה בפענוח מאובטח של XML: {e}")
