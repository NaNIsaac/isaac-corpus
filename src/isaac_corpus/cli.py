from __future__ import annotations
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from .chatgpt import canonical_messages
from .kakao import parse_export, to_dicts
from .store import merge_parquet

DEFAULT_ALIASES = ["러셀", "sujebi", "라플란다우에", "Laplandaue", "우겐스타인", "Wuggenstein", "이삭"]

def kakao_main() -> None:
    p = argparse.ArgumentParser(prog="kakao-import")
    p.add_argument("exports", nargs="+", type=Path)
    p.add_argument("-o", "--output", type=Path, default=Path("corpus/messages.parquet"))
    p.add_argument("--alias", action="append", dest="aliases")
    p.add_argument("--conversation-id", help="Stable room ID for repeated exports.")
    args = p.parse_args()
    aliases = args.aliases or DEFAULT_ALIASES
    rows, russell = [], 0
    for path in args.exports:
        messages = parse_export(path, aliases, args.conversation_id)
        rows.extend(to_dicts(messages))
        russell += sum(m.is_russell for m in messages)
    total, new, dup = merge_parquet(rows, args.output)
    print(f"Parsed:      {len(rows):>8,}")
    print(f"New:         {new:>8,}")
    print(f"Duplicates:  {dup:>8,}")
    print(f"Russell:     {russell:>8,}")
    print(f"Corpus:      {total:>8,}")
    print(f"Output:      {args.output}")

def chatgpt_main() -> None:
    p = argparse.ArgumentParser(prog="chatgpt-import")
    p.add_argument("export", type=Path)
    p.add_argument("-o", "--output", type=Path, default=Path("corpus/chatgpt.jsonl"))
    args = p.parse_args()
    rows = canonical_messages(args.export)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")
    print(f"Canonical messages: {len(rows):,}")
    print(f"Output: {args.output}")
