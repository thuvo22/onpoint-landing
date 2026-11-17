#!/usr/bin/env python3
"""Add published starting prices to Service structured data (idempotent).

Thu 2026-11-17, after the Brock Misner review ("everything that we missed, do it"): AI answers
and Google read prices from structured data first, and our Service schema had none.
Only prices already published on the site are used:
  bathroom remodeling  -> full bathroom remodels start at $18,000 (llms.txt, bathroom pages)
  drywall              -> $1,000 project minimum (drywall pages, Colony pages)
Painting and flooring are quoted per project, so they get no price.

Every JSON-LD block on the site round-trips through json byte for byte (checked 11/17), so a
block is only rewritten when it re-serializes to the exact original text first.
Usage: python3 tools/schema_prices.py [--check]
"""
import json, re, subprocess, sys

BATH = {"@type": "Offer", "priceCurrency": "USD",
        "priceSpecification": {"@type": "PriceSpecification", "minPrice": 18000, "priceCurrency": "USD"},
        "description": "Full bathroom remodels start at $18,000. Most projects are $25,000 to $45,000. Every project gets its own fixed written quote."}
DRY = {"@type": "Offer", "priceCurrency": "USD",
       "priceSpecification": {"@type": "PriceSpecification", "minPrice": 1000, "priceCurrency": "USD"},
       "description": "Drywall projects have a $1,000 minimum. Every project gets its own written quote."}


def offer_for(svc):
    t = f"{svc.get('serviceType') or ''} {svc.get('name') or ''}".lower()
    if "bathroom remodel" in t and "tub" not in t:
        return BATH
    if any(w in t for w in ("drywall", "ceiling", "popcorn", "texture")) and "paint" not in (svc.get("serviceType") or "").lower().replace("and painting", ""):
        return DRY
    return None


def walk(o, changed):
    if isinstance(o, dict):
        if o.get("@type") == "Service" and "offers" not in o:
            off = offer_for(o)
            if off:
                o["offers"] = off
                changed.append(o.get("name") or o.get("serviceType"))
        if o.get("@type") == "Offer" and isinstance(o.get("itemOffered"), dict) and "priceSpecification" not in o:
            off = offer_for(o["itemOffered"])
            if off:
                o["priceCurrency"] = "USD"
                o["priceSpecification"] = off["priceSpecification"]
                changed.append("catalog: " + (o["itemOffered"].get("name") or ""))
        for k, v in list(o.items()):
            if k == "itemOffered" and o.get("@type") == "Offer":
                continue   # the catalog offer carries the price; no second offer nested inside it
            walk(v, changed)
    elif isinstance(o, list):
        for v in o:
            walk(v, changed)


def dump_like(obj, raw):
    for kw in ({"separators": (",", ":"), "ensure_ascii": False}, {"ensure_ascii": False},
               {"separators": (",", ":")}, {}):
        if json.dumps(json.loads(raw), **kw) == raw:
            return json.dumps(obj, **kw)
    return None


def main():
    check = "--check" in sys.argv
    files = subprocess.run(["git", "ls-files", "*.html"], capture_output=True, text=True, check=True).stdout.split()
    total = 0
    for f in files:
        s = open(f, encoding="utf-8").read()
        out, pos, edits = [], 0, []
        for m in re.finditer(r'(<script type="application/ld\+json">)(.*?)(</script>)', s, re.S):
            raw = m.group(2)
            obj = json.loads(raw)
            changed = []
            walk(obj, changed)
            if not changed:
                continue
            new = dump_like(obj, raw)
            if new is None:
                print("SKIP (style not reproducible):", f)
                continue
            out.append(s[pos:m.start(2)]); out.append(new); pos = m.end(2); edits += changed
        if edits:
            total += len(edits)
            print(f"{f}: {len(edits)} ({'; '.join(e[:40] for e in edits[:3])})")
            if not check:
                out.append(s[pos:])
                open(f, "w", encoding="utf-8").write("".join(out))
    print("services priced:", total, "(check only)" if check else "")


if __name__ == "__main__":
    main()
