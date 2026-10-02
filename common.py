"""Shared helpers for the page builders: site config, nav, page layout, Fair Dinkum box."""
import html, json, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).parent
cfg = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
SITE, YT, EMAIL = cfg["site_url"], cfg["youtube_url"], cfg["contact_email"]
e = html.escape

NAV = [("Imitation Lab", "/lab/"), ("Phrases", "/phrases/"), ("Guides", "/guides/"),
       ("Tools", "/tools/"), ("Episodes", "/episodes/"), ("Slang", "https://fairdinkumslang.au")]

def page(folder, title, desc, body, nav_on="", head_extra="", script="", band=None):
    nav = "".join(f'<a{" class=on" if href == nav_on else ""} href="{href}">{label}</a>' for label, href in NAV)
    if band:  # (h1, subtitle) -> coloured band with crumbs, then main content
        top = (f'<div class="band"><div class="wrap"><div class="crumbs" style="padding:0 0 10px;color:#B7CEDD">'
               f'<a href="/">Home</a> › {e(band[2])}</div><h1>{band[0]}</h1><p>{band[1]}</p></div></div>')
    else:
        top = ""
    out = f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc, quote=True)}">
<link rel="canonical" href="{SITE}/{folder}/">
<meta property="og:title" content="{e(title, quote=True)}">
<meta property="og:description" content="{e(desc, quote=True)}">
<meta property="og:url" content="{SITE}/{folder}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
{head_extra}
</head>
<body>
<header class="nav"><div class="wrap">
<a class="brand" href="/">English <span>Down Under</span></a>
<nav>{nav}</nav>
</div></header>
{top}
{body}
<footer><div class="wrap">
<div>© English Down Under · Made with love in Australia</div>
<div style="display:flex;gap:18px;flex-wrap:wrap"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a><a href="https://fairdinkumslang.au">Fair Dinkum</a></div>
</div></footer>
{script}
</body>
</html>
"""
    d = ROOT / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(out, encoding="utf-8")

SISTER = ('<div class="sister"><div><strong>🦘 Want the slang meanings?</strong><br>'
          '<span style="color:var(--muted)">Fair Dinkum has 600+ Aussie slang words with origin stories.</span></div>'
          '<a class="btn" href="https://fairdinkumslang.au">Visit Fair Dinkum →</a></div>')

