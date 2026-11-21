#!/usr/bin/env python3
"""
doclib.py — آرشیو اسناد چندمجموعه‌ای

ساختار:
  documents/
    index.db                     SQLite ایندکس
    collections/<name>/
      raw/{files,web,audio,images}
      wiki/{index.md,log.md,sources,entities,concepts}

دستورها:
  add <path> [--collection NAME]       افزودن فایل یا پوشه به ایندکس
  search "<query>" [--collection NAME] جستجو (بدون NAME = همه مجموعه‌ها)
  list [--collection NAME]             فهرست فایل‌ها
  show <file_id>                       نمایش چانک‌ها
  rm <file_id>                         حذف از ایندکس
  reindex [--collection NAME]          بازسازی ایندکس
  stats                                آمار
  collections                          فهرست مجموعه‌ها
"""

import argparse
import hashlib
import os
import re
import sqlite3
import sys
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/opt/data"))

# پوشه اسناد در کنار HOME نیست؛ مسیر قطعی /opt/data/documents است.
ROOT = Path(os.environ.get("DOCLIB_ROOT", "/opt/data/documents"))
DB = ROOT / "index.db"
COLLECTIONS = ROOT / "collections"

CHUNK_SIZE = 1400
CHUNK_OVERLAP = 200

SOURCE_EXTS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "docx",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
    ".pptx": "pptx",
    ".txt": "text",
    ".md": "text",
    ".csv": "text",
    ".json": "text",
    ".html": "text",
}


# ---------------------------------------------------------------- نرمال‌سازی
_ARABIC_MAP = {
    "\u064a": "ی",  # ي → ی
    "\u0643": "ک",  # ك → ک
    "\u0629": "ه",  # ة → ه
    "\u0649": "ی",  # ى → ی
    "\u0623": "ا",
    "\u0625": "ا",
    "\u0622": "ا",
    "\u0624": "و",
    "\u0626": "ی",
    # اعراب — حذف
    "\u064b": "", "\u064c": "", "\u064d": "", "\u064e": "",
    "\u064f": "", "\u0650": "", "\u0651": "", "\u0652": "",
    "\u0653": "", "\u0654": "",
}
_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_LATIN_DIGITS = "0123456789"

# نویسه‌هایی که «حذف» می‌شوند تا «تأخیر» و «تاخیر» یکی شوند
_DROP_CHARS = "".join(_ARABIC_MAP[c] for c in _ARABIC_MAP if _ARABIC_MAP[c] == "")

# همزه روی پایه — «تأخیر» → «تاخیر» ولی «مسئول» → «مسيول» این‌طور نمی‌شود
# پس نرمال‌سازی تهاجمی جدا از نرمال‌سازی ذخیره‌سازی است.
_SEARCH_FOLD = {
    "\u0623": "ا", "\u0625": "ا", "\u0622": "ا",
    "\u0624": "و", "\u0626": "ی",
    "\u0629": "ه", "\u0649": "ی",
    "\u064a": "ی", "\u0643": "ک",
}


def normalize(text: str) -> str:
    """نرمال‌سازی برای ذخیره: نیم‌فاصله، حروف عربی، ارقام را یکسان می‌کند."""
    if not text:
        return ""
    text = text.replace("\u200c", " ").replace("\u200d", "")
    for a, p in _ARABIC_MAP.items():
        text = text.replace(a, p)
    for d in _PERSIAN_DIGITS:
        text = text.replace(d, _LATIN_DIGITS[_PERSIAN_DIGITS.index(d)])
    for d in _ARABIC_DIGITS:
        text = text.replace(d, _LATIN_DIGITS[_ARABIC_DIGITS.index(d)])
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def match_fold(text: str) -> str:
    """
    فرم تهاجمی برای مطابقت: همزه و اعراب حذف، حروف عربی → فارسی،
    و «آ/أ/إ/ا» همه به «ا» تبدیل می‌شوند تا «تأخیر» == «تاخیر».
    """
    if not text:
        return ""
    text = normalize(text)
    for a, p in _SEARCH_FOLD.items():
        text = text.replace(a, p)
    text = re.sub(r"[^\w\s]", " ", text)   # جداکننده‌ها → فاصله
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fts_query(q: str) -> str:
    """
    تبدیل کوئری کاربر به عبارت FTS5.
    هر واژه جدا match می‌شود (AND) و واژه‌های تک‌حرفی حذف می‌شوند.
    """
    q = match_fold(q)
    tokens = [t for t in q.split() if len(t) > 1]
    if not tokens:
        return ""
    return " AND ".join(f'"{t}"*' for t in tokens)


