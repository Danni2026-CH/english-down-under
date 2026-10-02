#!/usr/bin/env python3
"""Build the episodes hub and episode pages.

Usage:  python3 build_episodes.py
Reads   data/episodes.json, data/phrases.json, templates/episode.html
Writes  episodes/index.html and episodes/<slug>/index.html

Add an episode = add one object to data/episodes.json (copy episode 1 as a model),
paste its YouTube video ID into "youtube_id", then re-run.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).parent
SITE = "https://englishdownunder.au"
e = html.escape

episodes = sorted(json.loads((ROOT / "data" / "episodes.json").read_text(encoding="utf-8")),
                  key=lambda x: (x.get("season", 1), x["number"]))
phrases = {p["slug"]: p for p in json.loads((ROOT / "data" / "phrases.json").read_text(encoding="utf-8"))}
template = (ROOT / "templates" / "episode.html").read_text(encoding="utf-8")

REQUIRED = ["slug", "number", "title", "summary", "echo", "perspective", "summary_passages"]
for ep in episodes:
    missing = [k for k in REQUIRED if not ep.get(k)]
    if missing:
        raise SystemExit(f"Episode '{ep.get('slug', '?')}' is missing: {', '.join(missing)}")
    for s in ep.get("key_phrases", []):
        if s not in phrases:
            raise SystemExit(f"Episode '{ep['slug']}' references unknown phrase '{s}'")
    yt = ep.get("youtube_id", "")
    if yt and not re.fullmatch(r"[A-Za-z0-9_-]{11}", yt):
        raise SystemExit(f"Episode '{ep['slug']}' has an invalid youtube_id '{yt}' (should be 11 characters)")

def drill(item, mic=False):
    text = e(item["text"], quote=True)
    audio = f' data-audio="{e(item["audio"], quote=True)}"' if item.get("audio") else ""
    mic_btn = f'<button class="btn gold sm" type="button" data-mic="{text}">🎙️ Speak</button>' if mic else ""
    res = '<div class="res"></div>' if mic else ""
    return (f'<div class="drill"><p>{e(item["text"])}</p><div class="row">'
            f'<button class="btn ghost sm" type="button" data-say="{text}"{audio}>🔊 Hear</button>{mic_btn}</div>{res}</div>')

def render(ep, i):
    yt = ep.get("youtube_id", "")
    if yt:
        video = (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{yt}?rel=0" '
                 f'title="{e(ep["title"], quote=True)}" loading="lazy" '
                 'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
    else:
        video = ('<div class="video"><div><div class="play">▶</div><strong>Video coming soon</strong><br>'
                 '<small><a href="https://www.youtube.com/@Downunderenglish-jb1dm" style="text-decoration:underline">Watch the channel on YouTube</a></small></div></div>')

    phr = ""
    if ep.get("key_phrases"):
        links = "".join(f'<a href="/phrases/{s}/">{e(phrases[s]["phrase"])}</a>' for s in ep["key_phrases"])
        phr = f'<h2>Key phrases</h2><div class="related">{links}</div>'

    tr = ""
    if ep.get("transcript"):
        lines = "".join(f'<div class="line"><b>{e(t["speaker"])}:</b> {e(t["text"])}</div>' for t in ep["transcript"])
        tr = f'<h2>Transcript</h2><details class="card"><summary>Show the transcript</summary><div class="inner">{lines}</div></details>'

    prev = episodes[i - 1] if i > 0 else None
    nxt = episodes[i + 1] if i < len(episodes) - 1 else None
    pn = (f'<a class="btn ghost" href="/episodes/{prev["slug"]}/">← Episode {prev["number"]}</a>' if prev else "<span></span>") + \
         (f'<a class="btn ghost" href="/episodes/{nxt["slug"]}/">Episode {nxt["number"]} →</a>' if nxt else '<a class="btn ghost" href="/episodes/">All episodes</a>')

    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": f'Episode {ep["number"]}: {ep["title"]}', "description": ep["summary"],
        "inLanguage": "en-AU", "url": f'{SITE}/episodes/{ep["slug"]}/',
        "publisher": {"@type": "Organization", "name": "English Down Under", "url": SITE},
    }, ensure_ascii=False).replace("</", "<\\/")

    fields = {
        "slug": e(ep["slug"]), "number": str(ep["number"]), "season": str(ep.get("season", 1)),
        "title": e(ep["title"]), "summary": e(ep["summary"], quote=True), "minutes": str(ep.get("minutes", 20)),
        "video_html": video, "phrases_section": phr,
        "echo_html": "".join(drill(x, mic=True) for x in ep["echo"]),
        "persp_html": "".join(drill(x) for x in ep["perspective"]),
        "summ_html": "".join(drill(x) for x in ep["summary_passages"]),
        "transcript_section": tr, "prevnext_html": pn, "jsonld": jsonld,
    }
    out = template
    for k, v in fields.items():
        out = out.replace("{{" + k + "}}", v)
    if "{{" in out:
        raise SystemExit(f"Unfilled placeholder in episode {ep['slug']}")
    return out

out_dir = ROOT / "episodes"
for i, ep in enumerate(episodes):
    d = out_dir / ep["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(render(ep, i), encoding="utf-8")

cards = "".join(
    f'<a class="card" href="/episodes/{ep["slug"]}/"><span class="pill gold">Season {ep.get("season", 1)} · Episode {ep["number"]}</span>'
    f'<h3 style="margin-top:10px">{e(ep["title"])}</h3><p>{e(ep["summary"])}</p>'
    f'<p style="margin-top:12px"><span class="pill">{ep.get("minutes", 20)} min practice</span>'
    f'{"<span class=pill>Video</span>" if ep.get("youtube_id") else ""}</p></a>'
    for ep in episodes)

hub = f"""<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Episodes with Sam &amp; Leo — Australian English Practice | English Down Under</title>
<meta name="description" content="Watch and practise Australian English with Sam and Leo. Every episode has a video, listening practice and speaking exercises.">
<link rel="canonical" href="{SITE}/episodes/">
<meta property="og:title" content="Episodes with Sam &amp; Leo">
<meta property="og:url" content="{SITE}/episodes/">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head><body>
<header class="nav"><div class="wrap">
<a class="brand" href="/">English <span>Down Under</span></a>
<nav><a href="/lab/">Imitation Lab</a><a href="/phrases/">Phrases</a><a href="/guides/">Guides</a><a href="/tools/">Tools</a><a class="on" href="/episodes/">Episodes</a><a href="https://fairdinkumslang.au">Slang</a></nav>
</div></header>
<div class="band"><div class="wrap">
<div class="crumbs" style="padding:0 0 10px;color:#B7CEDD"><a href="/">Home</a> › Episodes</div>
<h1>Episodes with Sam &amp; Leo</h1>
<p>Each episode has a video, sentences to echo, thoughts to shift and ideas to summarise. All free, no login.</p>
</div></div>
<main class="wrap" style="max-width:1100px">
<div class="grid g3" style="margin-top:28px">{cards}</div>
<p style="color:var(--muted);margin-top:22px">More episodes are on the way. Subscribe on <a href="https://www.youtube.com/@Downunderenglish-jb1dm" style="text-decoration:underline">YouTube</a> to hear when they land.</p>
</main>
<footer><div class="wrap">
<div>© English Down Under · Made with love in Australia</div>
<div style="display:flex;gap:18px;flex-wrap:wrap"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a><a href="https://fairdinkumslang.au">Fair Dinkum</a></div>
</div></footer>
</body></html>"""
out_dir.mkdir(exist_ok=True)
(out_dir / "index.html").write_text(hub, encoding="utf-8")

print(f"Built {len(episodes)} episode page(s) + hub")
