#!/usr/bin/env python3
"""Build the tools hub, the Aussie vs US vs UK comparison page, and About / Contact / Privacy.

Usage:  python3 build_pages.py
Reads   data/site.json, data/compare.json
Writes  tools/, aussie-vs-us/, about/, contact/, privacy/  (each as <folder>/index.html)
"""
import html, json, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).parent
cfg = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
compare = json.loads((ROOT / "data" / "compare.json").read_text(encoding="utf-8"))
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

# ───────────────────────── TOOLS HUB ─────────────────────────
def tool_card(icon, name, text, href, tag, external=False, soon=False):
    t = f'<span class="pill{" gold" if soon else ""}">{tag}</span>'
    inner = f'<div class="ico">{icon}</div><h3>{name}</h3><p>{text}</p><p style="margin-top:12px">{t}</p>'
    if soon:
        return f'<div class="card soon">{inner}</div>'
    return f'<a class="card" href="{href}"{" rel=noopener" if external else ""}>{inner}</a>'

live = "".join([
    tool_card("🎙️", "Imitation Lab", "A 20-minute daily session: echo Sam, shift perspective with Leo, then summarise. Includes a practice streak.", "/lab/", "Speaking"),
    tool_card("🌏", "Aussie vs US vs UK", "Vocabulary, pronunciation and spelling side by side, with a quick quiz.", "/aussie-vs-us/", "Compare"),
    tool_card("📖", "Phrase Bank", "Phrases with audio, pronunciation notes, common mistakes and speaking practice.", "/phrases/", "Browse"),
    tool_card("🧭", "Situation Guides", "Cafés, job interviews, renting, small talk, phone calls, rhythm and vowels.", "/guides/", "Guides"),
])
fd = "".join([
    tool_card("🦘", "Slangle", "One slang word a day. Six guesses.", "https://fairdinkumslang.au/slangle", "Fair Dinkum ↗", external=True),
    tool_card("🧩", "Slang Connections", "Find the four hidden groups of slang.", "https://fairdinkumslang.au/slang-connections", "Fair Dinkum ↗", external=True),
    tool_card("🗣️", "Slang Translator", "Paste a sentence and decode the slang.", "https://fairdinkumslang.au/slang-translator", "Fair Dinkum ↗", external=True),
])
soon = "".join([
    tool_card("🎯", "Accent Checker", "Say a phrase and see how close you are to the Aussie version.", "", "Coming soon", soon=True),
    tool_card("✨", "Aussie-fy My Sentence", "Paste standard English and get a natural Australian version.", "", "Coming soon", soon=True),
    tool_card("🦘", "Daily Accent Puzzle", "Hear a word and spot the Aussie pronunciation.", "", "Coming soon", soon=True),
    tool_card("🧩", "Which Aussie Are You?", "A short quiz on how Aussie your English sounds.", "", "Coming soon", soon=True),
    tool_card("🏆", "Streak & Score Cards", "Make a shareable card of your streak or result.", "", "Coming soon", soon=True),
])
tools_body = f"""<main class="wrap wide" style="max-width:1100px">
<h2>Ready to use</h2>
<div class="grid g3">{live}</div>
<h2>More from Fair Dinkum</h2>
<p style="color:var(--muted);margin:0 0 12px">Our sister site has games and tools for Aussie slang.</p>
<div class="grid g3">{fd}</div>
<h2 id="coming">Coming soon</h2>
<p style="color:var(--muted);margin:0 0 12px">Tools we're building next.</p>
<div class="grid g3">{soon}</div>
{SISTER}
</main>"""
page("tools", "Free Tools for Practising Australian English | English Down Under",
     "Free tools for practising Australian English: speaking lessons, accent and vocabulary comparisons, phrase audio and slang games.",
     tools_body, nav_on="/tools/",
     band=("Free tools for Australian English", "Practise speaking, compare accents and play with slang. No login needed.", "Tools"))

# ───────────────────────── COMPARE PAGE ─────────────────────────
FLAGS = (("au", "🇦🇺", "en-AU"), ("us", "🇺🇸", "en-US"), ("uk", "🇬🇧", "en-GB"))

def cell(item, key, flag, lang, hear_text):
    return (f'<div class="cell"><b>{flag} {key.upper()}</b>{e(item[key])}'
            f'<button class="hear" type="button" data-say="{e(hear_text, quote=True)}" data-lang="{lang}" aria-label="Hear {e(hear_text, quote=True)}">🔊</button></div>')

