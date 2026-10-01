#!/usr/bin/env python3
"""Site copy guard: em dashes, FAQ schema drift, markup validity.

    python3 tools/copy_check.py          # audit, exits 1 on any finding
    python3 tools/copy_check.py --fix    # repair in place

Three things it enforces, all of which silently regressed before:

1. No em dash used as sentence punctuation. Thu's rule (2026-07-29, extended
   2026-08-19) covers every customer-facing surface including landing pages,
   because an em dash reads as AI-written. Brand/title separators, image alt
   labels and verbatim review attributions are legitimate and are left alone.
2. FAQPage schema must match the visible <details> copy word for word. Google
   drops markup that drifts from on-page text, so the schema is rebuilt from
   the DOM rather than hand-maintained.
3. JSON-LD parses and container tags balance.

Run with --fix after any bulk content edit, then commit the result.
"""
import re, sys, glob, json, html

DASH = r'(?:—|&mdash;)'
VERBS = set("""is are was were has have had will would can could should may might must
costs cost means takes take gets get goes go makes make comes come reads read shows show
looks look runs run starts start ends end needs need works work happens happen matters matter
hides hide moves move adds add saves save keeps keep leaves leave turns turn sits sit
stays stay drops drop swells swell shrugs shrug handles handle survives survive requires require
wins win belongs belong depends depend varies vary ranges range lands land
remains remain reaches reach shrinks shrink separates separate""".split())
CONTR = re.compile(r"^(?:it|that|they|we|you|there|here|he|she)'(?:s|re|ll|ve|d)$", re.I)
SUBJ = set("it we you they that this there here he she".split())
TAGS = ("div", "p", "figure", "details", "table", "section", "li", "ul", "h1", "h2", "h3",
        "strong", "a", "summary")


def vis(s):
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', '', s))).strip()


# ---------------------------------------------------------------- em dashes

def protected_spans(h):
    """Regions where a dash is a separator or code, not sentence punctuation."""
    spans = []
    for m in re.finditer(r'<style\b[^>]*>.*?</style>|<script\b([^>]*)>(.*?)</script>',
                         h, re.S | re.I):
        if m.group(0)[:7].lower() == '<script' and 'ld+json' in (m.group(1) or '').lower():
            continue  # schema text IS customer copy
        spans.append((m.start(), m.end()))
    spans += [m.span() for m in re.finditer(r'<title\b[^>]*>.*?</title>', h, re.S | re.I)]
    # only brand-name values are separators; an FAQ Question's "name" is prose
    spans += [m.span() for m in re.finditer(r'"(?:name|headline|alternateName)"\s*:\s*"[^"]*"', h)
              if 'OnPoint' in m.group(0)]
    spans += [m.span() for m in re.finditer(
        r'<meta[^>]*(?:name|property)="[^"]*title[^"]*"[^>]*>', h, re.I)]
    spans += [m.span() for m in re.finditer(r'alt="[^"]*"', h)]
    return spans


def decide(left, right):
    """What a prose dash should become, or None to leave it."""
    if re.match(r'\s*Dillon\b', right):
        return None                                   # the one allowed sign-off dash
    vl = html.unescape(re.sub(r'<[^>]*>', '', left)).rstrip()
    if vl.endswith(('”', '"', '’')):
        return None                                   # "…" — Reviewer Name
    if re.search(r'(?:</strong>|</b>)\s*$', left):
        return ':'
    if re.search(r'(?:^|>|\s)(Yes|No)\s*$', vl):
        return ','
    if vl.endswith((',', ':', ';')):
        return ''
    vr = html.unescape(re.sub(r'<[^>]*>', '', right)).lstrip()
    sentence = re.split(r'(?<=[.!?])\s', vl)[-1]
    if len(re.findall(r'—', sentence)) % 2 == 0:       # an opening dash
        ahead = re.split(r'—|(?<=[.!?])\s', vr)[0]
        if ahead.count(',') >= 2 and ':' not in sentence[-60:]:
            return ':'                                # introduces a list
    w = re.findall(r"[A-Za-z']+", vr)[:2]
    if len(w) == 2 and (CONTR.match(w[0]) or
                        (w[0].lower() in SUBJ and w[1].lower() in VERBS)):
        return '.'                                    # a comma here would splice
    return ','


def dash_pass(h):
    spans = protected_spans(h)
    edits = []
    for m in re.finditer(DASH, h):
        if any(a <= m.start() < b for a, b in spans):
            continue
        rep = decide(h[max(0, m.start() - 160):m.start()], h[m.end():m.end() + 80])
        if rep is not None:
            edits.append((m.start(), m.end(), rep))
    for a, b, rep in reversed(edits):
        tail, head = h[b:].lstrip(' '), h[:a].rstrip(' ')
        if rep == '.':
            mm = re.match(r'((?:\s|<[^>]*>)*)([a-z])', tail)
            if mm:
                tail = tail[:mm.start(2)] + mm.group(2).upper() + tail[mm.end(2):]
        h = head + rep + ' ' + tail
    return h, len(edits)


# ---------------------------------------------------------------- FAQ schema

def faq_pairs(h):
    m = re.search(r'Frequently Asked Questions|Common Questions|FAQ', h, re.I)
    pairs = []
    for d in re.finditer(r'<details[^>]*>(.*?)</details>', h[m.start() if m else 0:], re.S):
        body = d.group(1)
        q = re.search(r'<summary[^>]*>(.*?)</summary>', body, re.S)
        answers = [a for a in (vis(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', body, re.S)) if a]
        if q and answers:
            pairs.append((vis(q.group(1)), ' '.join(answers)))
    return pairs


def faq_pass(h):
    if '"FAQPage"' not in h:
        return h, 0
    pairs = faq_pairs(h)
    if not pairs:
        return h, 0
    want = [{"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]
    drift = 0
    for m in list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)):
        raw = m.group(1)
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            continue
        groups = d if isinstance(d, list) else [d]
        hit = False
        for g in groups:
            if isinstance(g, dict) and g.get("@type") == "FAQPage":
                if g.get("mainEntity") != want:
                    drift += 1
                g["mainEntity"] = want
                hit = True
        if hit:
            h = h.replace(raw, json.dumps(d, ensure_ascii=False), 1)
    return h, drift


# ---------------------------------------------------------------- driver

def main():
    fix = '--fix' in sys.argv
    files = sorted(glob.glob("**/*.html", recursive=True))
    dashes = drifted = broken = 0
    for p in files:
        h = original = open(p, encoding="utf-8").read()
        h, nd = dash_pass(h)
        h, nf = faq_pass(h)
        dashes += nd
        drifted += nf
        if nd and not fix:
            print(f"  em dash in prose: {p} ({nd})")
        if nf and not fix:
            print(f"  FAQ schema drifted from visible copy: {p}")
        for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                json.loads(s)
            except json.JSONDecodeError as e:
                broken += 1
                print(f"  invalid JSON-LD: {p}: {e}")
        for t in TAGS:
            o, c = len(re.findall(rf'<{t}[\s>]', h)), h.count(f'</{t}>')
            if o != c:
                broken += 1
                print(f"  unbalanced <{t}>: {p} ({o} open / {c} close)")
        if fix and h != original:
            open(p, "w", encoding="utf-8").write(h)
    verb = "fixed" if fix else "found"
    print(f"{len(files)} files | {verb} {dashes} prose em dashes, "
          f"{drifted} drifted FAQ blocks | {broken} markup problems")
    return 1 if (not fix and (dashes or drifted or broken)) or broken else 0


if __name__ == "__main__":
    sys.exit(main())
