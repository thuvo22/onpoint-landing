#!/usr/bin/env python3
"""Build the-colony/ folder: the OnPoint Pros Remodeling drywall office site.

    python3 tools/build_colony.py

The Colony business (OnPoint Pros Remodeling, 5752 Grandscape Blvd Ste 225,
The Colony TX 75056, (469) 933-0888) is a second Google Business Profile with
Dry wall contractor as its primary category. Google links each listing to a
page, and that page should carry the listing's own name, address and phone.
The Patch Boys run every franchise this way: one domain, one folder per
office. This folder is that page set. Edit the content below and rerun; the
HTML files in the-colony/ are generated and committed.

Rules baked in: no em dashes, no "handyman", "fully insured" never
"licensed", no superlatives, Dillon's plain voice, no review count printed
(tools/update_review_count.py rewrites "<n> Google reviews" phrases with the
Allen count, so the Colony pages say "5.0 on Google" and nothing more).
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "the-colony"
BASE = "https://onpointprostx.com/the-colony/"

BIZ = {
    "name": "OnPoint Pros Remodeling",
    "street": "5752 Grandscape Blvd Ste 225",
    "city": "The Colony",
    "state": "TX",
    "zip": "75056",
    "phone": "(469) 933-0888",
    "tel": "tel:+14699330888",
    "e164": "+1-469-933-0888",
    "hours": "7 days a week, 6 AM to 8 PM",
    "maps": "https://www.google.com/maps/place/?q=place_id:ChIJL1TLkO8lvi8RPjwtQBlCM3s",
    "lat": 33.0743314,
    "lng": -96.8611537,
}
NAP = f'{BIZ["street"]}, {BIZ["city"]}, {BIZ["state"]} {BIZ["zip"]}'
BIZ_ID = BASE + "#business"
HERO = "/images/colony/hero-garage-drywall.jpg"

REVIEWS = [
    # (image, reviewer, alt text). Real screenshots of the Google reviews on the
    # OnPoint Pros Remodeling listing, cropped to the review itself. Re-shoot if a
    # reviewer edits or removes a review. Anita's review is left out because it
    # says "handyman", a word we never put on the site.
    ("/images/colony/review-travis.jpg", "Travis Winter", "Five star Google review from Travis Winter: OnPoint Pros replaced the drywall in a Lewisville garage, with clear communication and a crew respectful of the home"),
    ("/images/colony/review-anish.jpg", "Anish Bhattarai", "Five star Google review from Anish Bhattarai: a major garage ceiling drywall repair and refinish in Lewisville, with shelves, belongings and floor covered before the work"),
    ("/images/colony/review-jiya.jpg", "Jiya Patel", "Five star Google review from Jiya Patel: a leak damaged staircase ceiling in Lewisville patched and texture matched with no obvious patch"),
]

PHOTOS = [
    ("/images/jobs/ba-07-door-hole.jpg", "Before and after: a doorknob hole patched and textured so it disappears", 1600, 656),
    ("/images/jobs/ba-05-attic-ceiling.jpg", "Before and after: an open ceiling cut closed with new drywall and matched texture", 1600, 656),
    ("/images/jobs/ba-02-shower-ceiling.jpg", "Before and after: bathroom ceiling drywall repaired and retextured", 1600, 656),
    ("/images/jobs/ba-09-ceiling-vent.jpg", "Before and after: ceiling drywall repaired around a vent", 1600, 656),
    ("/images/jobs/ba-10-corner-patch.jpg", "Before and after: a corner patch blended into the wall texture", 1600, 656),
    ("/images/jobs/ba-18-popcorn.jpg", "Before and after: popcorn ceiling removed and refinished smooth", 1600, 656),
]

def _p(cat, n, alt, w=1200, h=900):
    return (f"/images/colony/{cat}-{n:02d}.jpg", alt, w, h)

def _pair(title, before, after, caption, labels=("BEFORE", "AFTER")):
    return dict(title=title, before=before, after=after, caption=caption, labels=labels)

PAIR_ATTIC = _pair("Ceiling hole next to the attic panel",
    _p("repair", 3, "Ceiling drywall torn open next to the attic access panel"),
    _p("repair", 4, "The same ceiling patched, textured and painted around the panel"),
    "Torn ceiling drywall beside the attic access, then the same spot patched, textured and painted so the panel sits in a clean ceiling again.")
PAIR_WINDOW = _pair("Wall under a window, rebuilt",
    _p("repair", 5, "The wall under a window opened back to the insulation"),
    _p("repair", 6, "The same wall patched, textured and painted with the baseboard back on"),
    "The wall below the window was cut back to the insulation, then new drywall, texture, paint and the baseboard reinstalled.")
PAIR_WET_CEILING = _pair("Water damaged ceiling corner",
    _p("ceiling", 2, "A water damaged ceiling corner cut open to dry the framing"),
    _p("ceiling", 3, "The same ceiling corner replaced, textured and painted"),
    "The wet drywall came out so the framing could dry, then the corner was closed with new board, textured and painted.")
PAIR_GARAGE = _pair("Garage drywall, studs to finished board",
    _p("install", 5, "The garage stripped to the studs with the floor protected"),
    _p("install", 7, "The garage hung and taped, ready for texture and paint"),
    "The garage stripped to the studs with the floor covered, then every wall and the ceiling hung and taped.")

PAIR_VENT = _pair("Ceiling torn open beside a vent",
    _p("ceiling", 1, "Ceiling drywall torn open beside an air vent after a leak"),
    _p("ceiling", 11, "The same ceiling replaced, textured and painted, lights and vent back in"),
    "The ceiling came apart beside the vent after a leak. New drywall, matched texture and paint, with the recessed lights and vent reset.")
PAIR_BEDROOM = _pair("Bedroom ceiling opened to the joists",
    _p("ceiling", 4, "A bedroom ceiling cut open to the joists so the wet drywall can come out"),
    _p("ceiling", 12, "The same bedroom ceiling closed, textured and painted"),
    "The wet section cut out to the joists so the framing could dry, then new board, texture and paint across the whole ceiling.")
PAIR_LIGHT = _pair("Ceiling hole next to a recessed light",
    _p("ceiling", 13, "Ceiling drywall torn open next to a recessed light and vent"),
    _p("texture", 3, "The same ceiling finished in light orange peel around the recessed light"),
    "A torn hole beside the recessed light, then the patch textured in light orange peel so it disappears into the ceiling.")
PAIR_ENTRY = _pair("Two story entry, new drywall to finished",
    _p("repair", 7, "Our crew finishing new drywall in a two story entry, floors covered in plastic"),
    _p("repair", 9, "The same entry finished, painted and cleaned up"),
    "Our crew on ladders finishing the new board in the entry, then the same entry painted with the floors uncovered.", ("IN PROGRESS", "AFTER"))
PAIR_CONVERSION = _pair("Garage conversion, drywall to finished room",
    _p("install", 3, "New drywall hung and mudded around a built in cabinet in a garage conversion"),
    _p("install", 10, "The same garage conversion finished, with the kitchenette and new floor in place"),
    "The conversion with the drywall hung and mudded around the cabinet run, then the finished room with the kitchenette, paint and flooring in.", ("DRYWALL", "FINISHED"))

PAIR_POPCORN = _pair("Popcorn ceiling removed",
    _p("texture", 1, "A popcorn ceiling with dated crown molding in an empty room"),
    _p("texture", 2, "The same room with the popcorn scraped off and the ceiling ready for texture"),
    "The popcorn ceiling and dark crown molding, then the same room from the window side with the popcorn scraped off, the molding out and the ceiling ready for its new finish.")

PAIR_SHOWER = _pair("Shower ceiling after a leak",
    _p("ceiling", 16, "A tile shower ceiling torn open to the framing after a leak from above"),
    _p("ceiling", 17, "The same shower ceiling closed, textured and painted"),
    "The shower ceiling opened up to dry out after a leak, then new moisture resistant board, texture and paint over the tile.")
PAIR_GARAGE_WALL = _pair("Garage wall opened to the insulation",
    _p("repair", 10, "A garage wall cut back to the insulation behind the fridge"),
    _p("repair", 11, "The same garage wall closed, textured and painted"),
    "The damaged section cut out to the studs and insulation, then new board, texture and paint with the fridge back in place.")
PAIR_LAUNDRY = _pair("Laundry room wall split open",
    _p("repair", 12, "A laundry room wall split along the seam from floor to cabinet"),
    _p("repair", 13, "The same laundry wall rebuilt, textured and painted"),
    "A seam that opened from the baseboard to the cabinets, cut back, retaped and finished so the crack does not come back.")
PAIR_SINK = _pair("Wall opened behind a pedestal sink",
    _p("repair", 14, "The wall cut open behind a pedestal sink for a plumbing repair"),
    _p("repair", 15, "The same wall closed and textured to match"),
    "The plumber's access cut behind the sink, then new drywall and matched texture so the wall reads as one piece.")
PAIR_HALLWAY = _pair("Hallway ceiling collapse",
    _p("ceiling", 14, "A hallway ceiling sagging and torn open after a leak", 900, 1200),
    _p("ceiling", 15, "The same hallway ceiling rebuilt with a framed access panel", 900, 1200),
    "The ceiling came down after a leak above. We replaced the drywall, framed a clean access panel and textured and painted the hallway.")

S_CREW_ENTRY = _p("repair", 7, "Our crew finishing new drywall in a two story entry, floors covered in plastic")
S_CEIL_VENT = _p("ceiling", 1, "Ceiling drywall torn open beside an air vent after a leak, before we started")
S_CEIL_JOISTS = _p("ceiling", 4, "A bedroom ceiling cut open to the joists so the wet drywall can come out")
S_SCAFFOLD = _p("ceiling", 5, "Scaffold and plastic over the stairs for a two story living room ceiling repair")
S_STAIN = _p("ceiling", 7, "A water stain spreading across a textured ceiling, the first sign of a leak above")
S_KITCHEN_CEIL = _p("ceiling", 9, "A kitchen ceiling after the patch, retexture and paint")
S_HALL_PATCH = _p("ceiling", 10, "A hallway ceiling patch cut square and ready for new drywall")
S_POPCORN_1 = _p("texture", 1, "A popcorn ceiling in an empty room, ready for removal")
S_POPCORN_2 = _p("texture", 2, "The same room from the window side, popcorn ceiling and old border")
S_ORANGE_PEEL = _p("texture", 3, "A finished ceiling in light orange peel around a recessed light")
S_SPRAY_1 = _p("texture", 4, "Our crew spraying new ceiling texture with the room sealed in plastic")
S_SPRAY_2 = _p("texture", 5, "Spraying texture across a garage ceiling from the ladder")
S_HOPPER = _p("texture", 6, "The texture hopper gun at work, everything below covered")
S_MASKED = _p("texture", 7, "A living room masked in plastic before the ceiling is retextured")
S_LIVING_CEIL = _p("texture", 9, "A retextured living room ceiling blended into the crown molding")
S_CONV_HANG = _p("install", 1, "New drywall going up next to open insulated studs in a garage conversion")
S_CONV_TAPED = _p("install", 2, "A garage conversion hung and taped, waiting on texture")
S_CABINET = _p("install", 3, "New drywall hung and mudded around a built in cabinet")
S_GARAGE_BEFORE = _p("install", 4, "A garage cleared out ahead of new drywall on every wall and the ceiling")
S_GARAGE_CREW = _p("install", 6, "Our crew hanging the new garage drywall")
S_CLOSET = _p("install", 8, "New drywall hung in a closet during a bath remodel")
S_SMOOTH = _p("install", 9, "A small room finished smooth and primed")

REPAIR_PHOTOS = dict(pairs=[PAIR_GARAGE_WALL, PAIR_LAUNDRY, PAIR_WINDOW, PAIR_ATTIC, PAIR_SINK, PAIR_ENTRY], singles=[S_SCAFFOLD, S_STAIN, S_KITCHEN_CEIL])
CEILING_PHOTOS = dict(pairs=[PAIR_VENT, PAIR_HALLWAY, PAIR_WET_CEILING, PAIR_BEDROOM, PAIR_SHOWER, PAIR_LIGHT, PAIR_ATTIC], singles=[S_STAIN, S_SCAFFOLD, S_KITCHEN_CEIL])
TEXTURE_PHOTOS = dict(pairs=[PAIR_POPCORN, PAIR_LIGHT, PAIR_SINK], singles=[S_MASKED, S_SPRAY_1, S_HOPPER, S_LIVING_CEIL, S_SMOOTH, S_KITCHEN_CEIL])
INSTALL_PHOTOS = dict(pairs=[PAIR_GARAGE, PAIR_CONVERSION, PAIR_GARAGE_WALL], singles=[S_GARAGE_BEFORE, S_GARAGE_CREW, S_CONV_HANG, S_CONV_TAPED, S_CLOSET, S_SMOOTH])
MIX_PHOTOS = dict(pairs=[PAIR_VENT, PAIR_GARAGE_WALL, PAIR_CONVERSION], singles=[S_SPRAY_1, S_GARAGE_CREW, S_SCAFFOLD])
CITY_PHOTOS = {
    "lewisville": dict(pairs=[PAIR_GARAGE, PAIR_VENT, PAIR_LAUNDRY], singles=[S_GARAGE_CREW, S_SPRAY_1, S_SCAFFOLD]),
    "little-elm": dict(pairs=[PAIR_ATTIC, PAIR_BEDROOM, PAIR_GARAGE_WALL], singles=[S_CONV_TAPED, S_MASKED, S_SCAFFOLD]),
    "frisco": dict(pairs=[PAIR_WET_CEILING, PAIR_ENTRY, PAIR_SHOWER], singles=[S_MASKED, S_CONV_HANG, S_KITCHEN_CEIL]),
    "plano": dict(pairs=[PAIR_WINDOW, PAIR_POPCORN, PAIR_HALLWAY], singles=[S_SPRAY_1, S_GARAGE_CREW, S_MASKED]),
}

SERVICES = [
    ("drywall-repair.html", "Drywall Repair", "Holes, cracks, nail pops and damage left by plumbers or electricians, patched and textured so you cannot find them."),
    ("ceiling-water-damage-repair.html", "Ceilings and Water Damage", "Wet, sagging or stained ceilings cut out, replaced, retextured and painted after the leak is fixed."),
    ("texture-matching-popcorn-removal.html", "Texture and Popcorn Removal", "Knockdown, orange peel and smooth finishes matched on a sample first. Popcorn scraped and refinished."),
    ("drywall-installation.html", "New Drywall", "Garages, additions, closets and whole rooms hung, taped, finished and ready for paint."),
]

CITIES = [
    ("the-colony", "The Colony", "index.html", ['Austin Ranch', 'The Tribute', 'Stewart Peninsula', 'Legend Crest', 'Ridgepointe', 'Eastvale', 'Stewart Creek Estates', 'Memorial', 'Riviera', 'Homestead']),
    ("lewisville", "Lewisville", "lewisville.html", ['Castle Hills', 'Coronado', 'Garden Ridge', 'Valley Ridge', 'Timbercreek', 'Vista Ridge', 'Old Town Lewisville', 'Lakepointe', 'Indian Creek', 'College Street District']),
    ("little-elm", "Little Elm", "little-elm.html", ['Union Park', 'Sunset Pointe', 'Hillstone Pointe', 'Lakewood', 'Villages of Woodlake', 'Wynfield Farms', 'Frisco Lakes', 'Hidden Cove', 'Oak Point Estates', 'The Enclave']),
    ("frisco", "Frisco", "frisco.html", ['Stonebriar', 'Starwood', 'Phillips Creek Ranch', 'Newman Village', 'The Trails', 'Stonebrook', 'Plantation Resort', 'Panther Creek', 'Frisco Lakes', 'Heritage Lakes']),
    ("plano", "Plano", "plano.html", ['Willow Bend', 'Deerfield', 'Kings Ridge', 'Hunters Glen', 'Los Rios', 'Prestonwood', 'Russell Creek', 'Legacy West', 'Preston Meadow', 'Kingswood']),
]
CITY_NAMES = [c[1] for c in CITIES]
AREA_SENTENCE = "The Colony, Lewisville, Little Elm, Frisco and Plano"

NAV = [
    ("drywall-repair.html", "Drywall Repair"),
    ("ceiling-water-damage-repair.html", "Ceilings"),
    ("texture-matching-popcorn-removal.html", "Texture"),
    ("drywall-installation.html", "New Drywall"),
    ("index.html#areas", "Areas"),
    ("contact.html", "Contact"),
]


def esc(s):
    return html.escape(s, quote=True)


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def business_entity(full=False):
    ent = {"@type": "HomeAndConstructionBusiness", "@id": BIZ_ID, "name": BIZ["name"], "telephone": BIZ["e164"], "url": BASE}
    if full:
        ent.update({
            "image": "https://onpointprostx.com" + HERO,
            "address": {"@type": "PostalAddress", "streetAddress": BIZ["street"], "addressLocality": BIZ["city"], "addressRegion": BIZ["state"], "postalCode": BIZ["zip"], "addressCountry": "US"},
            "geo": {"@type": "GeoCoordinates", "latitude": BIZ["lat"], "longitude": BIZ["lng"]},
            "hasMap": BIZ["maps"],
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "06:00", "closes": "20:00"}],
            "areaServed": [{"@type": "City", "name": c} for c in CITY_NAMES],
            "parentOrganization": {"@type": "HomeAndConstructionBusiness", "name": "OnPoint Pros", "@id": "https://onpointprostx.com/#business", "url": "https://onpointprostx.com/"},
            "knowsAbout": ["Drywall repair", "Drywall installation", "Ceiling repair", "Water damage drywall repair", "Texture matching", "Popcorn ceiling removal"],
            "founder": {"@type": "Person", "name": "Dillon Hubbard"},
        })
    return ent


def head(title, desc, path, extra_ld):
    url = BASE + ("" if path == "index.html" else path)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{esc(desc)}">
    <title>{esc(title)}</title>
    <link rel="icon" type="image/webp" href="/images/logo.webp">
    <link rel="canonical" href="{url}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:image" content="https://onpointprostx.com{HERO}">
    <meta property="og:url" content="{url}">
    <meta property="og:type" content="website">
    <link rel="preload" href="/assets/fonts/montserrat-latin-variable.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="/assets/css/site.min.css?v={css_version()}">
    <style>body{{font-family:'Montserrat',sans-serif;}}</style>
    {chr(10).join('    ' + x for x in extra_ld)}
</head>
<body class="bg-slate-50 text-slate-800 antialiased" data-phone="{BIZ['phone']}" data-tel="{BIZ['tel']}">
"""


