"""books.toscrape.com scraper.

Gets every book from the catalogue (all pages), then opens each book's own page
to read the category (breadcrumb) and the exact stock count, which the list
page does not show. Result is saved to kitaplar.csv.
"""
import logging
import random
import re
import sys
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"
OUTPUT_CSV = "kitaplar.csv"
DELAY_RANGE = (0.5, 1.0)  # seconds between requests, to be polite to the site
MAX_RETRIES = 3
TIMEOUT = 15

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("scraper.log", encoding="utf-8")],
)
log = logging.getLogger("scraper")

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (educational scraper; books.toscrape.com practice)"


def polite_sleep():
    time.sleep(random.uniform(*DELAY_RANGE))


def fetch(url):
    """GET with retries. Returns BeautifulSoup or None if the page cannot be opened."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            resp.encoding = "utf-8"  # site sends no charset; without this '£' becomes 'Â£'
            return BeautifulSoup(resp.text, "lxml")
        except requests.RequestException as exc:
            log.warning("attempt %d/%d failed for %s: %s", attempt, MAX_RETRIES, url, exc)
            time.sleep(attempt * 2)  # back off a bit more every time
    log.error("giving up on %s", url)
    return None


def parse_price(text):
    """'£51.77' -> 51.77 ; None if there is no number."""
    match = re.search(r"\d+(?:\.\d+)?", text or "")
    return float(match.group()) if match else None


def parse_rating(tag):
    """<p class="star-rating Three"> -> 3 ; None if missing."""
    if tag is None:
        return None
    for cls in tag.get("class", []):
        if cls in RATING_WORDS:
            return RATING_WORDS[cls]
    return None


def parse_stock(text):
    """'In stock (22 available)' -> ('In stock', 22)."""
    text = " ".join((text or "").split())
    if not text:
        return None, None
    count = re.search(r"\((\d+) available\)", text)
    status = "In stock" if text.lower().startswith("in stock") else text
    return status, int(count.group(1)) if count else None


def text_or_none(tag):
    return tag.get_text(strip=True) if tag else None


def scrape_listing():
    """Walk every catalogue page by following the 'next' link."""
    books, url, page_no = [], BASE_URL, 0
    while url:
        soup = fetch(url)
        if soup is None:
            log.error("listing page failed, stopping pagination at %s", url)
            break
        page_no += 1
        for art in soup.select("article.product_pod"):
            try:
                link = art.h3.a
                books.append({
                    "title": link.get("title") or link.get_text(strip=True),
                    "price": parse_price(text_or_none(art.select_one("p.price_color"))),
                    "rating": parse_rating(art.select_one("p.star-rating")),
                    "url": urljoin(url, link["href"]),
                })
            except (AttributeError, KeyError, TypeError) as exc:
                log.warning("skipping malformed book card on %s: %s", url, exc)
        log.info("listing page %d done, %d books so far", page_no, len(books))
        nxt = soup.select_one("li.next a")
        url = urljoin(url, nxt["href"]) if nxt else None
        polite_sleep()
    return books


def scrape_detail(book):
    """Add category + stock from the book's own page. Never raises."""
    book.update(category=None, stock_status=None, stock_count=None)
    soup = fetch(book["url"])
    if soup is None:
        return
    try:
        crumbs = soup.select("ul.breadcrumb li")
        if len(crumbs) >= 3:
            book["category"] = text_or_none(crumbs[2])
        book["stock_status"], book["stock_count"] = parse_stock(
            text_or_none(soup.select_one("p.availability"))
        )
    except Exception as exc:  # a weird page must not kill a 1000-page crawl
        log.warning("could not parse details of %s: %s", book["url"], exc)


def main():
    books = scrape_listing()
    total = len(books)
    log.info("listing finished: %d books, now reading detail pages", total)
    for i, book in enumerate(books, 1):
        scrape_detail(book)
        if i % 50 == 0 or i == total:
            log.info("detail pages: %d/%d", i, total)
        polite_sleep()

    df = pd.DataFrame(books).rename(columns={
        "title": "kitap_adi", "price": "fiyat", "rating": "puan",
        "stock_status": "stok_durumu", "stock_count": "stok_adedi", "category": "kategori",
    })
    df = df[["kitap_adi", "fiyat", "puan", "stok_durumu", "stok_adedi", "kategori", "url"]]
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    log.info("saved %d rows to %s", len(df), OUTPUT_CSV)
    missing = df.isna().sum()
    if missing.any():
        log.warning("missing values per column:\n%s", missing[missing > 0].to_string())


if __name__ == "__main__":
    sys.exit(main())