# ---------------------------------------------------------------- پایگاه‌داده
SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    file_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    collection  TEXT NOT NULL,
    name        TEXT NOT NULL,
    rel_path    TEXT NOT NULL,
    source_type TEXT NOT NULL,
    size        INTEGER,
    sha256      TEXT,
    n_chunks    INTEGER DEFAULT 0,
    added_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection, rel_path)
);

CREATE TABLE IF NOT EXISTS chunks (
    file_id INTEGER NOT NULL,
    idx     INTEGER NOT NULL,
    page    INTEGER,
    text    TEXT NOT NULL,
    fts_key TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (file_id, idx),
    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    fts_key,
    content='chunks',
    content_rowid='rowid',
    tokenize="unicode61 remove_diacritics 2"
);

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, fts_key) VALUES (new.rowid, new.fts_key);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, fts_key) VALUES ('delete', old.rowid, old.fts_key);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, fts_key) VALUES ('delete', old.rowid, old.fts_key);
    INSERT INTO chunks_fts(rowid, fts_key) VALUES (new.rowid, new.fts_key);
END;

CREATE INDEX IF NOT EXISTS idx_chunks_file ON chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_files_coll ON files(collection);
"""


def db():
    ROOT.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------- استخراج متن
def extract_pdf(path: Path):
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    out = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            out.append((i, page.extract_text() or ""))
        except Exception as e:
            out.append((i, f"[خطا در استخراج صفحه {i}: {e}]"))
    return out


def extract_docx(path: Path):
    try:
        import docx
        d = docx.Document(str(path))
        parts = []
        for p in d.paragraphs:
            if p.text.strip():
                parts.append(p.text)
        for ti, table in enumerate(d.tables, start=1):
            parts.append(f"\n[جدول {ti}]")
            for row in table.rows:
                cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                parts.append(" | ".join(cells))
        return [(None, "\n".join(parts))]
    except Exception:
        # فایل DOCX خراب/غیراستاندارد — استخراج خام XML به‌عنوان جایگزین
        return [(None, _docx_raw_xml(path))]


def _docx_raw_xml(path: Path):
    """استخراج متن از word/document.xml بدون کتابخانه، وقتی python-docx شکست بخورد."""
    import zipfile
    import html

    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<w:tab[^>]*/>", " ", xml)
        xml = re.sub(r"<[^>]+>", "", xml)
        text = html.unescape(xml)
        return re.sub(r"\n{3,}", "\n\n", text).strip()
    except Exception as e:
        return f"[استخراج DOCX ناموفق: {e}]"


def extract_xlsx(path: Path):
    import openpyxl
    wb = openpyxl.load_workbook(str(path), data_only=True, read_only=True)
    out = []
    for sheet in wb.worksheets:
        lines = [f"\n[شیت: {sheet.title}]"]
        for row in sheet.iter_rows(values_only=True):
            cells = ["" if c is None else str(c) for c in row]
            if any(c.strip() for c in cells):
                lines.append(" | ".join(cells))
        out.append((None, "\n".join(lines)))
    wb.close()
    return out


def extract_pptx(path: Path):
    from pptx import Presentation
    prs = Presentation(str(path))
    out = []
    for i, slide in enumerate(prs.slides, start=1):
        parts = [f"[اسلاید {i}]"]
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                parts.append(shape.text_frame.text)
            if shape.has_table:
                for row in shape.table.rows:
                    parts.append(" | ".join(c.text.strip() for c in row.cells))
        out.append((i, "\n".join(parts)))
    return out


def extract_text(path: Path):
    for enc in ("utf-8", "utf-8-sig", "cp1256", "latin-1"):
        try:
            return [(None, path.read_text(encoding=enc))]
        except UnicodeDecodeError:
            continue
    return [(None, path.read_text(errors="replace"))]


EXTRACTORS = {
    "pdf": extract_pdf,
    "docx": extract_docx,
    "xlsx": extract_xlsx,
    "pptx": extract_pptx,
    "text": extract_text,
}


def chunkify(text: str):
    """متن را به تکه‌های همپوشان می‌شکند، ترجیحاً روی مرز جمله."""
    text = normalize(text)
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + CHUNK_SIZE, n)
        if end < n:
            window = text[start:end]
            for sep in ("\n\n", ". ", "؟ ", "! ", "\n"):
                pos = window.rfind(sep)
                if pos > CHUNK_SIZE * 0.5:
                    end = start + pos + len(sep)
                    break
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


# ---------------------------------------------------------------- عملیات
def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def detect_source_type(path: Path) -> str:
    return SOURCE_EXTS.get(path.suffix.lower(), "")


def rel_path_of(path: Path, collection: str) -> str:
    """مسیر نسبی نسبت به raw/ مجموعه (یا خود مجموعه اگر بیرون raw باشد)."""
    raw = COLLECTIONS / collection / "raw"
    try:
        return str(path.resolve().relative_to(raw.resolve()))
    except ValueError:
        return str(path.resolve().relative_to((COLLECTIONS / collection).resolve()))


def add_file(conn, path: Path, collection: str, verbose=True):
    stype = detect_source_type(path)
    if not stype:
        if verbose:
            print(f"  رد شد (پسوند پشتیبانی نمی‌شود): {path.name}")
        return None

    rel = rel_path_of(path, collection)
    extractor = EXTRACTORS[stype]
    try:
        pages = extractor(path)
    except Exception as e:
        print(f"  ✗ خطای استخراج {path.name}: {e}")
        return None

    sha = sha256_of(path)
    existing = conn.execute(
        "SELECT file_id FROM files WHERE collection=? AND sha256=?", (collection, sha)
    ).fetchone()
    if existing:
        if verbose:
            print(f"  = از قبل هست: {path.name} (id={existing[0]})")
        return existing[0]

    cur = conn.execute(
        """INSERT INTO files (collection, name, rel_path, source_type, size, sha256)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (collection, path.name, rel, stype, path.stat().st_size, sha),
    )
    fid = cur.lastrowid

    idx = 0
    for page, text in pages:
        for piece in chunkify(text):
            conn.execute(
                "INSERT INTO chunks (file_id, idx, page, text, fts_key) VALUES (?, ?, ?, ?, ?)",
                (fid, idx, page, piece, match_fold(piece)),
            )
            idx += 1

    conn.execute("UPDATE files SET n_chunks=? WHERE file_id=?", (idx, fid))
    if verbose:
        print(f"  + {path.name} → {idx} تکه (id={fid})")
    return fid


