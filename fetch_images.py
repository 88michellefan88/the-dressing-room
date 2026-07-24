"""
Fetch product images for each row in sourcing-list.csv.

For each row, searches DuckDuckGo Images for "{brand} {name}",
downloads the first result, and saves it under the filename in `save_as`.

Rows it can't resolve are printed at the end.
"""

import csv
import os
import sys
import time

from ddgs import DDGS
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "sourcing-list.csv")
OUT_DIR = os.path.join(HERE, "images")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}


def fetch_one(brand: str, name: str, category: str, save_path: str) -> bool:
    """Search for one image and save it. Returns True on success."""
    if category == "shoes":
        query = f"{brand} {name} pair product"
    else:
        query = f"{brand} {name} product"
    print(f"  searching: {query}")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=5))
    except Exception as e:
        print(f"  search failed: {e}")
        return False

    if not results:
        print("  no results")
        return False

    for i, result in enumerate(results):
        url = result.get("image")
        if not url:
            continue
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
            print(f"  saved (result #{i + 1}) from {url[:80]}")
            return True
        except Exception as e:
            print(f"  result #{i + 1} download failed: {e}")
            continue

    return False


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    misses = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Processing {len(rows)} rows -> {OUT_DIR}\n")

    for row in rows:
        item_id = row["id"]
        brand = row["brand"]
        name = row["name"]
        save_as = row["save_as"]
        save_path = os.path.join(OUT_DIR, save_as)

        print(f"[{item_id}] {brand} — {name}")

        if os.path.exists(save_path):
            print("  already downloaded, skipping")
            continue

        category = row["category"]
        ok = fetch_one(brand, name, category, save_path)
        if not ok:
            misses.append((item_id, brand, name))

        time.sleep(1)  # be polite

    print("\n" + "=" * 40)
    if misses:
        print(f"Could not resolve {len(misses)} items:")
        for item_id, brand, name in misses:
            print(f"  {item_id}: {brand} — {name}")
    else:
        print("All items downloaded successfully.")


if __name__ == "__main__":
    sys.exit(main())
