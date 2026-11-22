# Wiki Layer Commands

## `links`
```bash
python3 /opt/data/documents/doclib.py links sources/<page> -c <collection>
```
Outgoing (with ✓/✗), incoming backlinks, missing links.

## `lint`
```bash
python3 /opt/data/documents/doclib.py lint [-c <collection>]
```
6 checks: broken links, missing source, orphan, not in index, no sources, duplicate title. **Mandatory after every ingest.**

## `graph`
```bash
python3 /opt/data/documents/doclib.py graph [-c <collection>]
```
ASCII map: page | in-degree (← bar) | out-degree (→ bar).

## Page Contract
See Architecture.md. Key: relative paths, `## Sources` mandatory, `index.md` link mandatory, `## Related` for connectivity.

## `index.md` Structure
```markdown
# Collection
> Desc

## Sources
| # | Source | Type | Date | Wiki Page |
|---|---|---|---|---|
| 1 | Contract | PDF | 2026-11-20 | [contract](sources/contract.md) |

## Entities
- [Pars Steel](../entities/pars-steel.md)

## Concepts
- [Delay Penalty](../concepts/delay-penalty.md)
```

## `log.md` Structure
```markdown
# Log

## YYYY-MM-DD — Title
- Raw: `raw/files/...`
- Wiki: `wiki/sources/...`
- File ID: 3
- Chunks: 22
```
