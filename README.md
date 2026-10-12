# xml-feed-to-csv

Converts a supplier **YML/XML product feed** (`<yml_catalog><shop><categories/><offers/></shop></yml_catalog>`, the format many Ukrainian suppliers and marketplaces use) into one flat **CSV** that you can open in Excel or Google Sheets, plus a list of problems found. Python standard library only.

## What it does
- One row per `<offer>`: `id, available, name, vendor, price, currency, category, url, pictures, description`.
- **Category path** from the `<categories>` tree (`Parent / Child`). A broken `parentId` loop does not hang the tool.
- **Params become columns** (`param: Розмір`, `param: Колір`, ...). Limit of 30 different params by default; if there are more, a warning says so.
- Several `<picture>` tags are joined with `|`. Line breaks in descriptions become single spaces.
- **Problems reported** (not hidden): no id, duplicate id (the later offer is dropped), no name, price missing or not positive, no picture.
- **Safety:** feeds with `DOCTYPE`/`ENTITY` declarations are refused (protection against entity-expansion files), files above 50 MB are refused, and text that starts with `=`, `+`, `-` or `@` gets a leading `'` so spreadsheets do not run it as a formula.

## Use
```bash
PYTHONPATH=src python3 -m feed_csv examples/feed.xml --out feed.csv --issues issues.json
```
Tests: `python3 -m unittest discover -s tests`.

## Limits (read this)
- It reads the YML structure only: `name` (or `model`), `vendor`, `price`, `currencyId`, `categoryId`, `url`, `picture`, `description`, `param`. Other tags are ignored.
- It does not download feeds from a URL, and it does not merge size/colour variants into one model card.
- Prices are copied as text from the feed; the check only tells whether they are positive numbers.
- Tested on a small example feed and on generated cases, not on every supplier's dialect.

MIT license.

---

# xml-feed-to-csv (українською)

Перетворює XML/YML-фід постачальника на плоский **CSV** і показує знайдені проблеми. Лише стандартна бібліотека Python.

**Запуск:** `PYTHONPATH=src python3 -m feed_csv examples/feed.xml --out feed.csv --issues issues.json`. Параметри товару стають окремими колонками, категорії — повним шляхом. Фіди з `DOCTYPE`/`ENTITY` відхиляються.

**Важливо:** це не завантажує фід за посиланням і не об'єднує варіанти розміру й кольору в одну картку моделі; перевірено на прикладі й згенерованих випадках, не на всіх форматах постачальників.
