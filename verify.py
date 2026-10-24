"""Compare kitaplar.csv with the numbers the site itself reports.

1. Total: 'N results' text on the first catalogue page.
2. Per category: 'N results' text on each category page (50 requests).
"""
import re
import sys
import time

import pandas as pd

from scraper import fetch, polite_sleep

HOME = "https://books.toscrape.com/catalogue/page-1.html"


def results_count(soup):
    """'1000 results - showing 1 to 20.' -> 1000"""
    strong = soup.select_one("form.form-horizontal strong")
    match = re.search(r"\d+", strong.get_text()) if strong else None
    return int(match.group()) if match else None


def main():
    df = pd.read_csv("kitaplar.csv")
    home = fetch(HOME)
    if home is None:
        print("cannot open site, verification skipped")
        return 1

    site_total = results_count(home)
    print(f"Site total: {site_total} | CSV rows: {len(df)} | unique URLs: {df['url'].nunique()}")
    ok = site_total == len(df) == df["url"].nunique()

    rows = []
    for link in home.select("ul.nav-list ul a"):
        name = link.get_text(strip=True)
        soup = fetch("https://books.toscrape.com/catalogue/" + link["href"])
        rows.append((name, results_count(soup) if soup else None, int((df["kategori"] == name).sum())))
        polite_sleep()
    cat = pd.DataFrame(rows, columns=["kategori", "sitede", "csv_de"])
    bad = cat[cat["sitede"] != cat["csv_de"]]
    print(f"Categories checked: {len(cat)} | mismatches: {len(bad)}")
    if len(bad):
        print(bad.to_string(index=False))
    cat.to_csv("dogrulama_kategori.csv", index=False)
    print("RESULT:", "OK - everything matches" if ok and bad.empty else "MISMATCH")
    return 0 if ok and bad.empty else 2


if __name__ == "__main__":
    sys.exit(main())
