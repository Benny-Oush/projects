import fitz  # PyMuPDF
import zipfile
from pathlib import Path
from typing import Dict, Any, Tuple, List
from html import escape
from book_ai.security.files import FileSecurityError

class PdfHandler:
    @staticmethod
    def convert_pdf_to_epub(pdf_path: Path, work_dir: Path) -> Tuple[Path, Dict[str, Any]]:
        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            raise FileSecurityError(f"לא ניתן לפתוח את קובץ ה-PDF: {e}")

        page_count = len(doc)
        if page_count == 0:
            raise FileSecurityError("קובץ ה-PDF ריק (0 עמודים).")

        total_chars = 0
        chapters_html: List[Tuple[str, str]] = []
        current_title = pdf_path.stem
        current_blocks: List[str] = []

        for page_idx in range(page_count):
            page = doc[page_idx]
            blocks = page.get_text("blocks")
            for b in blocks:
                if b[6] != 0:
                    continue
                text = b[4].strip()
                if not text:
                    continue
                total_chars += len(text)
                clean_lines = " ".join(line.strip() for line in text.splitlines() if line.strip())
                if len(clean_lines) < 80 and (clean_lines.startswith("Chapter") or clean_lines.startswith("פרק") or clean_lines.isupper()):
                    if current_blocks:
                        chapters_html.append((current_title, "\n".join(current_blocks)))
                        current_blocks = []
                    current_title = clean_lines
                    current_blocks.append(f"<h2>{escape(clean_lines)}</h2>")
                else:
                    current_blocks.append(f"<p>{escape(clean_lines)}</p>")

        if current_blocks:
            chapters_html.append((current_title, "\n".join(current_blocks)))

        if total_chars < 20:
            raise FileSecurityError(
                "קובץ ה-PDF זוהה כמסמך סרוק ללא שכבת טקסט תקינה. "
                "גרסה זו אינה מבצעת OCR אוטומטי כדי למנוע שיבוש תוכן שקט."
            )

        extraction_report = {
            "page_count": page_count,
            "total_characters": total_chars,
            "detected_chapters": len(chapters_html),
            "is_scanned": False,
            "limitations_notice": "מקור הקובץ הוא PDF. החילוץ שומר על סדר הקריאה והפסקאות, אך עיצוב עמוד מורכב של PDF מומר למבנה EPUB זורם."
        }

        generated_epub = work_dir / "converted_from_pdf.epub"
        PdfHandler._write_minimal_epub(generated_epub, pdf_path.stem, chapters_html)
        return generated_epub, extraction_report

    @staticmethod
    def _write_minimal_epub(epub_out: Path, title: str, chapters: List[Tuple[str, str]]) -> None:
        with zipfile.ZipFile(epub_out, "w") as zf:
            zf.writestr(zipfile.ZipInfo("mimetype"), b"application/epub+zip", compress_type=zipfile.ZIP_STORED)
            zf.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""")

            manifest_items = []
            spine_items = []
            for idx, (ch_title, ch_body) in enumerate(chapters, start=1):
                fname = f"ch_{idx:03d}.xhtml"
                manifest_items.append(f'<item id="ch{idx}" href="{fname}" media-type="application/xhtml+xml"/>')
                spine_items.append(f'<itemref idref="ch{idx}"/>')
                xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head><title>{escape(ch_title)}</title></head>
<body>
{ch_body}
</body>
</html>"""
                zf.writestr(f"OEBPS/{fname}", xhtml.encode("utf-8"))

            opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{escape(title)}</dc:title>
    <dc:language>en</dc:language>
    <dc:identifier id="BookId">urn:uuid:pdf-converted-book</dc:identifier>
  </metadata>
  <manifest>
    {''.join(manifest_items)}
  </manifest>
  <spine>
    {''.join(spine_items)}
  </spine>
</package>"""
            zf.writestr("OEBPS/content.opf", opf.encode("utf-8"))
