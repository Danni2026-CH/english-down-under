#!/usr/bin/env python3
"""Build the Aussie-fy My Sentence tool and the Daily Accent Puzzle.

Usage:  python3 build_tools.py
Reads   data/aussiefy.json, data/compare.json
Writes  aussie-fy/index.html, accent-puzzle/index.html
"""
import json
from common import *

def js_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

# ═════════════════════════ AUSSIE-FY MY SENTENCE ═════════════════════════
rules = json.loads((ROOT / "data" / "aussiefy.json").read_text(encoding="utf-8"))

af_css = """<style>
#src{width:100%;min-height:130px;padding:14px;border:1px solid var(--line);border-radius:12px;font:inherit;font-size:1.02rem;resize:vertical;background:#fff}
#src:focus{outline:none;border-color:var(--ocean);box-shadow:0 0 0 3px var(--ocean-soft)}
.opt{display:flex;gap:8px;align-items:flex-start;padding:10px 12px;border:1px solid var(--line);border-radius:12px;background:#fff;cursor:pointer;flex:1;min-width:210px}
.opt input{margin-top:4px;accent-color:var(--ocean)}
.opt b{display:block;color:var(--ocean-dark)}
.opt small{color:var(--muted)}
.out{font-size:1.15rem;line-height:1.7;background:var(--ocean-soft);border-radius:12px;padding:16px;min-height:90px;word-wrap:break-word}
.out mark{background:var(--gold);color:var(--ink);border-radius:5px;padding:1px 5px;font-weight:600}
.chg{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.chg li{padding:10px 12px;border:1px solid var(--line);border-radius:12px;background:#fff}
.chg s{color:var(--muted)}
.chg .arrow{margin:0 6px;color:var(--ocean)}
.chg .n{display:block;color:var(--muted);font-size:.88rem;margin-top:2px}
.chg .w{display:block;color:#9A6B00;font-size:.88rem;margin-top:2px}
.ex{display:flex;gap:8px;flex-wrap:wrap}
.ex button{font:inherit;font-size:.88rem;background:#fff;border:1.5px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer;color:var(--ocean-dark);text-align:left}
.ex button:hover{border-color:var(--ocean)}
</style>"""

af_body = f"""<main class="wrap">
<h2 style="margin-top:28px">1. Paste your sentence</h2>
<div class="card">
<textarea id="src" maxlength="1500" placeholder="Type or paste some English here…" aria-label="Sentence to convert"></textarea>
<div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:6px;color:var(--muted);font-size:.85rem"><span>Try an example:</span><span id="count">0 / 1500</span></div>
<div class="ex" style="margin-top:6px">
<button type="button" data-ex="I'm going to put my sweater in the trunk and drive to the gas station to get a soda.">🚗 Road trip</button>
<button type="button" data-ex="My mom organized a barbecue for the afternoon, so I bought candy and sunglasses at the drugstore.">🍖 Barbecue</button>
<button type="button" data-ex="Hello! Thank you for the ride. I think a lot of people take the elevator to the movie theater.">👋 Greetings</button>
</div>
</div>

<h2>2. Choose what to change</h2>
<div class="row" style="gap:10px">
<label class="opt"><input type="checkbox" id="o-spelling" checked><span><b>Spelling</b><small>color → colour, organize → organise</small></span></label>
<label class="opt"><input type="checkbox" id="o-words" checked><span><b>Everyday words</b><small>sweater → jumper, trunk → boot</small></span></label>
<label class="opt"><input type="checkbox" id="o-slang"><span><b>Casual slang</b><small>afternoon → arvo, hello → g'day</small></span></label>
</div>

<h2>3. Your Aussie version</h2>
<div class="card">
<div class="out" id="out" aria-live="polite"><span style="color:var(--muted)">Your converted sentence will appear here.</span></div>
<div class="row" style="margin-top:12px">
<button class="btn" id="copy" type="button">📋 Copy</button>
<button class="btn ghost" id="hear" type="button">🔊 Hear it (Aussie)</button>
</div>
<div id="summary" style="margin-top:12px;color:var(--muted)"></div>
</div>

<div id="changes-wrap" style="display:none">
<h2>What changed</h2>
<ul class="chg" id="changes"></ul>
</div>

<h2>How it works</h2>
<div class="card">
<p style="margin-top:0">This tool swaps words and spellings using a list of Australian equivalents. It works best on American English, because British spelling and vocabulary are already close to Australian. It <strong>can't</strong> change grammar or tone, and it can't tell what a word means in context. Words marked ⚠ may not fit your sentence, so always read the result.</p>
<p style="margin-bottom:0"><strong>Casual slang</strong> is informal. Not every Australian uses these words, and they don't suit formal writing. Want the full story on a slang word? Look it up on <a href="https://fairdinkumslang.au" style="text-decoration:underline">Fair Dinkum</a>.</p>
</div>
{SISTER}
</main>"""

