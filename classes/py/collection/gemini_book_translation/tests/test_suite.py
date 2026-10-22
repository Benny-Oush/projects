import io
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup

from book_ai.security.files import safe_extract_zip, safe_parse_xml, FileSecurityError
from book_ai.security.secrets import secret_manager
from book_ai.core.tag_protector import protect_element_inner_html, validate_and_restore_placeholders
from book_ai.core.chunker import Chunker
from book_ai.backend.app import app

client = TestClient(app)

def create_sample_epub_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(zipfile.ZipInfo("mimetype"), b"application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""")
        zf.writestr("OEBPS/style.css", "body { font-family: serif; }")
        zf.writestr("OEBPS/ch1.xhtml", """<?xml version="1.0" encoding="utf-8"?>
<html xmlns="[http://www.w3.org/1999/xhtml](http://www.w3.org/1999/xhtml)" lang="en">
<head><title>Chapter One</title><link rel="stylesheet" href="style.css"/></head>
<body>
  <h1 id="title1">Chapter 1: The Beginning</h1>
  <p>Hello <em>world</em> with a <a href="#fn1">footnote link</a> and <strong>bold text</strong>.</p>
  <ul>
    <li>First item</li>
    <li>Second item</li>
  </ul>
  <table><tr><td>Cell A</td><td>Cell B</td></tr></table>
  <aside id="fn1"><p>Footnote explanation text.</p></aside>
</body>
</html>""")
        zf.writestr("OEBPS/content.opf", """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="[http://www.idpf.org/2007/opf](http://www.idpf.org/2007/opf)" unique-identifier="BookId" version="3.0">
  <metadata xmlns:dc="[http://purl.org/dc/elements/1.1/](http://purl.org/dc/elements/1.1/)">
    <dc:title>Test Complex Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="BookId">urn:uuid:12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="css" href="style.css" media-type="text/css"/>
    <item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
  </spine>
</package>""")
    return buf.getvalue()

def test_tag_protection_and_validation():
    soup = BeautifulSoup('<p>Text with <em class="hl">italic</em>, <a href="[http://example.com](http://example.com)">link</a> and <br/> break.</p>', "html.parser")
    p_tag = soup.find("p")
    protected_str, meta = protect_element_inner_html(p_tag)
    assert "⟪T1⟫italic⟪/T1⟫" in protected_str
    assert "⟪T2⟫link⟪/T2⟫" in protected_str
    assert "⟪V1/⟫" in protected_str

    translated = "טקסט עם ⟪T1⟫נטוי⟪/T1⟫, ⟪T2⟫קישור⟪/T2⟫ ו-⟪V1/⟫ שבירת שורה."
    ok, restored, errs = validate_and_restore_placeholders(translated, meta, attempt_repair=False)
    assert ok is True
    assert not errs
    assert '<em class="hl">נטוי</em>' in restored
    assert '<a href="[http://example.com](http://example.com)">קישור</a>' in restored

    corrupted = "טקסט שבו המודל מחק את התגיות לגמרי."
    ok2, _, errs2 = validate_and_restore_placeholders(corrupted, meta, attempt_repair=False)
    assert ok2 is False
    assert len(errs2) > 0

def test_chunker_with_overlap():
    units = [
        {"id": f"u{i}", "chapter_id": "c1", "source_text": "A" * 40, "result_text": f"R{i}"}
        for i in range(1, 6)
    ]
    target_ids = {"u1", "u2", "u3", "u4", "u5"}
    chunks = Chunker.build_chunks(units, target_ids, chunk_chars=90, overlap_units=2)
    assert len(chunks) == 3
    assert [u["id"] for u in chunks[0]["target_units"]] == ["u1", "u2"]
    assert len(chunks[0]["context_units"]) == 0
    assert [c["id"] for c in chunks[1]["context_units"]] == ["u1", "u2"]
    assert [u["id"] for u in chunks[1]["target_units"]] == ["u3", "u4"]

def test_zip_slip_prevention(tmp_path: Path):
    malicious_zip = tmp_path / "evil.epub"
    with zipfile.ZipFile(malicious_zip, "w") as zf:
        zf.writestr("../../evil.txt", "pwned")
    with pytest.raises(FileSecurityError):
        safe_extract_zip(malicious_zip, tmp_path / "out")

def test_xxe_prevention():
    xxe_xml = b"""<?xml version="1.0"?>
<!DOCTYPE lolz [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>"""
    root = safe_parse_xml(xxe_xml)
    assert "root:" not in (root.text or "")

def test_secret_redaction():
    secret_manager.save_key("openai", "sk-secret1234567890abcdef")
    log_msg = "Failed call with key sk-secret1234567890abcdef on endpoint"
    clean = secret_manager.redact(log_msg)
    assert "sk-secret1234567890abcdef" not in clean
    assert "***REDACTED" in clean

def test_full_api_workflow():
    epub_bytes = create_sample_epub_bytes()
    files = {"file": ("sample.epub", epub_bytes, "application/epub+zip")}
    data = {
        "name": "ספר בדיקה מקצה לקצה",
        "settings_json": '{"src_lang":"en","tgt_lang":"he","goal":"translate_edit","provider":"mock","model":"mock-deterministic","mock":true}'
    }
    res = client.post("/api/projects", files=files, data=data)
    assert res.status_code == 200
    proj = res.json()
    pid = proj["id"]
    assert proj["stats"]["total"] >= 6

    ctrl_res = client.post(f"/api/projects/{pid}/control", json={"action": "start"})
    assert ctrl_res.status_code == 200

    import time
    for _ in range(25):
        details = client.get(f"/api/projects/{pid}").json()
        if details["project"]["status"] == "completed":
            break
        time.sleep(0.1)

    units = client.get(f"/api/projects/{pid}/units").json()["units"]
    assert all(u["status"] == "done" for u in units)

    first_u = units[0]
    edit_res = client.put(f"/api/units/{first_u['id']}", json={"result_text": "כותרת ערוכה ידנית"})
    assert edit_res.status_code == 200
    assert edit_res.json()["status"] == "manual"

    conflict_res = client.post(f"/api/projects/{pid}/control", json={
        "action": "resend_unit", "unit_id": first_u["id"], "force_manual_override": False
    })
    assert conflict_res.status_code == 409

    build_res = client.post(f"/api/projects/{pid}/build")
    assert build_res.status_code == 200
    assert build_res.json()["output_ready"] is True
    assert build_res.json()["report"]["valid"] is True

    dl_res = client.get(f"/api/projects/{pid}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/epub+zip"
