"""OPTIONAL: shorten every book URL with the bit.ly API -> qisa_linkler.csv.

You run this yourself with your own token (never paste the token into chat or code):
    PowerShell:  $env:BITLY_TOKEN = "<your token>" ; python shorten_links.py
Then re-run:  python clean_export.py   (merges the short links into the CSV/Excel)

Notes: bit.ly free plans allow only a handful of new links per month, 1000 links
needs a paid plan. Resumable: already shortened URLs are skipped.
"""
import os
import sys
import time

import pandas as pd
import requests

OUT = "qisa_linkler.csv"
API = "https://api-ssl.bitly.com/v4/shorten"


def main():
    token = os.environ.get("BITLY_TOKEN")
    if not token:
        print("Set the BITLY_TOKEN environment variable first.")
        return 1
    urls = pd.read_csv("kitaplar.csv")["url"].tolist()
    done = pd.read_csv(OUT) if os.path.exists(OUT) else pd.DataFrame(columns=["url", "qisa_link"])
    seen = dict(zip(done["url"], done["qisa_link"]))
    for i, url in enumerate(urls, 1):
        if url in seen:
            continue
        try:
            r = requests.post(API, json={"long_url": url}, headers={"Authorization": f"Bearer {token}"}, timeout=15)
            r.raise_for_status()
            seen[url] = r.json()["link"]
        except (requests.RequestException, KeyError, ValueError) as exc:
            print(f"[{i}] failed for {url}: {exc}")
            if getattr(exc, "response", None) is not None and exc.response.status_code in (402, 403, 429):
                print("Plan/rate limit reached, stopping. Progress is saved; re-run later.")
                break
        pd.DataFrame(list(seen.items()), columns=["url", "qisa_link"]).to_csv(OUT, index=False)
        time.sleep(1)
    print(f"{len(seen)}/{len(urls)} links shortened -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