def rows_vocab():
    out = ""
    for it in compare["vocab"]:
        cells = "".join(cell(it, k, f, l, it[k]) for k, f, l in FLAGS)
        note = f'<div class="cnote">{e(it["note"])}</div>' if it.get("note") else ""
        out += (f'<div class="crow" data-s="{e((it["concept"]+" "+it["au"]+" "+it["us"]+" "+it["uk"]).lower(), quote=True)}">'
                f'<div class="cell concept"><b>Meaning</b>{e(it["concept"])}</div>{cells}{note}</div>')
    return out

def rows_pron():
    out = ""
    for it in compare["pron"]:
        cells = "".join(cell(it, k, f, l, it["word"]) for k, f, l in FLAGS)
        note = f'<div class="cnote">{e(it["note"])}</div>' if it.get("note") else ""
        out += (f'<div class="crow" data-s="{e(it["word"].lower(), quote=True)}">'
                f'<div class="cell concept"><b>Word</b><strong>{e(it["word"])}</strong></div>{cells}{note}</div>')
    return out

def rows_spell():
    out = ""
    for it in compare["spell"]:
        cells = "".join(f'<div class="cell"><b>{f} {k.upper()}</b>{e(it[k])}</div>' for k, f, l in FLAGS)
        note = f'<div class="cnote">{e(it["note"])}</div>' if it.get("note") else ""
        out += (f'<div class="crow spell" data-s="{e((it["au"]+" "+it["us"]+" "+it["uk"]).lower(), quote=True)}">'
                f'{cells}{note}</div>')
    return out

quiz_data = json.dumps([{"us": v["us"], "au": v["au"], "concept": v["concept"]}
                        for v in compare["vocab"] if v["au"].lower() != v["us"].lower()],
                       ensure_ascii=False).replace("</", "<\\/")

compare_css = """<style>
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0 10px}
.tabs button{font:inherit;font-weight:600;background:#fff;border:1.5px solid var(--line);border-radius:999px;padding:9px 18px;cursor:pointer;color:var(--ocean-dark)}
.tabs button.on{background:var(--ocean);border-color:var(--ocean);color:#fff}
#cf{width:100%;padding:13px 16px;border:1px solid var(--line);border-radius:12px;font:inherit;font-size:1rem;margin:6px 0 10px}
.crow{display:grid;grid-template-columns:1.1fr 1fr 1fr 1fr;gap:10px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin:8px 0;align-items:start}
.crow.spell{grid-template-columns:1fr 1fr 1fr}
.cell{position:relative;padding-right:30px}
.cell.concept{padding-right:0}
.cell b{display:block;font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px}
.hear{position:absolute;right:0;top:12px;border:0;background:var(--ocean-soft);border-radius:8px;cursor:pointer;width:26px;height:26px;font-size:.8rem}
.hear:hover{background:var(--gold)}
.cnote{grid-column:1/-1;color:var(--muted);font-size:.88rem;border-top:1px dashed var(--line);padding-top:8px}
.pane{display:none}.pane.on{display:block}
.empty{color:var(--muted);padding:16px 4px;display:none}
.quiz .opts{display:grid;gap:8px;margin:14px 0}
.quiz .opts button{font:inherit;font-weight:600;text-align:left;background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:12px 14px;cursor:pointer}
.quiz .opts button:hover:not(:disabled){border-color:var(--ocean)}
.quiz .opts button.ok{background:#E6F6EA;border-color:#2E9E55}
.quiz .opts button.no{background:#FDECEC;border-color:#D64545}
.qq{font-size:1.15rem;font-family:Fraunces,serif;color:var(--ocean-dark)}
@media(max-width:700px){.crow{grid-template-columns:1fr 1fr 1fr}.crow .concept{grid-column:1/-1}.cell{padding-right:0}.hear{position:static;margin-top:4px;display:block}}
</style>"""

