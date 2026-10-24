"""Final spot-check through the Playwright MCP server (config: .mcp.json).

A real Chrome, driven by MCP tools (browser_navigate + browser_evaluate), opens a
random sample of book pages plus the first and last book, reads title, price,
rating, category and stock *as rendered in the browser* and compares them with
kitaplar_temiz.csv. Also checks the site-reported total. Writes mcp_verify_report.csv.
"""
import json
import random
import re
import sys
import time

import pandas as pd

from mcp_client import McpClient

SAMPLE = 60
READ_BOOK = """() => ({
  title: document.querySelector('h1').innerText.trim(),
  price: document.querySelector('p.price_color').innerText.trim(),
  rating: [...document.querySelector('p.star-rating').classList].find(c => c !== 'star-rating'),
  category: document.querySelectorAll('ul.breadcrumb li')[2].innerText.trim(),
  stock: document.querySelector('p.availability').innerText.trim()
})"""
READ_TOTAL = "() => document.querySelector('form.form-horizontal strong').innerText.trim()"
WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def evaluate(mcp, function):
    """Run JS in the page via MCP and return the parsed JSON result."""
    text = mcp.call("browser_evaluate", function=function)
    block = re.search(r"### Result\s*(.*?)(?:\n###|\Z)", text, re.S).group(1).strip()
    block = re.sub(r"^```(?:json)?|```$", "", block, flags=re.M).strip()
    return json.loads(block)


def main():
    df = pd.read_csv("kitaplar_temiz.csv")
    rng = random.Random(2026)
    rows = [df.iloc[0], df.iloc[-1]] + [df.iloc[i] for i in rng.sample(range(1, len(df) - 1), SAMPLE)]
    mcp = McpClient()
    problems = []
    try:
        print("MCP tools available:", len(mcp.list_tools()))
        mcp.call("browser_navigate", url="https://books.toscrape.com/catalogue/page-1.html")
        total = int(re.search(r"\d+", evaluate(mcp, READ_TOTAL)).group())
        print(f"Site total via MCP browser: {total} | CSV rows: {len(df)}")
        if total != len(df):
            problems.append(("-", f"total {total} != {len(df)}"))
        for i, r in enumerate(rows, 1):
            mcp.call("browser_navigate", url=r["Link"])
            d = evaluate(mcp, READ_BOOK)
            price = float(re.search(r"[\d.]+", d["price"]).group())
            stock = int(re.search(r"\((\d+) available\)", d["stock"]).group(1))
            errs = []
            if d["title"] != r["Kitap Adı"]: errs.append(f"title {d['title']!r}")
            if abs(price - r["Fiyat"]) > 0.001: errs.append(f"price {price}")
            if WORDS[d["rating"]] != r["Puan"]: errs.append(f"rating {d['rating']}")
            if d["category"] != r["Kategori"]: errs.append(f"category {d['category']}")
            if stock != r["Stok Adedi"]: errs.append(f"stock {stock}")
            if errs:
                problems.append((r["Link"], "; ".join(errs)))
            if i % 20 == 0:
                print(f"{i}/{len(rows)} checked, {len(problems)} problems", flush=True)
            time.sleep(0.5)
    finally:
        mcp.close()
    pd.DataFrame(problems, columns=["link", "problem"]).to_csv("mcp_verify_report.csv", index=False)
    print(f"MCP CHECK DONE: {len(rows)} books opened in Chrome via Playwright MCP, {len(problems)} problems")
    return 0 if not problems else 2


if __name__ == "__main__":
    sys.exit(main())
