# SCHEMA — قواعد آرشیو اسناد

این فایل «قانون اساسی» آرشیو است. هر سشن جدیدی که با آرشیو کار می‌کند باید اول این را بخواند.

## ساختار

```
documents/
├── SCHEMA.md                       همین فایل
├── index.db                        SQLite — index جستجو (خودکار ساخته می‌شود)
├── doclib.py                       اسکریپت استخراج/ایندکس/جستجو
├── doclib.single-collection.py.bak نسخه قدیمی (استفاده نمی‌شود)
└── collections/<name>/
    ├── COLLECTION.md               موضوع این مجموعه، چه چیزی داخلش می‌رود
    ├── raw/                        منبع حقیقت — هرگز تغییر نمی‌کند
    │   ├── files/                  PDF, DOCX, XLSX, PPTX, TXT, MD, CSV
    │   ├── web/                    نسخه markdown بلاگ‌پست‌ها
    │   ├── audio/                  فایل صوتی اصلی + رونویسی
    │   └── images/                 عکس اصلی + متنی که مدل خوانده
    └── wiki/
        ├── index.md                فهرست همه منابع این مجموعه
        ├── log.md                  تاریخچه عملیات (چه چیزی کِی اضافه شد)
        ├── sources/                یک صفحه per منبع
        ├── entities/               افراد، سازمان‌ها، تجهیزات (فقط وقتی لازم شد)
        └── concepts/               مفاهیم، اصطلاحات (فقط وقتی لازم شد)
```

## سه لایه

1. **`raw/`** — فایل اصلی، دست‌نخورده. مرجع نهایی. **هرگز ویرایش یا حذف نمی‌شود.**
2. **`index.db`** — متن استخراج‌شده، تکه‌تکه‌شده، برای جستجوی سریع نقطه‌ای.
3. **`wiki/`** — صفحات markdown که *من* نوشتم. نقشه و تحلیل، نه کپی خام.

## قواعد سخت

### ۱. اصل فایل تغییر نمی‌کند
هرگز محتوای `raw/` را ویرایش نکن. اگر منبع جدیدی نسخه بهتری داشت، فایل جدید با نام جدید اضافه می‌شود.

### ۲. هر عدد و ادعای عددی باید ارجاع داشته باشد
در صفحات `wiki/`، هر عدد باید به منبع و جای مشخصش اشاره کند:
`بودجه ۴۵ میلیارد ریال (`raw/files/contract.pdf`، ص ۳)`

بدون ارجاع، عدد نوشته نمی‌شود.

### ۳. Extend, don't create
قبل از ساختن صفحه جدید در `wiki/`، جستجو کن آیا صفحه‌ای درباره همان موضوع هست. اگر هست، **همان را گسترش بده**، نه اینکه صفحه دوم بسازی.

### ۴. ویکی حداقلی
`sources/` همیشه ساخته می‌شود (یک صفحه per منبع).
`entities/` و `concepts/` **فقط وقتی** ساخته می‌شوند که واقعاً موضوعی تکرار شده باشد که ارزش صفحه مستقل داشته باشد.

### ۵. زبان / Language Rules
- زبان محتوای `wiki/` = زبان منبع اصلی (فارسی→فارسی، انگلیسی→انگلیسی) / Wiki content language = source language (fa→fa, en→en)
- متن دوزبانه → فارسی با اصطلاحات فنی به انگلیسی در پرانتز / Mixed → Persian with English terms in parentheses
- **نام فایل‌های ویکی همیشه انگلیسی و کوتاه** (مثلاً `steel-plant-contract.md`) / Wiki filenames always English short
- **زبان پاسخ = زبان سؤال** / **Response language = question language**: سؤال فارسی → جواب فارسی، English question → English answer
- پرسش ترکیبی دوزبانه → زبان غالب / Mixed query → dominant language

### ۶. آپلود بدون تأیید ممنوع
هیچ فایلی بدون اینکه اول موضوعش تشخیص داده شود، مجموعه‌اش پیشنهاد شود و کاربر تأیید کند، اضافه نمی‌شود.

## قرارداد صفحه ویکی

هر صفحه در `wiki/sources/` **باید** این ساختار را داشته باشد. `lint` نبودش را گزارش می‌دهد.

```markdown
# عنوان فارسی

> یک خط توضیح — این خط در `index.md` و `collections` استفاده می‌شود.

## خلاصه
دو تا پنج خط: این سند چیست، طرفین/موضوع، بازه زمانی، مهم‌ترین عددها.

## محتوا
جزئیات ساختاریافته. جدول برای اعداد. هر عدد با ارجاع.

## منابع
- [نام فایل](../../raw/files/contract.pdf) — ص ۳، ۷
- [عکس بودجه](../../raw/images/2026-11-20-budget.md)

## مرتبط
- [پارس فولاد](../entities/pars-steel.md)
- [تأخیر و جریمه](../concepts/delay-penalty.md)
```

### قواعد لینک‌دهی

- **مسیر نسبی از محل فایل.** صفحه در `wiki/sources/` است → `../entities/x.md` و `../../raw/files/y.pdf`.
- **بخش `مرتبط` اجباری نیست** اگر واقعاً چیزی مرتبط نیست — ولی اگر هست و ننویسی، صفحه یتیم می‌شود و `lint` می‌گیردش.
- **صفحه بدون `## منابع` = صفحه بی‌منبع.** `lint` علامت می‌زند. فقط `index.md`، `log.md`، `entities/` و `concepts/` معاف‌اند.

### ساختار `index.md`

`index.md` **باید** به همه صفحات `sources/` لینک بدهد. این تنها راهی است که یک صفحه از «یتیم» بودن نجات پیدا می‌کند:

