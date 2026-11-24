# Skills & Automation

This project uses **Hermes Agent skills** as persistent operational memory. The skill encapsulates the entire ingest/query/lint workflow so it survives session boundaries (`/new`, restarts, compression).

## Skill: `document-archive`

**Location:** `/opt/data/skills/productivity/document-archive/SKILL.md`
**Category:** `productivity`
**Size:** ~484 lines + 9 reference files (~54 KB)
**Loads:** On `skill_view(name='document-archive')` — the description is injected into every session's context

### What the Skill Encodes

| Aspect | In Skill | In Wiki/Code |
|---|---|---|
| Hard rules (8) | ✅ Approval gate, evidence-before-claiming | ✅ `Ingest-Workflow.md` |
| Ingest flow (6 steps) | ✅ Exact order: add → wiki page → `doclib.py add` → log | ✅ `Ingest-Workflow.md` |
| Query dual-path | ✅ Decision rules + fallback chain | ✅ `Architecture.md` |
| Lint discipline | ✅ Script checks + human content rules | ✅ `Wiki-Layer.md` |
| Collection routing | ✅ Human confirmation required | ✅ `Design-Decisions.md` |
| Persian normalization | ✅ Two-layer (storage + search fold) | ✅ `Architecture.md` |
| CLI commands (14) | ✅ All mapped, incl. `ur-*` | ✅ `CLI-Reference.md` |
| File naming conventions | ✅ English short names, date prefixes | ✅ `Architecture.md` |
| Extend-don't-create | ✅ Explicit rule | ✅ `Design-Decisions.md` |
| Reference Map | ✅ 9-entry routing table | ✅ `references/` in this repo |

### Where the Skill Lives in This Repo

The full skill content is mirrored here — **this page is not a copy of it**:

| Skill artifact | Mirror in repo |
|---|---|
| `SKILL.md` (main instructions) | [`Ingest-Workflow.md`](Ingest-Workflow.md) |
| `references/bootstrap.md` | [`references/bootstrap.md`](references/bootstrap.md) |
| `references/collection-scope.md` | [`references/collection-scope.md`](references/collection-scope.md) |
| `references/ingest-procedures.md` | [`references/ingest-procedures.md`](references/ingest-procedures.md) |
| `references/wiki-page-contract.md` | [`references/wiki-page-contract.md`](references/wiki-page-contract.md) |
| `references/living-source.md` | [`references/living-source.md`](references/living-source.md) |
| `references/dual-path-query.md` | [`references/dual-path-query.md`](references/dual-path-query.md) |
| `references/persian-normalization.md` | [`references/persian-normalization.md`](references/persian-normalization.md) |
| `references/wiki-lint.md` | [`references/wiki-lint.md`](references/wiki-lint.md) |
| `references/github-wiki-setup.md` | [`references/github-wiki-setup.md`](references/github-wiki-setup.md) |

**Rule:** `SKILL.md` is the single source of truth. This page explains the skill's *role and architecture* only — for the actual instructions, read `Ingest-Workflow.md`.

### How the Skill Works in Practice

1. **Session start** → Hermes injects the skill description into context
2. **User sends file/link/voice** → read `SCHEMA.md` → follow ingest flow
3. **User asks a point question** → SQLite FTS5 `search`
4. **User asks an analytical question** → wiki `index.md` → `links` graph traversal, then targeted `search` fallback
5. **After ingest** → run `lint` (mandatory before reporting)
6. **New collection needed** → skill gives exact `mkdir` sequence + templates

### Skill vs. Wiki vs. Code

| Layer | Purpose | Audience |
|---|---|---|
| **Skill (`document-archive`)** | Operational memory — *how I execute* | Hermes Agent |
| **Wiki (this repo + GitHub Wiki)** | Documentation — *how the system works* | Humans, future maintainers |
| **Code (`doclib.py`)** | Execution — *the actual machinery* | Runtime |

The skill is **not** loaded from this repo — it lives in the Hermes profile at `/opt/data/skills/productivity/document-archive/`. This repo carries a **mirror** so the system is portable: clone the repo, read `Ingest-Workflow.md` + `references/`, and you have the full operational knowledge.

To port the system to another Hermes instance: copy `doclib.py`, `SCHEMA.md`, the collections structure, and install the skill from the mirrored `Ingest-Workflow.md` + `references/`.

### Related Skills

- `hermes-agent-skill-authoring` — for creating/editing skills
- `obsidian` — if using Obsidian as wiki frontend
- `weekly-review-planning` — for periodic archive reviews
