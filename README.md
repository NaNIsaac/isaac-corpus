# isaac-corpus

Private-first conversation corpus tooling for **RussellLM**, stylometry, and persona research.

**Code is public; conversations are not.** KakaoTalk/ChatGPT exports, generated corpora, and attachments are ignored by Git.

## What works

- KakaoTalk TXT export parsing
- multiline message preservation
- Russell alias labeling
- deterministic IDs + incremental deduplication
- Parquet corpus storage
- ChatGPT `chat.html` parsing
- canonical branch reconstruction via `current_node -> parent`
- context → Russell-response dataset building

## Install

```powershell
git clone https://github.com/NaNIsaac/isaac-corpus.git
cd isaac-corpus
uv sync --extra dev
uv run pytest
```

## Incrementally import KakaoTalk

```powershell
uv run kakao-import "raw/kakao/KakaoTalkChats.txt" --conversation-id python-room
```

Export the same room again later and rerun the command. Keep the same
`--conversation-id`; deterministic message IDs prevent old messages from being added twice.

## Import ChatGPT

Put your exported `chat.html` outside Git or under an ignored directory:

```powershell
uv run chatgpt-import "raw/chatgpt/chat.html"
```

The importer follows each conversation's selected `current_node` back through its parents.
Discarded/regenerated branches therefore do not silently become persona training data.

## Persona direction

The intended unit is not merely a Russell sentence. It is:

```text
conversation context
→ Russell response
→ register / relationship / state metadata
```

That supports retrieval-based RussellLM first, then controlled SFT/LoRA experiments later.

## Privacy

Never commit raw conversations or generated corpora. The repository's
`.gitignore` blocks common exports and corpus formats by default.

## Next

- pseudonymization/anonymization
- relationship/register labels
- retrieval index for RussellLM
- cross-platform Russell stylometry benchmark
- incremental import manifest and export watcher
