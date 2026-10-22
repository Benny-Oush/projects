import re
from typing import List, Dict, Any

class Chunker:
    @staticmethod
    def build_chunks(all_chapter_units: List[Dict[str, Any]],
                     target_unit_ids: set,
                     chunk_chars: int = 6000,
                     overlap_units: int = 2) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        n = len(all_chapter_units)
        i = 0

        while i < n:
            u = all_chapter_units[i]
            if u["id"] not in target_unit_ids:
                i += 1
                continue

            current_targets: List[Dict[str, Any]] = []
            current_chars = 0
            start_idx = i

            while i < n and all_chapter_units[i]["id"] in target_unit_ids:
                candidate = all_chapter_units[i]
                cand_len = len(candidate["source_text"])
                if current_targets and (current_chars + cand_len > chunk_chars):
                    break
                current_targets.append(candidate)
                current_chars += cand_len
                i += 1

            overlap_start = max(0, start_idx - overlap_units)
            context_before = []
            for k in range(overlap_start, start_idx):
                prev_u = all_chapter_units[k]
                context_before.append({
                    "id": prev_u["id"],
                    "source_text": prev_u["source_text"],
                    "result_text": prev_u.get("result_text") or ""
                })

            chunks.append({
                "chapter_id": u["chapter_id"],
                "context_units": context_before,
                "target_units": current_targets,
                "total_chars": current_chars
            })

        return chunks

    @staticmethod
    def split_oversized_text(text: str, max_chars: int) -> List[str]:
        if len(text) <= max_chars:
            return [text]
        sentences = re.split(r'(?<=[.!?।。！？])\s+', text)
        parts: List[str] = []
        current = ""
        for sent in sentences:
            if len(current) + len(sent) + 1 <= max_chars:
                current = f"{current} {sent}".strip() if current else sent
            else:
                if current:
                    parts.append(current)
                current = sent
        if current:
            parts.append(current)
        return parts
