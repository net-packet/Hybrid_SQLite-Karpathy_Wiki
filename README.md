# Hybrid SQLite + Karpathy Wiki Archive / آرشیو ترکیبی SQLite + ویکی کارپتی

**A bilingual (Persian/English) document archive system combining SQLite FTS5 for instant search with Karpathy-style markdown wiki for synthesis.**

**سیستم آرشیو اسناد دوزبانه (فارسی/انگلیسی) که جستجوی لحظه‌ای SQLite FTS5 را با ویکی مارک‌داون به سبک کارپتی برای تحلیل و ترکیب ترکیب می‌کند.**

---

## ✨ Features / ویژگی‌ها

| Feature | English | فارسی |
|---|---|---|
| **Multi-collection** | Separate archives: `office-works`, `maintenance-learning`, `ai-learning` | چندمجموعه: `office-works`، `maintenance-learning`، `ai-learning` |
| **Source types** | PDF, DOCX, XLSX, PPTX, TXT, Web, Audio (Groq STT), Images (model vision) | PDF، DOCX، XLSX، PPTX، متن، وب، صدا (Groq STT)، عکس (ویژن مدل) |
| **Search** | Point queries → SQLite FTS5 (instant, cited) | سؤال نقطه‌ای → SQLite FTS5 (لحظه‌ای، با منبع) |
| **Synthesis** | Analytical queries → Wiki graph traversal | سؤال تحلیلی → پیمایش گراف ویکی |
| **Persian support** | Two-layer normalization (storage + search fold) | نرمال‌سازی دو لایه (ذخیره + جستجوی فولد) |
| **Bilingual** | Wiki content = source language; Response = question language | محتوای ویکی = زبان منبع؛ جواب = زبان سؤال |
| **Immutable raw** | Original files never modified | فایل‌های خام هرگز تغییر نمی‌کنند |
| **Human-in-the-loop** | No auto-ingest; user confirms collection | بدون ingest خودکار؛ تأیید کاربر الزامی |
| **Wiki lint** | Structural (broken links, orphans) + Content (number drift) | لنت ساختاری + محتوایی (انحراف اعداد) |
| **Portable** | Single `doclib.py` + SQLite file + markdown folders | واحد `doclib.py` + فایل SQLite + پوشه‌های مارک‌داون |

---

## 🚀 Quick Start / شروع سریع

```bash
# 1. Clone
git clone https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki.git
cd Hybrid_SQLite-Karpathy_Wiki

# 2. Bootstrap your local archive
python3 setup.py --root ~/my-archive

# 3. Install deps (one-time)
python3 -m pip install --user -r requirements.txt

# 4. Configure
export DOCLIB_ROOT=~/my-archive
echo "GROQ_API_KEY=your_key" >> ~/.env   # for audio STT

# 5. Use
python3 ~/my-archive/doclib.py add contract.pdf -c office-works
python3 ~/my-archive/doclib.py search "budget penalty"
python3 ~/my-archive/doclib.py lint -c office-works
```

---

## 📁 Structure / ساختار

```
~/my-archive/                    # DOCLIB_ROOT
├── SCHEMA.md                    # Constitution / قانون اساسی
├── index.db                     # SQLite + FTS5
├── doclib.py                    # Main script / اسکریپت اصلی
└── collections/
    ├── office-works/
    │   ├── COLLECTION.md        # Scope / دامنه
    │   ├── raw/{files,web,audio,images}
    │   └── wiki/{index.md,log.md,sources/,entities/,concepts/}
    ├── maintenance-learning/    # (same structure)
    └── ai-learning/             # (same structure)
```

---

## 📖 Documentation / مستندات

| Page | Description |
|---|---|
| [Home (SCHEMA)](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/Home) | Constitution: rules, contracts, query paths, commands / قانون اساسی: قواعد، قراردادها، مسیرهای پرسش، دستورات |
| [Ingest Workflow](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/Ingest-Workflow) | Step-by-step ingest for all source types / ingest قدم‌به‌قدم برای همه انواع منبع |
| [CLI Reference](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/CLI-Reference) | All 11 `doclib.py` commands / تمام ۱۱ دستور `doclib.py` |
| [Architecture](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/Architecture) | Data model, FTS5, trade-offs / مدل داده، FTS5، مقایسه‌ها |
| [Wiki Layer](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/Wiki-Layer) | `links`, `lint`, `graph` commands / دستورات `links`، `lint`، `graph` |
| [Design Decisions](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/Design-Decisions) | Why hybrid, schema choices / چرا ترکیبی، انتخاب‌های اسکیما |
| [Collections](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/Collection-office-works) | Scope & storage per collection / دامنه و ذخیره‌سازی هر مجموعه |
| [Skills & Automation](https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki/wiki/Skills-And-Automation) | Hermes skill as persistent memory / مهارت هرمز به عنوان حافظه دائمی |

---

## 🔑 Key Concepts / مفاهیم کلیدی

### Dual-Path Query / پرسش دو مسیری
1. **Point Query** (SQLite): "What was the penalty %?" → Instant, cited chunks
2. **Analytical Query** (Wiki): "3-year trend?" → Read `index.md` → Follow `links` → Synthesize
   - Analytical **never** goes direct to SQLite. Wiki is the starting point.
   - State which path you used in your answer.

### Language Rules / قواعد زبان
- **Wiki content** = source language (fa→fa, en→en)
- **Response** = question language (Persian Q → Persian A)
- **Filenames** = English short (`monthly-payment-report-1404.md`)
- **Mixed** = Persian with English terms in parentheses

### Wiki Contract / قرارداد ویکی
Every `sources/` page must have: `# Title`, `> One-line`, `## Summary`, `## Content`, `## Sources` (mandatory), `## Related`. `lint` enforces this.

---

## 🛠 Requirements / پیش‌نیازها

- Python 3.11+
- `pypdf`, `python-docx`, `openpyxl`, `python-pptx` (via `requirements.txt`)
- `ffmpeg` (for audio splitting >25MB)
- Groq API key (for Whisper STT) — optional, only for audio

---

## 📜 License / مجوز

MIT — Free to use, modify, distribute.

---

## 🙏 Credits / تقدیر

- **Karpathy Wiki Method** — Andrej Karpathy's [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- **Groq** — Fast Whisper inference
- **SQLite FTS5** — Full-text search engine
- **Hermes Agent** — Platform this was built on

---

**Built with Hermes Agent** — persistent skills, local-first, privacy-respecting.
