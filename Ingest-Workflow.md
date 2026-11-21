---
name: document-archive
description: Use for the user's document archive - ingest or search.
---

# آرشیو اسناد چندمجموعه‌ای

کاربر یک آرشیو دائمی دارد در `/opt/data/documents/`.

**هر بار:** (1) فایل/لینک/ویس/عکس جدید رسید، یا (2) کاربر خواست در اسنادش بگردی، یا (3) سؤال درباره قرارداد/بودجه/نگهداشت/یادداشت‌هایش پرسید → اول این را بخوان:

```bash
cat /opt/data/documents/SCHEMA.md
```

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

مجموعه‌های موجود: `office-works` (کارهای اداری), `maintenance-learning` (آموزش نگهداشت), `ai-learning` (آموزش هوش مصنوعی).

**قاعده مقیاس‌بندی ویکی:** `entities/` و `concepts/` فقط وقتی ساخته می‌شوند که موضوع در **چند منبع** تکرار شده باشد. یک منبع → فقط `sources/` page. این از پر شدن ویکی با صفحات نیمه‌پر جلوگیری می‌کند.

## قواعد سخت

1. **هرگز محتوای `raw/` را تغییر نده.** منبع حقیقت است.
2. **هیچ فایلی بدون تأیید کاربر اضافه نمی‌شود.** اول موضوع را تشخیص بده، مجموعه را پیشنهاد بده، تأیید بگیر.
3. **هر عدد در `wiki/` باید ارجاع داشته باشد** (فایل + صفحه). بدون ارجاع، عدد ننویس.
4. **Extend, don't create** — قبل از ساخت صفحه جدید، جستجو کن صفحه‌ای هست یا نه.
5. **`entities/` و `concepts/` فقط وقتی لازم شد** — نه از ابتدا.
6. **فایل `.md` همراه در `raw/`:** عکس → `<name>.md` (متنی که مدل خواند)، صدا → `<name>.transcript.md`.

## جریان ingest

1. فایل را به پوشه درست `raw/` کپی کن
2. ایندکس کن:
   ```bash
   python3 /opt/data/documents/doclib.py add <path> -c <collection>
   ```
3. صفحه ویکی بساز در `wiki/sources/<short-english-name>.md` — با قرارداد کامل (پایین)
4. به صفحه جدید در `wiki/index.md` لینک بده — وگرنه lint آن را یتیم می‌بیند
5. `wiki/log.md` را آپدیت کن
6. **`doclib.py add` روی صفحه ویکی هم بزن** — وگرنه ویکی در `search` پیدا نمی‌شود
7. `python3 /opt/data/documents/doclib.py lint -c <collection>` بزن و ایرادها را درست کن
8. به کاربر گزارش بده

## پردازش انواع منبع

| نوع | روش |
|---|---|
| PDF/DOCX/XLSX/PPTX/TXT/MD/CSV | `doclib.py add` (pypdf, python-docx, openpyxl, python-pptx) |
| عکس/اسکرین‌شات | **خود مدل می‌خواند** — صفر نصب. متن را در `.md` کنار عکس بنویس، بعد ایندکس کن |
| صدا/ویس | Groq Whisper (پایین) → رونویسی را در `.transcript.md` بنویس، بعد ایندکس کن |
| لینک/بلاگ | `web_extract` → markdown در `raw/web/YYYY-MM-DD-slug.md` با خط `source: <URL>` |

### گام‌های ingest برای لینک/بلاگ

1. `web_extract` — HTML را بگیر، تبلیغات/منو/فوتر را حذف کن (dev.to: خطوط بعد از `* * *` که ad است)
2. فایل ذخیره در `raw/web/YYYY-MM-DD-slug.md` با هدر YAML:
   ```yaml
   source: <URL>
   title: <عنوان>
   author: <نویسنده>
   published: <تاریخ>
   retrieved: <امروز>
   lang: <en/fa>
   ```
3. `doclib.py add` روی فایل خام
4. صفحه ویکی بساز در `wiki/sources/<short-english-name>.md` — زبان ویکی = زبان منبع
5. `doclib.py add` **روی صفحه ویکی هم بزن** — وگرنه صفحه ویکی در جستجو پیدا نمی‌شود (باگ واقعی، در تست پیدا شد)
6. به `wiki/index.md` لینک بده + `wiki/log.md` آپدیت کن
7. `lint` بزن

### رونویسی صدا با Groq

`whisper-large-v3` با زبان `fa`. **نمونه کد:** `/opt/data/cache/scratch/stt_test.py`.

```bash
KEY=$(grep -E '^GROQ_API_KEY=' /opt/data/.env | head -1 | cut -d= -f2- | tr -d '"')
curl -sS https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $KEY" \
  -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36" \
  -F "file=@<audio>" -F "model=whisper-large-v3" -F "language=fa" -F "response_format=json"
```

**پیت‌فال‌ها:**
- بدون یوزر-ایجنت مرورگر → `HTTP 403 error 1010` (Cloudflare). حتماً `-A` بده.
- سقف حجم ~۲۵ مگابایت. فایل بزرگ‌تر را با `ffmpeg` به تکه‌های ۱۰ دقیقه‌ای بشکن، با ۵ ثانیه همپوشانی، بعد به هم بچسبان.
- `whisper-large-v3-turbo` سریع‌تر و ارزان‌تر است؛ برای فارسی ابتدا `large-v3` را امتحان کن.
- رونویسی ممکن است اصطلاح تخصصی را غلط بنویسد؛ **متن خام را به کاربر نشان بده** تا تصحیح کند.
- `prompt` پارامتر پشتیبانی می‌شود — لیست اصطلاحات تخصصی را آنجا بده.

