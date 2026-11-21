# Skills & Automation

This project uses **Hermes Agent skills** as persistent operational memory. The skill encapsulates the entire ingest/query/lint workflow so it survives session boundaries (`/new`, restarts, compression).

## Skill: `document-archive`

**Location:** `/opt/data/skills/productivity/document-archive/SKILL.md`  
**Category:** `productivity`  
**Loads:** Automatically in every session (skill system injects description + full content on `skill_view`)

### What the Skill Encodes

| Aspect | In Skill | In Wiki/Code |
|---|---|---|
| Ingest flow (8 steps) | ✅ Step-by-step with triggers | ✅ `Ingest-Workflow.md` |
| Query dual-path | ✅ Decision rules + examples | ✅ `Architecture.md` |
| Lint discipline | ✅ 6 script checks + human content rules | ✅ `Wiki-Layer.md` |
| Collection routing | ✅ Human confirmation required | ✅ `Design-Decisions.md` |
| Persian normalization | ✅ Two-layer rules | ✅ `Architecture.md` |
| CLI commands | ✅ All 11 mapped to Karpathy ops | ✅ `CLI-Reference.md` |
| File naming conventions | ✅ English short names, date prefixes | ✅ `Architecture.md` |
| Extend-don't-create | ✅ Explicit rule | ✅ `Design-Decisions.md` |

### Skill Content (Full)

The skill is a Markdown file with YAML frontmatter. Key sections:

```markdown
---
name: document-archive
description: Use for the user's document archive - ingest or search.
---

# آرشیو اسناد چندمجموعه‌ای

## ساختار
/opt/data/documents/
├── SCHEMA.md          ← قانون اساسی آرشیو (اول بخوان)
├── index.db           ← SQLite + FTS5
├── doclib.py          ← اسکریپت استخراج/ایندکس/جستجو
└── collections/<name>/
    ├── COLLECTION.md  ← موضوع این مجموعه
    ├── raw/{files,web,audio,images}
    └── wiki/{index.md,log.md,sources,entities,concepts}

مجموعه‌های موجود: `office-works`, `maintenance-learning`, `ai-learning`.

## قواعد سخت
1. هرگز محتوای `raw/` را تغییر نده.
2. هیچ فایلی بدون تأیید کاربر اضافه نمی‌شود.
3. هر عدد در `wiki/` باید ارجاع داشته باشد.
4. Extend, don't create.
5. `entities/` و `concepts/` فقط وقتی لازم شد.
6. فایل `.md` همراه در `raw/`...

## جریان ingest (8 steps)
1. فایل را به پوشه درست `raw/` کپی کن
2. `doclib.py add <path> -c <collection>`
3. من `wiki/sources/x.md` می‌نویسم
4. **`doclib.py add` روی صفحه ویکی هم بزن** ← critical bug fix
5. من `index.md` + `log.md` بروز می‌کنم
6. `doclib.py lint -c <collection>`
7. به کاربر گزارش بده

## پردازش انواع منبع (PDF, DOCX, Image, Audio, Web)
...

## جستجو — دو مسیر
مسیر ۱ — نقطه‌ای: `search` → SQLite
مسیر ۲ — تحلیلی: `index.md` → `links` → ترکیب

## لایه ویکی — ابزارها
`links`, `lint`, `graph` — full docs

## قرارداد صفحه ویکی
...

## نکات فنی مهم
- DOCLIB_ROOT = /opt/data/documents
- نرمال‌سازی دو لایه
- fts_key column
- DOCX fallback
...

## افزودن مجموعه جدید
...
```

### How the Skill Works in Practice

1. **Session start** → Hermes loads skill description into context
2. **User sends file/link/voice** → I read `SCHEMA.md` (via skill instruction) → follow ingest flow
3. **User asks question** → I apply Query dual-path (skill encodes the decision rules)
4. **After ingest** → I run `lint` (skill says mandatory)
5. **New collection needed** → Skill gives exact `mkdir` command + templates

### Skill vs. Wiki vs. Code

| Layer | Purpose | Audience |
|---|---|---|
| **Skill (`document-archive`)** | Operational memory — *how I execute* | Me (Hermes Agent) |
| **Wiki (this GitHub Wiki)** | Documentation — *how the system works* | Humans, future maintainers |
| **Code (`doclib.py`)** | Execution — *the actual machinery* | Runtime |

The skill is **not** in the GitHub repo — it lives in the Hermes profile at `/opt/data/skills/productivity/document-archive/`. To port this system to another Hermes instance, copy the skill directory + `doclib.py` + `SCHEMA.md` + collections structure.

### Related Skills

- `hermes-agent-skill-authoring` — for creating/editing skills
- `obsidian` — if using Obsidian as wiki frontend
- `weekly-review-planning` — for periodic archive reviews
