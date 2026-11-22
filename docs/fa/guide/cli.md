# CLI Reference

```bash
python3 /opt/data/documents/doclib.py --help
```

usage: doclib.py [-h]
                 {add,search,list,show,rm,reindex,stats,collections,links,lint,graph} ...

آرشیو اسناد چندمجموعه‌ای

positional arguments:
  {add,search,list,show,rm,reindex,stats,collections,links,lint,graph}
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