def header(active):
    links = "".join(f'<a href="/the-colony/{h}" class="hover:text-red-600{" text-red-600" if h == active else ""}">{t}</a>' for h, t in NAV)
    return f"""
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-20">
            <a href="/the-colony/" class="flex items-center gap-3"><img src="/images/logo.webp" alt="{BIZ['name']}" class="h-14 w-auto" width="93" height="102"><span class="hidden sm:block leading-tight"><span class="block font-extrabold text-slate-900">OnPoint Pros Remodeling</span><span class="block text-xs text-slate-500">Drywall office, The Colony TX</span></span></a>
            <nav class="hidden lg:flex items-center gap-6 text-slate-700 font-medium">{links}</nav>
            <div class="flex items-center gap-3"><a href="{BIZ['tel']}" class="inline-flex items-center px-5 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg shadow-lg">{BIZ['phone']}</a></div>
        </div>
    </header>
"""


def crumbs(items):
    """items: list of (label, href or None). Returns nav html + BreadcrumbList json-ld."""
    parts = []
    ld = []
    for i, (label, href) in enumerate(items, 1):
        if href:
            parts.append(f'<a href="{href}" class="hover:text-red-600">{esc(label)}</a>')
            ld.append({"@type": "ListItem", "position": i, "name": label, "item": ("https://onpointprostx.com" + href) if href.startswith("/") else href})
        else:
            parts.append(f'<span class="text-slate-700">{esc(label)}</span>')
            ld.append({"@type": "ListItem", "position": i, "name": label})
    nav = f"""
    <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-sm text-slate-500">{' / '.join(parts)}</nav>
"""
    return nav, jsonld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld})


