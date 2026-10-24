# isaac-corpus

Private-first conversation corpus tooling for **RussellLM**, stylometry, and persona research.

The repository contains **code only**. KakaoTalk exports and generated corpora are ignored by Git and must stay private.

## v0

- Parse KakaoTalk text exports
- Preserve multiline messages
- Mark Russell aliases
- Generate deterministic message IDs
- Incrementally merge re-exports without duplicating old messages
- Store the canonical corpus as compressed Parquet

## Install

```powershell
git clone https://github.com/NaNIsaac/isaac-corpus.git
cd isaac-corpus
uv sync
```

## Import a room

```powershell
uv run kakao-import "raw/kakao/KakaoTalkChats.txt" `
  --conversation-id python-room
```

Re-export the same room later and run the command again. Existing messages are deduplicated; only unseen messages are added. Keep the same `--conversation-id` for the same KakaoTalk room.

## Privacy

Never commit KakaoTalk exports, ChatGPT exports, generated Parquet/JSONL corpora, or private attachments. `.gitignore` blocks these by default.

## Next

- ChatGPT importer with canonical-branch reconstruction
- context windows (`previous N -> Russell response`)
- anonymization/pseudonymization
- register/relationship labels
- RussellLM retrieval layer
- stylometry benchmark