def cmd_add(args):
    path = Path(args.path).expanduser()
    if not path.exists():
        print(f"مسیر پیدا نشد: {path}")
        return 1

    collection = args.collection
    if not collection:
        print("--collection لازم است. مجموعه‌های موجود:")
        cmd_collections(args)
        return 1

    coll_dir = COLLECTIONS / collection
    if not coll_dir.exists():
        print(f"مجموعه «{collection}» وجود ندارد. موجود: "
              f"{', '.join(sorted(p.name for p in COLLECTIONS.iterdir()))}")
        return 1

    conn = db()
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    if not files:
        print("فایلی پیدا نشد.")
        return 1

    print(f"افزودن به «{collection}» ({len(files)} فایل):")
    added = 0
    for f in files:
        if add_file(conn, f, collection):
            added += 1
    conn.commit()
    print(f"تمام. {added} فایل ایندکس شد.")
    conn.close()
    return 0


def cmd_search(args):
    conn = db()
    q = fts_query(args.query)
    if not q:
        print("کوئری خالی است.")
        return 1

    where = "WHERE chunks_fts MATCH ?"
    params = [q]
    if args.collection:
        where += " AND f.collection = ?"
        params.append(args.collection)
    if args.file:
        where += " AND f.name LIKE ?"
        params.append(f"%{args.file}%")

    sql = f"""
        SELECT f.collection, f.name, c.page, c.idx, c.text,
               bm25(chunks_fts) AS rank
        FROM chunks_fts
        JOIN chunks c ON c.rowid = chunks_fts.rowid
        JOIN files f ON f.file_id = c.file_id
        {where}
        ORDER BY rank
        LIMIT ?
    """
    params.append(args.limit)

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError as e:
        print(f"خطای جستجو: {e}")
        return 1

    if not rows:
        print(f"نتیجه‌ای برای «{args.query}» پیدا نشد.")
        return 0

    tokens = fts_query(args.query)
    print(f"{len(rows)} نتیجه برای «{args.query}»:\n")
    for coll, name, page, idx, text, _ in rows:
        loc = f"ص {page}" if page else f"تکه {idx}"
        print(f"[{coll}/{name} — {loc}]")
        print(f"  {make_snippet(text, tokens)}\n")
    conn.close()
    return 0