def hero(kicker, h1, lead, cta):
    return f"""
    <section class="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div class="absolute inset-0 opacity-30"><img src="{HERO}" alt="OnPoint Pros Remodeling crew finishing garage drywall" class="w-full h-full object-cover" width="1600" height="900"></div>
        <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
            <p class="text-amber-300 font-semibold uppercase tracking-wider mb-3 text-sm">{esc(kicker)}</p>
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold mb-6 max-w-3xl leading-tight">{esc(h1)}</h1>
            <p class="text-xl text-slate-200 max-w-3xl mb-8">{lead}</p>
            <div class="flex flex-col sm:flex-row gap-4">
                <a href="#estimate" class="inline-flex justify-center px-8 py-4 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 shadow-xl">{esc(cta)}</a>
                <a href="{BIZ['tel']}" class="inline-flex justify-center px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-lg border border-slate-700">Call {BIZ['phone']}</a>
            </div>
        </div>
    </section>
"""


def quick_answer(text):
    return f"""
    <section class="py-8 bg-amber-50 border-b border-amber-200">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <p class="text-lg text-slate-800 leading-relaxed">{text}</p>
        </div>
    </section>
"""


def prose(h2, paragraphs):
    ps = "".join(f'<p class="text-lg text-slate-600 leading-relaxed mb-5">{p}</p>' for p in paragraphs)
    return f"""
    <section class="py-16">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-5">{h2}</h2>
            {ps}
        </div>
    </section>
"""


