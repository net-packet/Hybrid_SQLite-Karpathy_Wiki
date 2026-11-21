---
name: document-archive
description: Use for the user's document archive - ingest or search.
---

# آرشیو اسناد چندمجموعه‌ای / Multi-Collection Document Archive

کاربر یک آرشیو دائمی دارد در `/opt/data/documents/`.
User has a permanent archive at `/opt/data/documents/`.

**هر بار:** (1) فایل/لینک/ویس/عکس جدید رسید، یا (2) کاربر خواست در اسنادش بگردی، یا (3) سؤال درباره قرارداد/بودجه/نگهداشت/یادداشت‌هایش پرسید → اول این را بخوان:

```bash
cat /opt/data/documents/SCHEMA.md
```

**Every time:** (1) new file/link/voice/image arrives, or (2) user wants to search, or (3) question about contracts/budgets/maintenance/notes → read SCHEMA.md first.

## ساختار

```
/opt/data/documents/
├── SCHEMA.md          ← قانون اساسی آرشیو (اول بخوان)
├── index.db           ← SQLite + FTS5
├── doclib.py          ← اسکریپت استخراج/ایندکس/جستجو
└── collections/<name>/
    ├── COLLECTION.md  ← موضوع این مجموعه
    ├── raw/{files,web,audio,images}
    └── wiki/{index.md,log.md,sources,entities,concepts}
```

مجموعه‌های موجود: `office-works` (کارهای اداری / Admin Works), `maintenance-learning` (آموزش نگهداشت / Maintenance Learning), `ai-learning` (آموزش هوش مصنوعی / AI Learning).

**قاعده مقیاس‌بندی ویکی:** `entities/` و `concepts/` فقط وقتی ساخته می‌شوند که موضوع در **چند منبع** تکرار شده باشد. یک منبع → فقط `sources/` page. این از پر شدن ویکی با صفحات نیمه‌پر جلوگیری می‌کند.

**Wiki scaling rule:** `entities/` and `concepts/` only created when topic appears in **multiple sources**. One source → only `sources/` page. Prevents half-empty wiki pages.

## قواعد سخت / Hard Rules

1. **هرگز محتوای `raw/` را تغییر نده.** منبع حقیقت است.
   **Never modify `raw/` content.** It is the source of truth.
2. **هیچ فایلی بدون تأیید کاربر اضافه نمی‌شود.** اول موضوع را تشخیص بده، مجموعه را پیشنهاد بده، تأیید بگیر.
   **No file added without user confirmation.** Detect topic, propose collection, get approval.
3. **هر عدد در `wiki/` باید ارجاع داشته باشد** (فایل + صفحه). بدون ارجاع، عدد ننویس.
   **Every number in `wiki/` must have a citation** (file + page). No citation = no number.
4. **Extend, don't create** — قبل از ساخت صفحه جدید، جستجو کن صفحه‌ای هست یا نه.
   **Extend, don't create** — search before making a new page.
5. **`entities/` و `concepts/` فقط وقتی لازم شد** — نه از ابتدا.
   **`entities/` and `concepts/` only when needed** — not upfront.
