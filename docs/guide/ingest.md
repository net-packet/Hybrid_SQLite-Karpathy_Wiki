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
   > تنها استثنا: `raw/files/User-Reading-*.md` — فایل **فقط append + اصلاح علامت‌دار** است (بخش «منبع در حال مطالعه» را ببین).
   > Only exception: `raw/files/User-Reading-*.md` — **append-only + marked corrections** (see "Living Source" section).
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
7. **پیشنهاد ≠ تصمیم.** وقتی مجموعه‌ای را پیشنهاد می‌دهی و نمی‌پرسی، این «تأیید ضمنی» نیست. هرگز جملاتی مثل «نمی‌پرسَم، تک‌گزینگی روشن است» ننویس — همان لحظه بپرس، یا صریح بنویس «پیش‌فرض: X، اگر اعتراضی داری بگو» و منتظر بمان.
   **Proposing ≠ deciding.** A unilateral proposal is not implicit approval. Never write "I won't ask, the fit is obvious" — ask, or state "default: X, object if wrong" and wait.
8. **گزارش «انجام شد» فقط با شاهد واقعی.** قبل از گفتن «ویکی ساخته شد / فایل ایندکس شد / lint پاس شد» یا برعکس «ساخته نشده»، همان لحظه وضعیت دیسک را چک کن (فهرست پوشه با `search_files`، جستجوی متن در `index.md`، خروجی `lint`). تست موفق یک مرحله (استخراج PDF یا `add`) به معنی ساخته شدن کل صفحه ویکی نیست.
   **Report "done" only with fresh evidence.** Check the disk (`ls`, `grep` in `index.md`, `lint` output) immediately before claiming a page/file exists — or that it is missing. A passing extraction step is not a built wiki page.

## زبان مراجع — دوزبانه با حفظ خوانایی / Reference Language — Bilingual, Readable

مراجع `references/` **دوزبانه**اند، ولی دوزبانگی نباید خوانایی را خراب کند. فارسی و انگلیسی هرگز در یک خط قاطی نمی‌شوند.
References are **bilingual**, but bilingual must not hurt legibility. Persian and English never interleave on one line.

| لایه / Layer | قاعده / Rule |
|---|---|
| عنوان `#` و `##` | یک خط با «فارسی / English» / One line: `فارسی / English` |
| متن توضیحی | **فارسی بالا، انگلیسی پایین، دو خط جدا** / Persian line, then English line |
| فهرست‌ها | دو فهرست جدا: `**In scope:**` (EN) و `**دامنه (فارسی):**` — نه آیتم دوزبانه درون‌خطی / Two lists, never `- Contracts / قراردادها` |
| جدول‌ها | **فقط انگلیسی**، سرستون دوزبانه: `| مورد / Item | مقدار / Value |` / English body, bilingual header |
| بلوک کد و کامنت‌ها | انگلیسی فقط؛ توضیح فارسی بیرون کد / English only; Persian explanation outside the fence |
| گام‌های شماره‌دار | دو بلوک جدا (۱. فارسی، بعد 1. انگلیسی) / Two blocks, not one mixed list |

سنجش پس از ویرایش / Measure after editing:

```python
# خطی که هم فارسی طولانی دارد و هم ۱۰+ کلمهٔ لاتین = مخلوط سنگین
if len(re.findall(r'[\u0600-\u06FF]', line)) > 18 and len(re.findall(r'[A-Za-z]{3,}', line)) > 10:
    report(line)
```

هدف: صفر خط مخلوط سنگین بیرون از جدول و بلوک کد. بعد از تأیید نهایی، حجم می‌تواند دو برابر شود — این مشکل نیست، خوانایی هدف است.
Goal: zero heavy-mixed lines outside tables and code blocks. Doubling file size is expected and fine.

## نقشهٔ مراجع / Reference Map

`SKILL.md` منبع نهایی است. مراجع فقط دانش تکمیلی دارند. **در تناقض، `SKILL.md` برنده است.**