def make_snippet(text: str, query: str, width: int = 220) -> str:
    """برش متن اصلی اطراف اولین واژهٔ مطابق، با برجسته‌سازی واژه‌ها."""
    if not text:
        return ""
    flat = re.sub(r"\s+", " ", text).strip()

    terms = []
    for part in query.split(" AND "):
        t = part.strip().strip('"').rstrip("*")
        if t:
            terms.append(t)

    folded = match_fold(flat)
    pos = -1
    for t in terms:
        p = folded.find(t)
        if p != -1 and (pos == -1 or p < pos):
            pos = p

    if pos == -1:
        seg = flat[:width]
        return seg + ("…" if len(flat) > width else "")

    start = max(0, pos - width // 3)
    end = min(len(flat), start + width)
    seg = flat[start:end]

    for t in terms:
        seg = re.sub(f"({re.escape(t)})", r"»\1«", seg, flags=re.IGNORECASE)

    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(flat) else ""
    return f"{prefix}{seg}{suffix}"


def cmd_list(args):
    conn = db()
    sql = "SELECT file_id, collection, name, source_type, n_chunks, size, added_at FROM files"
    params = []
    if args.collection:
        sql += " WHERE collection = ?"
        params.append(args.collection)
    sql += " ORDER BY collection, name"
    rows = conn.execute(sql, params).fetchall()
    if not rows:
        print("آرشیو خالی است.")
        return 0
    cur_coll = None
    for fid, coll, name, stype, nch, size, added in rows:
        if coll != cur_coll:
            print(f"\n=== {coll} ===")
            cur_coll = coll
        print(f"  [{fid:3d}] {name}  ({stype}, {nch} تکه, {(size or 0)//1024}KB, {added[:10]})")
    conn.close()
    return 0


def cmd_show(args):
    conn = db()
    row = conn.execute(
        "SELECT name, collection FROM files WHERE file_id=?", (args.file_id,)
    ).fetchone()
    if not row:
        print("file_id پیدا نشد.")
        return 1
    print(f"=== {row[1]}/{row[0]} ===\n")
    for idx, page, text in conn.execute(
        "SELECT idx, page, text FROM chunks WHERE file_id=? ORDER BY idx", (args.file_id,)
    ):
        loc = f"ص{page}" if page else f"تکه {idx}"
        print(f"--- {loc} ---\n{text}\n")
    conn.close()
    return 0


def cmd_rm(args):
    conn = db()
    row = conn.execute("SELECT name FROM files WHERE file_id=?", (args.file_id,)).fetchone()
    if not row:
        print("file_id پیدا نشد.")
        return 1
    conn.execute("DELETE FROM chunks WHERE file_id=?", (args.file_id,))
    conn.execute("DELETE FROM files WHERE file_id=?", (args.file_id,))
    conn.commit()
    print(f"حذف شد از ایندکس: {row[0]} (فایل اصلی دست‌نخورده است)")
    conn.close()
    return 0


def cmd_reindex(args):
    conn = db()
    sql = "SELECT file_id, collection, rel_path FROM files"
    params = []
    if args.collection:
        sql += " WHERE collection = ?"
        params.append(args.collection)
    rows = conn.execute(sql, params).fetchall()
    for fid, coll, rel in rows:
        conn.execute("DELETE FROM chunks WHERE file_id=?", (fid,))
        path = COLLECTIONS / coll / "raw" / rel
        if not path.exists():
            path = COLLECTIONS / coll / rel
        if not path.exists():
            print(f"  ! فایل نیست: {coll}/{rel}")
            continue
        stype = detect_source_type(path)
        if not stype:
            continue
        pages = EXTRACTORS[stype](path)
        idx = 0
        for page, text in pages:
            for piece in chunkify(text):
                conn.execute(
                    "INSERT INTO chunks (file_id, idx, page, text, fts_key) VALUES (?, ?, ?, ?, ?)",
                    (fid, idx, page, piece, match_fold(piece)),
                )
                idx += 1
        conn.execute("UPDATE files SET n_chunks=? WHERE file_id=?", (idx, fid))
        print(f"  ↻ {coll}/{rel} → {idx} تکه")
    conn.commit()
    conn.close()
    return 0


def cmd_stats(args):
    conn = db()
    total = conn.execute("SELECT COUNT(*), COALESCE(SUM(n_chunks),0) FROM files").fetchone()
    print(f"کل: {total[0]} فایل، {total[1]} تکه\n")
    for coll, nf, nch in conn.execute(
        """SELECT collection, COUNT(*), COALESCE(SUM(n_chunks),0)
           FROM files GROUP BY collection ORDER BY collection"""
    ):
        print(f"  {coll:24s} {nf:3d} فایل، {nch:5d} تکه")
    conn.close()
    return 0


def cmd_collections(args):
    if not COLLECTIONS.exists():
        print("پوشه collections نیست.")
        return 1
    for p in sorted(COLLECTIONS.iterdir()):
        if p.is_dir():
            desc = ""
            cm = p / "COLLECTION.md"
            if cm.exists():
                for line in cm.read_text(encoding="utf-8").splitlines():
                    if line.startswith("> "):
                        desc = line[2:].strip()
                        break
            print(f"  {p.name:24s} {desc}")
    return 0


def _wiki_dirs(collection=None):
    """تمام پوشه‌های wiki، یا فقط یکی."""
    if collection:
        p = COLLECTIONS / collection / "wiki"
        return [p] if p.exists() else []
    if not COLLECTIONS.exists():
        return []
    return [p / "wiki" for p in sorted(COLLECTIONS.iterdir())
            if p.is_dir() and (p / "wiki").exists()]


LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def _scan_pages(wiki_dir):
    """همه صفحات md یک ویکی + لینک‌های خروجی هر کدام.
    برمی‌گرداند: {rel_path: [target_rel_path, ...]}
    """
    pages = {}
    if not wiki_dir.exists():
        return pages
    for md in sorted(wiki_dir.rglob("*.md")):
        rel = md.relative_to(wiki_dir).as_posix()
        targets = []
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            text = ""
        for _, href in LINK_RE.findall(text):
            href = href.split("#")[0].strip()
            if not href or href.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (md.parent / href).resolve()
            try:
                trel = resolved.relative_to(wiki_dir.resolve()).as_posix()
            except ValueError:
                continue  # لینک بیرون از wiki (مثلاً به raw/)
            if trel.endswith(".md"):
                targets.append(trel)
        pages[rel] = targets
    return pages


def cmd_links(args):
    wiki_dir = COLLECTIONS / args.collection / "wiki"
    if not wiki_dir.exists():
        print(f"ویکی این مجموعه نیست: {args.collection}")
        return 1
    pages = _scan_pages(wiki_dir)

    target = args.page
    if not target.endswith(".md"):
        target += ".md"
    target = target.lstrip("./")

    if target not in pages:
        hits = [p for p in pages if target.split("/")[-1] == p.split("/")[-1]]
        print(f"«{target}» در ویکی نیست.")
        if hits:
            print("شبیه این‌ها را داری:")
            for h in hits:
                print(f"  {h}")
        return 1

    out = pages[target]
    back = [p for p, ts in pages.items() if target in ts]

    print(f"=== {args.collection}/wiki/{target} ===\n")
    print(f"لینک‌های خروجی ({len(out)}):")
    for t in out:
        mark = "" if t in pages else "  ← شکسته"
        print(f"  → {t}{mark}")
    if not out:
        print("  (هیچ)")

    print(f"\nلینک‌های ورودی / backlinks ({len(back)}):")
    for b in back:
        print(f"  ← {b}")
    if not back:
        print("  (هیچ — این صفحه یتیم است)")
    return 0


def cmd_lint(args):
    dirs = _wiki_dirs(args.collection)
    if not dirs:
        print("هیچ ویکی‌ای پیدا نشد.")
        return 1

    issues = []
    page_count = 0

    for wiki_dir in dirs:
        coll = wiki_dir.parent.name
        pages = _scan_pages(wiki_dir)
        page_count += len(pages)

        # ۱. لینک شکسته
        for page, targets in pages.items():
            for t in targets:
                if t not in pages:
                    issues.append((coll, "لینک شکسته", f"{page} → {t}"))

        # ۲. صفحه یتیم (نه backlink دارد نه در index.md)
        index_targets = set(pages.get("index.md", []))
        for page in pages:
            if page in ("index.md", "log.md"):
                continue
            incoming = any(page in ts for p, ts in pages.items() if p != page)
            if not incoming and page not in index_targets:
                issues.append((coll, "صفحه یتیم", page))

        # ۳. صفحه‌ای که در index.md نیست
        for page in pages:
            if page in ("index.md", "log.md"):
                continue
            if page not in index_targets and pages.get("index.md") is not None:
                parent = page.split("/")[0]
                if parent in ("sources", "entities", "concepts"):
                    issues.append((coll, "در index نیست", page))

        # ۴. ارجاع به فایل خام که وجود ندارد
        raw_dir = wiki_dir.parent / "raw"
        for page, _ in pages.items():
            try:
                text = (wiki_dir / page).read_text(encoding="utf-8")
            except Exception:
                continue
            for _, href in LINK_RE.findall(text):
                href = href.split("#")[0].strip()
                if "/raw/" not in href and not href.startswith("../raw/"):
                    continue
                resolved = (wiki_dir / page).parent / href
                if not resolved.exists():
                    issues.append((coll, "منبع گم‌شده", f"{page} → {href}"))

        # ۵. صفحه بی‌منبع (هیچ ارجاعی به raw ندارد)
        if raw_dir.exists():
            for page in pages:
                if page in ("index.md", "log.md") or page.startswith(("entities/", "concepts/")):
                    continue
                try:
                    text = (wiki_dir / page).read_text(encoding="utf-8")
                except Exception:
                    continue
                if "/raw/" not in text and "../raw/" not in text:
                    issues.append((coll, "صفحه بی‌منبع", page))

        # ۶. عنوان تکراری
        titles = {}
        for page in pages:
            try:
                first = (wiki_dir / page).read_text(encoding="utf-8").splitlines()[:3]
            except Exception:
                continue
            for line in first:
                if line.startswith("# "):
                    t = line[2:].strip()
                    if t:
                        titles.setdefault(t, []).append(page)
                    break
        for t, ps in titles.items():
            if len(ps) > 1:
                issues.append((coll, "عنوان تکراری", f"«{t}»: {', '.join(ps)}"))

    print(f"ویکی: {page_count} صفحه در {len(dirs)} مجموعه\n")
    if not issues:
        print("✅ هیچ ایرادی پیدا نشد.")
        return 0

    order = ["لینک شکسته", "منبع گم‌شده", "صفحه یتیم", "در index نیست",
             "صفحه بی‌منبع", "عنوان تکراری"]
    counts = {}
    for coll in sorted({c for c, _, _ in issues}):
        rows = [i for i in issues if i[0] == coll]
        print(f"=== {coll} === ({len(rows)} ایراد)")
        for kind in order:
            hits = [d for _, k, d in rows if k == kind]
            if not hits:
                continue
            counts[kind] = counts.get(kind, 0) + len(hits)
            print(f"  [{kind}] {len(hits)}")
            for h in hits[:20]:
                print(f"     - {h}")
            if len(hits) > 20:
                print(f"     ... و {len(hits) - 20} مورد دیگر")
        print()

    print("خلاصه:")
    for kind in order:
        if kind in counts:
            print(f"  {kind}: {counts[kind]}")
    return 0


def cmd_graph(args):
    dirs = [COLLECTIONS / args.collection / "wiki"] if args.collection else _wiki_dirs()
    for wiki_dir in dirs:
        if not wiki_dir.exists():
            continue
        coll = wiki_dir.parent.name
        pages = _scan_pages(wiki_dir)
        if not pages:
            print(f"=== {coll} === (خالی)\n")
            continue
        print(f"=== {coll} === ({len(pages)} صفحه)\n")
        rows = []
        for page, targets in sorted(pages.items()):
            back = sum(1 for ts in pages.values() if page in ts)
            rows.append((page, len(targets), back))
        rows.sort(key=lambda r: -r[2])
        for page, out_n, in_n in rows:
            bar = "█" * min(in_n, 20)
            print(f"  {in_n:3d}←  {page:40s} {out_n:2d}→  {bar}")
        print()


def main():
    ap = argparse.ArgumentParser(description="آرشیو اسناد چندمجموعه‌ای")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="افزودن فایل/پوشه")
    p.add_argument("path")
    p.add_argument("--collection", "-c")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("search", help="جستجو")
    p.add_argument("query")
    p.add_argument("--collection", "-c")
    p.add_argument("--file", "-f")
    p.add_argument("--limit", "-n", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("list", help="فهرست فایل‌ها")
    p.add_argument("--collection", "-c")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="نمایش تکه‌های یک فایل")
    p.add_argument("file_id", type=int)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("rm", help="حذف از ایندکس")
    p.add_argument("file_id", type=int)
    p.set_defaults(func=cmd_rm)

    p = sub.add_parser("reindex", help="بازسازی ایندکس")
    p.add_argument("--collection", "-c")
    p.set_defaults(func=cmd_reindex)

    p = sub.add_parser("stats", help="آمار")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("collections", help="فهرست مجموعه‌ها")
    p.set_defaults(func=cmd_collections)

    p = sub.add_parser("links", help="لینک‌های ورودی/خروجی یک صفحه ویکی")
    p.add_argument("page", help="مثلاً sources/steel-plant-contract")
    p.add_argument("--collection", "-c", required=True)
    p.set_defaults(func=cmd_links)

    p = sub.add_parser("lint", help="بازبینی سلامت ویکی")
    p.add_argument("--collection", "-c")
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("graph", help="نقشه لینک‌های ویکی")
    p.add_argument("--collection", "-c")
    p.set_defaults(func=cmd_graph)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