af_script = r"""<script>
var DATA=""" + js_json(rules) + r""";
function escRe(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}
function matchCase(src,to){
  if(src.length>1&&src===src.toUpperCase()&&/[A-Z]/.test(src))return to.toUpperCase();
  if(/^[A-Z]/.test(src))return to.charAt(0).toUpperCase()+to.slice(1);
  return to;
}
function pickArticle(w){
  var f=w.toLowerCase();
  if(/^(hour|honest|heir)/.test(f))return 'an';
  if(/^(uni|ute|use|usual|one)/.test(f))return 'a';
  return /^[aeiou]/.test(f)?'an':'a';
}
function compile(list,kind){
  return list.map(function(r){
    var froms=[].concat(r.from);
    var len=Math.max.apply(null,froms.map(function(f){return f.length}));
    var re=new RegExp('\\b(?:(a|an)\\s+)?('+froms.map(escRe).join('|')+')'+(r.pl?'(s)?':'()')+'\\b','gi');
    return {re:re,to:r.to,note:r.note,warn:r.warn,kind:kind,len:len,stem:false};
  });
}
function compileStems(list){
  return list.map(function(r){
    return {re:new RegExp('\\b'+escRe(r.stem)+'('+r.suf+')?\\b','gi'),to:r.to,kind:'spelling',len:r.stem.length+4,stem:true};
  });
}
function decode(s){return s.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&')}

// Pure function so it can be tested: returns {html, plain, changes}
function aussify(text,opts){
  var s=text.replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,'').replace(/[‘’]/g,"'");
  s=s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  var rules=[];
  if(opts.slang)rules=rules.concat(compile(DATA.casual,'slang'));
  if(opts.words)rules=rules.concat(compile(DATA.words,'word'));
  if(opts.spelling)rules=rules.concat(compileStems(DATA.spelling)).concat(compile(DATA.spelling_words,'spelling'));
  rules.sort(function(a,b){return b.len-a.len});      // longest phrase first; stable, so slang wins ties
  var changes=[],keeps=[];
  if((opts.words||opts.slang)&&DATA.keep&&DATA.keep.length){   // fixed expressions that must stay as written
    rules.unshift({keep:true,re:new RegExp('\\b(?:'+DATA.keep.map(escRe).join('|')+')\\b','gi')});
  }
  rules.forEach(function(r){
    r.re.lastIndex=0;
    s=s.replace(r.re,function(){
      var a=arguments,from,to;
      if(r.keep){return '\u0003'+(keeps.push(a[0])-1)+'\u0004'}
      if(r.stem){
        from=a[0];to=matchCase(from,r.to+(a[1]||''));
      }else{
        var art=a[1],term=a[2],pls=a[3]||'';
        to=matchCase(term,r.to+pls);
        from=(art?art+' ':'')+term+pls;
        if(art){to=matchCase(art,pickArticle(to))+' '+to}
      }
      if(from===to)return a[0];
      var n=changes.push({from:from,to:to,note:r.note,warn:r.warn,kind:r.kind})-1;
      return '\u0001'+n+'\u0002';
    });
  });
  var restore=function(x){return x.replace(/\u0003(\d+)\u0004/g,function(m,i){return keeps[i]})};
  var htmlOut=restore(s.replace(/\u0001(\d+)\u0002/g,function(m,i){return '<mark>'+changes[i].to+'</mark>'})).replace(/\n/g,'<br>');
  var plain=decode(restore(s.replace(/\u0001(\d+)\u0002/g,function(m,i){return changes[i].to})));
  var seen={},uniq=[];
  changes.forEach(function(c){var k=c.from.toLowerCase()+'>'+c.to.toLowerCase();if(!seen[k]){seen[k]=1;uniq.push(c)}});
  return {html:htmlOut,plain:plain,changes:uniq,total:changes.length};
}

// ---- page wiring ----
var src=document.getElementById('src'),out=document.getElementById('out'),last='';
function opts(){return {spelling:document.getElementById('o-spelling').checked,words:document.getElementById('o-words').checked,slang:document.getElementById('o-slang').checked}}
function update(){
  var t=src.value;
  document.getElementById('count').textContent=t.length+' / 1500';
  var cw=document.getElementById('changes-wrap'),ul=document.getElementById('changes'),sm=document.getElementById('summary');
  if(!t.trim()){out.innerHTML='<span style="color:var(--muted)">Your converted sentence will appear here.</span>';last='';cw.style.display='none';sm.textContent='';return}
  var r=aussify(t,opts());last=r.plain;out.innerHTML=r.html;
  if(!r.total){
    sm.textContent='Nothing to change. This may already sound Australian, or our word list doesn\'t cover it yet.';cw.style.display='none';return;
  }
  sm.textContent=r.total+(r.total===1?' change made.':' changes made.');
  ul.innerHTML='';
  r.changes.forEach(function(c){
    var li=document.createElement('li');
    li.innerHTML='<s></s><span class="arrow">→</span><strong></strong>';
    li.querySelector('s').textContent=c.from;li.querySelector('strong').textContent=c.to;
    if(c.note){var n=document.createElement('span');n.className='n';n.textContent=c.note;li.appendChild(n)}
    if(c.warn){var w=document.createElement('span');w.className='w';w.textContent='⚠ '+c.warn;li.appendChild(w)}
    ul.appendChild(li);
  });
  cw.style.display='block';
}
src.addEventListener('input',update);
['o-spelling','o-words','o-slang'].forEach(function(id){document.getElementById(id).addEventListener('change',update)});
document.querySelectorAll('[data-ex]').forEach(function(b){b.onclick=function(){src.value=b.getAttribute('data-ex');update()}});
document.getElementById('copy').onclick=function(){
  if(!last)return;var btn=this;
  function done(){btn.textContent='✅ Copied';setTimeout(function(){btn.textContent='📋 Copy'},1500)}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(last).then(done,function(){})}
  else{var ta=document.createElement('textarea');ta.value=last;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done()}catch(e){}document.body.removeChild(ta)}
};
document.getElementById('hear').onclick=function(){
  if(!last||!window.speechSynthesis)return;
  var u=new SpeechSynthesisUtterance(last);u.lang='en-AU';
  var v=speechSynthesis.getVoices().filter(function(x){return x.lang.replace('_','-').toLowerCase()==='en-au'})[0];if(v)u.voice=v;u.rate=.92;
  speechSynthesis.cancel();speechSynthesis.speak(u);
};
update();
</script>"""

