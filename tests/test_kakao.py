from pathlib import Path
from isaac_corpus.kakao import parse_export

def test_parse_multiline_and_alias(tmp_path: Path):
    p = tmp_path / "room.txt"
    p.write_text(
        "2026년 3월 19일 오전 10:40, 러셀 : 첫줄\n"
        "둘째줄\n"
        "2026년 3월 19일 오전 10:41, 친구 : 답변\n",
        encoding="utf-8",
    )
    rows = parse_export(p, ["러셀"], conversation_id="room-1")
    assert len(rows) == 2
    assert rows[0].text == "첫줄\n둘째줄"
    assert rows[0].is_russell is True
    assert rows[1].is_russell is False

def test_stable_ids_across_reexport(tmp_path: Path):
    content = "2026년 3월 19일 오후 1:02, 러셀 : 어캐함\n"
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text(content, encoding="utf-8")
    b.write_text(content, encoding="utf-8")
    x = parse_export(a, ["러셀"], conversation_id="same-room")[0]
    y = parse_export(b, ["러셀"], conversation_id="same-room")[0]
    assert x.message_id == y.message_id
