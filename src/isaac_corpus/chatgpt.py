from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

@dataclass(frozen=True)
class ChatMessage:
    message_id: str
    conversation_id: str
    timestamp: str
    role: str
    text: str
    source_file: str

def _extract_json_data(html: str) -> list[dict]:
    marker = "jsonData = "
    pos = html.find(marker)
    if pos < 0:
        raise ValueError("Could not find ChatGPT export jsonData")
    value, _ = json.JSONDecoder().raw_decode(html[pos + len(marker):].lstrip())
    if not isinstance(value, list):
        raise ValueError("Expected jsonData to be a list of conversations")
    return value

def _text(message: dict) -> str:
    content = message.get("content") or {}
    parts = content.get("parts") or []
    return "\n".join(p for p in parts if isinstance(p, str)).strip()

def _iso(ts: object) -> str:
    if not isinstance(ts, (int, float)):
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

def canonical_messages(path: str | Path) -> list[ChatMessage]:
    path = Path(path)
    conversations = _extract_json_data(path.read_text(encoding="utf-8", errors="replace"))
    out: list[ChatMessage] = []
    for conv in conversations:
        mapping = conv.get("mapping") or {}
        node_id = conv.get("current_node")
        chain: list[dict] = []
        seen: set[str] = set()
        while node_id and node_id not in seen:
            seen.add(node_id)
            node = mapping.get(node_id)
            if not node:
                break
            chain.append(node)
            node_id = node.get("parent")
        chain.reverse()
        cid = conv.get("conversation_id") or conv.get("id") or ""
        for node in chain:
            msg = node.get("message")
            if not msg:
                continue
            role = ((msg.get("author") or {}).get("role") or "").strip()
            text = _text(msg)
            if role not in {"user", "assistant"} or not text:
                continue
            out.append(ChatMessage(
                message_id=str(msg.get("id") or node.get("id")),
                conversation_id=str(cid),
                timestamp=_iso(msg.get("create_time")),
                role=role,
                text=text,
                source_file=path.name,
            ))
    return out
