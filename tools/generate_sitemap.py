#!/usr/bin/env python3
"""Build the sitemap from canonical, indexable HTML; --check detects drift.

lastmod comes from tools/sitemap-lastmod.json, a ledger of each page's content
hash and the date that hash was first seen, so a page's lastmod only moves when
its bytes change. Run the generator after editing pages and commit both files.
--seed-from-git initialises the ledger from each file's last commit date.
"""

import argparse
import datetime
import fnmatch
import hashlib
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}
LEDGER = "tools/sitemap-lastmod.json"


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "meta" and (attrs.get("name") or "").lower() in {"robots", "googlebot"}:
            directives = (attrs.get("content") or "").lower().replace(",", " ").split()
            self.noindex |= "noindex" in directives or "none" in directives


def collect_entries(root):
    """Return [(canonical_url, relative_path)] for every sitemap-eligible page."""
    policy = root / "sitemap-exclude.txt"
    exclusions = [line.strip() for line in policy.read_text().splitlines()
                  if line.strip() and not line.lstrip().startswith("#")] if policy.exists() else []
    urls = {}
    for path in sorted(root.rglob("*.html")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if any(fnmatch.fnmatch(relative.as_posix(), pattern) for pattern in exclusions):
            continue
        metadata = PageMetadata()
        metadata.feed(path.read_text(encoding="utf-8"))
        if metadata.noindex:
            continue
        if len(metadata.canonicals) != 1:
            raise ValueError(f"{relative}: expected exactly one canonical URL")
        canonical = metadata.canonicals[0]
        parsed = urlsplit(canonical)
        if parsed.scheme != "https" or parsed.netloc != "onpointprostx.com" or parsed.query or parsed.fragment:
            raise ValueError(f"{relative}: invalid canonical URL {canonical!r}")
        canonical_path = unquote(parsed.path).lstrip("/")
        if not canonical_path or canonical_path.endswith("/"):
            canonical_path += "index.html"
        # Redirect/duplicate documents can point elsewhere; include the target's own file.
        if canonical_path != relative.as_posix():
            continue
        if canonical in urls:
            raise ValueError(f"Duplicate canonical: {canonical}")
        urls[canonical] = relative.as_posix()
    return sorted(urls.items())


def collect_urls(root):
    return [url for url, _ in collect_entries(root)]


def load_ledger(root):
    path = root / LEDGER
    return json.loads(path.read_text()) if path.exists() else {}


def lastmod_map(root, entries, ledger, today=None, seed_from_git=False):
    """Return ({url: date}, new_ledger). A date moves only when the file's hash changes."""
    today = today or datetime.date.today().isoformat()
    dates, new_ledger = {}, {}
    for url, relative in entries:
        digest = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        record = ledger.get(relative)
        if record and record.get("sha256") == digest:
            date = record["lastmod"]
        elif seed_from_git:
            date = _git_date(root, relative) or today
        else:
            date = today
        new_ledger[relative] = {"sha256": digest, "lastmod": date}
        dates[url] = date
    return dates, new_ledger


def _git_date(root, relative):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", relative], cwd=root,
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return out or None


def render_sitemap(urls, lastmod=None):
    ET.register_namespace("", NAMESPACE)
    document = ET.Element(f"{{{NAMESPACE}}}urlset")
    for url in urls:
        entry = ET.SubElement(document, f"{{{NAMESPACE}}}url")
        ET.SubElement(entry, f"{{{NAMESPACE}}}loc").text = url
        if lastmod and lastmod.get(url):
            ET.SubElement(entry, f"{{{NAMESPACE}}}lastmod").text = lastmod[url]
    ET.indent(document, space="  ")
    return ET.tostring(document, encoding="utf-8", xml_declaration=True) + b"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--seed-from-git", action="store_true", help="first run only: take lastmod from git history")
    args = parser.parse_args()
    try:
        entries = collect_entries(ROOT)
    except ValueError as error:
        parser.exit(1, f"Sitemap validation failed: {error}\n")
    urls = [url for url, _ in entries]
    ledger = load_ledger(ROOT)
    dates, new_ledger = lastmod_map(ROOT, entries, ledger, seed_from_git=args.seed_from_git)
    expected = render_sitemap(urls, dates)
    output = ROOT / "sitemap.xml"
    ledger_bytes = (json.dumps(new_ledger, indent=1, sort_keys=True) + "\n").encode()
    if args.check:
        if not output.exists() or output.read_bytes() != expected or new_ledger != ledger:
            parser.exit(1, "Sitemap is out of date. Run python3 tools/generate_sitemap.py\n")
        print(f"Sitemap verified: {len(urls)} canonical URLs")
    else:
        output.write_bytes(expected)
        (ROOT / LEDGER).write_bytes(ledger_bytes)
        print(f"Sitemap generated: {len(urls)} canonical URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