| موضوع | فایل | کِی بخوان |
|---|---|---|
| راه‌اندازی آرشیو جدید | `references/bootstrap.md` | ساخت آرشیو برای کاربر جدید |
| دامنهٔ مجموعه‌ها (In/Out scope) | `references/collection-scope.md` | قبل از پیشنهاد مجموعه به کاربر |
| جریان کامل ingest + پیت‌فال‌ها | `references/ingest-procedures.md` | شروع هر ingest |
| قرارداد صفحهٔ ویکی + نمونهٔ کامل | `references/wiki-page-contract.md` | قبل از نوشتن صفحهٔ `sources/` |
| منبع در حال مطالعه (User-Reading) | `references/living-source.md` | کاربر گفت «کتاب X را شروع کردم» |
| تصمیم مسیر جستجو (نقطه‌ای vs تحلیلی) | `references/dual-path-query.md` | قبل از پاسخ به سؤال |
| نرمال‌سازی فارسی + FTS5 | `references/persian-normalization.md` | خطای فولدینگ یا ارقام فارسی در جستجو |
| Lint ساختاری + محتوایی | `references/wiki-lint.md` | قبل از گزارش به کاربر |
| GitHub Wiki + VitePress Pages | `references/github-wiki-setup.md` | آپدیت ویکی/سایت آنلاین، بازبینی کهنگی repo |

## جریان ingest / Ingest Flow

**قواعد مقدم بر جریان:** موضوع را تشخیص بده → **یک** مجموعه پیشنهاد بده → **تأیید بگیر**؛ بدون تأیید هیچ فایلی کپی نمی‌شود. جزئیات کامل هر مرحله و پیت‌فال‌های نوع منبع در `references/ingest-procedures.md`.

**Preconditions:** detect topic → propose **one** collection → get approval. Nothing is copied before approval. Full per-step detail and source-type pitfalls: `references/ingest-procedures.md`.

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
5. **`doclib.py add` روی صفحه ویکی هم بزن** — وگرنه ویکی در `search` پیدا نمی‌شود
   **`doclib.py add` the wiki page too** — or wiki invisible to search
6. `wiki/log.md` را آپدیت کن
   Update `wiki/log.md`
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
   title: <actual article title>
   author: <actual author>
   published: <actual publish date>
   retrieved: <today>
   lang: <en|fa>
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

**Voice command vs question detection:** The model cannot distinguish from audio alone. Use speech markers ("اضافه کن", "ثبت کن" vs "چیه؟", "معلومه؟") + file accompaniment. **Always confirm before ingest** — show transcript, ask "Add to &lt;collection&gt;?". In doubt, show transcript and ask briefly.

## منبع در حال مطالعه / Living Source

**کاربر می‌گوید «کتاب X را شروع کردم».** این یک مسیر جدا از ingest عادی است: فایل خام می‌تواند رشد کند.
**User says "I started book X".** Separate path from normal ingest: the raw file may grow.

### جریان اجباری / Mandatory Flow

1. **جستجو** — `ur-list` و `search "<عنوان>"` بزن. کتاب از قبل هست؟
   **Search** — run `ur-list` and `search`. Does the book already exist?
   - هست → همان را ادامه بده (`ur-add`)، فایل جدید نساز
   - Exists → continue it (`ur-add`), do not create a new file
2. **موضوع → مجموعه** — پیشنهاد بده. اگر در دو مجموعه جا داشت، **بپرس**.
   **Topic → collection** — propose. If it fits two, **ask**.
3. **فیلدهای گم‌شده** — فقط چیزهایی که کاربر نداد و برای پیش‌نمایش لازم است بپرس (عنوان، نویسنده، زبان حتماً؛ ناشر/سال/ISBN اختیاری).
   **Missing fields** — ask only what's needed (title, author, lang required; publisher/year/ISBN optional).
4. **پیش‌نمایش + تأیید** — جدول زیر را نشان بده. **تا «تأیید» نگرفتی، هیچ فایلی نساز.**
   **Preview + confirm** — show the table below. **Create nothing before "approved".**

```
📖 پیش‌نمایش منبع جدید / New source preview

عنوان / Title      ...
نویسنده / Author   ...
سال / Year         ...
ناشر / Publisher   ...
زبان / Language    ...
مجموعه / Collection ...
نام فایل / Filename User-Reading-<slug>.md
صفحه ویکی / Wiki    wiki/sources/user-reading-<slug>.md
```

5. **ساخت** — `ur-new` (فایل خام + صفحه ویکی + ثبت در `index.md` خودکار)
   **Create** — `ur-new` (raw + wiki page + `index.md` entry, all automatic)
6. **هر نقل‌قول بعدی** — `ur-add`، بدون پیش‌نمایش مجدد
   **Each later quote** — `ur-add`, no re-preview

### نام‌گذاری / Naming

```
raw/files/User-Reading-<english-slug>.md
wiki/sources/user-reading-<english-slug>.md
```