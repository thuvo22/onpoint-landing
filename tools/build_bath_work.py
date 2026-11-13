#!/usr/bin/env python3
"""Inject the shared "Recent bathroom work" section into the bathroom pages.

Photos are real OnPoint jobs from the crew's phones (images/projects/bath/).
Captions name the work, not the city: Thu 11/13, bathroom photos can go on
any city page. Run build, then tools/optimize_project_images.py.
Markers <!-- bath-work:start --> ... <!-- bath-work:end --> make it idempotent.
"""
import pathlib, re, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = "/images/projects/bath/"
START, END = "<!-- bath-work:start -->", "<!-- bath-work:end -->"

PAIRS = {
    "shower-tub": dict(title="Framed shower stall and old tub to a glass shower and tub deck",
        before=("shower-tub-before.jpg", "Before: gold framed shower stall with a curtain and the original drop-in tub under the window"),
        after=("shower-tub-after.jpg", "After: tiled walk-in shower with frameless glass and a black tub deck in the same spot"),
        caption="The framed stall and the old tub came out. A tiled walk-in shower with frameless glass and a black tub deck went in, with the same window and vanity.", labels=("BEFORE", "AFTER")),
    "tub-wall": dict(title="Tub wall from bare board to finished tile",
        before=("tub-wall-before.jpg", "Before: tub wall stripped to green board with a framed niche opening"),
        after=("tub-wall-after.jpg", "After: the same wall in large dark tile with a built in niche and the tub reset on its deck"),
        caption="After demo the tub wall was bare board. The same wall finished in large dark tile with a built in niche, and the tub reset on its deck.", labels=("BEFORE", "AFTER")),
    "shower-floor": dict(title="Shower floor rebuilt",
        before=("shower-floor-before.jpg", "Before: shower pan with stained grout and mold at the curb"),
        after=("shower-floor-after.jpg", "After: new hex tile pan with a glass mosaic band and a new sliding glass door"),
        caption="The old pan had stained grout and mold at the curb. We took the floor out, waterproofed, set a new hex tile pan with a mosaic band and hung a new sliding glass door.", labels=("BEFORE", "AFTER")),
    "vanity-side": dict(title="The same remodel from the vanity side",
        before=("vanity-side-before.jpg", "Before: original tub and framed shower stall seen from the vanity"),
        after=("vanity-side-after.jpg", "After: tub deck and frameless glass shower seen from the vanity"),
        caption="Same room from the vanity. The framed stall and tub were replaced with a glass shower, dark tile and a tub deck.", labels=("BEFORE", "AFTER")),
    "tub-wall-tile": dict(title="Tub wall on tile day",
        before=("tub-wall-board.jpg", "Cement board and a framed niche over the tub before tile"),
        after=("tub-wall-tile.jpg", "Large marble look tile set over the tub with spacers in, grout next"),
        caption="Cement board and a framed niche over the tub, then large marble look tile set with spacers before grout.", labels=("BOARD UP", "TILE SET")),
}
SINGLES = {
    "glass-band": ("single-shower-glass-band.jpg", "Walk-in shower with gray tile, a white accent band, frameless glass and a marble curb"),
    "tub-deck": ("single-tub-deck-floor.jpg", "Drop-in tub with a tile deck and new large format floor tile next to the glass shower"),
    "gray-hex": ("single-shower-gray-hex.jpg", "Finished shower with large gray tile, a glass panel and a hex mosaic floor"),
    "tub-surround": ("single-tub-surround.jpg", "Tub and shower surround retiled in gray stone look tile"),
    "dark-glass": ("single-dark-shower-glass.jpg", "Dark tile walk-in shower with frameless glass next to the tub deck"),
    "niche": ("single-niche-detail.jpg", "Built in shower niche trimmed in dark tile against a geometric patterned wall"),
}
GOOGLE_LISTING = "https://www.google.com/maps?cid=12396670433062033498"
# Google reviews from bathroom homeowners on the Allen listing, word for word, in the
# card design from the bathroom offer page (avatar, name, meta line, stars, highlights,
# the homeowner's own photos, Read on Google). Photos live in images/reviews/.
REVIEWS = [
    {"name": "Varun", "initial": "V", "avatar": "varun-avatar-20261028.png",
     "meta": "Frisco, TX · primary bathroom remodel · October 2026",
     "url": "https://maps.app.goo.gl/VAmCpaLmLo2xrXG56",
     "text": "This is the second time I’ve hired OnPoint Pros, this time for our primary bathroom remodel in Frisco. They were just as responsive as before, respected our home and kept us updated whenever anything changed. We’re very happy with how the vanity and tiled shower with gold fixtures turned out. <mark>The finished bathroom exceeded our expectations</mark>, and we would happily hire them again.",
     "photos": [("varun-review-shower-20261028", "Varun's review photo: tiled shower with gold fixtures"),
                ("varun-review-vanity-front-20261028", "Varun's review photo: new vanity")]},
    {"name": "Thùy Dung", "initial": "T", "avatar": "thuy-dung-avatar-20261022.webp",
     "meta": "Flower Mound, TX · bathroom remodel · September 2026",
     "url": "https://maps.app.goo.gl/tAL8x4fj7FrqtTqD7",
     "text": "We had an excellent experience with our bathroom remodel in Flower Mound. <mark>The transformation came out beautiful!</mark> The new walk-in shower, frameless glass, tile work, flooring, and vanity area completely changed the look and feel of the bathroom. The team was professional, responsive, and paid attention to the details throughout the project. They communicated well, kept everything moving, and made sure we were happy with the finished work.",
     "photos": [("thuy-dung-review-bathroom-20261028", "Thùy Dung's review photo: remodeled bathroom with walk-in shower")]},
    {"name": "Mohan Yechuri", "initial": "M", "avatar": None,
     "meta": "Allen, TX · primary bathroom remodel · November 2026",
     "url": GOOGLE_LISTING,
     "text": "My mom had difficulty getting in and out of the old shower, so we hired OnPoint Pros to remodel the primary bathroom in our Allen home. They also repaired the drywall and ceiling texture in the hallway. We’re really happy with how everything turned out, and <mark>it was a relief to have the same team handle both projects</mark>. We’d gladly call Dillon and his team again.",
     "photos": [("mohan-yechuri-review-tub-20261113", "Mohan's review photo: freestanding tub against blue marble look tile with gold fixtures"),
                ("mohan-yechuri-review-vanity-20261113", "Mohan's review photo: white vanity with gold faucet and arched mirror on blue marble look tile")]},
    {"name": "Siya Patel", "initial": "S", "avatar": None,
     "meta": "Allen, TX · shower remodel · November 2026",
     "url": GOOGLE_LISTING,
     "text": "The shower in our Allen home felt dated, and we were ready to replace the old tile and curtain. OnPoint Pros replaced them with <mark>green tile and frameless glass, which significantly improved the bathroom's appearance</mark>. They also added a niche and a new showerhead. We love how much more open the shower feels now. Really happy we decided to update it.",
     "photos": []},
    {"name": "Anshu Bhattarai", "initial": "A", "avatar": None,
     "meta": "Allen, TX · guest bath shower rebuild · November 2026",
     "url": GOOGLE_LISTING,
     "text": "OnPoint Pros rebuilt the shower in our guest bathroom in Allen TX. They tore out the old tub, redid the waterproofing and pan, and tiled the walls in a large stone look tile with a built-in niche and a gray hex tile floor. We got a rain shower head, a sliding glass door, and a grab bar they set into blocking so it is solid. Dillon helped us pick the tile and laid out the niche so the pattern lined up. The crew kept the hallway covered, <mark>finished when they said they would, and the price matched the quote</mark>. The shower looks like it belongs in a much newer house.",
     "photos": []},
    {"name": "Evan K", "initial": "E", "avatar": None,
     "meta": "Allen, TX · bathroom remodel · November 2026",
     "url": GOOGLE_LISTING,
     "text": "We had OnPoint Pros do our bathroom remodel and couldn’t be happier with the result. They <mark>helped us pick the design and materials, kept us informed the whole time</mark>, and were careful with our house. <mark>The shower came out beautiful.</mark> The tile, the hex floor, the glass doors and the shiplap all look great together. Would definitely recommend them!",
     "photos": [("evan-k-review-shower-20261110", "Evan K's review photo: walk-in shower with frameless glass, beige tile and black fixtures"),
                ("evan-k-review-shower-detail-20261110", "Evan K's review photo: shower tile with corner shelf and gray hex floor")]},
]
REV_IMG = "/images/reviews/"
SETS = [
    (["shower-tub", "shower-floor"], ["glass-band", "gray-hex", "tub-surround"]),
    (["tub-wall", "tub-wall-tile"], ["tub-deck", "gray-hex", "niche"]),
    (["shower-floor", "vanity-side"], ["glass-band", "tub-surround", "niche"]),
    (["tub-wall-tile", "shower-tub"], ["tub-deck", "gray-hex", "tub-surround"]),
    (["tub-wall", "shower-floor"], ["glass-band", "niche", "tub-surround"]),
]
CITY_PAGES = sorted(p for p in (ROOT / "bathroom").glob("*.html"))
SERVICE = ROOT / "services/bathroom-remodel.html"
INDEX = ROOT / "index.html"
CSS_LINK = '<link rel="stylesheet" href="/assets/css/project-proof.css?v=20261113-bath-work3">'