compare_body = f"""<main class="wrap wide" style="max-width:1100px">
<div class="tabs" id="tabs" role="tablist">
<button class="on" data-p="vocab">Vocabulary</button><button data-p="pron">Pronunciation</button><button data-p="spell">Spelling</button>
</div>
<input id="cf" type="search" placeholder="Filter, e.g. “thongs” or “tomato”…" aria-label="Filter the comparison">
<div class="pane on" id="p-vocab">{rows_vocab()}</div>
<div class="pane" id="p-pron"><p style="color:var(--muted);margin:4px 0 10px;font-size:.92rem">Respellings are shown for each accent. The 🔊 button uses your device's voice for that accent, so it may not match perfectly. For real accent practice, listen to recordings of real speakers.</p>{rows_pron()}</div>
<div class="pane" id="p-spell">{rows_spell()}</div>
<div class="empty" id="empty">Nothing matches that filter.</div>

<h2>Quick quiz: what would an Aussie say?</h2>
<div class="card quiz" id="quiz">
<div class="qq" id="qq"></div>
<div class="opts" id="opts"></div>
<div id="qfb" style="min-height:1.5em;color:var(--muted)"></div>
<div class="row" style="margin-top:10px"><button class="btn gold" id="qnext" type="button">Next question →</button><span id="qscore" style="align-self:center;font-weight:600;color:var(--ocean-dark)"></span></div>
</div>
{SISTER}
</main>"""

compare_script = """<script>
var QUIZ=""" + quiz_data + """;
// Tabs + filter
var cur='vocab',cf=document.getElementById('cf');
function refilter(){
  var s=cf.value.trim().toLowerCase(),shown=0;
  document.querySelectorAll('#p-'+cur+' .crow').forEach(function(r){
    var ok=!s||r.getAttribute('data-s').indexOf(s)>-1;r.style.display=ok?'':'none';if(ok)shown++;
  });
  document.getElementById('empty').style.display=shown?'none':'block';
}
document.getElementById('tabs').addEventListener('click',function(ev){
  var b=ev.target.closest('button');if(!b)return;cur=b.getAttribute('data-p');
  document.querySelectorAll('#tabs button').forEach(function(x){x.classList.toggle('on',x===b)});
  document.querySelectorAll('.pane').forEach(function(p){p.classList.toggle('on',p.id==='p-'+cur)});
  refilter();
});
cf.addEventListener("input",refilter);

// Hear in the device's voice for that accent
function voiceFor(lang){
  var vs=window.speechSynthesis?speechSynthesis.getVoices():[];
  var want=lang.toLowerCase();
  return vs.filter(function(v){return v.lang.replace('_','-').toLowerCase()===want})[0]||null;
}
if(window.speechSynthesis)speechSynthesis.onvoiceschanged=function(){};
document.addEventListener('click',function(ev){
  var b=ev.target.closest('.hear');if(!b||!window.speechSynthesis)return;
  var u=new SpeechSynthesisUtterance(b.getAttribute('data-say'));
  var lang=b.getAttribute('data-lang');u.lang=lang;var v=voiceFor(lang);if(v)u.voice=v;u.rate=.9;
  speechSynthesis.cancel();speechSynthesis.speak(u);
});

// Quiz: show the US word, pick the Aussie one
var qi=0,score=0,asked=0,order=QUIZ.slice().sort(function(){return Math.random()-.5});
function shuffle(a){return a.slice().sort(function(){return Math.random()-.5})}
function ask(){
  if(qi>=order.length){order=shuffle(QUIZ);qi=0}
  var q=order[qi++],wrong=shuffle(QUIZ.filter(function(x){return x.au!==q.au})).slice(0,2);
  var opts=shuffle([q].concat(wrong));
  document.getElementById('qq').textContent='What do Aussies usually say for “'+q.us+'”?';
  var box=document.getElementById('opts');box.innerHTML='';
  opts.forEach(function(o){
    var b=document.createElement('button');b.type='button';b.textContent=o.au;
    b.onclick=function(){
      asked++;var right=o.au===q.au;if(right)score++;
      Array.prototype.forEach.call(box.children,function(c){c.disabled=true;if(c.textContent===q.au)c.classList.add('ok')});
      if(!right)b.classList.add('no');
      document.getElementById('qfb').textContent=right?'Yes! “'+q.au+'” is the Aussie word.':'Not quite. Aussies say “'+q.au+'”.';
      document.getElementById('qscore').textContent='Score: '+score+' / '+asked;
    };
    box.appendChild(b);
  });
  document.getElementById('qfb').textContent='';
}
document.getElementById('qnext').onclick=ask;ask();
</script>"""
page("aussie-vs-us", "Aussie vs US vs UK English: Vocabulary, Pronunciation & Spelling | English Down Under",
     "Compare Australian, American and British English: everyday vocabulary, pronunciation and spelling side by side, with audio and a quick quiz.",
     compare_body, nav_on="/tools/", head_extra=compare_css, script=compare_script,
     band=("Aussie vs US vs UK English", "The same language, different words. Compare vocabulary, pronunciation and spelling.", "Tools › Aussie vs US vs UK"))

