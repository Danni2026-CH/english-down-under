#!/usr/bin/env python3
"""Build static phrase pages for englishdownunder.au.

Usage:  python3 build_phrases.py
Reads   data/phrases.json  +  templates/phrase.html
Writes  phrases/<slug>/index.html, phrases/index.html (A-Z hub), data/phrase-index.json

Optional per-phrase field "audio": "/audio/phrases/<slug>.mp3" adds a recorded
player above the browser voice. Add a phrase = add one object to the JSON, rerun.
"""
import html, json, pathlib

ROOT = pathlib.Path(__file__).parent
SITE = "https://englishdownunder.au"
phrases = json.loads((ROOT / "data" / "phrases.json").read_text(encoding="utf-8"))
template = (ROOT / "templates" / "phrase.html").read_text(encoding="utf-8")
by_slug = {p["slug"]: p for p in phrases}
e = html.escape

REQUIRED = ["slug", "phrase", "ipa", "respell", "meaning", "category", "level",
            "aussie", "standard", "mistake", "tip", "examples"]
for p in phrases:
    missing = [k for k in REQUIRED if not p.get(k)]
    if missing:
        raise SystemExit(f"Phrase '{p.get('slug', '?')}' is missing: {', '.join(missing)}")

def short(text, n=140):
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"

def render(p):
    related = [by_slug[s] for s in p.get("related", []) if s in by_slug]
    audio = ""
    if p.get("audio"):
        audio = f'<audio controls preload="none" src="{e(p["audio"])}" style="margin-top:14px;width:100%"></audio>'
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": f'How to say "{p["phrase"]}" in Australian English',
        "description": short(p["meaning"]),
        "url": f'{SITE}/phrases/{p["slug"]}/',
        "inLanguage": "en-AU",
        "publisher": {"@type": "Organization", "name": "English Down Under", "url": SITE},
    }, ensure_ascii=False).replace("</", "<\\/")
    fields = {
        "phrase": e(p["phrase"]), "slug": e(p["slug"]), "ipa": e(p["ipa"]),
        "respell": e(p["respell"]), "meaning": e(p["meaning"]),
        "meaning_short": e(short(p["meaning"])), "category": e(p["category"]),
        "level": e(p["level"]), "aussie": e(p["aussie"]), "standard": e(p["standard"]),
        "mistake": e(p["mistake"]), "tip": e(p["tip"]),
        "examples_html": "".join(f"<li>{e(x)}</li>" for x in p["examples"]),
        "related_html": "".join(f'<a href="/phrases/{r["slug"]}/">{e(r["phrase"])}</a>' for r in related)
                        or '<span style="color:var(--muted)">More phrases coming soon.</span>',
        "audio_block": audio,
        "jsonld": jsonld,
        "phrase_js": json.dumps(p["phrase"], ensure_ascii=False).replace("</", "<\\/"),
    }
    out = template
    for k, v in fields.items():
        out = out.replace("{{" + k + "}}", v)
    if "{{" in out:
        raise SystemExit(f"Unfilled placeholder in {p['slug']}")
    return out

out_dir = ROOT / "phrases"
for p in phrases:
    d = out_dir / p["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(render(p), encoding="utf-8")

# ---- Hub page (A-Z, grouped by category, with live filter) ----
cats = {}
for p in sorted(phrases, key=lambda x: x["phrase"].lower()):
    cats.setdefault(p["category"], []).append(p)
cards = ""
for cat in sorted(cats):
    cards += f'<h2>{e(cat)}</h2><div class="list">'
    for p in cats[cat]:
        cards += (f'<a class="item" href="/phrases/{p["slug"]}/" data-s="{e((p["phrase"]+" "+p["meaning"]).lower())}">'
                  f'<strong>{e(p["phrase"])}</strong><small>{e(short(p["meaning"], 90))}</small>'
                  f'<span class="pill">{e(p["level"])}</span></a>')
    cards += "</div>"

hub = f"""<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aussie Phrase Bank — Pronunciation &amp; Meaning | English Down Under</title>
<meta name="description" content="Browse Australian English phrases with pronunciation, meaning, common mistakes and speaking practice.">
<link rel="canonical" href="{SITE}/phrases/">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--ocean:#1B4F72;--ocean-dark:#123852;--ocean-soft:#E8F1F7;--gold:#F4D03F;--ink:#14232E;--muted:#5B6B77;--bg:#FBFAF6;--line:#E3E8EC}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}}
a{{color:inherit;text-decoration:none}}.wrap{{max-width:900px;margin:0 auto;padding:0 20px}}
header{{background:var(--ocean-dark)}}header .wrap{{height:60px;display:flex;align-items:center;max-width:1100px}}
.brand{{font-family:Fraunces,serif;font-weight:800;color:#fff;font-size:1.15rem}}.brand span{{color:var(--gold)}}
h1{{font-family:Fraunces,serif;font-weight:800;color:var(--ocean-dark);font-size:clamp(2rem,5vw,2.8rem);margin:32px 0 6px}}
h2{{font-family:Fraunces,serif;color:var(--ocean-dark);margin:30px 0 10px}}
input{{width:100%;padding:14px 16px;border:1px solid var(--line);border-radius:12px;font:inherit;font-size:1rem;margin:14px 0 6px}}
.list{{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}}
.item{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px;display:block}}.item:hover{{border-color:var(--ocean)}}
.item small{{display:block;color:var(--muted);margin:4px 0 8px}}
.pill{{font-size:.7rem;font-weight:600;padding:3px 9px;border-radius:999px;background:var(--ocean-soft);color:var(--ocean)}}
</style></head><body>
<header><div class="wrap"><a class="brand" href="/">English <span>Down Under</span></a></div></header>
<main class="wrap"><h1>Phrase Bank</h1>
<p style="color:var(--muted);margin:0">{len(phrases)} phrases with pronunciation, meaning and practice. New ones added regularly.</p>
<input id="f" type="search" placeholder="Filter phrases…" aria-label="Filter phrases">
{cards}</main>
<script>
document.getElementById('f').addEventListener('input',function(){{
  var s=this.value.toLowerCase();
  document.querySelectorAll('.item').forEach(function(a){{a.style.display=a.dataset.s.indexOf(s)>-1?'':'none'}});
}});
</script></body></html>"""
out_dir.mkdir(exist_ok=True)
(out_dir / "index.html").write_text(hub, encoding="utf-8")

# ---- Phrase search index for the homepage (also usable by other pages) ----
index = [{"t": p["phrase"], "d": f'{p["category"]} · {short(p["meaning"], 60)}',
          "u": f'/phrases/{p["slug"]}/'} for p in phrases]
(ROOT / "data" / "phrase-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"Built {len(phrases)} phrase pages + hub + phrase-index.json")
