#!/usr/bin/env python3
"""Build the "Which Aussie Are You?" quiz.  Usage: python3 build_quiz.py
Reads data/aussie-types.json   Writes which-aussie-are-you/index.html"""
import json
from common import *

def js_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

data = json.loads((ROOT / "data" / "aussie-types.json").read_text(encoding="utf-8"))

css = """<style>
.pbar{height:8px;background:var(--ocean-soft);border-radius:999px;overflow:hidden;margin:6px 0 16px}
.pbar i{display:block;height:100%;background:var(--gold);width:0;transition:width .3s}
.qtext{font-family:Fraunces,Georgia,serif;font-size:clamp(1.25rem,4vw,1.6rem);color:var(--ocean-dark);font-weight:800;line-height:1.25}
.popts{display:grid;gap:10px;margin:16px 0 4px}
.popts button{font:inherit;font-size:1.05rem;font-weight:600;text-align:left;background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:14px 16px;cursor:pointer;color:var(--ink)}
.popts button:hover{border-color:var(--ocean);background:var(--ocean-soft)}
.rbig{font-size:3.4rem;line-height:1}
.rname{font-family:Fraunces,serif;font-size:clamp(1.8rem,6vw,2.4rem);font-weight:800;color:var(--ocean-dark);margin:6px 0 2px}
.says{list-style:none;padding:0;margin:8px 0 0;display:grid;gap:6px}
.says li{background:var(--ocean-soft);border-radius:10px;padding:8px 12px;font-weight:600}
.mix{display:grid;gap:6px;margin-top:8px}
.mix div{display:flex;align-items:center;gap:8px;font-size:.92rem;color:var(--muted)}
.mix i{display:block;height:8px;background:var(--gold);border-radius:999px}
</style>"""

body = f"""<main class="wrap">
<noscript><div class="card" style="margin-top:14px">This quiz needs JavaScript. Please turn it on and reload.</div></noscript>

<div class="card" id="game" style="margin-top:22px">
<div style="color:var(--muted);font-size:.9rem" id="prog"></div>
<div class="pbar"><i id="bar"></i></div>
<div class="qtext" id="qtext"></div>
<div class="popts" id="opts"></div>
</div>

<div class="card" id="res" style="margin-top:22px;display:none;text-align:center">
<div style="color:var(--muted)">You're…</div>
<div class="rbig" id="remoji"></div>
<div class="rname" id="rname"></div>
<div style="color:var(--muted);font-weight:600" id="rtag"></div>
<p id="rblurb" style="margin:14px auto;max-width:520px"></p>
<div style="text-align:left;max-width:520px;margin:0 auto">
<strong>You'd probably say:</strong>
<ul class="says" id="rsay"></ul>
<div class="mix" id="rmix"></div>
</div>
<div class="row" style="justify-content:center;margin-top:18px"><button class="btn" id="share" type="button">📋 Copy result to share</button><a class="btn gold" href="/score-card/">🏆 Make a card</a><button class="btn ghost" id="again" type="button">Take it again</button></div>
<div id="copied" style="color:var(--muted);min-height:1.4em;margin-top:8px" aria-live="polite"></div>
<h2 style="font-size:1.2rem;margin-top:26px">Learn next</h2>
<div class="related" id="rlearn" style="justify-content:center"></div>
</div>

<h2>About this quiz</h2>
<div class="card">
<p style="margin:0">This is just for fun. It's a light-hearted look at the kind of Aussie your habits sound like, and it isn't a test of your English level. Real Australians are a mix of all five types, and so are most learners. Your answers stay on your device.</p>
</div>
{SISTER}
</main>"""

script = r"""<script>
var D=""" + js_json(data) + r""";
var SITE='""" + SITE + r"""';
var Q=D.questions,T=D.types,i=0,pts={};
function load(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function $(id){return document.getElementById(id)}
function sydneyDate(){
  try{return new Intl.DateTimeFormat('en-CA',{timeZone:'Australia/Sydney',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())}
  catch(e){return new Date().toISOString().slice(0,10)}
}
function start(){
  i=0;pts={};Object.keys(T).forEach(function(k){pts[k]=0});
  $('res').style.display='none';$('game').style.display='';show();
}
function show(){
  var q=Q[i];
  $('prog').textContent='Question '+(i+1)+' of '+Q.length;
  $('bar').style.width=(i/Q.length*100)+'%';
  $('qtext').textContent=q.q;
  var box=$('opts');box.innerHTML='';
  q.opts.forEach(function(o){
    var b=document.createElement('button');b.type='button';b.textContent=o[0];
    b.onclick=function(){pick(o[1])};box.appendChild(b);
  });
}
function pick(k){
  pts[k]+=1;i++;
  if(i<Q.length)show();else finish();
}
function winner(){
  var keys=Object.keys(T),best=keys[0];
  keys.forEach(function(k){if(pts[k]>pts[best])best=k});
  return best;
}
function finish(){
  var w=winner(),t=T[w];
  save('edu_aussie_type',{type:w,name:t.name,emoji:t.emoji,date:sydneyDate()});
  $('game').style.display='none';$('res').style.display='';
  $('remoji').textContent=t.emoji;$('rname').textContent=t.name;
  $('rtag').textContent=t.tag;$('rblurb').textContent=t.blurb;
  var s=$('rsay');s.innerHTML='';
  t.say.forEach(function(x){var li=document.createElement('li');li.textContent='“'+x+'”';s.appendChild(li)});
  var m=$('rmix');m.innerHTML='';
  Object.keys(T).sort(function(a,b){return pts[b]-pts[a]}).forEach(function(k){
    var d=document.createElement('div'),lab=document.createElement('span'),bar=document.createElement('i');
    lab.style.minWidth='170px';lab.textContent=T[k].emoji+' '+T[k].name;
    bar.style.width=Math.max(pts[k]/Q.length*100,2)+'%';
    d.appendChild(lab);d.appendChild(bar);m.appendChild(d);
  });
  var l=$('rlearn');l.innerHTML='';
  t.learn.forEach(function(x){var a=document.createElement('a');a.href=x[0];a.textContent=x[1];l.appendChild(a)});
  $('copied').textContent='';window.scrollTo(0,0);
}
function shareText(){
  var t=load('edu_aussie_type');
  return 'I got '+t.emoji+' '+t.name+' on Which Aussie Are You?\n'+SITE+'/which-aussie-are-you/';
}
$('share').onclick=function(){
  var txt=shareText();
  function ok(){$('copied').textContent='Copied! Paste it anywhere.'}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(ok,function(){fallback(txt,ok)})}
  else fallback(txt,ok);
};
function fallback(txt,ok){
  var ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();
  try{document.execCommand('copy');ok()}catch(e){$('copied').textContent='Press and hold to copy: '+txt}
  document.body.removeChild(ta);
}
$('again').onclick=start;
start();
</script>"""

page("which-aussie-are-you", "Which Aussie Are You? A Fun Quiz | English Down Under",
     "Eight quick questions to find out which kind of Aussie your English sounds like: Larrikin, Flat White Local, Bush Yarner, Beach Local or Office Legend.",
     body, nav_on="/tools/", head_extra=css, script=script,
     band=("Which Aussie Are You?", "Eight quick questions. Find out which kind of Aussie your English sounds like.", "Tools › Which Aussie Are You?"))
print("Built Which Aussie Are You?")
