"""Independent verification PASS 1.

Starts from the *final* kitaplar_temiz.csv (not from the scraper's memory), opens
every book's own page again from its Link and compares title (h1), price, rating,
category and stock with the row. Proves each link sits next to the right book.
Writes recheck_detail_report.csv. Does not import scraper.py on purpose.
"""
import re
import sys
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
s = requests.Session()


def get(url):
    for i in range(3):
        try:
            r = s.get(url, timeout=15)
            r.raise_for_status()
            return BeautifulSoup(r.content.decode("utf-8"), "lxml")
        except requests.RequestException:
            time.sleep(2 * (i + 1))
    return None


df = pd.read_csv("kitaplar_temiz.csv").fillna("")
bad = []
for i, row in enumerate(df.itertuples(index=False), 1):
    soup = get(row.Link)
    if soup is None:
        bad.append((row.Link, "page not reachable"))
        continue
    h1 = soup.select_one("h1").get_text(strip=True)
    price = float(re.search(r"[\d.]+", soup.select_one("p.price_color").get_text()).group())
    rating = next(RATING[c] for c in soup.select_one("p.star-rating")["class"] if c in RATING)
    cat = soup.select("ul.breadcrumb li")[2].get_text(strip=True)
    stock = int(re.search(r"\((\d+) available\)", soup.select_one("p.availability").get_text()).group(1))
    upc_id = re.search(r"_(\d+)/index\.html$", row.Link).group(1)
    errs = []
    if h1 != row[1]: errs.append(f"title '{h1}' != '{row[1]}'")
    if abs(price - row.Fiyat) > 0.001: errs.append(f"price {price} != {row.Fiyat}")
    if rating != row.Puan: errs.append(f"rating {rating} != {row.Puan}")
    if cat != row.Kategori: errs.append(f"category {cat} != {row.Kategori}")
    if stock != row[5]: errs.append(f"stock {stock} != {row[5]}")
    if str(row[0]) != upc_id: errs.append(f"id {row[0]} != url id {upc_id}")
    if errs:
        bad.append((row.Link, "; ".join(errs)))
    if i % 100 == 0:
        print(f"{i}/{len(df)} checked, {len(bad)} problems", flush=True)
    time.sleep(0.5)

pd.DataFrame(bad, columns=["link", "problem"]).to_csv("recheck_detail_report.csv", index=False)
print(f"PASS 1 DONE: {len(df)} rows, {len(bad)} problems")
sys.exit(0 if not bad else 2)