## جستجو — دو مسیر، نه یکی

**مسیر ۱ — سؤال نقطه‌ای** («بودجه چقدر بود؟»، «جریمه چند درصد؟»):

```bash
python3 /opt/data/documents/doclib.py search "کوئری"              # همه مجموعه‌ها
python3 /opt/data/documents/doclib.py search "کوئری" -c office-works
python3 /opt/data/documents/doclib.py search "کوئری" -f contract
python3 /opt/data/documents/doclib.py list [-c <collection>]
python3 /opt/data/documents/doclib.py stats
python3 /opt/data/documents/doclib.py show <file_id>
```

**مسیر ۲ — سؤال ترکیبی/تحلیلی** («روند سه ساله»، «مقایسه کن»، «تناقضی هست؟»). ویکی نقطه شروع است، **نه آخرین راه‌حل**:

1. `wiki/index.md` را بخوان
2. صفحه(های) مرتبط را پیدا کن و بخوان
3. `doclib.py links sources/X -c <coll>` بزن → صفحات مرتبط بعدی
4. ترکیب کن

مسیر ۱ جواب نداد → مسیر ۲. **مسیر ۲ کافی نبود** → `search`.
سؤال تحلیلی هرگز مستقیم به SQLite نمی‌رود. **بگو از کدام مسیر جواب دادی.**

## لایه ویکی — ابزارها

```bash
python3 /opt/data/documents/doclib.py links sources/name -c <coll>   # لینک ورودی/خروجی + تشخیص شکستگی
python3 /opt/data/documents/doclib.py lint [-c <coll>]               # بازبینی سلامت
python3 /opt/data/documents/doclib.py graph [-c <coll>]              # نقشه لینک‌ها
```

`lint` شش چیز را می‌گیرد: لینک شکسته، منبع گم‌شده، صفحه یتیم، صفحه‌ای که در `index.md` نیست، صفحه بی‌منبع، عنوان تکراری.

**بعد از هر ingest، `lint` بزن.** اگر ایراد داد، قبل از گزارش به کاربر درست کن.

### Lint محتوایی — کار من است، نه اسکریپت

قبل از نوشتن یا آپدیت یک صفحه که منبع جدیدی برایش آمده: **عددهای صفحه موجود را با منبع جدید مقایسه کن.** اختلاف؟ → گزارش به کاربر، با هر دو عدد و منبعشان. تصمیم با کاربر است. هیچ‌وقت ساکت از روی عدد قدیمی رد نشو.

## قرارداد صفحه ویکی

هر صفحه در `wiki/sources/` باید داشته باشد: `# عنوان` / `> یک‌خط` / `## خلاصه` / `## محتوا` / `## منابع` / `## مرتبط`.

- مسیر نسبی از محل فایل: `../entities/x.md` و `../../raw/files/y.pdf`
- `## منابع` اجباری است — نبودش = «صفحه بی‌منبع» در lint
- `index.md` **باید** به همه صفحات `sources/` لینک بدهد — تنها نجات‌دهنده از یتیمی
- بخش `مرتبط` همان چیزی است که ویکی را ویکی می‌کند؛ بدون آن هر صفحه یک جزیره است

ساختار کامل در `SCHEMA.md` → «قرارداد صفحه ویکی».

## نکات فنی مهم

- **مسیر ریشه:** `DOCLIB_ROOT` یا پیش‌فرض `/opt/data/documents`. پوشه اسناد کنار `HOME` نیست (`HOME=/opt/data/home`).
- **نرمال‌سازی فارسی:** ذخیره با `normalize()`، ایندکس با `match_fold()`. دومی تهاجمی‌تر است تا «تأخیر» == «تاخیر» و «مسئول» == «مسیول».
- **`fts_key`** ستون جداگانه در `chunks` است که فرم fold‌شده را نگه می‌دارد — FTS روی آن ایندکس می‌شود، ولی نمایش از `text` اصلی می‌آید.
- ارقام فارسی/عربی در ذخیره به لاتین تبدیل می‌شوند؛ جستجوی «۹۲۲۰» و «9220» هر دو کار می‌کند.
- ارقام در **صفحه ویکی** هم باید به هر دو صورت موجود باشند یا fit_ fold پوشش دهد — در تست `۱۰ ابزار` پیدا نشد، `ده ابزار` پیدا شد. اگر عدد در متن فارسی است، هم فارسی و هم انگلیسی در ویکی بنویس.
- DOCX خراب → fallback به استخراج خام XML (تابع `_docx_raw_xml`).

## افزودن مجموعه جدید

با کاربر تأیید بگیر، بعد:

```bash
mkdir -p /opt/data/documents/collections/<new-name>/{raw/{files,web,audio,images},wiki/{sources,entities,concepts}}
```

و `COLLECTION.md`، `wiki/index.md`، `wiki/log.md` بساز (از مجموعه‌های موجود الگو بگیر).
