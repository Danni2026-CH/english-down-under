#!/usr/bin/env python3
"""Build the guides hub and guide pages.

Usage:  python3 build_guides.py
Reads   data/guides.json, data/phrases.json, templates/guide.html
Writes  guides/index.html (hub with category filter) and guides/<slug>/index.html
"""
import html, json, pathlib

ROOT = pathlib.Path(__file__).parent
SITE = "https://englishdownunder.au"
e = html.escape

guides = json.loads((ROOT / "data" / "guides.json").read_text(encoding="utf-8"))
phrases = {p["slug"]: p for p in json.loads((ROOT / "data" / "phrases.json").read_text(encoding="utf-8"))}
template = (ROOT / "templates" / "guide.html").read_text(encoding="utf-8")
by_slug = {g["slug"]: g for g in guides}

REQUIRED = ["slug", "title", "icon", "category", "level", "summary", "intro", "sections"]
for g in guides:
    missing = [k for k in REQUIRED if not g.get(k)]
    if missing:
        raise SystemExit(f"Guide '{g.get('slug', '?')}' is missing: {', '.join(missing)}")
    for s in g.get("key_phrases", []):
        if s not in phrases:
            raise SystemExit(f"Guide '{g['slug']}' references unknown phrase '{s}'")
    for s in g.get("related", []):
        if s not in by_slug:
            raise SystemExit(f"Guide '{g['slug']}' references unknown guide '{s}'")
    for sec in g["sections"]:
        for it in sec["items"]:
            if it.get("phrase") and it["phrase"] not in phrases:
                raise SystemExit(f"Guide '{g['slug']}' links unknown phrase '{it['phrase']}'")

def slugify(text):
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")

def section_html(sec):
    rows = ""
    for it in sec["items"]:
        link = ""
        if it.get("phrase"):
            link = f' <a href="/phrases/{it["phrase"]}/" style="color:var(--ocean);font-weight:600;font-size:.85rem">Full phrase page →</a>'
        rows += (f'<div class="say"><div><strong>{e(it["say"])}</strong>'
                 f'<span>{e(it["note"])}{link}</span></div>'
                 f'<button class="btn ghost sm" type="button" data-say="{e(it["say"], quote=True)}" aria-label="Hear {e(it["say"], quote=True)}">🔊 Hear</button></div>')
    tip = f'<div class="tipbox"><strong>Tip:</strong> {e(sec["tip"])}</div>' if sec.get("tip") else ""
    return f'<h2 id="{slugify(sec["heading"])}">{e(sec["heading"])}</h2><div class="card">{rows}</div>{tip}'

def render(g):
    toc = "".join(f'<a href="#{slugify(s["heading"])}">{e(s["heading"])}</a>' for s in g["sections"])
    ph = "".join(f'<a href="/phrases/{s}/">{e(phrases[s]["phrase"])}</a>' for s in g.get("key_phrases", [])) \
         or '<span style="color:var(--muted)">More phrases coming soon.</span>'
    rel = "".join(f'<a href="/guides/{s}/">{by_slug[s]["icon"]} {e(by_slug[s]["title"])}</a>' for s in g.get("related", [])) \
          or '<a href="/guides/">All guides</a>'
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": g["title"], "description": g["summary"], "inLanguage": "en-AU",
        "url": f'{SITE}/guides/{g["slug"]}/',
        "publisher": {"@type": "Organization", "name": "English Down Under", "url": SITE},
    }, ensure_ascii=False).replace("</", "<\\/")
    fields = {
        "title": e(g["title"]), "slug": e(g["slug"]), "icon": g["icon"], "category": e(g["category"]),
        "level": e(g["level"]), "summary": e(g["summary"], quote=True), "intro": e(g["intro"]),
        "toc_html": toc, "sections_html": "".join(section_html(s) for s in g["sections"]),
        "phrases_html": ph, "related_html": rel, "jsonld": jsonld,
    }
    out = template
    for k, v in fields.items():
        out = out.replace("{{" + k + "}}", v)
    if "{{" in out:
        raise SystemExit(f"Unfilled placeholder in guide {g['slug']}")
    return out

out_dir = ROOT / "guides"
for g in guides:
    d = out_dir / g["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(render(g), encoding="utf-8")

# ---- Hub ----
cats = []
for g in guides:
    if g["category"] not in cats:
        cats.append(g["category"])
buttons = '<button class="on" data-c="all">All</button>' + "".join(
    f'<button data-c="{e(c, quote=True)}">{e(c)}</button>' for c in cats)
cards = "".join(
    f'<a class="card" href="/guides/{g["slug"]}/" data-c="{e(g["category"], quote=True)}">'
    f'<div class="ico">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["summary"])}</p>'
    f'<p style="margin-top:12px"><span class="pill">{e(g["category"])}</span><span class="pill">{e(g["level"])}</span></p></a>'
    for g in guides)

hub = f"""<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Australian English Guides — Real-Life Situations | English Down Under</title>
<meta name="description" content="Guides to speaking Australian English in real situations: cafés, job interviews, renting, small talk, phone calls, rhythm and vowel sounds.">
<link rel="canonical" href="{SITE}/guides/">
<meta property="og:title" content="Australian English Guides">
<meta property="og:url" content="{SITE}/guides/">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head><body>
<header class="nav"><div class="wrap">
<a class="brand" href="/">English <span>Down Under</span></a>
<nav><a href="/lab/">Imitation Lab</a><a href="/phrases/">Phrases</a><a class="on" href="/guides/">Guides</a><a href="/tools/">Tools</a><a href="/episodes/">Episodes</a><a href="https://fairdinkumslang.au">Slang</a></nav>
</div></header>
<div class="band"><div class="wrap">
<div class="crumbs" style="padding:0 0 10px;color:#B7CEDD"><a href="/">Home</a> › Guides</div>
<h1>English for real life in Australia</h1>
<p>What to say, how to say it, and what locals actually do. Every phrase has audio.</p>
</div></div>
<main class="wrap wide" style="max-width:1100px">
<div class="filters" id="filters">{buttons}</div>
<div class="grid g3" id="cards" style="margin-top:16px">{cards}</div>
<div class="sister">
<div><strong>🦘 Looking for slang?</strong><br><span style="color:var(--muted)">Fair Dinkum has 600+ Aussie slang words with origin stories.</span></div>
<a class="btn" href="https://fairdinkumslang.au">Visit Fair Dinkum →</a></div>
</main>
<footer><div class="wrap">
<div>© English Down Under · Made with love in Australia</div>
<div style="display:flex;gap:18px;flex-wrap:wrap"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a><a href="https://fairdinkumslang.au">Fair Dinkum</a></div>
</div></footer>
<script>
document.getElementById('filters').addEventListener('click',function(ev){{
  var b=ev.target.closest('button');if(!b)return;
  document.querySelectorAll('#filters button').forEach(function(x){{x.classList.toggle('on',x===b)}});
  var c=b.getAttribute('data-c');
  document.querySelectorAll('#cards .card').forEach(function(a){{a.style.display=(c==='all'||a.getAttribute('data-c')===c)?'':'none'}});
}});
</script>
</body></html>"""
out_dir.mkdir(exist_ok=True)
(out_dir / "index.html").write_text(hub, encoding="utf-8")

print(f"Built {len(guides)} guides + hub")
