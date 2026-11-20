#!/usr/bin/env python3
"""Inject the shared bathroom section into the bathroom pages.

Thu 11/13: bathroom photos on our pages are the homeowners' own review photos
from the Allen Google listing, shown as review cards (offer page design) with
the photos large. Photos live in images/reviews/ (already sized, no optimizer
pass needed). Any bathroom photo can go on any city page.
Markers <!-- bath-work:start --> ... <!-- bath-work:end --> make it idempotent.
"""
import pathlib, re, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
START, END = "<!-- bath-work:start -->", "<!-- bath-work:end -->"

GOOGLE_LISTING = "https://www.google.com/maps?cid=12396670433062033498"
COLONY_LISTING = "https://www.google.com/maps/place/?q=place_id:ChIJL1TLkO8lvi8RPjwtQBlCM3s"   # OnPoint Pros Remodeling, The Colony
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
     "photos": [("anshu-bhattarai-review-shower-20261113", "Anshu's review photo: large stone look tile shower with a built in niche, rain head and sliding glass door")]},
    {"name": "Evan K", "initial": "E", "avatar": None,
     "meta": "Allen, TX · bathroom remodel · November 2026",
     "url": GOOGLE_LISTING,
     "text": "We had OnPoint Pros do our bathroom remodel and couldn’t be happier with the result. They <mark>helped us pick the design and materials, kept us informed the whole time</mark>, and were careful with our house. <mark>The shower came out beautiful.</mark> The tile, the hex floor, the glass doors and the shiplap all look great together. Would definitely recommend them!",
     "photos": [("evan-k-review-shower-20261110", "Evan K's review photo: walk-in shower with frameless glass, beige tile and black fixtures"),
                ("evan-k-review-shower-detail-20261110", "Evan K's review photo: shower tile with corner shelf and gray hex floor"),
                ("evan-k-review-glass-door-20261110", "Evan K's review photo: frameless glass door on the new shower")]},
]
# Home page only (Thu 2026-11-19: "replace two of the weaker ones with biggest drywall jobs or bundle jobs you find
# on our page or the colony listing", then "use E and Loomer"). Word for word from Google: Erin Knight on the Allen
# listing (the largest whole-house job with a review) and Ian Loomer on the Colony listing (the largest drywall job
# there with a review, and it has photos). Erin's second photo shows painted kitchen cabinets; Thu allowed this one
# photo the same evening ("You can use [her] second photo"). The no-kitchen rule still stands everywhere else.
HOME_EXTRA = [
    {"name": "Erin Knight", "initial": "E", "avatar": None,
     "meta": "Richardson, TX · whole-house floors, paint and wall repair · October 2026",
     "url": GOOGLE_LISTING,
     "text": "I can’t recommend On Point Pros enough. Dillon was amazing to work with. His communication and dedication to the project is unmatched. On Point Pros <mark>painted our interior, did flooring throughout the house, repaired cracks in the walls, and updated lighting</mark>. His team was very respectful and made sure the job was done well. They did a fantastic job and I will definitely use them again.",
     "photos": [("erin-knight-review-floor-20261018", "Erin's review photo: a room with new plank flooring, fresh wall paint and new baseboards"),
                ("erin-knight-review-cabinets-20261018", "Erin's review photo: cabinets painted a light color with new gold hardware")]},
    {"name": "Ian Loomer", "initial": "I", "avatar": None,
     "meta": "Frisco, TX · skim coat of a stairwell and the whole upstairs · November 2026",
     "url": COLONY_LISTING,
     "text": "Dillon and his team at On Point Pros were great to work with. Im Frisco based and he was able to swing by quickly to get a good estimate. I had a large stairwell I was looking to have skim coated to remove the knockdown texture. Dillon was able to quote such a good deal and meet timelines in an expedited way <mark>I ended up having his team do my whole upstairs</mark>. <mark>The team even wrapped it up a day ahead of schedule.</mark> All throughout I was in consistent communication and had good Project manager over site from On Point Pros.",
     "photos": [("ian-loomer-review-stairwell-20261118", "Ian's review photo: tall stairwell with smooth skim coated walls and ceiling"),
                ("ian-loomer-review-upstairs-20261118", "Ian's review photo: upstairs landing with smooth walls after the skim coat")]},
]
REV_IMG = "/images/reviews/"
SETS = [
    (["shower-tub", "shower-floor"], ["glass-band", "gray-hex", "tub-surround"]),
    (["tub-wall", "tub-wall-tile"], ["tub-deck", "gray-hex", "niche"]),
    (["shower-floor", "vanity-side"], ["glass-band", "tub-surround", "niche"]),
    (["tub-wall-tile", "shower-tub"], ["tub-deck", "gray-hex", "tub-surround"]),
    (["tub-wall", "shower-floor"], ["glass-band", "niche", "tub-surround"]),
]
# city pages only: a page without the reviews section (the cost estimator, added Nov 17) is not touched
CITY_PAGES = sorted(p for p in (ROOT / "bathroom").glob("*.html") if '<section id="reviews"' in p.read_text())
SERVICE = ROOT / "services/bathroom-remodel.html"
INDEX = ROOT / "index.html"
CSS_LINK = '<link rel="stylesheet" href="/assets/css/project-proof.css?v=20261113-bath-work4">'

