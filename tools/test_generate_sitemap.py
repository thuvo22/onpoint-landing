"""Protect noindex funnels and canonical URL handling when rebuilding the sitemap."""

from pathlib import Path
import tempfile
import unittest

from generate_sitemap import collect_entries, collect_urls, lastmod_map, render_sitemap


class SitemapEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def page(self, path, head):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(f"<!doctype html><html><head>{head}</head><body>Page</body></html>")

    def test_noindex_funnel_is_excluded_without_needing_a_canonical(self):
        self.page("list/thanks.html", '<meta name="robots" content="NOINDEX, nofollow">')
        self.assertEqual(collect_urls(self.root), [])

    def test_googlebot_none_is_excluded(self):
        self.page("before/index.html", '<meta name="googlebot" content="none">')
        self.assertEqual(collect_urls(self.root), [])

    def test_home_and_directory_index_use_canonical_urls(self):
        self.page("index.html", '<link rel="canonical" href="https://onpointprostx.com/">')
        self.page("blog/index.html", '<link rel="canonical" href="https://onpointprostx.com/blog/">')
        self.assertEqual(collect_urls(self.root), ["https://onpointprostx.com/", "https://onpointprostx.com/blog/"])

    def test_duplicate_document_does_not_create_an_extra_sitemap_entry(self):
        head = '<link rel="canonical" href="https://onpointprostx.com/about.html">'
        self.page("about.html", head)
        self.page("old-about.html", head)
        self.assertEqual(collect_urls(self.root), ["https://onpointprostx.com/about.html"])

    def test_explicit_policy_excludes_legal_page(self):
        (self.root / "sitemap-exclude.txt").write_text("# Keep accessible, omit from sitemap\nprivacy.html\n")
        self.page("privacy.html", '<link rel="canonical" href="https://onpointprostx.com/privacy.html">')
        self.assertEqual(collect_urls(self.root), [])

    def test_insecure_external_or_parameterized_canonical_fails(self):
        for url in ["http://onpointprostx.com/about.html", "https://other.example/about.html", "https://onpointprostx.com/about.html?tracking=1"]:
            with self.subTest(url=url):
                self.page("about.html", f'<link rel="canonical" href="{url}">')
                with self.assertRaises(ValueError):
                    collect_urls(self.root)

    def test_missing_canonical_fails_instead_of_silently_omitting_a_live_page(self):
        self.page("contact.html", "<title>Contact</title>")
        with self.assertRaises(ValueError):
            collect_urls(self.root)

    def test_lastmod_moves_only_when_page_bytes_change(self):
        self.page("about.html", '<link rel="canonical" href="https://onpointprostx.com/about.html">')
        entries = collect_entries(self.root)
        dates, ledger = lastmod_map(self.root, entries, {}, today="2026-10-01")
        self.assertEqual(dates["https://onpointprostx.com/about.html"], "2026-10-01")
        dates, ledger = lastmod_map(self.root, entries, ledger, today="2026-10-17")
        self.assertEqual(dates["https://onpointprostx.com/about.html"], "2026-10-01")
        self.page("about.html", '<link rel="canonical" href="https://onpointprostx.com/about.html"><title>Changed</title>')
        dates, ledger = lastmod_map(self.root, entries, ledger, today="2026-10-17")
        self.assertEqual(dates["https://onpointprostx.com/about.html"], "2026-10-17")
        self.assertIn(b"<lastmod>2026-10-17</lastmod>", render_sitemap(["https://onpointprostx.com/about.html"], dates))

    def test_removed_page_leaves_the_ledger(self):
        self.page("a.html", '<link rel="canonical" href="https://onpointprostx.com/a.html">')
        _, ledger = lastmod_map(self.root, collect_entries(self.root), {"gone.html": {"sha256": "x", "lastmod": "2026-01-01"}}, today="2026-10-17")
        self.assertEqual(set(ledger), {"a.html"})


if __name__ == "__main__":
    unittest.main()
