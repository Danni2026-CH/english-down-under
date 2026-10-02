#!/usr/bin/env python3
"""Rebuild every generated page, then the sitemap.   Usage: python3 build_all.py"""
import datetime, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).parent
SITE = "https://englishdownunder.au"

for script in ("build_phrases.py", "build_guides.py", "build_episodes.py", "build_pages.py"):
    subprocess.run([sys.executable, str(ROOT / script)], check=True)

# Sitemap: homepage, lab, and every generated index.html under the section folders
urls = [f"{SITE}/", f"{SITE}/lab/"]
for section in ("phrases", "guides", "episodes", "tools", "accent-checker", "aussie-vs-us", "about", "contact", "privacy"):
    for f in sorted((ROOT / section).rglob("index.html")):
        rel = f.parent.relative_to(ROOT).as_posix()
        urls.append(f"{SITE}/{rel}/")
today = datetime.date.today().isoformat()
body = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
    encoding="utf-8")
print(f"Sitemap: {len(urls)} URLs")
