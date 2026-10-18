#!/usr/bin/env python3
"""Refresh the Google review count printed on public pages and in llms.txt.

    python3 tools/update_review_count.py --count 57
    python3 tools/update_review_count.py --from-api   # bathroom.onpointprostx.com/api/reviews

The count drifts every time a review lands, so run this before a release and
commit the result. It only rewrites the visible trust-bar phrases
("<n> Google reviews" and the linked "<n> reviews"). It never adds
AggregateRating or Review schema; the site deliberately carries none.
"""
import argparse, json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://bathroom.onpointprostx.com/api/reviews"
SKIP = {".git", "node_modules", ".venv", "__pycache__"}


def live_count():
    with urllib.request.urlopen(API, timeout=10) as response:
        data = json.load(response)
    if data.get("status") != "ok" or not isinstance(data.get("count"), int) or data["count"] <= 0:
        sys.exit("Live review count unavailable; pass --count explicitly.")
    return data["count"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--count", type=int)
    group.add_argument("--from-api", action="store_true")
    args = parser.parse_args()
    count = args.count if args.count else live_count()
    if count <= 0:
        sys.exit("Count must be positive.")
    google = re.compile(r"\b\d+ Google reviews?\b")
    linked = re.compile(r"(>)\d+ reviews(</a>)")
    changed = 0
    files = [p for p in ROOT.rglob("*.html") if not SKIP & set(p.relative_to(ROOT).parts)] + [ROOT / "llms.txt"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        new = google.sub(f"{count} Google reviews", text)
        new = linked.sub(rf"\g<1>{count} reviews\g<2>", new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Review count set to {count} in {changed} files")


if __name__ == "__main__":
    main()
