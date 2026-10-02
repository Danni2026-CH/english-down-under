#!/usr/bin/env python3
"""Build the tools hub, the Aussie vs US vs UK comparison page, and About / Contact / Privacy.

Usage:  python3 build_pages.py
Reads   data/site.json, data/compare.json
Writes  tools/, aussie-vs-us/, about/, contact/, privacy/  (each as <folder>/index.html)
"""
import html, json, pathlib, urllib.parse
from common import *

compare = json.loads((ROOT / "data" / "compare.json").read_text(encoding="utf-8"))

# ───────────────────────── TOOLS HUB ─────────────────────────
def tool_card(icon, name, text, href, tag, external=False, soon=False):
    t = f'<span class="pill{" gold" if soon else ""}">{tag}</span>'
    inner = f'<div class="ico">{icon}</div><h3>{name}</h3><p>{text}</p><p style="margin-top:12px">{t}</p>'
    if soon:
        return f'<div class="card soon">{inner}</div>'
    return f'<a class="card" href="{href}"{" rel=noopener" if external else ""}>{inner}</a>'

live = "".join([
    tool_card("🎙️", "Imitation Lab", "A 20-minute daily session: echo Sam, shift perspective with Leo, then summarise. Includes a practice streak.", "/lab/", "Speaking"),
    tool_card("🎯", "Accent Checker", "Say a phrase and see which words come through clearly, with pace feedback.", "/accent-checker/", "Speaking"),
    tool_card("✨", "Aussie-fy My Sentence", "Paste a sentence and see it in Australian English, with every change explained.", "/aussie-fy/", "Convert"),
    tool_card("🦘", "Daily Accent Puzzle", "Five quick questions a day. Spot the Aussie way to say, name and spell things.", "/accent-puzzle/", "Daily game"),
    tool_card("🌏", "Aussie vs US vs UK", "Vocabulary, pronunciation and spelling side by side, with a quick quiz.", "/aussie-vs-us/", "Compare"),
    tool_card("📖", "Phrase Bank", "Phrases with audio, pronunciation notes, common mistakes and speaking practice.", "/phrases/", "Browse"),
    tool_card("🧩", "Which Aussie Are You?", "Eight quick questions. Find out which kind of Aussie your English sounds like.", "/which-aussie-are-you/", "Quiz"),
    tool_card("🏆", "Streak & Score Cards", "Turn your streak, puzzle score or quiz result into a shareable card.", "/score-card/", "Share"),
    tool_card("🧭", "Situation Guides", "Cafés, job interviews, renting, small talk, phone calls, rhythm and vowels.", "/guides/", "Guides"),
])
fd = "".join([
    tool_card("🦘", "Slangle", "One slang word a day. Six guesses.", "https://fairdinkumslang.au/slangle", "Fair Dinkum ↗", external=True),
    tool_card("🧩", "Slang Connections", "Find the four hidden groups of slang.", "https://fairdinkumslang.au/slang-connections", "Fair Dinkum ↗", external=True),
    tool_card("🗣️", "Slang Translator", "Paste a sentence and decode the slang.", "https://fairdinkumslang.au/slang-translator", "Fair Dinkum ↗", external=True),
])
soon = ""
tools_body = f"""<main class="wrap wide" style="max-width:1100px">
<h2>Ready to use</h2>
<div class="grid g3">{live}</div>
<h2>More from Fair Dinkum</h2>
<p style="color:var(--muted);margin:0 0 12px">Our sister site has games and tools for Aussie slang.</p>
<div class="grid g3">{fd}</div>
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

# ───────────────────────── ACCENT CHECKER ─────────────────────────
phrases_data = json.loads((ROOT / "data" / "phrases.json").read_text(encoding="utf-8"))
ac_items = []
for ph in phrases_data:
    ac_items.append({"text": ph["phrase"], "group": ph["category"], "respell": ph["respell"], "tip": ph["tip"], "slug": ph["slug"]})
for ph in phrases_data:
    for ex in ph["examples"]:
        ac_items.append({"text": ex, "group": "Sentences: " + ph["category"], "respell": "", "tip": ph["tip"], "slug": ph["slug"]})
groups = []
for i, it in enumerate(ac_items):
    if it["group"] not in groups:
        groups.append(it["group"])
ac_options = ""
for g in groups:
    ac_options += f'<optgroup label="{e(g, quote=True)}">'
    for i, it in enumerate(ac_items):
        if it["group"] == g:
            ac_options += f'<option value="{i}">{e(it["text"])}</option>'
    ac_options += "</optgroup>"
ac_json = json.dumps(ac_items, ensure_ascii=False).replace("</", "<\\/")

ac_css = """<style>
.target{font-family:Fraunces,Georgia,serif;font-size:clamp(1.6rem,5vw,2.4rem);color:var(--ocean-dark);font-weight:800;line-height:1.2}
#sel{width:100%;padding:13px 14px;border:1px solid var(--line);border-radius:12px;font:inherit;font-size:1rem;background:#fff}
.mic{width:88px;height:88px;border-radius:50%;font-size:2rem;background:var(--gold);border:0;cursor:pointer;box-shadow:0 6px 16px rgba(18,56,82,.18)}
.mic:disabled{opacity:.5;cursor:not-allowed}
.mic.rec{background:#E85D5D;animation:pulse 1s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(232,93,93,.5)}100%{box-shadow:0 0 0 18px rgba(232,93,93,0)}}
.w{display:inline-block;margin:3px;padding:6px 11px;border-radius:10px;font-weight:600}
.w.ok{background:#E6F6EA;color:#1E7A41}.w.no{background:#FDECEC;color:#B53030}
.stats3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:16px 0}
.stat{background:var(--ocean-soft);border-radius:12px;padding:12px 8px;text-align:center}
.stat b{display:block;font-family:Fraunces,serif;font-size:1.5rem;color:var(--ocean-dark)}
.stat small{color:var(--muted);font-size:.78rem}
#result{display:none}
.hist{margin:0;padding-left:20px;color:var(--muted)}
</style>"""

ac_body = f"""<main class="wrap">
<h2 style="margin-top:28px">1. Choose something to say</h2>
<div class="card">
<label for="sel" style="font-weight:600;display:block;margin-bottom:6px">Phrase or sentence</label>
<select id="sel">{ac_options}</select>
<div class="row" style="margin-top:10px"><button class="btn ghost sm" id="rand" type="button">🎲 Random</button></div>
</div>

<div class="card" style="margin-top:14px">
<div class="target" id="target"></div>
<div style="color:var(--muted);font-style:italic;margin:6px 0 12px;min-height:1.4em" id="respell"></div>
<div class="row"><button class="btn" id="hear" type="button">🔊 Hear it (Aussie)</button><button class="btn ghost" id="slow" type="button">🐢 Slow</button></div>
<div class="tipbox" id="tipbox"><strong>Try this:</strong> <span id="tip"></span></div>
</div>

<h2>2. Say it out loud</h2>
<div class="card" style="text-align:center">
<button class="mic" id="mic" type="button" aria-label="Start listening">🎙️</button>
<div id="status" style="margin-top:10px;color:var(--muted)" aria-live="polite">Press the mic, then say the phrase.</div>
</div>

<div id="result" class="card" style="margin-top:14px" aria-live="polite">
<div id="chips"></div>
<div style="color:var(--muted);margin-top:8px">We heard: <em id="heard"></em></div>
<div class="stats3">
<div class="stat"><b id="s-match">–</b><small>Words matched</small></div>
<div class="stat"><b id="s-conf">–</b><small>Recogniser confidence</small></div>
<div class="stat"><b id="s-pace">–</b><small>Pace</small></div>
</div>
<div id="verdict" style="font-weight:600;color:var(--ocean-dark)"></div>
<div id="pacenote" style="color:var(--muted);margin-top:4px"></div>
<div class="row" style="margin-top:14px"><button class="btn gold" id="again" type="button">Try again</button><a class="btn ghost" id="plink" href="/phrases/">About this phrase →</a></div>
</div>

<div class="card" id="histbox" style="margin-top:14px;display:none"><strong>This session</strong><ol class="hist" id="hist"></ol></div>

<h2>What this tool does (and doesn't)</h2>
<div class="card">
<p style="margin-top:0">Your browser's speech recogniser listens in <strong>Australian English</strong> and turns your voice into text. We then compare that text with the phrase, word by word. If the right words come through, you were clear. This is a useful practice guide, but it does <strong>not</strong> judge how Australian your accent sounds. For that, listen carefully to real speakers and compare.</p>
<p>Casual sounds can be written differently: "ya" is treated as "you", but other informal forms may be spelled differently by the recogniser. Your voice goes to your browser's speech service, not to us. See the <a href="/privacy/" style="text-decoration:underline">privacy policy</a>. This works in Chrome, Edge and Safari.</p>
<a class="btn ghost" href="/lab/">Do the full 20-minute lesson →</a>
</div>
{SISTER}
</main>"""

ac_script = r"""<script>
var ITEMS=""" + ac_json + r""";
var cur=ITEMS[0],sel=document.getElementById('sel');

// ---- text analysis (kept as plain functions so it can be tested) ----
function norm(s){
  return s.toLowerCase().replace(/['’]/g,'').replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim();
}
function words(s){
  var n=norm(s);if(!n)return [];
  var t=n.split(' ').map(function(w){return w==='ya'?'you':w}),out=[],i;
  for(i=0;i<t.length;i++){          // recognisers often write "g'day" as "good day"
    if(t[i]==='good'&&t[i+1]==='day'){out.push('gday');i++}else out.push(t[i]);
  }
  return out;
}
function matchInOrder(t,h){            // longest common subsequence -> which target words were heard, in order
  var m=t.length,n=h.length,dp=[],i,j;
  for(i=0;i<=m;i++){dp.push(new Array(n+1).fill(0))}
  for(i=1;i<=m;i++)for(j=1;j<=n;j++)
    dp[i][j]=t[i-1]===h[j-1]?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]);
  var ok=new Array(m).fill(false);i=m;j=n;
  while(i>0&&j>0){
    if(t[i-1]===h[j-1]){ok[i-1]=true;i--;j--}
    else if(dp[i-1][j]>=dp[i][j-1])i--;else j--;
  }
  return ok;
}
function analyse(target,heard,conf,secs){
  var t=words(target),h=words(heard),ok=matchInOrder(t,h);
  var hit=ok.filter(Boolean).length;
  return {
    words:t,ok:ok,hit:hit,pct:t.length?Math.round(hit/t.length*100):0,
    heard:heard,conf:(conf>0?Math.round(conf*100):null),
    wps:(secs>0&&h.length>=4)?h.length/secs:null
  };
}

// ---- show a phrase ----
function show(i){
  cur=ITEMS[i];sel.value=i;
  document.getElementById('target').textContent=cur.text;
  document.getElementById('respell').textContent=cur.respell?'Say it: “'+cur.respell+'”':'';
  document.getElementById('tip').textContent=cur.tip||'';
  document.getElementById('tipbox').style.display=cur.tip?'':'none';
  document.getElementById('plink').href='/phrases/'+cur.slug+'/';
  document.getElementById('result').style.display='none';
  document.getElementById('status').textContent='Press the mic, then say the phrase.';
}
sel.onchange=function(){show(+sel.value)};
document.getElementById('rand').onclick=function(){show(Math.floor(Math.random()*ITEMS.length))};
document.getElementById('again').onclick=function(){document.getElementById('result').style.display='none';window.scrollTo({top:0,behavior:'smooth'})};

// ---- hear it ----
function voiceFor(lang){
  var vs=window.speechSynthesis?speechSynthesis.getVoices():[];
  return vs.filter(function(v){return v.lang.replace('_','-').toLowerCase()===lang.toLowerCase()})[0]||null;
}
function say(rate){
  if(!window.speechSynthesis)return;
  var u=new SpeechSynthesisUtterance(cur.text);u.lang='en-AU';var v=voiceFor('en-AU');if(v)u.voice=v;u.rate=rate;
  speechSynthesis.cancel();speechSynthesis.speak(u);
}
document.getElementById('hear').onclick=function(){say(.95)};
document.getElementById('slow').onclick=function(){say(.6)};

// ---- listen ----
var SR=window.SpeechRecognition||window.webkitSpeechRecognition,rec=null,t0=0,t1=0;
var mic=document.getElementById('mic'),statusEl=document.getElementById('status'),hist=[];
if(!SR){mic.disabled=true;statusEl.textContent="Speech recognition isn't available in this browser. Try Chrome, Edge or Safari."}

function render(a){
  var chips=document.getElementById('chips');chips.innerHTML='';
  a.words.forEach(function(w,i){
    var s=document.createElement('span');s.className='w '+(a.ok[i]?'ok':'no');s.textContent=(a.ok[i]?'✓ ':'✗ ')+w;chips.appendChild(s);
  });
  document.getElementById('heard').textContent='“'+a.heard+'”';
  document.getElementById('s-match').textContent=a.pct+'%';
  document.getElementById('s-conf').textContent=a.conf===null?'–':a.conf+'%';
  document.getElementById('s-pace').textContent=a.wps===null?'–':a.wps.toFixed(1)+'/s';
  var v=a.pct>=90?'Excellent! Clear and complete. 🎉':a.pct>=70?'Good. Most of your words came through.':a.pct>=40?'Getting there. Try again a little more slowly.':"Let's try again. Check your mic and speak a bit louder.";
  document.getElementById('verdict').textContent=v;
  var pn='';
  if(a.wps!==null){pn=a.wps<1.5?'Your pace was a little slow. Natural conversation is about 2 to 3 words per second, so try linking the words.':a.wps>4?'Your pace was quite fast. Slow down slightly so every word is clear.':'Your pace is in a natural range.'}
  document.getElementById('pacenote').textContent=pn;
  document.getElementById('result').style.display='block';
  document.getElementById('result').scrollIntoView({behavior:'smooth',block:'nearest'});
  hist.unshift(cur.text+' — '+a.pct+'%');hist=hist.slice(0,5);
  var ol=document.getElementById('hist');ol.innerHTML='';
  hist.forEach(function(x){var li=document.createElement('li');li.textContent=x;ol.appendChild(li)});
  document.getElementById('histbox').style.display='block';
}

mic.onclick=function(){
  if(!SR)return;
  if(rec){rec.stop();return}
  rec=new SR();rec.lang='en-AU';rec.interimResults=false;rec.maxAlternatives=1;rec.continuous=false;
  t0=0;t1=0;
  rec.onstart=function(){mic.classList.add('rec');statusEl.textContent='Listening… say it now.'};
  rec.onspeechstart=function(){t0=Date.now()};
  rec.onspeechend=function(){t1=Date.now()};
  rec.onresult=function(e){
    var r=e.results[0][0],secs=(t0&&t1&&t1>t0)?(t1-t0)/1000:0;
    statusEl.textContent='Done. See your result below.';
    render(analyse(cur.text,r.transcript,r.confidence,secs));
  };
  rec.onerror=function(e){
    statusEl.textContent=e.error==='not-allowed'?'The microphone is blocked. Allow it for this site and try again.':
      e.error==='no-speech'?"We didn't hear anything. Check your mic and try again.":
      'Something went wrong ('+e.error+'). Please try again.';
  };
  rec.onend=function(){mic.classList.remove('rec');rec=null;if(statusEl.textContent.indexOf('Listening')===0)statusEl.textContent='Press the mic and try again.'};
  rec.start();
};
show(0);
</script>"""

page("accent-checker", "Accent Checker: Practise Speaking Australian English | English Down Under",
     "Say a phrase out loud and see which words come through clearly. Free speaking practice with an Australian English speech model.",
     ac_body, nav_on="/tools/", head_extra=ac_css, script=ac_script,
     band=("Accent Checker", "Say a phrase out loud and see how clearly it comes through.", "Tools › Accent Checker"))

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
<p>The Imitation Lab saves your practice streak and the date of your last visit, and the Daily Accent Puzzle saves your results and streak, and Which Aussie Are You? saves your latest result, in your browser's local storage. This information stays on your device. We don't receive it. You can remove it at any time by clearing this site's data in your browser.</p>

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
