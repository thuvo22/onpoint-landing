# OnPoint Pros website

Static HTML, images, and small JavaScript files for onpointprostx.com. Published files live at the repository root for GitHub Pages.

## Build the production CSS

Use Node.js and npm:

```sh
npm ci
npm run build:css
python3 tools/generate_sitemap.py --check
python3 tools/test_generate_sitemap.py
```

Commit both source changes and the generated `assets/css/site.min.css` and `assets/css/default.min.css` files. GitHub Pages serves the checked-in files; it does not need Node at runtime.

After adding or removing public pages, run `python3 tools/generate_sitemap.py`, review the resulting `sitemap.xml`, then run the checks above. The generator follows the explicit exclusions in `sitemap-exclude.txt`; campaign funnels and legal pages are intentionally omitted.

Tailwind is pinned to 3.4.17 in `package-lock.json`. The build scans all public HTML directories and the root JavaScript files, including the classes used by the gallery, estimate form, mobile navigation, and cookie controls. Keep dynamically selected classes as complete literal strings so Tailwind can find them. Rebuild CSS whenever those classes change. Add a content path to `tailwind.config.cjs` when adding a new template directory.

Most pages use `site.min.css`, preserving their Montserrat font stack and custom brand colors. Contact, privacy, terms, and the three campaign pages under `before/` and `list/` use `default.min.css`, preserving their original Tailwind defaults and inline font choices. No new Tailwind plugins are enabled.

Fonts are self-hosted in `assets/fonts/` and declared in `styles/site.css` with `font-display: swap`. The Latin and Latin Extended files are loaded only when the page needs their characters. Font source URLs, checksums, and SIL Open Font Licenses are included alongside the assets. Do not restore the Google Fonts stylesheet or Tailwind browser CDN script.

## Preview and verify

```sh
python3 -m http.server 8080
```

Check the homepage at mobile and desktop widths, a service page, contact form, gallery and project dialog, cookie controls, and a campaign page. Confirm styles and fonts load without a third-party CSS request. Do not submit real lead forms during visual checks. Homepage hero images should load eagerly; below-fold images should remain lazy-loaded.

Production deployment uses the repository's configured GitHub Pages branch and custom domain. DNS, HTTPS redirect settings, and third-party business profiles are managed separately from these static files.
