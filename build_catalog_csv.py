"""
Read every catalog item out of dressing-room.html and (re)write sourcing-list.csv
with a row per item. The scraper reads this CSV, so any item in it becomes a
candidate for an image fetch.
"""

import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(HERE, "dressing-room.html")
CSV_PATH = os.path.join(HERE, "sourcing-list.csv")

# Matches each catalog entry's opening line, e.g.:
#   { id:"s1", category:"shoes", name:"Leather loafers, black", brand:"G.H. Bass",
# And a second line later containing:
#   search_url:"https://..."
ITEM_RE = re.compile(
    r'\{\s*id:"(?P<id>[^"]+)",\s*'
    r'category:"(?P<category>[^"]+)",\s*'
    r'name:"(?P<name>[^"]+)",\s*'
    r'brand:"(?P<brand>[^"]+)"'
    r'.*?search_url:"(?P<search_url>[^"]+)"',
    re.DOTALL,
)


def main() -> None:
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()

    rows = []
    seen_ids = set()
    for m in ITEM_RE.finditer(html):
        item = m.groupdict()
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])
        rows.append(
            {
                "id": item["id"],
                "category": item["category"],
                "name": item["name"],
                "brand": item["brand"],
                "search_url": item["search_url"],
                "save_as": f"{item['id']}.jpg",
            }
        )

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "category", "name", "brand", "search_url", "save_as"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {CSV_PATH}")
    by_cat = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