page("aussie-fy", "Aussie-fy My Sentence: Convert English to Australian | English Down Under",
     "Paste a sentence and see it in Australian English: spelling, everyday words and casual slang, with a list of every change.",
     af_body, nav_on="/tools/", head_extra=af_css, script=af_script,
     band=("Aussie-fy My Sentence", "Paste a sentence and turn it into Australian English, with every change explained.", "Tools › Aussie-fy My Sentence"))

# ═════════════════════════ DAILY ACCENT PUZZLE ═════════════════════════
cmp_ = json.loads((ROOT / "data" / "compare.json").read_text(encoding="utf-8"))
pz_pron = [{"word": x["word"], "au": x["au"], "us": x["us"], "note": x.get("note", "")}
           for x in cmp_["pron"] if x["au"].lower() != x["us"].lower()]
pz_vocab = [{"concept": x["concept"], "au": x["au"], "us": x["us"], "note": x.get("note", "")}
            for x in cmp_["vocab"] if x["au"].lower() != x["us"].lower()]
pz_spell = [{"au": x["au"], "us": x["us"], "note": x.get("note", "")}
            for x in cmp_["spell"] if "(" not in x["au"] and "(" not in x["us"] and x["au"].lower() != x["us"].lower()]

pz_css = """<style>
.pbar{height:8px;background:var(--ocean-soft);border-radius:999px;overflow:hidden;margin:6px 0 16px}
.pbar i{display:block;height:100%;background:var(--gold);width:0;transition:width .3s}
.qtext{font-family:Fraunces,Georgia,serif;font-size:clamp(1.25rem,4vw,1.6rem);color:var(--ocean-dark);font-weight:800;line-height:1.25}
.popts{display:grid;gap:10px;margin:16px 0}
.popts button{font:inherit;font-size:1.05rem;font-weight:600;text-align:left;background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:14px 16px;cursor:pointer;color:var(--ink)}
.popts button:hover:not(:disabled){border-color:var(--ocean)}
.popts button.ok{background:#E6F6EA;border-color:#2E9E55}
.popts button.no{background:#FDECEC;border-color:#D64545}
.popts button:disabled{cursor:default}
#fb{min-height:1.5em;color:var(--ink)}
#fb .why{display:block;color:var(--muted);margin-top:4px;font-size:.95rem}
.emoji{font-size:2rem;letter-spacing:4px;margin:8px 0}
.big{font-family:Fraunces,serif;font-size:3rem;font-weight:800;color:var(--ocean-dark);line-height:1}
.pill-row{display:flex;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:.9rem}
</style>"""

