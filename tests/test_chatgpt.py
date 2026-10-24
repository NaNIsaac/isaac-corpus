import json
from pathlib import Path
from isaac_corpus.chatgpt import canonical_messages
from isaac_corpus.context import build_response_examples

def test_canonical_branch_and_context(tmp_path: Path):
    conv = [{
        "conversation_id": "c1",
        "current_node": "a2",
        "mapping": {
            "u1": {"id":"u1","parent":None,"message":{
                "id":"m1","author":{"role":"user"},"create_time":1,
                "content":{"parts":["질문"]}}},
            "a1": {"id":"a1","parent":"u1","message":{
                "id":"m2","author":{"role":"assistant"},"create_time":2,
                "content":{"parts":["옛 답변"]}}},
            "a2": {"id":"a2","parent":"u1","message":{
                "id":"m3","author":{"role":"assistant"},"create_time":3,
                "content":{"parts":["현재 답변"]}}},
        }
    }]
    p = tmp_path/"chat.html"
    p.write_text("<script>var jsonData = "+json.dumps(conv)+"; var assetsJson = {}</script>")
    rows = canonical_messages(p)
    assert [x.text for x in rows] == ["질문", "현재 답변"]

    data = [
        {"conversation_id":"x","message_id":"a","timestamp":"1","role":"assistant","text":"A"},
        {"conversation_id":"x","message_id":"u","timestamp":"2","role":"user","text":"러셀 응답"},
    ]
    ex = build_response_examples(data, 2)
    assert ex[0]["response"] == "러셀 응답"
    assert ex[0]["context"][0]["text"] == "A"