def cards(h2, items, link=True):
    out = []
    for h, t, d in items:
        title = f'<a href="/the-colony/{h}" class="hover:text-red-600">{esc(t)}</a>' if link else esc(t)
        out.append(f'<div class="bg-slate-50 rounded-2xl p-6 border border-slate-200"><h3 class="font-bold text-lg text-slate-900 mb-2">{title}</h3><p class="text-slate-600">{esc(d)}</p></div>')
    return f"""
    <section class="py-16 bg-white border-y border-slate-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-12 text-center">{esc(h2)}</h2>
            <div class="grid md:grid-cols-2 lg:grid-cols-{min(3, len(items))} gap-6">{''.join(out)}</div>
        </div>
    </section>
"""


def _img(src, alt, w, h, extra=""):
    return f'<img src="{src}" alt="{esc(alt)}" loading="lazy" class="w-full h-auto{extra}" width="{w}" height="{h}">'

def photos(h2, picks):
    pairs, singles = picks.get("pairs", []), picks.get("singles", [])
    out = []
    for pr in pairs:
        b, a = pr["before"], pr["after"]
        lb, la = pr.get("labels", ("BEFORE", "AFTER"))
        out.append(f'<figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden mb-6"><div class="grid grid-cols-2 gap-1 bg-slate-200">'
                   f'<div class="relative">{_img(*b)}<span class="absolute top-0 left-0 bg-slate-900 text-amber-300 text-xs sm:text-base font-bold tracking-wide px-2 py-1">{lb}</span></div>'
                   f'<div class="relative">{_img(*a)}<span class="absolute top-0 left-0 bg-slate-900 text-amber-300 text-xs sm:text-base font-bold tracking-wide px-2 py-1">{la}</span></div></div>'
                   f'<figcaption class="p-4"><h3 class="font-bold text-slate-900">{esc(pr["title"])}</h3><p class="text-sm text-slate-600 mt-1">{esc(pr["caption"])}</p></figcaption></figure>')
    pair_html = "".join(out)
    single_html = ""
    if singles:
        figs = "".join(f'<figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden">{_img(src, alt, w, h)}<figcaption class="p-4 text-sm text-slate-600">{esc(alt)}</figcaption></figure>' for src, alt, w, h in singles)
        sub = '<h3 class="text-xl font-bold text-slate-900 mt-10 mb-5 text-center">On the Job</h3>' if pairs else ""
        single_html = f'{sub}<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">{figs}</div>'
    intro = "Each two photo card is the same spot, shot by our crew at the start and once we were done." if pairs else "Our own jobs, photographed by our crew."
    return f"""
    <section class="py-16 bg-slate-100">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-3 text-center">{esc(h2)}</h2>
            <p class="text-center text-slate-500 mb-10">{intro}</p>
            {pair_html}{single_html}
        </div>
    </section>
"""


def reviews(h2):
    cards_html = "".join(
        f'<a href="{BIZ["maps"]}" target="_blank" rel="noopener" class="block"><img src="{src}" alt="{esc(alt)}" width="1076" height="435" loading="lazy" decoding="async" class="w-full h-auto rounded-xl shadow-md"></a>'
        for src, name, alt in REVIEWS)
    return f"""
    <section id="reviews" class="py-16 bg-white">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-3 text-center">{esc(h2)}</h2>
            <p class="text-center text-slate-500 mb-10">Rated <span class="font-bold text-slate-900">5.0</span> on Google. <a href="{BIZ['maps']}" target="_blank" rel="noopener" class="underline underline-offset-2 decoration-amber-400 decoration-2 hover:text-red-600">Read the reviews on our Google listing</a>.</p>
            <div class="grid gap-6 max-w-3xl mx-auto">{cards_html}</div>
        </div>
    </section>
"""


def neighborhoods(city, names):
    cells = "".join(f'<div class="bg-slate-50 border border-slate-200 rounded-lg py-3">{esc(n)}</div>' for n in names)
    return f"""
    <section class="py-16 bg-white border-t border-slate-200">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-5 text-center">{esc(city)} Neighborhoods We Work In</h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 text-center text-slate-700 mt-10">{cells}</div>
        </div>
    </section>
"""


def faq(h2, qa):
    blocks = "".join(f'<div class="bg-white rounded-xl border border-slate-200 p-6"><h3 class="font-bold text-slate-900">{esc(q)}</h3><p class="mt-4 text-slate-600">{esc(a)}</p></div>' for q, a in qa)
    ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    sec = f"""
    <section class="py-16 bg-slate-100">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-10 text-center">{esc(h2)}</h2>
            <div class="space-y-4">{blocks}</div>
        </div>
    </section>
"""
    return sec, ld


def areas(current=None):
    pills = "".join(f'<a href="/the-colony/{f}" class="px-5 py-3 {"bg-slate-900 text-white" if slug == current else "bg-slate-100 hover:bg-slate-900 hover:text-white"} rounded-full font-medium transition">{esc(name)}</a>' for slug, name, f, _ in CITIES)
    return f"""
    <section id="areas" class="py-12 bg-white border-y border-slate-200">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 class="text-2xl font-bold text-slate-900 mb-3">Where the Colony Office Works</h2>
            <p class="text-slate-600 mb-6">Our office is at Grandscape in The Colony. These are the cities we drive to every week.</p>
            <div class="flex flex-wrap justify-center gap-3">{pills}</div>
            <p class="mt-6 text-slate-500">Need drywall in Allen, McKinney or Prosper? That side of the family runs from our <a href="/services/drywall-repair.html" class="text-red-600 font-semibold underline">Allen office</a>.</p>
        </div>
    </section>
"""


def bathroom_handoff():
    return """
    <section class="py-16 bg-slate-900 text-white">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 class="text-3xl font-extrabold mb-4">Bathroom Remodels Run Through Our Allen Office</h2>
            <p class="text-lg text-slate-300 mb-6">OnPoint Pros Remodeling is the drywall side of OnPoint Pros. Full bathroom remodels start at $20,000 and are planned and built by the Allen office, the same owner and the same crew standards.</p>
            <a href="/services/bathroom-remodel.html" class="inline-flex px-6 py-3 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700">See OnPoint Pros Bathroom Remodeling &rarr;</a>
        </div>
    </section>
"""


