import shutil
import subprocess
from pathlib import Path
from book_ai.security.files import FileSecurityError

class MobiHandler:
    @staticmethod
    def convert_mobi_to_epub(mobi_path: Path, work_dir: Path) -> Path:
        converter = shutil.which("ebook-convert")
        if not converter:
            raise FileSecurityError(
                "כלי ההמרה 'ebook-convert' (Calibre) אינו מותקן בסביבה הנוכחית. "
                "להמרת קובצי MOBI, התקן את Calibre ונסה שוב."
            )

        out_epub = work_dir / "converted_from_mobi.epub"
        try:
            proc = subprocess.run(
                [converter, str(mobi_path), str(out_epub)],
                capture_output=True,
                text=True,
                timeout=180,
                check=False
            )
            if proc.returncode != 0 or not out_epub.exists() or out_epub.stat().st_size == 0:
                raise FileSecurityError(f"המרת קובץ ה-MOBI נכשלה: {proc.stderr[:300]}")
            return out_epub
        except subprocess.TimeoutExpired:
            raise FileSecurityError("המרת קובץ ה-MOBI חרגה ממגבלת הזמן (180 שניות).")
