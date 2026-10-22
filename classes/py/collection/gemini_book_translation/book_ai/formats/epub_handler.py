import os
import posixpath
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Tuple
from lxml import etree
from bs4 import BeautifulSoup, Tag

from book_ai.config import SUPPORTED_LANGUAGES
from book_ai.security.files import safe_extract_zip, safe_parse_xml, verify_safe_path, FileSecurityError
from book_ai.core.tag_protector import protect_element_inner_html, validate_and_restore_placeholders, apply_rtl_isolation

BLOCK_SELECTORS = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "th", "td", "figcaption", "dt", "dd"]

class EpubHandler:
    @staticmethod
    def ingest_epub(epub_path: Path, work_dir: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        unpacked_dir = work_dir / "unpacked"
        safe_extract_zip(epub_path, unpacked_dir)

        container_xml = unpacked_dir / "META-INF" / "container.xml"
        if not container_xml.exists():
            raise FileSecurityError("קובץ META-INF/container.xml חסר בחבילת ה-EPUB.")

        root = safe_parse_xml(container_xml.read_bytes())
        ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        rootfiles = root.xpath("//c:rootfile/@full-path", namespaces=ns)
        if not rootfiles:
            raise FileSecurityError("לא נמצא קובץ OPF בתוך container.xml.")

        opf_rel_path = rootfiles[0]
        opf_path = verify_safe_path(unpacked_dir, unpacked_dir / opf_rel_path)
        if not opf_path.exists():
            raise FileSecurityError(f"קובץ ה-OPF לא נמצא בנתיב: {opf_rel_path}")

        opf_dir = opf_path.parent
        opf_root = safe_parse_xml(opf_path.read_bytes())
        opf_ns = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/"
        }

        title_el = opf_root.xpath("//dc:title/text()", namespaces=opf_ns)
        creator_el = opf_root.xpath("//dc:creator/text()", namespaces=opf_ns)
        lang_el = opf_root.xpath("//dc:language/text()", namespaces=opf_ns)
        ident_el = opf_root.xpath("//dc:identifier/text()", namespaces=opf_ns)

        metadata = {
            "title": title_el[0].strip() if title_el else epub_path.stem,
            "author": creator_el[0].strip() if creator_el else "לא ידוע",
            "language": lang_el[0].strip() if lang_el else "en",
            "identifier": ident_el[0].strip() if ident_el else "book-ai-id",
            "opf_rel_path": opf_rel_path
        }

        manifest: Dict[str, Dict[str, str]] = {}
        for item in opf_root.xpath("//*[local-name()='manifest']/*[local-name()='item']"):
            item_id = item.get("id")
            href = item.get("href")
            media_type = item.get("media-type", "")
            if item_id and href:
                manifest[item_id] = {"href": href, "media_type": media_type, "properties": item.get("properties", "")}

        spine_itemrefs = [
            itemref.get("idref")
            for itemref in opf_root.xpath("//*[local-name()='spine']/*[local-name()='itemref']")
            if itemref.get("idref") in manifest
        ]

        if not spine_itemrefs:
            raise FileSecurityError("ה-Spine של הספר ריק או אינו מכיל הפניות תקינות.")

        chapters: List[Dict[str, Any]] = []
        units: List[Dict[str, Any]] = []
        unit_global_ord = 0

        for ch_idx, idref in enumerate(spine_itemrefs, start=1):
            href = manifest[idref]["href"]
            doc_path = verify_safe_path(unpacked_dir, opf_dir / href)
            if not doc_path.exists():
                continue

            rel_doc_path = str(doc_path.relative_to(unpacked_dir)).replace("\\", "/")
            raw_html = doc_path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(raw_html, "html.parser")

            ch_id = f"ch_{ch_idx:03d}"
            heading = soup.find(["h1", "h2", "h3", "title"])
            ch_title = heading.get_text(strip=True) if heading and heading.get_text(strip=True) else f"פרק {ch_idx}"

            ch_units: List[Dict[str, Any]] = []
            body = soup.find("body") or soup

            for elem in body.find_all(BLOCK_SELECTORS):
                if elem.find(BLOCK_SELECTORS):
                    continue
                text_content = elem.get_text(strip=True)
                if not text_content:
                    continue

                unit_global_ord += 1
                u_id = f"u_{ch_idx:03d}_{unit_global_ord:05d}"
                elem["data-bookai-id"] = u_id

                protected_str, protected_meta = protect_element_inner_html(elem)
                if not protected_str.strip():
                    continue

                ch_units.append({
                    "id": u_id,
                    "chapter_id": ch_id,
                    "ord": unit_global_ord,
                    "unit_type": elem.name.lower(),
                    "source_text": protected_str,
                    "protected": protected_meta
                })

            doc_path.write_text(str(soup), encoding="utf-8")

            if ch_units:
                chapters.append({
                    "id": ch_id,
                    "ord": ch_idx,
                    "title": ch_title[:120],
                    "doc_path": rel_doc_path
                })
                units.extend(ch_units)

        if not units:
            raise FileSecurityError("הספר אינו מכיל יחידות טקסט הניתנות לעיבוד.")

        return metadata, chapters, units

    @staticmethod
    def build_and_verify_epub(project: Dict[str, Any], chapters: List[Dict[str, Any]],
                              units: List[Dict[str, Any]], output_file: Path) -> Dict[str, Any]:
        work_dir = Path(project["work_dir"])
        unpacked_dir = work_dir / "unpacked"
        build_tmp_dir = work_dir / "build_staging"
        if build_tmp_dir.exists():
            shutil.rmtree(build_tmp_dir)
        shutil.copytree(unpacked_dir, build_tmp_dir)

        settings = project["settings"]
        layout = settings.get("layout", {})
        tgt_lang = settings.get("tgt_lang", "he")
        tgt_dir = SUPPORTED_LANGUAGES.get(tgt_lang, {}).get("dir", "ltr")
        if layout.get("force_direction") in ("rtl", "ltr"):
            tgt_dir = layout["force_direction"]

        unit_map = {u["id"]: u for u in units}
        unrestored_placeholders = 0
        replaced_units_count = 0

        for ch in chapters:
            doc_file = verify_safe_path(build_tmp_dir, build_tmp_dir / ch["doc_path"])
            if not doc_file.exists():
                continue
            soup = BeautifulSoup(doc_file.read_text(encoding="utf-8", errors="replace"), "html.parser")

            html_tag = soup.find("html")
            if html_tag:
                html_tag["xml:lang"] = tgt_lang
                html_tag["lang"] = tgt_lang
                html_tag["dir"] = tgt_dir

            body_tag = soup.find("body")
            if body_tag:
                body_tag["dir"] = tgt_dir

            if not layout.get("preserve_original", True):
                if layout.get("strip_inline_styles"):
                    for tag in soup.find_all(True):
                        tag.attrs.pop("style", None)
                if layout.get("strip_original_css"):
                    for link in soup.find_all("link", rel="stylesheet"):
                        link.decompose()

            custom_rules = []
            if not layout.get("preserve_original", True):
                if layout.get("font_family"):
                    custom_rules.append(f"body {{ font-family: {layout['font_family']} !important; }}")
                if layout.get("font_size"):
                    custom_rules.append(f"body {{ font-size: {layout['font_size']} !important; }}")
                if layout.get("line_height"):
                    custom_rules.append(f"body, p {{ line-height: {layout['line_height']} !important; }}")
                if layout.get("text_align"):
                    custom_rules.append(f"p, li {{ text-align: {layout['text_align']} !important; }}")
                if layout.get("custom_css"):
                    custom_rules.append(layout["custom_css"])

            if custom_rules or tgt_dir == "rtl":
                head = soup.find("head")
                if head:
                    style_tag = soup.new_tag("style", type="text/css")
                    rtl_css = f"body {{ direction: {tgt_dir}; unicode-bidi: embed; }}\n" if tgt_dir == "rtl" else ""
                    style_tag.string = rtl_css + "\n".join(custom_rules)
                    head.append(style_tag)

            for elem in soup.find_all(attrs={"data-bookai-id": True}):
                u_id = elem["data-bookai-id"]
                del elem["data-bookai-id"]
                u = unit_map.get(u_id)
                if not u:
                    continue

                chosen_text = u["result_text"] if u.get("result_text") else u["source_text"]
                ok, restored_html, _ = validate_and_restore_placeholders(chosen_text, u["protected"], attempt_repair=True)
                if not ok or "⟪" in restored_html or "⟫" in restored_html:
                    _, restored_html, _ = validate_and_restore_placeholders(u["source_text"], u["protected"], attempt_repair=True)

                restored_html = apply_rtl_isolation(restored_html, tgt_dir, settings.get("rtl_isolate", True))
                frag = BeautifulSoup(f"<div>{restored_html}</div>", "html.parser").div
                elem.clear()
                for child in list(frag.children):
                    elem.append(child)
                replaced_units_count += 1

            final_html = str(soup)
            if "⟪T" in final_html or "⟪V" in final_html:
                unrestored_placeholders += 1
            doc_file.write_text(final_html, encoding="utf-8")

        opf_rel = project["metadata"].get("opf_rel_path", "")
        opf_file = verify_safe_path(build_tmp_dir, build_tmp_dir / opf_rel)
        if opf_file.exists():
            opf_text = opf_file.read_text(encoding="utf-8", errors="replace")
            opf_text = opf_text.replace(
                f"<dc:language>{project['metadata'].get('language', 'en')}</dc:language>",
                f"<dc:language>{tgt_lang}</dc:language>"
            )
            opf_file.write_text(opf_text, encoding="utf-8")

        tmp_epub = output_file.with_suffix(".tmp.epub")
        mimetype_file = build_tmp_dir / "mimetype"
        if not mimetype_file.exists():
            mimetype_file.write_bytes(b"application/epub+zip")

        with zipfile.ZipFile(tmp_epub, "w") as zf:
            zf.write(mimetype_file, "mimetype", compress_type=zipfile.ZIP_STORED)
            for root_dir, _, files in os.walk(build_tmp_dir):
                for file in sorted(files):
                    full_p = Path(root_dir) / file
                    rel_p = full_p.relative_to(build_tmp_dir).as_posix()
                    if rel_p == "mimetype":
                        continue
                    zf.write(full_p, rel_p, compress_type=zipfile.ZIP_DEFLATED)

        report = EpubHandler.verify_epub_package(tmp_epub, len(chapters), len(units), replaced_units_count, unrestored_placeholders)
        if report["valid"]:
            tmp_epub.replace(output_file)
        else:
            if tmp_epub.exists():
                tmp_epub.unlink()
        return report

    @staticmethod
    def verify_epub_package(epub_path: Path, expected_chapters: int, expected_units: int,
                            replaced_units: int, unrestored_placeholders: int) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        if not epub_path.exists() or epub_path.stat().st_size == 0:
            return {"valid": False, "errors": ["קובץ הפלט לא נוצר או שהוא ריק."], "warnings": []}

        try:
            with zipfile.ZipFile(epub_path, "r") as zf:
                names = zf.namelist()
                if not names or names[0] != "mimetype":
                    errors.append("קובץ ה-mimetype אינו הרשומה הראשונה בארכיון ה-EPUB.")
                else:
                    mt_info = zf.getinfo("mimetype")
                    if mt_info.compress_type != zipfile.ZIP_STORED:
                        errors.append("קובץ ה-mimetype חייב להיות שמור ללא דחיסה (ZIP_STORED).")

                if "META-INF/container.xml" not in names:
                    errors.append("חסר META-INF/container.xml בפלט.")
                else:
                    c_root = safe_parse_xml(zf.read("META-INF/container.xml"))
                    opf_paths = c_root.xpath("//*[local-name()='rootfile']/@full-path")
                    if not opf_paths or opf_paths[0] not in names:
                        errors.append("קובץ ה-OPF המוגדר ב-container.xml חסר בארכיון.")
                    else:
                        opf_p = opf_paths[0]
                        opf_dir = posixpath.dirname(opf_p)
                        opf_root = safe_parse_xml(zf.read(opf_p))
                        for item in opf_root.xpath("//*[local-name()='manifest']/*[local-name()='item']"):
                            href = item.get("href", "").split("#")[0]
                            if href:
                                full_href = posixpath.normpath(posixpath.join(opf_dir, href)) if opf_dir else href
                                if full_href not in names:
                                    errors.append(f"משאב מופנה ב-Manifest חסר בארכיון: {full_href}")
        except Exception as e:
            errors.append(f"שגיאה בבדיקת שלמות ארכיון ה-EPUB: {e}")

        if replaced_units < expected_units:
            errors.append(f"מספר היחידות שהורכבו ({replaced_units}) קטן ממספר היחידות בספר ({expected_units}).")
        if unrestored_placeholders > 0:
            errors.append(f"נמצאו {unrestored_placeholders} מסמכים עם Placeholders שלא שוחזרו.")

        return {
            "valid": len(errors) == 0,
            "expected_chapters": expected_chapters,
            "expected_units": expected_units,
            "replaced_units": replaced_units,
            "unrestored_placeholders": unrestored_placeholders,
            "errors": errors,
            "warnings": warnings
        }
