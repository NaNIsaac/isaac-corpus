from __future__ import annotations
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

def merge_parquet(rows: list[dict], output: str | Path) -> tuple[int, int, int]:
    output = Path(output)
    old = pq.read_table(output).to_pylist() if output.exists() else []
    by_id = {r["message_id"]: r for r in old}
    before = len(by_id)
    for row in rows:
        by_id.setdefault(row["message_id"], row)
    merged = sorted(by_id.values(), key=lambda r: (r["timestamp"], r["message_id"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(merged), output, compression="zstd")
    new = len(merged) - before
    return len(merged), new, len(rows) - new
