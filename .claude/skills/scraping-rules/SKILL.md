---
name: scraping-rules
description: Project rules for scraping books.toscrape.com. Use whenever writing or changing crawler, cleaning or analysis code in this project.
---

# Scraping rules (books-scraper)

1. **Always wait** 0.5-1 s (random) between requests. Never hammer the site.
2. **Never crash**: wrap every request in retries (3 attempts, growing back-off) and every parse step in try/except. A failed page is logged and skipped; an empty field becomes `None`/NaN.
3. **Log everything** with `logging` to console and `scraper.log`: progress every page/50 books, every warning, every skipped item.
4. **Encoding**: set `resp.encoding = "utf-8"` (the site sends no charset, otherwise `£` turns into `Â£`).
5. **Follow the `next` link** for pagination instead of hardcoding page numbers.
6. **List page is not enough**: category and exact stock live on the book's own page.
7. **Numeric output**: price as float (`51.77`), rating as int 1-5 (`Three` -> 3).
8. **Save to CSV** (`kitaplar.csv`, utf-8-sig) and **verify**: compare total and per-category counts with the numbers the site reports (`verify.py`). Do not call the data complete before they match.
9. **Reporting**: when a script fails, give the error message plus the expected result, never just "it does not work".
