from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

LINE_RE = re.compile(
    r"^(?P<date>\d{4}년 \d{1,2}월 \d{1,2}일 "
    r"(?:오전|오후) \d{1,2}:\d{2}), (?P<speaker>.+?) : (?P<text>.*)$"
)

SYSTEM_PATTERNS = ("님이 들어왔습니다.", "님이 나갔습니다.", "님을 초대했습니다.")

@dataclass(frozen=True)
class Message:
    message_id: str
    conversation_id: str
    timestamp: str
    speaker: str
    is_russell: bool
    text: str
    source_file: str

def parse_korean_datetime(value: str) -> datetime:
    # Locale-independent: %p does not understand Korean 오전/오후 on many CI systems.
    m = re.fullmatch(
        r"(\d{4})년 (\d{1,2})월 (\d{1,2})일 (오전|오후) (\d{1,2}):(\d{2})",
        value,
    )
    if not m:
        raise ValueError(f"Unsupported KakaoTalk timestamp: {value!r}")
    year, month, day, period, hour, minute = m.groups()
    hour = int(hour)
    if not 1 <= hour <= 12:
        raise ValueError(f"Invalid 12-hour clock value: {hour}")
    if period == "오전":
        hour = 0 if hour == 12 else hour
    else:
        hour = 12 if hour == 12 else hour + 12
    return datetime(int(year), int(month), int(day), hour, int(minute))

def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()

def stable_id(conversation_id: str, timestamp: str, speaker: str, text: str) -> str:
    payload = "\x1f".join((conversation_id, timestamp, speaker, text))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]

def conversation_id_for(path: Path, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    stem = re.sub(r"\s*\(\d+\)$", "", path.stem)
    return hashlib.sha256(stem.encode("utf-8")).hexdigest()[:16]

def parse_export(path: str | Path, aliases: Iterable[str],
                 conversation_id: str | None = None) -> list[Message]:
    path = Path(path)
    aliases = {x.strip() for x in aliases if x.strip()}
    cid = conversation_id_for(path, conversation_id)
    raw = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    rows: list[tuple[str, str, list[str]]] = []

    for line in raw:
        m = LINE_RE.match(line)
        if m:
            rows.append((m.group("date"), m.group("speaker"), [m.group("text")]))
        elif rows:
            rows[-1][2].append(line)

    out: list[Message] = []
    for date_s, speaker, parts in rows:
        text = normalize_text("\n".join(parts))
        if not text or any(text.endswith(p) for p in SYSTEM_PATTERNS):
            continue
        ts = parse_korean_datetime(date_s).isoformat(timespec="minutes")
        out.append(Message(
            message_id=stable_id(cid, ts, speaker, text),
            conversation_id=cid,
            timestamp=ts,
            speaker=speaker,
            is_russell=speaker in aliases,
            text=text,
            source_file=path.name,
        ))
    return out

def to_dicts(messages: Iterable[Message]) -> list[dict]:
    return [asdict(m) for m in messages]