def img(fname, alt, w, h):
    return f'<img src="{IMG}{fname}" alt="{html.escape(alt)}" loading="lazy" decoding="async" width="{w}" height="{h}">'

def pair_card(key):
    p = PAIRS[key]
    b, a = p["before"], p["after"]; l1, l2 = p["labels"]
    return (f'<figure class="proof-card proof-wide" id="bath-{key}"><div class="proof-pair" role="group" aria-label="{html.escape(p["title"])}: {l1.lower()} and {l2.lower()}">'
            f'<div class="proof-half">{img(b[0], b[1], 1600, 1200)}<span class="proof-label" aria-hidden="true">{l1}</span></div>'
            f'<div class="proof-half">{img(a[0], a[1], 1600, 1200)}<span class="proof-label" aria-hidden="true">{l2}</span></div></div>'
            f'<figcaption><h3>{html.escape(p["title"])}</h3><p>{html.escape(p["caption"])}</p></figcaption></figure>')

def single_card(key):
    f, alt = SINGLES[key]
    return f'<figure class="proof-card">{img(f, alt, 1200, 1600)}<figcaption>{html.escape(alt)}</figcaption></figure>'

def review_card(r):
    if r["avatar"]:
        av = f'<div class="rv-avatar"><img src="{REV_IMG}{r["avatar"]}" width="40" height="40" alt="" loading="lazy"></div>'
    else:
        av = f'<div class="rv-avatar" aria-hidden="true">{r["initial"]}</div>'
    photos = ""
    if r["photos"]:
        photos = '<div class="rv-photos">' + "".join(
            f'<a href="{REV_IMG}{f}.webp" target="_blank" rel="noopener"><img src="{REV_IMG}{f}-600.webp" alt="{html.escape(alt)}" loading="lazy" decoding="async" width="600" height="800"></a>'
            for f, alt in r["photos"]) + '</div>'
    return (f'<article class="rv-card"><div class="rv-head">{av}<div><p class="rv-name">{html.escape(r["name"])}</p><p class="rv-meta">{r["meta"]}</p></div></div>'
            f'<div class="rv-stars" aria-label="5 stars">★★★★★</div><p class="rv-text">{r["text"]}</p>{photos}'
            f'<a class="rv-link" href="{r["url"]}" target="_blank" rel="noopener">Read on Google</a></article>')

