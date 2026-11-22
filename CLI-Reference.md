# CLI Reference

```bash
python3 /opt/data/documents/doclib.py --help
```

usage: doclib.py [-h]
                 {add,search,list,show,rm,reindex,stats,collections,links,lint,graph,ur-new,ur-add,ur-list} ...

آرشیو اسناد چندمجموعه‌ای

positional arguments:
  {add,search,list,show,rm,reindex,stats,collections,links,lint,graph,ur-new,ur-add,ur-list}
    add                 افزودن فایل/پوشه
    search              جستجو
    list                فهرست فایل‌ها
    show                نمایش تکه‌های یک فایل
    rm                  حذف از ایندکس
    reindex             بازسازی ایندکس
    stats               آمار
    collections         فهرست مجموعه‌ها
    links               لینک‌های ورودی/خروجی یک صفحه ویکی
    lint                بازبینی سلامت ویکی
    graph               نقشه لینک‌های ویکی
    ur-new              ساخت کتاب جدید در حال مطالعه
    ur-add              افزودن نقل‌قول به کتاب در حال مطالعه
    ur-list             فهرست کتاب‌های در حال مطالعه

options:
  -h, --help            show this help message and exit


## `add`

```bash

usage: doclib.py add [-h] [--collection COLLECTION] path

positional arguments:
  path

options:
  -h, --help            show this help message and exit
  --collection, -c COLLECTION

```


## `search`

```bash

usage: doclib.py search [-h] [--collection COLLECTION] [--file FILE]
                        [--limit LIMIT]
                        query

positional arguments:
  query

options:
  -h, --help            show this help message and exit
  --collection, -c COLLECTION
  --file, -f FILE
  --limit, -n LIMIT

```


## `list`

```bash

usage: doclib.py list [-h] [--collection COLLECTION]

options:
  -h, --help            show this help message and exit
  --collection, -c COLLECTION

```


## `show`

```bash

usage: doclib.py show [-h] file_id

positional arguments:
  file_id

options:
  -h, --help  show this help message and exit

```


## `rm`

```bash

usage: doclib.py rm [-h] file_id

positional arguments:
  file_id

options:
  -h, --help  show this help message and exit

```


## `reindex`

```bash

usage: doclib.py reindex [-h] [--collection COLLECTION]

options:
  -h, --help            show this help message and exit
  --collection, -c COLLECTION

```


## `stats`

```bash

usage: doclib.py stats [-h]

options:
  -h, --help  show this help message and exit

```


## `collections`

```bash

usage: doclib.py collections [-h]

options:
  -h, --help  show this help message and exit

```


## `links`

```bash

usage: doclib.py links [-h] --collection COLLECTION page

positional arguments:
  page                  مثلاً sources/steel-plant-contract

options:
  -h, --help            show this help message and exit
  --collection, -c COLLECTION

```


## `lint`

```bash

usage: doclib.py lint [-h] [--collection COLLECTION]

options:
  -h, --help            show this help message and exit
  --collection, -c COLLECTION

```


## `graph`

```bash

usage: doclib.py graph [-h] [--collection COLLECTION]

options:
  -h, --help            show this help message and exit
  --collection, -c COLLECTION

```

## منبع در حال مطالعه / Living Source

تنها فایلی که بعد از ساخت می‌تواند رشد کند: `raw/files/User-Reading-<slug>.md`
The only file that may grow after creation.

```bash
# ساخت کتاب جدید / Create new book
python3 doclib.py ur-new maintenance-engineering \
  --title "مهندسی نگهداشت" -a "جان موبلی" -y 1399 \
  --publisher "نشر" --isbn "978-..." -c maintenance-learning

# افزودن نقل‌قول / Add a quote
python3 doclib.py ur-add maintenance-engineering \
  -p 156 -q "OEE از حاصل‌ضرب دسترس‌پذیری، عملکرد و کیفیت به دست می‌آید." \
  -t "KPI نگهداشت" -n "یادداشت اختیاری" -c maintenance-learning

# فهرست کتاب‌های در حال مطالعه / List active books
python3 doclib.py ur-list
```

| عمل / Action | مجاز / Allowed |
|---|---|
| افزودن `q-NNN` / Add quote | ✅ |
| اصلاح تایپی / Fix typo | ✅ با `**اصلاح:** <تاریخ>` |
| حذف نقل‌قول / Delete | ❌ — `**لغو:** دلیل` بنویس |
| تغییر frontmatter موجود / Modify field | ❌ |
| شماره‌گذاری مجدد / Renumber | ❌ — `q-NNN` شناسه ثبات است |

هر نقل‌قول یک تکه جدا در `index.db` با شماره صفحه است؛ جستجوی نقطه‌ای مستقیم نقل‌قول را با ارجاع برمی‌گرداند.
Each quote is a separate chunk in `index.db` with its page number; point query returns it with citation.
