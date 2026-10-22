import re
from typing import Dict, Any, Tuple, List
from bs4 import BeautifulSoup, NavigableString, Tag

VOID_TAGS = {"br", "img", "hr", "wbr"}
INLINE_TAGS = {"em", "i", "strong", "b", "u", "span", "a", "sup", "sub", "code", "small", "mark", "abbr", "cite", "q", "bdi", "bdo"}

class TagProtectionError(Exception):
    pass

def protect_element_inner_html(element: Tag) -> Tuple[str, Dict[str, Any]]:
    tag_map: Dict[str, Dict[str, Any]] = {}
    counter = {"t": 0, "v": 0}

    def _serialize_node(node) -> str:
        if isinstance(node, NavigableString):
            return str(node)
        if isinstance(node, Tag):
            name = node.name.lower()
            attrs = dict(node.attrs)
            if name in VOID_TAGS:
                counter["v"] += 1
                key = f"V{counter['v']}"
                tag_map[key] = {"tag": name, "attrs": attrs, "void": True}
                return f"⟪{key}/⟫"
            else:
                counter["t"] += 1
                key = f"T{counter['t']}"
                tag_map[key] = {"tag": name, "attrs": attrs, "void": False}
                inner = "".join(_serialize_node(child) for child in node.children)
                return f"⟪{key}⟫{inner}⟪/{key}⟫"
        return ""

    protected_text = "".join(_serialize_node(c) for c in element.children)
    protected_meta = {
        "root_tag": element.name,
        "root_attrs": dict(element.attrs),
        "tag_map": tag_map
    }
    return protected_text.strip(), protected_meta

def validate_and_restore_placeholders(translated_text: str, protected_meta: Dict[str, Any],
                                      attempt_repair: bool = True) -> Tuple[bool, str, List[str]]:
    errors: List[str] = []
    tag_map: Dict[str, Dict[str, Any]] = protected_meta.get("tag_map", {})
    working_text = translated_text

    found_tokens = re.findall(r"⟪(/?[TV]\d+/?)⟫", working_text)
    expected_tokens = set()
    for key, info in tag_map.items():
        if info["void"]:
            expected_tokens.add(f"{key}/")
        else:
            expected_tokens.add(key)
            expected_tokens.add(f"/{key}")

    for tok in found_tokens:
        if tok not in expected_tokens:
            if attempt_repair:
                working_text = working_text.replace(f"⟪{tok}⟫", "")
            else:
                errors.append(f"Placeholder זר התגלה בפלט: ⟪{tok}⟫")

    for key, info in tag_map.items():
        if info["void"]:
            token_str = f"⟪{key}/⟫"
            count = working_text.count(token_str)
            if count == 0:
                if attempt_repair:
                    working_text = working_text + token_str
                else:
                    errors.append(f"Placeholder יחיד חסר: {token_str}")
            elif count > 1:
                errors.append(f"Placeholder שוכפל בניגוד לכללים: {token_str}")
        else:
            open_tok = f"⟪{key}⟫"
            close_tok = f"⟪/{key}⟫"
            o_cnt = working_text.count(open_tok)
            c_cnt = working_text.count(close_tok)
            if o_cnt != 1 or c_cnt != 1:
                if attempt_repair and o_cnt == 1 and c_cnt == 0:
                    working_text = working_text + close_tok
                elif attempt_repair and o_cnt == 0 and c_cnt == 0:
                    errors.append(f"תגית מוגנת נמחקה על ידי המודל: {open_tok}...{close_tok}")
                else:
                    errors.append(f"חוסר איזון בתגית מוגנת {key}: פתיחה={o_cnt}, סגירה={c_cnt}")
            else:
                if working_text.find(open_tok) > working_text.find(close_tok):
                    errors.append(f"סדר תגיות הפוך עבור {key}")

    if errors:
        return False, working_text, errors

    restored = working_text
    for key, info in tag_map.items():
        tag_name = info["tag"]
        attrs_str = ""
        for k, v in info.get("attrs", {}).items():
            val_str = " ".join(v) if isinstance(v, list) else str(v)
            val_escaped = val_str.replace('"', '&quot;')
            attrs_str += f' {k}="{val_escaped}"'

        if info["void"]:
            restored = restored.replace(f"⟪{key}/⟫", f"<{tag_name}{attrs_str}/>")
        else:
            restored = restored.replace(f"⟪{key}⟫", f"<{tag_name}{attrs_str}>")
            restored = restored.replace(f"⟪/{key}⟫", f"</{tag_name}>")

    try:
        soup = BeautifulSoup(f"<div>{restored}</div>", "html.parser")
        _ = str(soup.div)
    except Exception as e:
        return False, restored, [f"שגיאת תחביר HTML לאחר שחזור: {e}"]

    return True, restored, []

def apply_rtl_isolation(html_fragment: str, target_dir: str, enabled: bool = True) -> str:
    if not enabled or target_dir != "rtl":
        return html_fragment
    parts = re.split(r"(<[^>]+>)", html_fragment)
    out = []
    for part in parts:
        if part.startswith("<"):
            out.append(part)
        else:
            isolated = re.sub(r"([A-Za-z0-9][A-Za-z0-9\-\._/:@#%&+=]{1,}[A-Za-z0-9])", r"<bdi>\1</bdi>", part)
            out.append(isolated)
    return "".join(out)