# ───────────────────────── ABOUT ─────────────────────────
about_body = f"""<main class="wrap">
<div class="crumbs"><a href="/">Home</a> › About</div>
<h1>About English Down Under</h1>
<p class="lead">A free place to practise real Australian English, by speaking it out loud.</p>

<h2>What you'll find here</h2>
<div class="card"><ul style="margin:0;padding-left:20px">
<li><strong><a href="/lab/" style="color:var(--ocean)">Imitation Lab</a></strong>: a 20-minute daily speaking session with a practice streak.</li>
<li><strong><a href="/phrases/" style="color:var(--ocean)">Phrase Bank</a></strong>: phrases with pronunciation notes, common mistakes and speaking practice.</li>
<li><strong><a href="/guides/" style="color:var(--ocean)">Guides</a></strong>: English for cafés, job interviews, renting, small talk and phone calls.</li>
<li><strong><a href="/episodes/" style="color:var(--ocean)">Episodes</a></strong>: lessons with Sam and Leo, with matching practice exercises.</li>
<li><strong><a href="/aussie-vs-us/" style="color:var(--ocean)">Aussie vs US vs UK</a></strong>: vocabulary, pronunciation and spelling compared.</li>
</ul></div>

<h2>How the practice works</h2>
<p>The idea is simple: to speak better, you have to speak. Instead of only studying, you imitate. In each lesson you echo a short sentence, change a thought from "I" to "he", "she" or "they", and then summarise an idea in your own words. Each step builds the rhythm and habits of natural speech.</p>

<h2>Meet Sam and Leo</h2>
<p>Sam and Leo are our two coaches. They are AI hosts with AI-generated voices, and the audio on this site is a guide to rhythm and wording rather than a recording of a real person. The Imitation Lab's optional in-depth feedback uses an AI model from Anthropic, with your own API key.</p>

<h2>A note on accents</h2>
<p>Australian English varies by region, age and background. There is no single correct Australian accent, so treat what you hear here as one useful model. Listen to lots of real speakers as well.</p>

<h2>Who makes this</h2>
<p>English Down Under is made in Australia by Danni, who also runs the <a href="{YT}" style="text-decoration:underline">Down Under English (DUE) YouTube channel</a> and the slang dictionary <a href="https://fairdinkumslang.au" style="text-decoration:underline">Fair Dinkum</a>. The channel and this website share the same lessons and characters.</p>

<div class="card" style="margin-top:28px">
<strong>Spotted a mistake, or want something covered?</strong>
<p style="margin:6px 0 12px">Corrections and ideas are very welcome.</p>
<a class="btn" href="/contact/">Get in touch →</a>
</div>
{SISTER}
</main>"""
page("about", "About English Down Under | Practise Australian English",
     "English Down Under is a free place to practise Australian English by speaking it, with daily lessons, phrase audio and guides.",
     about_body)

# ───────────────────────── CONTACT ─────────────────────────
def mailto(subject):
    return f"mailto:{EMAIL}?subject={urllib.parse.quote(subject)}"

contact_body = f"""<main class="wrap">
<div class="crumbs"><a href="/">Home</a> › Contact</div>
<h1>Get in touch</h1>
<p class="lead">Questions, corrections or ideas? Send an email and put the topic in the subject line.</p>
<div class="grid g2">
<a class="card" href="{mailto('Feedback or correction')}"><div class="ico">✏️</div><h3>Feedback or a correction</h3><p>Found a mistake in a phrase, guide or lesson? Tell us which page and what to fix.</p></a>
<a class="card" href="{mailto('Suggestion for a lesson or phrase')}"><div class="ico">💡</div><h3>Suggest a lesson or phrase</h3><p>Is there a situation or phrase you'd like covered?</p></a>
<a class="card" href="{mailto('Business or partnership enquiry')}"><div class="ico">🤝</div><h3>Business &amp; partnerships</h3><p>Collaborations, schools and teachers, or other business enquiries.</p></a>
<a class="card" href="{mailto('Question about a purchase')}"><div class="ico">🛒</div><h3>A question about a purchase</h3><p>Digital products are sold through Gumroad. Include the email you used to buy.</p></a>
</div>
<div class="card" style="margin-top:18px">
<strong>Email:</strong> <a href="mailto:{EMAIL}" style="color:var(--ocean);text-decoration:underline">{EMAIL}</a>
</div>
<h2>Elsewhere</h2>
<div class="related">
<a href="{YT}">📺 Down Under English on YouTube</a>
<a href="https://fairdinkumslang.au/submit-a-word">🦘 Submit a slang word (Fair Dinkum)</a>
</div>
</main>"""
page("contact", "Contact | English Down Under",
     "Contact English Down Under for feedback, corrections, lesson ideas or business enquiries.", contact_body)

