# Design Decisions

## Why Hybrid?
| Approach | Problem |
|---|---|
| Pure Karpathy | No PDF extraction, no Persian FTS, no instant point queries |
| Pure SQL | No synthesis, no link graph, no analytical path |
| **Hybrid** | SQLite for extraction/search, Wiki for synthesis |

## Trade-offs
| Chose | Rejected | Reason |
|---|---|---|
| SQLite + FTS5 | PostgreSQL/MySQL | Single file, no server |
| External-content FTS | FTS on `text` | Display original, search folded |
| `fts_key` column | Computed trigger | Simpler, faster |
| BM25 | Vector embeddings | Built-in, fast |
| Karpathy `index.md` | Auto-index | Human curation |
| Wiki indexed in SQLite | Wiki only in FS | Wiki searchable for Query Path 2 |

## Persian Handling
1. Two normalization functions (storage vs search)
2. Digits → Latin in storage; search works with any script
3. Wiki numbers: write both "۱۰" and "10" or rely on fold
4. No local OCR — model reads images; `raw/images/*.md` stores reading

## Ingest Discipline
- No auto-ingest — human confirms collection
- Raw immutable — new version = new file
- Wiki page MUST be `add`ed (bug: invisible to search without)
- `lint` mandatory — zero errors after ingest
- Extend, don't create — search before new page

## Rejected
- Local OCR (pytesseract/easyocr/rapidocr) — removed
- Heavy deps (numpy/opencv/onnx) — removed after disk pressure
- PostgreSQL/MySQL — overkill
- Vector embeddings — not needed
- Auto-classification — human judgment required
