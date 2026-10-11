#!/usr/bin/env python3
"""Build the sitemap from canonical, indexable HTML; --check detects drift."""

import argparse
import fnmatch
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}


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


def collect_urls(root):
    policy = root / "sitemap-exclude.txt"
    exclusions = [line.strip() for line in policy.read_text().splitlines()
                  if line.strip() and not line.lstrip().startswith("#")] if policy.exists() else []
    urls = set()
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
        urls.add(canonical)
    return sorted(urls)


def render_sitemap(urls):
    ET.register_namespace("", NAMESPACE)
    document = ET.Element(f"{{{NAMESPACE}}}urlset")
    for url in urls:
        entry = ET.SubElement(document, f"{{{NAMESPACE}}}url")
        ET.SubElement(entry, f"{{{NAMESPACE}}}loc").text = url
    # lastmod is optional; omit it instead of claiming each build changes page content.
    ET.indent(document, space="  ")
    return ET.tostring(document, encoding="utf-8", xml_declaration=True) + b"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        urls = collect_urls(ROOT)
    except ValueError as error:
        parser.exit(1, f"Sitemap validation failed: {error}\n")
    expected = render_sitemap(urls)
    output = ROOT / "sitemap.xml"
    if args.check:
        if not output.exists() or output.read_bytes() != expected:
            parser.exit(1, "Sitemap is out of date. Run python3 tools/generate_sitemap.py\n")
        print(f"Sitemap verified: {len(urls)} canonical URLs")
    else:
        output.write_bytes(expected)
        print(f"Sitemap generated: {len(urls)} canonical URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
