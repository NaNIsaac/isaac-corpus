from __future__ import annotations
from collections import defaultdict
from typing import Iterable

def build_response_examples(messages: Iterable[dict], context_messages: int = 6) -> list[dict]:
    """Build context -> Russell response examples without crossing conversations."""
    by_conv: dict[str, list[dict]] = defaultdict(list)
    for m in messages:
        by_conv[m["conversation_id"]].append(m)

    examples: list[dict] = []
    for cid, rows in by_conv.items():
        rows.sort(key=lambda x: (x.get("timestamp", ""), x.get("message_id", "")))
        for i, row in enumerate(rows):
            is_target = row.get("is_russell") is True or row.get("role") == "user"
            if not is_target or not row.get("text"):
                continue
            context = rows[max(0, i-context_messages):i]
            if not context:
                continue
            examples.append({
                "conversation_id": cid,
                "target_message_id": row["message_id"],
                "context": [
                    {"speaker": x.get("speaker") or x.get("role"), "text": x["text"]}
                    for x in context
                ],
                "response": row["text"],
            })
    return examples