# ───────────────────────── PRIVACY ─────────────────────────
privacy_body = f"""<main class="wrap">
<div class="crumbs"><a href="/">Home</a> › Privacy</div>
<h1>Privacy Policy</h1>
<p class="lead">Last updated: {cfg["policy_updated"]}</p>
<p>English Down Under (englishdownunder.au) is run by Danni, an Australian sole trader. This page explains in plain English what information the site handles. If you have questions, email <a href="mailto:{EMAIL}" style="text-decoration:underline">{EMAIL}</a>.</p>

<h2>What stays on your device</h2>
<p>The Imitation Lab saves your practice streak and the date of your last visit in your browser's local storage. This information stays on your device. We don't receive it. You can remove it at any time by clearing this site's data in your browser.</p>

<h2>Speech practice</h2>
<p>When you press a 🎙️ button, your browser's built-in speech recognition listens and turns your speech into text. In browsers such as Chrome and Edge, your audio may be sent to the browser maker's speech service (for example Google or Microsoft) to do this. We don't receive, record or store your audio or what you said.</p>

<h2>Optional AI feedback</h2>
<p>The Imitation Lab can give in-depth feedback if you choose to enter your own Anthropic API key in the settings. If you do, your key is kept in your browser for the current tab session only. When you ask for feedback, the sentence you practised and your response are sent directly from your browser to Anthropic. They do not pass through our servers, and we don't see them or your key. Anthropic's own <a href="https://www.anthropic.com/legal/privacy" style="text-decoration:underline">privacy policy</a> applies to that request. This feature is optional, and the rest of the Lab works without it.</p>

<h2>Email list</h2>
<p>If you sign up for emails, such as a phrase of the day, we collect your email address so we can send them. Each email has an unsubscribe link, and you can also ask us to delete your address at any time. Your address is stored by the email service we use to send the emails. We don't sell your email address.</p>

<h2>Messages you send us</h2>
<p>If you email us, we use your email address and message only to reply and to keep a record of the conversation.</p>

<h2>Cookies, analytics and ads</h2>
<p>This site does not currently run advertising or analytics. If we add them in future (for example Google AdSense or an analytics tool), we will update this page first and add any consent notice that is required. Embedded YouTube videos use the privacy-enhanced youtube-nocookie.com address, but YouTube may still store information on your device after you press play.</p>

<h2>Other services involved</h2>
<ul>
<li><strong>Hosting:</strong> the site is hosted on GitHub Pages. Like most web hosts, GitHub receives your IP address and browser details when you load a page.</li>
<li><strong>Fonts:</strong> the site loads fonts from Google Fonts, so Google receives your IP address when a page loads.</li>
<li><strong>YouTube:</strong> videos are played by YouTube, which has its own privacy policy.</li>
<li><strong>Gumroad:</strong> digital products are sold through Gumroad. Payments and purchase details are handled by Gumroad, and we don't see your card details.</li>
</ul>

<h2>Children</h2>
<p>Learners of all ages are welcome, but we don't knowingly collect personal information from children. Children should ask a parent or guardian before giving an email address.</p>

<h2>Your choices</h2>
<p>You can ask us what we hold about you, ask for it to be corrected or deleted, or unsubscribe from emails at any time by contacting <a href="mailto:{EMAIL}" style="text-decoration:underline">{EMAIL}</a>.</p>

<h2>Changes to this policy</h2>
<p>If we change how the site handles information, we'll update this page and the date at the top.</p>
</main>"""
page("privacy", "Privacy Policy | English Down Under",
     "How English Down Under handles your information: what stays on your device, speech practice, optional AI feedback and email sign-ups.",
     privacy_body)

if not cfg.get("contact_email_confirmed"):
    print(f"WARNING: contact email is still the placeholder '{EMAIL}'. Set it in data/site.json and set contact_email_confirmed to true.")
print("Built tools hub, Aussie vs US page, About, Contact, Privacy")
