#!/usr/bin/env python3
"""
Bootstrap script for Hybrid SQLite + Karpathy Wiki Archive.
Run: python3 setup.py [--root /path/to/archive]
"""
import argparse, os, shutil, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

def run(cmd, cwd=None):
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("DOCLIB_ROOT", str(Path.home() / "documents")),
                    help="Archive root directory (default: ~/documents or $DOCLIB_ROOT)")
    ap.add_argument("--collections", nargs="+", default=["office-works", "maintenance-learning", "ai-learning"],
                    help="Collection names to create")
    ap.add_argument("--skip-install", action="store_true", help="Skip pip install")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    print(f"📁 Archive root: {root}")

    # 1. Install Python packages
    if not args.skip_install:
        print("\n📦 Installing Python packages...")
        run(f"{sys.executable} -m pip install --user -r {REPO_ROOT}/requirements.txt")

    # 2. Check ffmpeg
    print("\n🔍 Checking ffmpeg...")
    try:
        run("ffmpeg -version 2>&1 | head -1")
    except subprocess.CalledProcessError:
        print("⚠️  ffmpeg not found. Install it for audio STT:")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: winget install ffmpeg")

    # 3. Create directory structure
    print(f"\n📂 Creating collections: {args.collections}")
    for coll in args.collections:
        base = root / "collections" / coll
        for sub in ["raw/files", "raw/web", "raw/audio", "raw/images",
                    "wiki/sources", "wiki/entities", "wiki/concepts"]:
            (base / sub).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {coll}")

    # 4. Copy doclib.py
    dst = root / "doclib.py"
    shutil.copy2(REPO_ROOT / "doclib.py", dst)
    print(f"\n📄 Copied doclib.py → {dst}")

    # 5. Copy SCHEMA.md
    schema_src = REPO_ROOT / "Home.md"  # wiki Home.md = SCHEMA.md
    if schema_src.exists():
        shutil.copy2(schema_src, root / "SCHEMA.md")
        print(f"📄 Copied SCHEMA.md → {root}/SCHEMA.md")

    # 6. Create COLLECTION.md for each collection (from wiki Collection-*.md)
    for coll in args.collections:
        wiki_coll = REPO_ROOT / f"Collection-{coll}.md"
        if wiki_coll.exists():
            dst = root / "collections" / coll / "COLLECTION.md"
            shutil.copy2(wiki_coll, dst)
            print(f"📄 Copied COLLECTION.md → {dst}")

    # 7. Create empty wiki/index.md and wiki/log.md for each collection
    for coll in args.collections:
        wiki_dir = root / "collections" / coll / "wiki"
        # index.md
        idx = wiki_dir / "index.md"
        if not idx.exists():
            idx.write_text(f"""# فهرست منابع — {coll}

> {get_collection_desc(coll)}

## منابع

_(هنوز منبعی اضافه نشده)_

## موضوعات

_(هنوز صفحه entity یا concept ساخته نشده)_
""", encoding="utf-8")
        # log.md
        log = wiki_dir / "log.md"
        if not log.exists():
            log.write_text(f"""# تاریخچه — {coll}

## {coll}

مجموعه ساخته شد. آماده دریافت منبع.
""", encoding="utf-8")

    print("\n✅ Setup complete!")
    print(f"\nNext steps:")
    print(f"  1. export DOCLIB_ROOT={root}")
    print(f"  2. Add GROQ_API_KEY to .env (for audio STT)")
    print(f"  3. python3 {root}/doclib.py collections")
    print(f"  4. python3 {root}/doclib.py add <file> -c <collection>")

def get_collection_desc(coll):
    descs = {
        "office-works": "مکاتبات، قراردادها، بخشنامه‌ها، بودجه، صورت‌جلسات و گزارش عملکرد",
        "maintenance-learning": "نگهداشت پیشگیرانه و اصلاحی، رویه‌های فنی، عیب‌یابی، استانداردها",
        "ai-learning": "یادگیری ماشین، مدل‌های زبانی، ابزارهای AI، کاربرد در مدیریت پروژه"
    }
    return descs.get(coll, coll)

if __name__ == "__main__":
    main()