def section(pairs, singles, more_link=True, h2="Recent bathroom work from our crew"):
    actions = '<a class="proof-button" href="#estimate">Plan your bathroom</a>'
    if more_link:
        actions += '<a class="proof-button secondary" href="/services/bathroom-remodel.html#bathroom-work">See more bathroom projects</a>'
    return (f'{START}\n<section id="bathroom-work" class="project-proof" aria-labelledby="bathroom-work-title"><div class="proof-wrap">'
            f'<h2 id="bathroom-work-title">{html.escape(h2)}</h2>'
            f'<p class="proof-intro">Our own jobs, shot on the crew\'s phones. Each two photo card is the same spot when we started and when we finished, or two stages of the same build. The single photos are finished showers and tubs from other homes we worked in.</p>'
            f'<div class="proof-grid">{"".join(pair_card(k) for k in pairs)}</div>'
            f'<div class="proof-grid proof-singles">{"".join(single_card(k) for k in singles)}</div>'
            f'<h3 class="proof-sub">Posted on Google by bathroom homeowners, word for word</h3>'
            f'<div class="proof-grid proof-reviews">{"".join(review_card(r) for r in REVIEWS)}</div>'
            f'<div class="proof-actions">{actions}</div></div></section>\n{END}')

def inject(path, block, anchor_re):
    t = path.read_text()
    t = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", t, flags=re.S)
    if "project-proof.css" not in t:
        t = t.replace('<link rel="stylesheet" href="/assets/css/site.min.css', CSS_LINK + '\n    <link rel="stylesheet" href="/assets/css/site.min.css', 1)
    m = re.search(anchor_re, t)
    assert m, f"anchor missing in {path}"
    t = t[:m.start()] + block + "\n" + t[m.start():]
    path.write_text(t)

for i, p in enumerate(CITY_PAGES):
    pairs, singles = SETS[i % len(SETS)]
    if p.stem == "plano":  # Plano's own project card already shows the dark tile room
        pairs, singles = ["shower-floor", "tub-wall-tile"], ["glass-band", "gray-hex", "tub-surround"]
    inject(p, section(pairs, singles), r'[ \t]*<section id="reviews"')
inject(SERVICE, section(["shower-tub", "tub-wall", "shower-floor", "tub-wall-tile"], ["glass-band", "tub-deck", "gray-hex", "tub-surround", "dark-glass", "niche"], more_link=False, h2="More bathroom work from our crew"), r'[ \t]*<section id="customer-stories"')
# home page: after the Plano before/after section, before the customer stories
inject(INDEX, section(["shower-floor"], ["glass-band", "gray-hex", "tub-surround"]), r'[ \t]*<section id="customer-stories"')
print("injected", len(CITY_PAGES) + 2, "pages")