pz_body = f"""<main class="wrap">
<div class="pill-row" style="margin-top:22px"><span class="pill gold" id="when"></span><span id="streakline"></span></div>
<noscript><div class="card" style="margin-top:14px">This puzzle needs JavaScript. Please turn it on and reload.</div></noscript>

<div class="card" id="game" style="margin-top:12px">
<div style="display:flex;justify-content:space-between;color:var(--muted);font-size:.9rem"><span id="prog"></span><span id="mode"></span></div>
<div class="pbar"><i id="bar"></i></div>
<div class="qtext" id="qtext"></div>
<div class="row" style="margin-top:10px"><button class="btn ghost sm" id="hear" type="button" style="display:none">🔊 Hear the word</button></div>
<div class="popts" id="opts"></div>
<div id="fb" aria-live="polite"></div>
<div class="row" style="margin-top:12px"><button class="btn gold" id="next" type="button" style="display:none">Next →</button></div>
</div>

<div class="card" id="end" style="margin-top:12px;display:none;text-align:center">
<div style="color:var(--muted)" id="endwhen"></div>
<div class="big" id="score"></div>
<div class="emoji" id="emojis"></div>
<div id="endmsg" style="font-weight:600;color:var(--ocean-dark)"></div>
<div id="streakend" style="color:var(--muted);margin-top:4px"></div>
<div class="row" style="justify-content:center;margin-top:16px"><button class="btn" id="share" type="button">📋 Copy result to share</button><button class="btn ghost" id="more" type="button">Practise more</button></div>
<p style="color:var(--muted);font-size:.9rem;margin:14px 0 0">A new puzzle appears every day at midnight Sydney time.</p>
</div>

<h2>How it works</h2>
<div class="card">
<p style="margin-top:0">Five quick questions every day, the same for everyone: how Aussies say a word, which word they use, and how they spell it. Your streak counts the days in a row you finish the puzzle. Everything stays on your device.</p>
<p>The pronunciations are written out as sounds, with capitals showing the stressed part. Accents vary between speakers and regions, so treat the answers as the common Australian pronunciation, not the only one. For the full list, see <a href="/aussie-vs-us/" style="text-decoration:underline">Aussie vs US vs UK</a>.</p>
<a class="btn ghost" href="/accent-checker/">Practise saying them →</a>
</div>
{SISTER}
</main>"""