6. **فایل `.md` همراه در `raw/`:** عکس → `<name>.md` (متنی که مدل خواند)، صدا → `<name>.transcript.md`.
   **Sidecar `.md` in `raw/`:** images → `<name>.md` (model's reading), audio → `<name>.transcript.md`.

## جریان ingest / Ingest Flow

1. فایل را به پوشه درست `raw/` کپی کن
   Copy file to correct `raw/` folder
2. ایندکس کن:
   ```bash
   python3 /opt/data/documents/doclib.py add <path> -c <collection>
   ```
   Index it
3. صفحه ویکی بساز در `wiki/sources/<short-english-name>.md` — با قرارداد کامل (پایین)
   Create wiki page at `wiki/sources/<short-english-name>.md` — full contract (below)
4. به صفحه جدید در `wiki/index.md` لینک بده — وگرنه lint آن را یتیم می‌بیند
   Link in `wiki/index.md` — or lint marks it orphan
5. `wiki/log.md` را آپدیت کن
   Update `wiki/log.md`
6. **`doclib.py add` روی صفحه ویکی هم بزن** — وگرنه ویکی در `search` پیدا نمی‌شود
   **`doclib.py add` the wiki page too** — or wiki invisible to search
7. `python3 /opt/data/documents/doclib.py lint -c <collection>` بزن و ایرادها را درست کن
   Run `lint`, fix all errors
8. به کاربر گزارش بده
   Report to user

## پردازش انواع منبع / Source Type Processing

| نوع / Type | روش / Method |
|---|---|
| PDF/DOCX/XLSX/PPTX/TXT/MD/CSV | `doclib.py add` (pypdf, python-docx, openpyxl, python-pptx) |
| عکس/اسکرین‌شات / Image/Screenshot | **خود مدل می‌خواند** — صفر نصب. متن را در `.md` کنار عکس بنویس، بعد ایندکس کن
   **Model reads directly** — zero install. Write text to `.md` beside image, then index |
| صدا/ویس / Voice/Audio | Groq Whisper → رونویسی را در `.transcript.md` بنویس، بعد ایندکس کن
   Groq Whisper → write transcript to `.transcript.md`, then index |
| لینک/بلاگ / Link/Blog | `web_extract` → markdown در `raw/web/YYYY-MM-DD-slug.md` با خط `source: <URL>`
   `web_extract` → markdown in `raw/web/YYYY-MM-DD-slug.md` with `source: <URL>` |

### گام‌های ingest برای لینک/بلاگ / Web Ingest Steps

1. `web_extract` — HTML را بگیر، تبلیغات/منو/فوتر را حذف کن (dev.to: خطوط بعد از `* * *` که ad است)
   `web_extract` — fetch HTML, strip ads/nav/footer (dev.to: lines after `* * *`)
2. فایل ذخیره در `raw/web/YYYY-MM-DD-slug.md` با هدر YAML:
   Save to `raw/web/YYYY-MM-DD-slug.md` with YAML header:
   ```yaml
   source: <URL>
   title: <عنوان>
   author: <نویسنده>
   published: <تاریخ>
   retrieved: <امروز>
   lang: <en/fa>
   ```
3. `doclib.py add` روی فایل خام
   `doclib.py add` on raw file
4. صفحه ویکی بساز در `wiki/sources/<short-english-name>.md` — **زبان ویکی = زبان منبع**
   Create wiki page — **wiki language = source language**
5. `doclib.py add` **روی صفحه ویکی هم بزن** — وگرنه صفحه ویکی در جستجو پیدا نمی‌شود (باگ واقعی، در تست پیدا شد)
   `doclib.py add` **on wiki page too** — or wiki invisible to search (real bug found in testing)
6. به `wiki/index.md` لینک بده + `wiki/log.md` آپدیت کن
   Link in `wiki/index.md` + update `wiki/log.md`
7. `lint` بزن
   Run `lint`

### رونویسی صدا با Groq / Groq STT

`whisper-large-v3` با زبان `fa`. **نمونه کد:** `/opt/data/cache/scratch/stt_test.py`.

```bash
KEY=$(grep -E '^GROQ_API_KEY=' /opt/data/.env | head -1 | cut -d= -f2- | tr -d '"')
curl -sS https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $KEY" \
  -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36" \
  -F "file=@<audio>" -F "model=whisper-large-v3" -F "language=fa" -F "response_format=json"
```

**پیت‌فال‌ها / Pitfalls:**
- بدون یوزر-ایجنت مرورگر → `HTTP 403 error 1010` (Cloudflare). حتماً `-A` بده.
   No browser UA → `HTTP 403 error 1010`. Must use `-A`.
- سقف حجم ~۲۵ مگابایت. فایل بزرگ‌تر را با `ffmpeg` به تکه‌های ۱۰ دقیقه‌ای بشکن، با ۵ ثانیه همپوشانی، بعد به هم بچسبان.
   ~25 MB limit. Split larger files with `ffmpeg` into 10-min chunks, 5s overlap, concat.
- `whisper-large-v3-turbo` سریع‌تر و ارزان‌تر است؛ برای فارسی ابتدا `large-v3` را امتحان کن.
   `whisper-large-v3-turbo` faster/cheaper; try `large-v3` first for Persian.
- رونویسی ممکن است اصطلاح تخصصی را غلط بنویسد؛ **متن خام را به کاربر نشان بده** تا تصحیح کند.
   Transcript may miswrite technical terms; **show raw to user** for correction.
- `prompt` پارامتر پشتیبانی می‌شود — لیست اصطلاحات تخصصی را آنجا بده.
   `prompt` param supported — put domain terms there.

## جستجو — دو مسیر، نه یکی / Query — Two Paths, Not One

**مسیر ۱ — سؤال نقطه‌ای / Point Query** («بودجه چقدر بود؟»، «جریمه چند درصد؟» / "What was the budget?", "Penalty %?"):

```bash
python3 /opt/data/documents/doclib.py search "کوئری"              # همه مجموعه‌ها / all collections
python3 /opt/data/documents/doclib.py search "کوئری" -c office-works
python3 /opt/data/documents/doclib.py search "کوئری" -f contract
python3 /opt/data/documents/doclib.py list [-c <collection>]
python3 /opt/data/documents/doclib.py stats
python3 /opt/data/documents/doclib.py show <file_id>
```

**مسیر ۲ — سؤال ترکیبی/تحلیلی / Analytical Query** («روند سه ساله»، «مقایسه کن»، «تناقضی هست؟" / "3-year trend", "compare", "any contradiction?"). ویکی نقطه شروع است، **نه آخرین راه‌حل** / Wiki is the starting point, **not the last resort**:

1. `wiki/index.md` را بخوان / Read `wiki/index.md`
2. صفحه(های) مرتبط را پیدا کن و بخوان / Find & read relevant pages
3. `doclib.py links sources/X -c <coll>` بزن → صفحات مرتبط بعدی / Run → next linked pages
4. ترکیب کن / Combine

مسیر ۱ جواب نداد → مسیر ۲. **مسیر ۲ کافی نبود** → `search`.
Path 1 fails → Path 2. **Path 2 insufficient** → `search`.
سؤال تحلیلی هرگز مستقیم به SQLite نمی‌رود. **بگو از کدام مسیر جواب دادی**.
Analytical query never goes direct to SQLite. **State which path you used.**

**زبان پاسخ = زبان سؤال / Response language = question language**
- سؤال فارسی → جواب فارسی
- English question → English answer
- Mixed → follow the dominant language

## لایه ویکی — ابزارها / Wiki Layer — Tools

```bash
python3 /opt/data/documents/doclib.py links sources/name -c <coll>   # لینک ورودی/خروجی + تشخیص شکستگی
python3 /opt/data/documents/doclib.py lint [-c <coll>]               # بازبینی سلامت / health check
python3 /opt/data/documents/doclib.py graph [-c <coll>]              # نقشه لینک‌ها / link map
```

`lint` شش چیز را می‌گیرد / `lint` catches six things: لینک شکسته (broken links)، منبع گم‌شده (missing source)، صفحه یتیم (orphan page)، صفحه‌ای که در `index.md` نیست (not in index)، صفحه بی‌منبع (no sources)، عنوان تکراری (duplicate title).

**بعد از هر ingest، `lint` بزن.** اگر ایراد داد، قبل از گزارش به کاربر درست کن.
**After every ingest, run `lint`.** Fix all errors before reporting to user.

### Lint محتوایی — کار من است، نه اسکریپت / Content Lint — My Job, Not Script

قبل از نوشتن یا آپدیت یک صفحه که منبع جدیدی برایش آمده: **عددهای صفحه موجود را با منبع جدید مقایسه کن.** اختلاف؟ → گزارش به کاربر، با هر دو عدد و منبعشان. تصمیم با کاربر است. هیچ‌وقت ساکت از روی عدد قدیمی رد نشو.
Before writing/updating a page with new source: **compare existing page numbers with new source.** Discrepancy? → report to user with both numbers + sources. User decides. Never silently overwrite.

## قرارداد صفحه ویکی / Wiki Page Contract

هر صفحه در `wiki/sources/` باید داشته باشد / Every page in `wiki/sources/` must have:
`# عنوان` / `# Title` · `> یک‌خط` / `> One-line` · `## خلاصه` / `## Summary` · `## محتوا` / `## Content` · `## منابع` / `## Sources` · `## مرتبط` / `## Related`.

- مسیر نسبی از محل فایل: `../entities/x.md` و `../../raw/files/y.pdf`
   Relative paths from file location
- `## منابع` اجباری است — نبودش = «صفحه بی‌منبع» در lint
   `## Sources` mandatory — missing = "no sources" in lint
- `index.md` **باید** به همه صفحات `sources/` لینک بدهد — تنها نجات‌دهنده از یتیمی
   `index.md` **must** link all `sources/` pages — only escape from orphan status
- بخش `مرتبط` همان چیزی است که ویکی را ویکی می‌کند؛ بدون آن هر صفحه یک جزیره است
   `## Related` is what makes wiki a wiki; without it every page is an island

ساختار کامل در `SCHEMA.md` → «قرارداد صفحه ویکی».
Full structure in `SCHEMA.md` → "Wiki Page Contract".

## نکات فنی مهم / Technical Notes

- **مسیر ریشه / Root path:** `DOCLIB_ROOT` یا پیش‌فرض `/opt/data/documents`. پوشه اسناد کنار `HOME` نیست (`HOME=/opt/data/home`).
   Not beside `HOME` (`HOME=/opt/data/home`).
- **نرمال‌سازی فارسی / Persian Normalization:** ذخیره با `normalize()`، ایندکس با `match_fold()`. دومی تهاجمی‌تر است تا «تأخیر» == «تاخیر» و «مسئول» == «مسیول».
   Storage via `normalize()`, indexing via `match_fold()`. Latter aggressive: "تأخیر" == "تاخیر", "مسئول" == "مسیول".
- **`fts_key`** ستون جداگانه در `chunks` است که فرم fold‌شده را نگه می‌دارد — FTS روی آن ایندکس می‌شود، ولی نمایش از `text` اصلی می‌آید.
   Separate `fts_key` column in `chunks` holds folded form — FTS indexes it, display uses original `text`.
- ارقام فارسی/عربی در ذخیره به لاتین تبدیل می‌شوند؛ جستجوی «۹۲۲۰» و «9220» هر دو کار می‌کند.
   Persian/Arabic digits → Latin in storage; search works with "۹۲۲۰" and "9220" alike.
- ارقام در **صفحه ویکی** هم باید به هر دو صورت موجود باشند یا fit_ fold پوشش دهد — در تست `۱۰ ابزار` پیدا نشد، `ده ابزار` پیدا شد. اگر عدد در متن فارسی است، هم فارسی و هم انگلیسی در ویکی بنویس.
   **Wiki pages** should also have both forms or rely on fold — test: `۱۰ ابزار` not found, `ده ابزار` found. Write both if Persian digits in source.
- DOCX خراب → fallback به استخراج خام XML (تابع `_docx_raw_xml`).
   Corrupt DOCX → fallback to raw XML extraction (`_docx_raw_xml`).

## افزودن مجموعه جدید / Adding New Collection

با کاربر تأیید بگیر، بعد:
Confirm with user, then:

```bash
mkdir -p /opt/data/documents/collections/<new-name>/{raw/{files,web,audio,images},wiki/{sources,entities,concepts}}
```

و `COLLECTION.md`، `wiki/index.md`، `wiki/log.md` بساز (از مجموعه‌های موجود الگو بگیر).
Create `COLLECTION.md`, `wiki/index.md`, `wiki/log.md` (copy from existing collections).