```markdown
# فهرست منابع — <نام مجموعه>

> توضیح مجموعه

## منابع
- [عنوان فارسی](sources/short-english-name.md) — نوع، تاریخ

## موضوعات
- [پارس فولاد](entities/pars-steel.md)
```

## سه عملیات ویکی

| عملیات | چه کسی | ابزار |
|---|---|---|
| **Ingest** | من + `add` | تشخیص موضوع → تأیید → کپی به `raw/` → `doclib.py add` (فایل خام) → نوشتن صفحه ویکی → **`doclib.py add` (صفحه ویکی)** → آپدیت `index.md` و `log.md` |
| **Query** | من + `search`/`links` | پایین را ببین |
| **Lint** | `doclib.py lint` + من | ساختاری با اسکریپت، محتوایی با خواندن |

### Query — دو مسیر

1. **نقطه‌ای** («بودجه چقدر بود؟»، «جریمه چند درصد؟») → `doclib.py search` → جواب + نام فایل + صفحه.
2. **ترکیبی/تحلیلی** («روند سه ساله»، «مقایسه کن»، «تناقضی هست؟») → این مسیر:
   1. `wiki/index.md` را بخوان
   2. صفحه(های) مرتبط را پیدا کن
   3. `doclib.py links <page> -c <coll>` بزن تا صفحات مرتبط بعدی را ببینی
   4. آن صفحات را بخوان و ترکیب کن
3. **مسیر ۱ جواب نداد** → برو مسیر ۲. **مسیر ۲ کافی نبود** → `search` بزن.
4. **در پاسخ بگو از کدام مسیر جواب دادی** و همه منابع را ذکر کن.

**قاعده:** سؤال تحلیلی هرگز مستقیم به SQLite نمی‌رود. ویکی نقطه شروع است، نه آخرین راه‌حل.
**Rule:** Analytical query never goes direct to SQLite. Wiki is the starting point, not the last resort.

**زبان پاسخ = زبان سؤال / Response language = question language**

### Lint — دو لایه

**لایه ساختاری (اسکریپت):** لینک شکسته، صفحه یتیم، منبع گم‌شده، صفحه بی‌منبع، عنوان تکراری، صفحه‌ای که در `index.md` نیست.

**لایه محتوایی (من، نه اسکریپت):**

> هر بار که منبع جدیدی مربوط به صفحه‌ای موجود است، **قبل از نوشتن**، عددهای صفحه موجود را با منبع جدید مقایسه کن. اگر اختلاف بود، **به کاربر گزارش بده** — هیچ‌وقت ساکت از روی عدد قدیمی رد نشو. تصمیم با کاربر است، نه من.

کهنگی هم همین‌طور: اگر منبعی که صفحه بر آن بنا شده عوض شد، صفحه باید بازخوانی شود.


## نوع منبع (`source_type`)

| نوع | مسیر | نحوه پردازش |
|---|---|---|
| `pdf` | `raw/files/` | pypdf، صفحه‌به‌صفحه |
| `docx` | `raw/files/` | python-docx، پاراگراف + جدول |
| `xlsx` | `raw/files/` | openpyxl، شیت‌به‌شیت با `\|` |
| `pptx` | `raw/files/` | python-pptx، اسلاید‌به‌اسلاید |
| `text` | `raw/files/` یا `raw/web/` | مستقیم |
| `image` | `raw/images/` | **مدل خودش می‌خواند** — صفر نصب |
| `audio` | `raw/audio/` | Groq Whisper large-v3 (STT) |

## فایل‌های مرتبط در `raw/`

هر فایل غیرمتنی یک فایل `.md` همراه دارد:

- `raw/images/2026-11-20-budget-table.jpg` ← عکس اصلی
- `raw/images/2026-11-20-budget-table.md` ← متن استخراج‌شده توسط مدل

- `raw/audio/2026-11-20-meeting.ogg` ← صدا
- `raw/audio/2026-11-20-meeting.transcript.md` ← رونویسی Groq

فایل `.md` همراه هم در `index.db` ایندکس می‌شود (چون `.md` یعنی `text`).

**صفحات `wiki/` هم باید ایندکس شوند.** پس از نوشتن صفحه در `wiki/sources/`، اجرا کن:

```bash
python3 /opt/data/documents/doclib.py add "wiki/sources/name.md" -c <collection>
```

بدون این، صفحه ویکی نوشته شده در جستجو پیدا نمی‌شود (فایل خام می‌شود، تحلیل نمی‌شود).

## دستورهای اسکریپت

```bash
python3 /opt/data/documents/doclib.py collections
python3 /opt/data/documents/doclib.py add <file> -c <collection>
python3 /opt/data/documents/doclib.py search "کوئری" -c <collection>
python3 /opt/data/documents/doclib.py search "کوئری"          # همه مجموعه‌ها
python3 /opt/data/documents/doclib.py list [-c <collection>]
python3 /opt/data/documents/doclib.py stats
python3 /opt/data/documents/doclib.py show <file_id>
python3 /opt/data/documents/doclib.py rm <file_id>
python3 /opt/data/documents/doclib.py reindex [-c <collection>]

# لایه ویکی
python3 /opt/data/documents/doclib.py links sources/name -c <collection>   # لینک ورودی/خروجی
python3 /opt/data/documents/doclib.py lint [-c <collection>]               # بازبینی سلامت
python3 /opt/data/documents/doclib.py graph [-c <collection>]              # نقشه لینک‌ها
```

## افزودن مجموعه جدید

```bash
mkdir -p /opt/data/documents/collections/<new-name>/{raw/{files,web,audio,images},wiki/{sources,entities,concepts}}
# سپس COLLECTION.md و wiki/index.md و wiki/log.md بساز
```

قبل از ساخت، با کاربر تأیید بگیر.