def review_card(r):
    if r["avatar"]:
        av = f'<div class="rv-avatar"><img src="{REV_IMG}{r["avatar"]}" width="40" height="40" alt="" loading="lazy"></div>'
    else:
        av = f'<div class="rv-avatar" aria-hidden="true">{r["initial"]}</div>'
    photos = ""
    if r["photos"]:
        photos = f'<div class="rv-photos rv-photos-{len(r["photos"])}">' + "".join(
            f'<a href="{REV_IMG}{f}.webp" target="_blank" rel="noopener"><img src="{REV_IMG}{f}-600.webp" alt="{html.escape(alt)}" loading="lazy" decoding="async" width="600" height="800"></a>'
            for f, alt in r["photos"]) + '</div>'
    return (f'<article class="rv-card"><div class="rv-head">{av}<div><p class="rv-name">{html.escape(r["name"])}</p><p class="rv-meta">{r["meta"]}</p></div></div>'
            f'<div class="rv-stars" aria-label="5 stars">★★★★★</div><p class="rv-text">{r["text"]}</p>{photos}'
            f'<a class="rv-link" href="{r["url"]}" target="_blank" rel="noopener">Read on Google</a></article>')

BATH_INTRO = "Finished bathrooms photographed by the homeowners themselves and posted with their Google reviews. Their words are word for word."

def section(keys=None, h2="Bathrooms our customers posted on Google", more_link=True, cards=None, intro=BATH_INTRO, button="Plan your bathroom"):
    cards = cards if cards is not None else [r for r in REVIEWS if keys is None or r["name"] in keys]
    actions = f'<a class="proof-button" href="#estimate">{button}</a>'
    if more_link:
        actions += '<a class="proof-button secondary" href="/services/bathroom-remodel.html#bathroom-work">See more bathroom reviews</a>'
    return (f'{START}\n<section id="bathroom-work" class="project-proof" aria-labelledby="bathroom-work-title"><div class="proof-wrap">'
            f'<h2 id="bathroom-work-title">{html.escape(h2)}</h2>'
            f'<p class="proof-intro">{intro}</p>'
            f'<div class="proof-grid proof-reviews">{"".join(review_card(r) for r in cards)}</div>'
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

for p in CITY_PAGES:
    inject(p, section(), r'[ \t]*<section id="reviews"')
inject(SERVICE, section(more_link=False), r'[ \t]*<section id="customer-stories"')
# home page: the largest whole-house job and the largest drywall job with a review, then two bathroom reviews
# (the repeat customer, and the one that had a bathroom and drywall done together)
_by = {r["name"]: r for r in REVIEWS}
inject(INDEX, section(cards=[HOME_EXTRA[0], HOME_EXTRA[1], _by["Varun"], _by["Mohan Yechuri"]],
                      h2="What our customers posted on Google",
                      intro="Reviews from homeowners on our Google listings, word for word, with the photos they posted.",
                      button="Get a free estimate"),
       r'[ \t]*<section id="customer-stories"')
print("injected", len(CITY_PAGES) + 2, "pages")
