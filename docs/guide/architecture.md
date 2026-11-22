# Architecture

## Data Model (SQLite)

```sql
CREATE TABLE files (
    file_id INTEGER PRIMARY KEY,
    collection TEXT NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    n_chunks INTEGER NOT NULL,
    mtime REAL NOT NULL,
    added_at REAL NOT NULL
);

CREATE TABLE chunks (
    file_id INTEGER NOT NULL,
    idx INTEGER NOT NULL,
    page INTEGER,
    text TEXT NOT NULL,
    fts_key TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (file_id, idx),
    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE
);
```

## FTS5 External Content Table

```sql
CREATE VIRTUAL TABLE chunks_fts USING fts5(
    fts_key,
    content='chunks',
    content_rowid='rowid',
    tokenize="unicode61 remove_diacritics 2"
);
```

Triggers: `chunks_ai`, `chunks_ad`, `chunks_au`.

## Chunking
- `CHUNK_SIZE = 1400`, `CHUNK_OVERLAP = 200`
- Page-aware (PDF/DOCX/PPTX), sheet-aware (XLSX)

## Persian Normalization (Two-Layer)
| Function | Purpose | Aggressiveness |
|---|---|---|
| `normalize()` | Storage | Mild — ZWNJ→space, ي/ك→ی/ک, strip diacritics, digits→Latin |
| `match_fold()` | Search | Aggressive — همزه/ة/ى collapse, "تأخیر"="تاخیر" |

- `fts_key` = `match_fold(text)` at index time
- Display uses original `text`

## Extractors
| Format | Library |
|---|---|
| PDF | `pypdf` |
| DOCX | `python-docx` + XML fallback |
| XLSX | `openpyxl` |
| PPTX | `python-pptx` |
| TXT/MD/CSV | stdlib |

## Wiki Layer
- `wiki/sources/` — 1 per source (mandatory)
- `wiki/entities/` — only when multi-source
- `wiki/concepts/` — only when multi-source
- `wiki/index.md` — curated TOC, must link all sources
- `wiki/log.md` — chronological log

### Page Contract (enforced by `lint`)
```markdown
# Title
> One-line description

## Summary
## Content
## Sources
- [Display](../../raw/.../file.ext) — p X
## Related
- [Other](../entities/x.md)
```
Relative paths. `lint` checks: broken links, missing sources, orphans, not in index, no-sources, duplicate titles.
