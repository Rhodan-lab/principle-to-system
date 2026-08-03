#!/usr/bin/env python3
"""Apply bounded learner route initialization-state recovery once."""
from pathlib import Path

HTML_PATH = Path("software/product_alpha/index.html")
TEST_PATH = Path("software/tests/test_product_alpha_learner_state.mjs")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


html = HTML_PATH.read_text(encoding="utf-8")
html = replace_once(
    html,
    '.button:disabled{cursor:not-allowed;opacity:.55}.primary{background:var(--accent);color:white}',
    '.button:disabled{cursor:not-allowed;opacity:.55}a[aria-disabled="true"]{pointer-events:none;opacity:.55}.primary{background:var(--accent);color:white}',
    "disabled learner link styling",
)
html = replace_once(
    html,
    '<h1 id="title">Loading route…</h1>',
    '<h1 id="title" tabindex="-1">Loading route…</h1>',
    "load failure heading focus target",
)
html = replace_once(
    html,
    '<p class="sr-only" id="stepStatus" aria-live="polite"></p>',
    '<p class="sr-only" id="stepStatus" role="status" aria-live="polite" aria-atomic="true"></p>',
    "learner load status semantics",
)
html = replace_once(
    html,
    'function markDiagnosisChecked(state){state.diagnosis.checked=true;return state}\nconst learnerStateApi={createLearnerState,rememberStep,saveNote,invalidateModelState,setModelPrediction,markModelRun,setDiagnosisChoice,markDiagnosisChecked,renderMarkdown:md,modelResultSummary};',
    'function markDiagnosisChecked(state){state.diagnosis.checked=true;return state}\nfunction learnerAvailability(state){if(!["loading","ready","error"].includes(state))throw new Error("invalid learner availability");return{busy:state==="loading",disabled:state!=="ready"}}\nconst learnerStateApi={createLearnerState,rememberStep,saveNote,invalidateModelState,setModelPrediction,markModelRun,setDiagnosisChoice,markDiagnosisChecked,learnerAvailability,renderMarkdown:md,modelResultSummary};',
    "learner availability contract",
)
html = replace_once(
    html,
    'function evidence(){q("#atlas").innerHTML=route.atlas.references.map(r=>`<article class="ref"><code>${esc(r.entity_id)}@${r.revision}</code><p>${esc(r.purpose)}</p><small>${esc(r.review_level)} · human verified: ${r.human_verified}</small></article>`).join("");q("#canonical").innerHTML=route.canonical_sources.map(s=>`<article class="ref"><strong>${esc(s.title)}</strong><p><code>${esc(s.path)}</code></p><small>status: ${esc(s.status||"unspecified")} · release: ${esc(s.release_status||"not applicable")}</small></article>`).join("")}',
    'function evidence(){q("#atlas").innerHTML=route.atlas.references.map(r=>`<article class="ref"><code>${esc(r.entity_id)}@${r.revision}</code><p>${esc(r.purpose)}</p><small>${esc(r.review_level)} · human verified: ${r.human_verified}</small></article>`).join("");q("#canonical").innerHTML=route.canonical_sources.map(s=>`<article class="ref"><strong>${esc(s.title)}</strong><p><code>${esc(s.path)}</code></p><small>status: ${esc(s.status||"unspecified")} · release: ${esc(s.release_status||"not applicable")}</small></article>`).join("")}\nfunction applyLearnerAvailability(state){const view=learnerAvailability(state),main=q("main");main.setAttribute("aria-busy",String(view.busy));document.querySelectorAll(\'a[href^="#"]\').forEach(link=>{if(view.disabled){link.setAttribute("aria-disabled","true");link.setAttribute("tabindex","-1")}else{link.removeAttribute("aria-disabled");link.removeAttribute("tabindex")}});q("#note").disabled=view.disabled;q("#evidence").disabled=view.disabled;if(view.disabled)q("#evidence").setAttribute("aria-disabled","true");else q("#evidence").removeAttribute("aria-disabled")}\nfunction reportLearnerLoadFailure(error){applyLearnerAvailability("error");const message=error&&error.message?error.message:String(error),title=q("#title");title.textContent="Product Alpha could not load";q("#subtitle").textContent=message;q("#stepStatus").setAttribute("aria-live","assertive");q("#stepStatus").textContent=`Product Alpha could not load. ${message}`;q("#evidence").setAttribute("aria-busy","false");document.title="Product Alpha could not load";if(typeof title.focus==="function")title.focus()}',
    "learner availability application",
)
html = replace_once(
    html,
    'async function init(){const r=await fetch("data/refrigerator.json",{cache:"no-store"});if(!r.ok)throw Error(`Unable to load route: ${r.status}`);route=await r.json();q("#title").textContent=route.title;q("#subtitle").textContent=route.subtitle;q("#sources").textContent=route.canonical_sources.length;evidence();q("#evidence").disabled=false;q("#evidence").removeAttribute("aria-busy");q("#note").addEventListener("input",event=>saveNote(session,active,event.target.value));step(order.includes(location.hash.slice(1))?location.hash.slice(1):"observe")}',
    'async function init(){applyLearnerAvailability("loading");const r=await fetch("data/refrigerator.json",{cache:"no-store"});if(!r.ok)throw Error(`Unable to load route: ${r.status}`);route=await r.json();q("#title").textContent=route.title;q("#subtitle").textContent=route.subtitle;q("#sources").textContent=route.canonical_sources.length;evidence();q("#evidence").removeAttribute("aria-busy");q("#note").addEventListener("input",event=>saveNote(session,active,event.target.value));applyLearnerAvailability("ready");step(order.includes(location.hash.slice(1))?location.hash.slice(1):"observe")}',
    "learner initialization states",
)
html = replace_once(
    html,
    'if(typeof document!=="undefined"){addEventListener("hashchange",()=>{announceStep=true;step(location.hash.slice(1));announceStep=false});q("#evidence").onclick=()=>q("#dialog").showModal();init().catch(e=>{q("#title").textContent="Product Alpha could not load";q("#subtitle").textContent=e.message;q("#evidence").setAttribute("aria-busy","false")})}',
    'if(typeof document!=="undefined"){addEventListener("hashchange",()=>{announceStep=true;step(location.hash.slice(1));announceStep=false});q("#evidence").onclick=()=>q("#dialog").showModal();init().catch(reportLearnerLoadFailure)}',
    "learner load failure handler",
)
HTML_PATH.write_text(html, encoding="utf-8")