def estimate(h2, lead):
    return f"""
    <section id="estimate" data-service="repairs" class="py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 class="text-3xl sm:text-4xl font-extrabold mb-6">{esc(h2)}</h2>
            <p class="text-lg text-slate-300 mb-8">{esc(lead)}</p>
            <a href="{BIZ['tel']}" class="px-8 py-4 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 shadow-xl">Call {BIZ['phone']}</a>
        </div>
    </section>
"""


def footer():
    return f"""
    <footer class="bg-slate-900 text-slate-400 py-10 text-center text-sm">
        <p class="text-white font-bold text-base">{BIZ['name']}</p>
        <p class="mt-1">{esc(NAP)}</p>
        <p class="mt-1"><a href="{BIZ['tel']}" class="hover:text-white">{BIZ['phone']}</a> &middot; Open {BIZ['hours']}</p>
        <p class="mt-2">Drywall contractor serving {AREA_SENTENCE} &middot; Fully insured &middot; Owner Dillon Hubbard</p>
        <p class="mt-3"><a href="/the-colony/" class="hover:text-white">Home</a> &middot; <a href="/the-colony/drywall-repair.html" class="hover:text-white">Drywall Repair</a> &middot; <a href="/the-colony/ceiling-water-damage-repair.html" class="hover:text-white">Ceilings</a> &middot; <a href="/the-colony/texture-matching-popcorn-removal.html" class="hover:text-white">Texture</a> &middot; <a href="/the-colony/drywall-installation.html" class="hover:text-white">New Drywall</a> &middot; <a href="/the-colony/contact.html" class="hover:text-white">Contact</a> &middot; <a href="{BIZ['maps']}" target="_blank" rel="noopener" class="hover:text-white">Google listing</a></p>
        <p class="mt-3">Part of <a href="/" class="underline hover:text-white">OnPoint Pros</a>, Allen TX, for bathroom remodeling and drywall in Collin County.</p>
        <p class="mt-4 text-sm"><a href="/privacy.html" class="underline hover:text-white">Privacy Policy</a> &middot; <a href="/terms.html" class="underline hover:text-white">Terms and Conditions</a> &middot; <a href="#" data-cookie-settings class="underline hover:text-white">Cookie Settings</a></p>
    </footer>
"""


MOBILE_MENU = """
<script>
(function(){
  var nav = document.querySelector('header nav.hidden.lg\\\\:flex');
  var header = document.querySelector('header');
  if (!nav || !header) return;
  var btn = document.createElement('button');
  btn.className = 'lg:hidden inline-flex items-center justify-center w-11 h-11 rounded-lg text-slate-700 hover:bg-slate-100 mr-1';
  btn.setAttribute('aria-label','Toggle menu');
  btn.innerHTML = '<svg id="mm-icon-open" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/></svg><svg id="mm-icon-close" class="w-7 h-7 hidden" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>';
  var ctaGroup = header.querySelector('div.flex.items-center.gap-3');
  if (ctaGroup) ctaGroup.insertBefore(btn, ctaGroup.firstChild);
  var panel = document.createElement('div');
  panel.className = 'lg:hidden hidden fixed inset-x-0 top-20 bg-white border-b border-slate-200 shadow-2xl z-40 max-h-[calc(100vh-5rem)] overflow-y-auto';
  var html = '<div class="max-w-7xl mx-auto px-4 py-6"><nav class="flex flex-col gap-1">';
  nav.querySelectorAll('a').forEach(function(a){
    html += '<a href="'+a.getAttribute('href')+'" class="block px-4 py-3 text-lg font-bold text-slate-800 hover:text-red-600 hover:bg-red-50 rounded-lg border-b border-slate-100">'+a.textContent.trim()+'</a>';
  });
  html += '</nav><a href="__TEL__" class="mt-5 inline-flex items-center justify-center w-full px-5 py-4 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg shadow-lg">Call __PHONE__</a><a href="#estimate" class="mt-3 inline-flex items-center justify-center w-full px-5 py-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-lg">Request a Drywall Quote</a></div>';
  panel.innerHTML = html;
  header.parentNode.insertBefore(panel, header.nextSibling);
  function toggle(){
    var open = panel.classList.toggle('hidden') === false;
    document.getElementById('mm-icon-open').classList.toggle('hidden', open);
    document.getElementById('mm-icon-close').classList.toggle('hidden', !open);
  }
  btn.addEventListener('click', toggle);
  panel.querySelectorAll('a').forEach(function(a){ a.addEventListener('click', function(){ if (!panel.classList.contains('hidden')) toggle(); }); });
})();
</script>
""".replace("__TEL__", BIZ["tel"]).replace("__PHONE__", BIZ["phone"])


def tail(scripts_v):
    return MOBILE_MENU + f"""
<script src="/phone-format.js" defer></script>
<script src="/cookie-consent.js?v={scripts_v['cookie']}" defer></script>
<script src="/site-measurement.js?v={scripts_v['measure']}" defer></script>
<script src="/estimate-form.js?v={scripts_v['estimate']}" defer></script>
</body>
</html>
"""


def service_ld(name, path, desc):
    return jsonld({"@context": "https://schema.org", "@type": "Service", "serviceType": name, "name": name + " in The Colony, TX", "url": BASE + path, "image": "https://onpointprostx.com" + HERO, "provider": business_entity(), "areaServed": [{"@type": "City", "name": c} for c in CITY_NAMES], "description": desc})


def page(path, title, desc, body, lds, scripts_v):
    html_out = head(title, desc, path, lds) + body + tail(scripts_v)
    (OUT / path).write_text(html_out, encoding="utf-8")
    return path