pz_script = r"""<script>
var PRON=""" + js_json(pz_pron) + r""", VOCAB=""" + js_json(pz_vocab) + r""", SPELL=""" + js_json(pz_spell) + r""";
var SITE='""" + SITE + r"""';

// ---- seeded randomness: everyone gets the same puzzle on the same Sydney date ----
function hash(s){var h=2166136261;for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function shuffle(arr,rnd){var a=arr.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(rnd()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a}
function sydneyDate(){
  try{return new Intl.DateTimeFormat('en-CA',{timeZone:'Australia/Sydney',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())}
  catch(e){return new Date().toISOString().slice(0,10)}
}
function dateLabel(){
  try{return new Intl.DateTimeFormat('en-AU',{timeZone:'Australia/Sydney',weekday:'short',day:'numeric',month:'short'}).format(new Date())}
  catch(e){return sydneyDate()}
}
function dayBefore(d){var t=new Date(d+'T00:00:00Z');t.setUTCDate(t.getUTCDate()-1);return t.toISOString().slice(0,10)}

function buildQuestions(seed){
  var rnd=mulberry32(hash(seed)),qs=[];
  shuffle(PRON,rnd).slice(0,2).forEach(function(w){
    qs.push({q:'Which is the Australian way to say “'+w.word+'”?',hear:w.word,
      opts:shuffle([{t:w.au,ok:true},{t:w.us,ok:false}],rnd),
      why:'Australians say “'+w.au+'”. Americans say “'+w.us+'”.'+(w.note?' '+w.note:'')});
  });
  shuffle(VOCAB,rnd).slice(0,2).forEach(function(v){
    var wrong=shuffle(VOCAB.filter(function(x){
      return x.au!==v.au&&x.au.indexOf(v.au)<0&&v.au.indexOf(x.au)<0;
    }),rnd).slice(0,2);
    qs.push({q:'What do Aussies usually say for “'+v.us+'”?',
      opts:shuffle([{t:v.au,ok:true}].concat(wrong.map(function(x){return {t:x.au,ok:false}})),rnd),
      why:'In Australia, “'+v.us+'” is “'+v.au+'”.'+(v.note?' '+v.note:'')});
  });
  shuffle(SPELL,rnd).slice(0,1).forEach(function(s){
    qs.push({q:'Which spelling would you use in Australia?',
      opts:shuffle([{t:s.au,ok:true},{t:s.us,ok:false}],rnd),
      why:'Australian spelling is “'+s.au+'”. American spelling is “'+s.us+'”.'+(s.note?' '+s.note:'')});
  });
  return shuffle(qs,rnd);
}

// ---- storage (always in try/catch: it can be blocked) ----
function load(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}

var today=sydneyDate(),qs=[],qi=0,results=[],daily=true,answered=false;
var $=function(id){return document.getElementById(id)};

function streakInfo(){var st=load('edu_puzzle_streak');return st&&st.count?st:{last:'',count:0}}
function showStreakLine(){var st=streakInfo();$('streakline').textContent=st.count?'🔥 '+st.count+'-day streak':''}

function startRound(seed,isDaily){
  qs=buildQuestions(seed);qi=0;results=[];daily=isDaily;
  $('end').style.display='none';$('game').style.display='block';
  $('mode').textContent=isDaily?'Daily puzzle':'Practice round (doesn\'t count)';
  showQ();
}
function showQ(){
  answered=false;var q=qs[qi];
  $('prog').textContent='Question '+(qi+1)+' of '+qs.length;
  $('bar').style.width=(qi/qs.length*100)+'%';
  $('qtext').textContent=q.q;$('fb').innerHTML='';$('next').style.display='none';
  $('hear').style.display=q.hear?'':'none';
  var box=$('opts');box.innerHTML='';
  q.opts.forEach(function(o){
    var b=document.createElement('button');b.type='button';b.textContent=o.t;
    b.onclick=function(){choose(b,o)};box.appendChild(b);
  });
}
function choose(btn,o){
  if(answered)return;answered=true;var q=qs[qi];
  results.push(o.ok?1:0);
  Array.prototype.forEach.call($('opts').children,function(c,i){c.disabled=true;if(q.opts[i].ok)c.classList.add('ok')});
  if(!o.ok)btn.classList.add('no');
  $('fb').innerHTML=(o.ok?'<strong>Yes!</strong> ':'<strong>Not quite.</strong> ')+'<span class="why"></span>';
  $('fb').querySelector('.why').textContent=q.why;
  $('next').textContent=qi===qs.length-1?'See my result →':'Next →';$('next').style.display='';
  $('bar').style.width=((qi+1)/qs.length*100)+'%';
}
$('next').onclick=function(){if(qi<qs.length-1){qi++;showQ()}else finish()};
$('hear').onclick=function(){
  if(!window.speechSynthesis)return;var u=new SpeechSynthesisUtterance(qs[qi].hear);u.lang='en-AU';
  var v=speechSynthesis.getVoices().filter(function(x){return x.lang.replace('_','-').toLowerCase()==='en-au'})[0];if(v)u.voice=v;
  u.rate=.9;speechSynthesis.cancel();speechSynthesis.speak(u);
};

function finish(){
  if(daily){
    save('edu_puzzle',{date:today,results:results});
    var st=streakInfo();
    if(st.last!==today){st.count=(st.last===dayBefore(today))?st.count+1:1;st.last=today;save('edu_puzzle_streak',st)}
  }
  showEnd(results,daily);
}
function showEnd(res,isDaily){
  var n=res.reduce(function(a,b){return a+b},0);
  $('game').style.display='none';$('end').style.display='block';
  $('endwhen').textContent=isDaily?'Daily Accent Puzzle · '+dateLabel():'Practice round';
  $('score').textContent=n+' / '+res.length;
  $('emojis').textContent=res.map(function(x){return x?'🟩':'🟥'}).join('');
  $('endmsg').textContent=n===res.length?'Perfect! You sound like a local. 🦘':n>=3?'Nice work, mate!':'Good effort. Try the Accent Checker to practise.';
  var st=streakInfo();
  $('streakend').textContent=isDaily&&st.count?'🔥 '+st.count+'-day streak':'';
  showStreakLine();
}
$('share').onclick=function(){
  var res=(load('edu_puzzle')||{}).results||results,btn=this;
  var text='Daily Accent Puzzle 🦘 '+dateLabel()+' '+res.reduce(function(a,b){return a+b},0)+'/'+res.length+'\n'+res.map(function(x){return x?'🟩':'🟥'}).join('')+'\n'+SITE+'/accent-puzzle/';
  function done(){btn.textContent='✅ Copied';setTimeout(function(){btn.textContent='📋 Copy result to share'},1600)}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(done,function(){})}
  else{var ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done()}catch(e){}document.body.removeChild(ta)}
};
$('more').onclick=function(){startRound('practice-'+Math.random(),false)};

// ---- start ----
$('when').textContent=dateLabel();showStreakLine();
var saved=load('edu_puzzle');
if(saved&&saved.date===today&&saved.results&&saved.results.length){showEnd(saved.results,true)}
else startRound(today,true);
</script>"""

page("accent-puzzle", "Daily Accent Puzzle: Spot the Aussie Pronunciation | English Down Under",
     "A free five-question daily puzzle: how do Aussies say it, what do they call it and how do they spell it? Build a streak and share your score.",
     pz_body, nav_on="/tools/", head_extra=pz_css, script=pz_script,
     band=("Daily Accent Puzzle", "Five quick questions a day. Spot the Aussie way to say, name and spell things.", "Tools › Daily Accent Puzzle"))

print("Built Aussie-fy My Sentence and Daily Accent Puzzle")