test_text = TEST_PATH.read_text(encoding="utf-8")
addition = r'''

test("learner availability distinguishes loading, ready, and error",()=>{
  assert.deepEqual(JSON.parse(JSON.stringify(api.learnerAvailability("loading"))),{
    busy:true,
    disabled:true,
  });
  assert.deepEqual(JSON.parse(JSON.stringify(api.learnerAvailability("ready"))),{
    busy:false,
    disabled:false,
  });
  assert.deepEqual(JSON.parse(JSON.stringify(api.learnerAvailability("error"))),{
    busy:false,
    disabled:true,
  });
  assert.throws(()=>api.learnerAvailability("unknown"),/invalid learner availability/);
});

test("learner route fails closed when route data cannot load",()=>{
  assert.match(html,/<h1 id="title" tabindex="-1">Loading route…<\/h1>/);
  assert.match(html,/id="stepStatus" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html,/a\[aria-disabled="true"\]\{pointer-events:none;opacity:\.55\}/);
  assert.match(html,/function applyLearnerAvailability\(state\)/);
  assert.match(html,/document\.querySelectorAll\('a\[href\^="#"\]'\)/);
  assert.match(html,/q\("#note"\)\.disabled=view\.disabled/);
  assert.match(html,/q\("#evidence"\)\.disabled=view\.disabled/);

  const initSource=html.match(/async function init\(\)\{([\s\S]*?)\}\nif\(typeof document/);
  assert.ok(initSource,"init source must be testable");
  const initBody=initSource[1];
  const loadingAt=initBody.indexOf('applyLearnerAvailability("loading")');
  const fetchAt=initBody.indexOf('await fetch("data/refrigerator.json"');
  const handlerAt=initBody.indexOf('q("#note").addEventListener');
  const readyAt=initBody.indexOf('applyLearnerAvailability("ready")');
  const stepAt=initBody.indexOf("step(",readyAt);
  assert.ok(loadingAt<fetchAt,"learner controls must lock before route loading begins");
  assert.ok(handlerAt<readyAt,"learner controls become ready only after handlers install");
  assert.ok(readyAt<stepAt,"the initial step renders only after controls become ready");

  const failureSource=html.match(/function reportLearnerLoadFailure\(error\)\{([\s\S]*?)\}\nasync function init/);
  assert.ok(failureSource,"load failure source must be testable");
  const failureBody=failureSource[1];
  const errorAt=failureBody.indexOf('applyLearnerAvailability("error")');
  const announceAt=failureBody.indexOf('setAttribute("aria-live","assertive")');
  const titleAt=failureBody.indexOf('document.title="Product Alpha could not load"');
  const focusAt=failureBody.indexOf('title.focus()');
  assert.ok(errorAt<announceAt,"controls must disable before the error is announced");
  assert.ok(announceAt<titleAt,"the live error must precede the document-title update");
  assert.ok(titleAt<focusAt,"the failure title must be updated before focus moves");
  assert.match(html,/init\(\)\.catch\(reportLearnerLoadFailure\)/);
});
'''
if addition.strip() in test_text:
    raise SystemExit("learner load-state tests already present")
TEST_PATH.write_text(test_text.rstrip() + addition, encoding="utf-8")