def build(scripts_v):
    OUT.mkdir(exist_ok=True)
    written = []

    # ---------------- home ----------------
    nav, bc = crumbs([("OnPoint Pros", "/"), ("The Colony Drywall Office", None)])
    f_sec, f_ld = faq("Questions The Colony Homeowners Ask Us", [
        ("How much does drywall repair cost in The Colony?", "Drywall projects at OnPoint Pros Remodeling start at $1,000. Put every repair area in one request, send photos, and we quote the whole job together before any work starts. Texture matching and paint are included in the price we give you."),
        ("Do you handle the ceiling after a roof or plumbing leak?", "Yes. Once the leak is fixed we cut out the wet drywall, replace it, match the texture and paint the ceiling. Send a photo of the stain or sag and we will tell you what it needs."),
        ("Can you match the texture so the patch does not show?", "Yes. Most homes in The Colony, Lewisville and Frisco are knockdown or orange peel. We spray a sample first and adjust until it matches, then blend it into the wall."),
        ("Where is your office?", f"{NAP}, at Grandscape. We drive to {AREA_SENTENCE}. Open {BIZ['hours']}."),
        ("Is this the same company as OnPoint Pros in Allen?", "Same owner, Dillon Hubbard. OnPoint Pros Remodeling is the drywall office for the west side of our area. Bathroom remodels run through the Allen office."),
    ])
    body = header(None) + nav + hero(
        "Drywall Contractor in The Colony, TX",
        "Drywall Repair and Installation in The Colony",
        f"OnPoint Pros Remodeling is the drywall office of OnPoint Pros, run by Dillon Hubbard from Grandscape in The Colony. We repair and install drywall, fix water damaged ceilings, match texture so the patch disappears, remove popcorn ceilings and paint the room when we are done. Rated 5.0 on Google.",
        "Get a Drywall Quote") + quick_answer(
        f"<strong>{BIZ['name']}, {esc(NAP)}, {BIZ['phone']}.</strong> Drywall projects start at $1,000. We serve {AREA_SENTENCE}, {BIZ['hours']}. Fully insured.") + prose(
        "What We Do, and How We Do It", [
            "Drywall is the whole job here, not a side service. Garages that were never finished, additions that need hanging and taping, ceilings that came down after a leak, holes left behind by a plumber or an electrician, popcorn ceilings that need to go. We handle all of it from the Colony office.",
            "A patch is easy. A patch you cannot find in afternoon light is the part most crews get wrong. We spray the texture on a sample board first, match it to your wall, then blend it in so the repair disappears. Then we prime and paint, so you are not left with a patch that still needs a painter.",
            "We show up when we say we will, protect your floors and furniture, give you one clear price before work starts and leave the house clean. That is the standard on every job, from a doorknob hole to a full garage.",
        ]) + cards("Drywall Services From the Colony Office", SERVICES) + photos("Recent Drywall Work", MIX_PHOTOS) + reviews("What Our Customers Say") + areas("the-colony") + neighborhoods("The Colony", CITIES[0][3]) + f_sec + bathroom_handoff() + estimate(
        "Get a Drywall Quote From the Colony Office", "Drywall projects start at $1,000. Send photos of every area and we will confirm the scope and price before work starts.") + footer()
    written.append(page("index.html",
        "Drywall Contractor The Colony TX | OnPoint Pros Remodeling",
        f"OnPoint Pros Remodeling, the drywall office of OnPoint Pros at Grandscape in The Colony. Drywall repair, water damaged ceilings, texture matching, popcorn removal and new drywall in {AREA_SENTENCE}. Call {BIZ['phone']}.",
        body, [jsonld({"@context": "https://schema.org", **business_entity(full=True)}), bc, f_ld], scripts_v))

    # ---------------- service pages ----------------
    svc_pages = {
        "drywall-repair.html": dict(
            title="Drywall Repair The Colony TX | OnPoint Pros Remodeling",
            desc=f"Drywall repair in The Colony, Lewisville, Little Elm, Frisco and Plano from the OnPoint Pros Remodeling office at Grandscape. Holes, cracks, nail pops and plumber cuts patched, textured and painted. Projects start at $1,000.",
            kicker="Drywall Repair, The Colony Office", h1="Drywall Repair You Cannot Find Afterward",
            lead="Holes, cracks, nail pops, damage from a plumber or electrician, and walls that have taken a beating. We patch, texture and paint from our office in The Colony.",
            h2="How We Repair Drywall", paragraphs=[
                "Every repair starts with photos. Send a picture of each area and we will tell you what it needs and give you one price for the whole list. Drywall projects start at $1,000, so it makes sense to put every hole, crack and corner in the same request.",
                "On the day, we cover the floor and furniture, cut the damaged area back to solid drywall, set a backer or new piece, tape, mud in two or three coats, and sand. Then the part that matters: texture. We spray a sample board first, compare it to your wall, and adjust until it matches. Knockdown, orange peel, splatter or smooth.",
                "We prime and paint the repair, or the full wall corner to corner when the color will not blend. You get a finished wall, not a patch waiting on a painter.",
            ],
            cards=[("", "Holes and Impact Damage", "Doorknob holes, furniture scrapes, TV mount scars and the mystery hole in the hallway."), ("", "Cracks and Nail Pops", "North Texas slabs move. We refasten, tape and mud so the crack stays closed."), ("", "Plumber and Electrician Cuts", "Access holes cut for a repair, closed up and textured so nobody knows they were there."), ("", "Water Stains and Soft Spots", "Once the leak is fixed, the damaged drywall comes out and new goes in."), ("", "Corners and Edges", "Dented corner bead and chipped edges rebuilt straight."), ("", "Garage Walls", "Unfinished or damaged garage drywall finished and ready for paint.")],
            photos=REPAIR_PHOTOS,
            faq=[("What is the minimum for a drywall repair?", "Drywall projects start at $1,000. Group every repair in your home into one request and we quote them together."), ("How long does a repair take?", "A single patch is usually one visit with a return for paint once the mud is dry. Larger repairs take two or three visits so each coat can dry properly."), ("Will the patch show?", "Not when the texture is matched on a sample first and the wall is painted to a natural break. That is how we do every repair.")]),
        "ceiling-water-damage-repair.html": dict(
            title="Ceiling and Water Damage Drywall Repair The Colony TX | OnPoint Pros Remodeling",
            desc="Water damaged ceiling repair in The Colony, Lewisville, Little Elm, Frisco and Plano. Sagging, stained and collapsed ceiling drywall replaced, retextured and painted by OnPoint Pros Remodeling.",
            kicker="Ceilings and Water Damage, The Colony Office", h1="Ceilings Fixed After the Leak",
            lead="Roof leaks, AC drain pans, upstairs tubs and burst lines all end up in the ceiling. We replace the wet drywall, match the texture and paint it so the stain and the sag are gone.",
            h2="What a Water Damaged Ceiling Needs", paragraphs=[
                "Fix the leak first. We will not close up a ceiling until the roofer or plumber has stopped the water, because wet drywall behind new paint comes back as a stain within weeks.",
                "Then we cut out the damaged section back to the joists, check the insulation, hang new drywall, tape and mud it, and match the ceiling texture. Ceilings in The Colony and Lewisville are mostly knockdown or a light splatter, and a ceiling patch shows more than a wall patch because of the way light rakes across it. We spray a sample first and blend the edges wide so the repair disappears.",
                "We finish with primer and ceiling paint across the whole ceiling or to a natural break, so there is no bright square where the patch was.",
            ],
            cards=[("", "Collapsed Ceilings", "Sections that came down after a leak or a storm, cleaned up and rebuilt."), ("", "Stains and Sags", "Bowed or stained drywall cut out and replaced, not painted over."), ("", "AC and Plumbing Access", "Holes cut by the HVAC or plumbing crew closed and textured."), ("", "Garage Ceilings", "Loose joints, cracked tape and damaged panels repaired and retextured."), ("", "Popcorn Ceilings", "Removed and refinished smooth or knockdown. See our popcorn removal page."), ("", "Attic Access and Vents", "Openings framed, trimmed and finished clean.")],
            photos=CEILING_PHOTOS,
            faq=[("Can you repair the ceiling before the leak is fixed?", "No. We ask that the roofer or plumber finish first. If you need a referral we can point you to people we have worked beside."), ("Will insurance cover the ceiling?", "Often, when the cause is sudden like a burst line or storm damage. We write a clear scope and price you can hand to your adjuster."), ("Do you paint the whole ceiling?", "Usually yes. A painted patch on a ceiling shows. Painting to a natural break or the whole ceiling is included in the price we quote.")]),
        "texture-matching-popcorn-removal.html": dict(
            title="Texture Matching and Popcorn Ceiling Removal The Colony TX | OnPoint Pros Remodeling",
            desc="Drywall texture matching and popcorn ceiling removal in The Colony, Lewisville, Little Elm, Frisco and Plano. Knockdown, orange peel and smooth finishes matched on a sample first by OnPoint Pros Remodeling.",
            kicker="Texture and Popcorn Removal, The Colony Office", h1="Texture That Matches and Popcorn That Is Gone",
            lead="Texture is where most drywall repairs fail. We spray a sample board, compare it to your wall and adjust until it matches. Popcorn ceilings we scrape, repair and refinish smooth or knockdown.",
            h2="Why Texture Is the Hard Part", paragraphs=[
                "Anyone can fill a hole. Making the repair disappear comes down to texture: the size of the splatter, how long it sits before the knockdown blade, the angle of the blade, and how wide the new texture feathers into the old. Get one of those wrong and the patch shows every afternoon when the sun comes across the wall.",
                "We test on a sample board before we touch your wall. Knockdown, orange peel, splatter, skip trowel and smooth are all finishes we match week to week in homes across The Colony, Lewisville and Frisco.",
                "Popcorn removal is its own job. We cover the room, wet and scrape the ceiling, repair the tape joints and nail pops that were hiding under the popcorn, skim where needed, then apply the finish you want and paint. Most homeowners choose smooth or a light knockdown.",
            ],
            cards=[("", "Knockdown", "The most common finish in newer homes here. Matched by splatter size and knockdown timing."), ("", "Orange Peel", "Fine spray texture matched by pressure and tip size."), ("", "Smooth, Level 5", "Skim coated flat walls and ceilings for a modern finish."), ("", "Popcorn Removal", "Scraped, repaired, refinished and painted."), ("", "Skip Trowel and Hand Textures", "Hand applied finishes matched by the same crew."), ("", "Retexture a Whole Wall", "When a patch will not blend, we retexture wall to wall.")],
            photos=TEXTURE_PHOTOS,
            faq=[("Does popcorn ceiling removal fall under the $1,000 minimum?", "Yes. Popcorn removal is a drywall project and almost always comes in above the minimum. We quote by the room after seeing photos or a quick visit."), ("Can old popcorn contain asbestos?", "Popcorn applied before the 1980s can. If your home is from that period we recommend a test before any scraping. Most homes in The Colony and Frisco are newer and this is not an issue."), ("Will the new texture match the rest of the house?", "Yes. We match the existing finish in the rooms we touch, or apply a new finish across the whole ceiling if you are changing styles.")]),
        "drywall-installation.html": dict(
            title="Drywall Installation The Colony TX | Garages, Additions, Whole Rooms | OnPoint Pros Remodeling",
            desc="New drywall hung, taped and finished in The Colony, Lewisville, Little Elm, Frisco and Plano. Garages, additions, closets and whole rooms by OnPoint Pros Remodeling.",
            kicker="New Drywall, The Colony Office", h1="New Drywall for Garages, Additions and Whole Rooms",
            lead="Unfinished garages, new additions, closets, media rooms and remodels. We hang, tape, finish and texture new drywall so it is ready for paint.",
            h2="How We Hang and Finish New Drywall", paragraphs=[
                "New drywall is most of what the Colony office does in garages. A finished garage changes how the space feels and how it holds temperature. We hang the panels, tape and mud the joints, finish the corners and apply the texture you choose. Fire rated board goes on the wall shared with the house where code calls for it.",
                "For additions and remodels we work with your framer or electrician. Once the inspection is passed we hang, finish and texture, and we can prime and paint so the room is done when we leave.",
                "The price depends on square footage, ceiling height, finish level and texture. Send rough dimensions and a few photos and we will give you a clear number before any work starts.",
                "For the long version, with rough ranges from our 2026 garage jobs, read <a href=\"https://www.linkedin.com/pulse/garage-drywall-installation-cost-onpoint-pros-ffqhc/\" class=\"text-red-600 font-semibold underline\">Garage Drywall Installation Cost</a> on LinkedIn.",
            ],
            cards=[("", "Garage Drywall", "Walls and ceilings hung and finished, with fire rated board where required."), ("", "Additions", "New rooms finished after framing, electrical and inspection."), ("", "Closets and Pantries", "Small spaces finished clean and ready for shelving."), ("", "Media and Game Rooms", "Finished walls and ceilings for converted spaces."), ("", "Ceilings", "New ceiling drywall hung, finished and textured."), ("", "Remodel Drywall", "Walls opened during a remodel closed up and finished.")],
            photos=INSTALL_PHOTOS,
            faq=[("How much does it cost to drywall a garage?", "It depends on size, ceiling height and finish. Send rough dimensions and photos and we will quote it. Garage projects are well above our $1,000 minimum."), ("Do you handle the permit?", "Hanging and finishing drywall in an existing garage usually does not need one. Additions and new rooms do, and your builder or framer carries that permit. We finish after the inspection."), ("Can you paint it too?", "Yes. Primer and paint can be included in the quote so the room is finished when we leave.")]),
    }
    for path, d in svc_pages.items():
        name = [t for h, t, _ in SERVICES if h == path][0]
        nav, bc = crumbs([("OnPoint Pros", "/"), ("The Colony Drywall Office", "/the-colony/"), (name, None)])
        f_sec, f_ld = faq(f"{name} Questions", d["faq"])
        body = header(path) + nav + hero(d["kicker"], d["h1"], esc(d["lead"]), "Get a Drywall Quote") + quick_answer(
            f"<strong>{BIZ['name']}, {esc(NAP)}, {BIZ['phone']}.</strong> Drywall projects start at $1,000. Serving {AREA_SENTENCE}, {BIZ['hours']}. Fully insured.") + prose(d["h2"], d["paragraphs"]) + cards(f"{name}: What We Handle", d["cards"], link=False) + photos("From Our Jobs", d["photos"]) + reviews("What Our Customers Say") + areas() + f_sec + estimate(
            f"Get a {name} Quote", "Send photos of every area and we will confirm the scope and price before work starts. Drywall projects start at $1,000.") + footer()
        written.append(page(path, d["title"], d["desc"], body, [service_ld(name, path, d["desc"]), bc, f_ld], scripts_v))

    # ---------------- city pages ----------------
    city_copy = {
        "lewisville": ["Lewisville is where the Colony office does most of its garage work. Castle Hills and the newer neighborhoods along 121 have a lot of unfinished and builder grade garages, and the older homes near Old Town have the cracks and nail pops that come with a few decades of slab movement.", "Three of our recent Google reviews are Lewisville garage ceilings and drywall patches. The office at Grandscape is a few minutes up the road, so scheduling is easy and we can come back for the paint coat without a long drive.", "We wrote up what Lewisville drywall repair involves and where the price lands in <a href=\"https://www.linkedin.com/pulse/drywall-repair-lewisville-tx-onpoint-pros-r0lqc/\" class=\"text-red-600 font-semibold underline\">Drywall Repair Lewisville TX</a> on LinkedIn."],
        "little-elm": ["Little Elm homes around Union Park, Sunset Pointe and Frisco Lakes are mostly newer builds with knockdown texture, which is the finish we match most. Nail pops along the ceiling line and cracks above door frames are the usual calls, plus garages that never got finished.", "We drive up 423 from The Colony. Send photos of every area and we will quote the whole list in one price."],
        "frisco": ["Frisco is split between our two offices. The Colony office covers the west side, Stonebriar, Starwood, Phillips Creek Ranch and the neighborhoods along the tollway. The Allen office handles the east side of Frisco and everything in Collin County beyond it.", "Either way it is the same owner, the same crew standards and the same $1,000 project minimum. Call the Colony number and we will route it."],
        "plano": ["West Plano, Willow Bend, Legacy West and the neighborhoods along the tollway are a short drive from Grandscape. Plano homes range from 1970s ranches with original texture to new builds, and we match both.", "If you are in east Plano, closer to Allen, our Allen office is just as good a call. Same owner, same crew standards, same price."],
    }
    for slug, city, path, hoods in CITIES[1:]:
        nav, bc = crumbs([("OnPoint Pros", "/"), ("The Colony Drywall Office", "/the-colony/"), (city, None)])
        f_sec, f_ld = faq(f"{city} Drywall Repair Questions", [
            (f"How much does drywall repair cost in {city}?", f"Drywall projects at OnPoint Pros Remodeling start at $1,000. Put every repair area in one request, send photos, and we quote the whole job together. Texture and paint are included."),
            (f"Do you come out to {city} for one hole?", f"Yes, as long as the project reaches the $1,000 minimum. Most homes have more than one spot that needs attention, and grouping them is how one visit pays for itself."),
            (f"Can you match the texture in my {city} home?", f"Yes. We spray a sample first, compare it to your wall and adjust until it matches before we blend it in."),
            ("Where are you based?", f"At Grandscape in The Colony. Open {BIZ['hours']}."),
        ])
        body = header(None) + nav + hero(f"Drywall Repair and Installation in {city}, TX", f"{city} Drywall Repair From Our Colony Office",
            esc(f"Holes, cracks, water damaged ceilings, texture matching, popcorn removal and new garage drywall for {city} homeowners. OnPoint Pros Remodeling, run by Dillon Hubbard from Grandscape in The Colony. Rated 5.0 on Google."), f"Get a {city} Drywall Quote") + quick_answer(
            f"<strong>{BIZ['name']} serves {esc(city)} from {esc(NAP)}, {BIZ['phone']}.</strong> Drywall projects start at $1,000. Open {BIZ['hours']}. Fully insured.") + prose(f"Drywall Work in {city}", city_copy[slug] + ["We show up when we say we will, protect your floors and furniture, give you one clear price before work starts and leave the house clean."]) + cards(f"What We Do in {city}", SERVICES) + photos("From Our Jobs", CITY_PHOTOS.get(slug, MIX_PHOTOS)) + reviews("What Our Customers Say") + neighborhoods(city, hoods) + areas(slug) + f_sec + bathroom_handoff() + estimate(
            f"Get a {city} Drywall Quote", "Send photos of every area and we will confirm the scope and price before work starts. Drywall projects start at $1,000.") + footer()
        written.append(page(path, f"Drywall Repair {city} TX | OnPoint Pros Remodeling, The Colony",
            f"Drywall repair, ceiling and water damage repair, texture matching, popcorn removal and garage drywall in {city}, TX from the OnPoint Pros Remodeling office in The Colony. Projects start at $1,000. Call {BIZ['phone']}.",
            body, [service_ld("Drywall Repair", path, f"Drywall repair and installation in {city}, TX by OnPoint Pros Remodeling."), bc, f_ld], scripts_v))

    # ---------------- contact ----------------
    nav, bc = crumbs([("OnPoint Pros", "/"), ("The Colony Drywall Office", "/the-colony/"), ("Contact", None)])
    body = header("contact.html") + nav + f"""
    <section class="py-16">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 grid md:grid-cols-2 gap-10">
            <div>
                <p class="text-amber-600 font-semibold uppercase tracking-wider mb-3 text-sm">Contact the Colony Office</p>
                <h1 class="text-4xl font-extrabold text-slate-900 mb-6">OnPoint Pros Remodeling</h1>
                <p class="text-lg text-slate-600 mb-6">Call or text with photos of every area that needs work. We reply the same day with what it needs and one price for the whole list. Drywall projects start at $1,000.</p>
                <dl class="space-y-4 text-slate-800">
                    <div><dt class="font-bold">Phone</dt><dd><a href="{BIZ['tel']}" class="text-red-600 font-semibold text-xl">{BIZ['phone']}</a></dd></div>
                    <div><dt class="font-bold">Office</dt><dd>{esc(NAP)}<br><a href="{BIZ['maps']}" target="_blank" rel="noopener" class="underline text-red-600">Open in Google Maps</a></dd></div>
                    <div><dt class="font-bold">Hours</dt><dd>Open {BIZ['hours']}</dd></div>
                    <div><dt class="font-bold">Service area</dt><dd>{AREA_SENTENCE}</dd></div>
                    <div><dt class="font-bold">Owner</dt><dd>Dillon Hubbard</dd></div>
                    <div><dt class="font-bold">Insurance</dt><dd>Fully insured</dd></div>
                </dl>
                <p class="mt-8 text-slate-500">Bathroom remodels and drywall in Allen, McKinney and Prosper go through our Allen office, <a href="/contact.html" class="underline text-red-600">OnPoint Pros</a>.</p>
            </div>
            <div>
                <img src="{HERO}" alt="OnPoint Pros Remodeling crew finishing a garage" class="rounded-2xl border border-slate-200 w-full h-auto" width="1600" height="900">
                <p class="mt-4 text-sm text-slate-500">Our crew finishing a garage. Floors covered, one clear price, house left clean.</p>
            </div>
        </div>
    </section>
""" + estimate("Send Us the Job", "Photos of every area, a rough size, and when you would like it done. We confirm scope and price before work starts.") + footer()
    written.append(page("contact.html", "Contact OnPoint Pros Remodeling | Drywall Office in The Colony TX",
        f"Contact the OnPoint Pros Remodeling drywall office: {NAP}, {BIZ['phone']}. Open {BIZ['hours']}. Serving {AREA_SENTENCE}.",
        body, [jsonld({"@context": "https://schema.org", "@type": "ContactPage", "url": BASE + "contact.html", "about": business_entity()}), bc], scripts_v))
    return written


def css_version():
    import hashlib
    return hashlib.sha256((ROOT / "assets/css/site.min.css").read_bytes()).hexdigest()[:12]


def script_versions():
    import hashlib
    v = {}
    for key, f in (("cookie", "cookie-consent.js"), ("measure", "site-measurement.js"), ("estimate", "estimate-form.js")):
        v[key] = hashlib.sha256((ROOT / f).read_bytes()).hexdigest()[:12]
    return v


if __name__ == "__main__":
    pages = build(script_versions())
    for p in pages:
        t = (OUT / p).read_text(encoding="utf-8")
        assert "handyman" not in t.lower(), p
        assert "—" not in t, p
        assert "licensed" not in t.lower(), p
        assert "617-5235" not in t, p
    print("wrote", len(pages), "pages:", ", ".join(pages))
