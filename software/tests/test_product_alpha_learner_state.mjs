import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import vm from "node:vm";
import {createRequire} from "node:module";
import {fileURLToPath} from "node:url";
import {dirname, resolve} from "node:path";

const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const modelAdapters=require("../product_alpha/model-adapters.js");
const html=readFileSync(resolve(here,"../product_alpha/index.html"),"utf8");
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,1,"index.html must contain one inline script");
const context={module:{exports:{}},exports:{},PrincipiaModelAdapters:modelAdapters};
vm.runInNewContext(scripts[0][1],context);
const api=context.module.exports;

test("creates isolated in-tab learner state",()=>{
  const first=api.createLearnerState();
  const second=api.createLearnerState();
  api.saveNote(first,"observe","one");
  assert.equal(first.notes.observe,"one");
  assert.equal(second.notes.observe,undefined);
});

test("tracks visited steps once",()=>{
  const state=api.createLearnerState();
  api.rememberStep(state,"observe");
  api.rememberStep(state,"model");
  api.rememberStep(state,"observe");
  assert.deepEqual([...state.visited],["observe","model"]);
});

test("invalidating model keeps controls but clears prediction and result",()=>{
  const state=api.createLearnerState();
  api.setModelPrediction(state,"falls");
  api.markModelRun(state);
  api.invalidateModelState(state,{room_temperature_c:24,cooling_on:true});
  assert.deepEqual({...state.model.values},{room_temperature_c:24,cooling_on:true});
  assert.equal(state.model.prediction,null);
  assert.equal(state.model.ran,false);
});

test("model prediction can be restored after navigation",()=>{
  const state=api.createLearnerState();
  api.invalidateModelState(state,{room_temperature_c:22});
  api.setModelPrediction(state,"rises");
  api.markModelRun(state);
  assert.equal(state.model.prediction,"rises");
  assert.equal(state.model.ran,true);
});

test("diagnosis choice survives navigation and resets checked result on change",()=>{
  const state=api.createLearnerState();
  api.setDiagnosisChoice(state,2);
  api.markDiagnosisChecked(state);
  assert.equal(state.diagnosis.checked,true);
  api.setDiagnosisChoice(state,1);
  assert.equal(state.diagnosis.choice,1);
  assert.equal(state.diagnosis.checked,false);
});

test("renders canonical tables with accessible relationships",()=>{
  const rendered=api.renderMarkdown([
    "| Type | Examples |",
    "| --- | --- |",
    "| Inputs | Electrical work |",
    "| Outputs | Rejected heat |",
  ].join("\n"));
  assert.match(rendered,/<div class="table-scroll" role="region" aria-label="Type reference table" tabindex="0">/);
  assert.match(rendered,/<caption class="sr-only">Type reference table<\/caption>/);
  assert.match(rendered,/<th scope="col">Type<\/th><th scope="col">Examples<\/th>/);
  assert.match(rendered,/<th scope="row">Inputs<\/th><td>Electrical work<\/td>/);
  assert.match(rendered,/<th scope="row">Outputs<\/th><td>Rejected heat<\/td>/);
});

test("learner route exposes visible keyboard focus",()=>{
  assert.match(html,/a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible/);
  assert.match(html,/\.content \.table-scroll:focus-visible/);
  assert.match(html,/\.content table\{width:100%;min-width:32rem/);
});

test("thermal chart summary remains available through the adapter boundary",()=>{
  const summary=JSON.parse(JSON.stringify(api.modelResultSummary(
    [{m:0,t:8.04},{m:60,t:4.96}],
    24,
    60,
  )));
  assert.deepEqual(summary,{
    outcome:"falls",
    result:"Model result: cabinet temperature falls to 5.0 °C after 60 minutes.",
    description:"Cabinet temperature falls from 8.0 °C to 5.0 °C over 60 minutes. Room temperature reference: 24.0 °C.",
  });
});

test("model chart exposes route-driven titles and a dynamic description",()=>{
  const adapterSource=readFileSync(resolve(here,"../product_alpha/model-adapters.js"),"utf8");
  const refrigeratorRoute=readFileSync(resolve(here,"../product_alpha/routes/refrigerator.json"),"utf8");
  const informationRoute=readFileSync(resolve(here,"../product_alpha/routes/distributed-information.json"),"utf8");
  assert.match(html,/id="chart"[^>]+aria-labelledby="chartTitle chartDescription"/);
  assert.match(html,/<title id="chartTitle">Predicted model response<\/title>/);
  assert.match(html,/<script src="model-adapters\.js"><\/script>/);
  assert.match(html,/adapter\.describeChart\(route\.model,result\)/);
  assert.match(html,/adapter\.draw\(route\.model,result,q\("#chart"\),description\)/);
  assert.match(adapterSource,/esc\(model\.chart\.title\)/);
  assert.match(refrigeratorRoute,/"title": "Predicted cabinet temperature"/);
  assert.match(informationRoute,/"title": "Predicted queue response"/);
  assert.doesNotMatch(html,/id="chart"[^>]+aria-label="Predicted cabinet temperature"/);
});

test("evidence dialog has an explicit accessible name and description",()=>{
  assert.match(html,/<dialog id="dialog" aria-labelledby="evidenceTitle" aria-describedby="evidenceBoundaryIntro">/);
  assert.match(html,/<h2 id="evidenceTitle">Evidence boundary<\/h2>/);
  assert.match(html,/<p id="evidenceBoundaryIntro">References are pinned and advisory\./);
});

test("model and diagnosis groups expose validation relationships",()=>{
  assert.match(html,/<fieldset class="prediction" id="modelPrediction" aria-describedby="modelFeedback">/);
  assert.match(html,/id="modelFeedback" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html,/<fieldset class="challenge" id="diagnosisChoice" aria-describedby="feedback">/);
  assert.match(html,/id="feedback" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html,/\.prediction\[aria-invalid="true"\],\.challenge\[aria-invalid="true"\]/);
});

test("choice validation marks the group and focuses its first radio",()=>{
  assert.match(html,/function reportChoiceError\(groupSelector,feedbackSelector,message\)/);
  assert.match(html,/group\.setAttribute\("aria-invalid","true"\)/);
  assert.match(html,/feedback\.setAttribute\("aria-live","assertive"\)/);
  assert.match(html,/group\.querySelector\('input\[type="radio"\]'\)/);
  assert.match(html,/first&&typeof first\.focus==="function"\)first\.focus\(\)/);
  assert.match(html,/function clearChoiceError\(groupSelector,feedbackSelector\)/);
  assert.match(html,/group\.removeAttribute\("aria-invalid"\)/);
  assert.match(html,/feedback\.setAttribute\("aria-live","polite"\)/);
});

test("model and diagnosis reject empty choices before recording completion",()=>{
  const runModelSource=html.match(/function runModel\(\)\{([\s\S]*?)\}\nfunction diagnosisFeedback/);
  assert.ok(runModelSource,"runModel source must be testable");
  assert.match(runModelSource[1],/if\(!picked\)\{reportChoiceError\("#modelPrediction","#modelFeedback"/);
  assert.ok(runModelSource[1].indexOf("reportChoiceError(")<runModelSource[1].indexOf("markModelRun(session)"));
  assert.ok(runModelSource[1].indexOf("modelAdapter().validate")<runModelSource[1].indexOf("markModelRun(session)"));

  const challengeSource=html.match(/function challenge\(box\)\{([\s\S]*?)\}\nfunction evidence/);
  assert.ok(challengeSource,"challenge source must be testable");
  assert.match(challengeSource[1],/if\(!picked\)\{reportChoiceError\("#diagnosisChoice","#feedback","Choose a diagnosis first\."\);return\}/);
  assert.ok(challengeSource[1].indexOf("reportChoiceError(")<challengeSource[1].indexOf("markDiagnosisChecked(session)"));
  assert.match(challengeSource[1],/clearChoiceError\("#diagnosisChoice","#feedback"\)/);
});

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
  const markerAt=initBody.indexOf('meta[name="principia-route"]');
  const fetchAt=initBody.indexOf('await fetch(`data/${routeId}.json`');
  const handlerAt=initBody.indexOf('q("#note").addEventListener');
  const readyAt=initBody.indexOf('applyLearnerAvailability("ready")');
  const stepAt=initBody.indexOf("step(",readyAt);
  assert.ok(loadingAt<markerAt&&markerAt<fetchAt,"learner controls must lock before the bound route loads");
  assert.ok(handlerAt<readyAt,"learner controls become ready only after handlers install");
  assert.ok(readyAt<stepAt,"the initial step renders only after controls become ready");
  assert.match(initBody,/if\(route\.route_id!==routeId\)throw Error\("Packaged route identity does not match its payload\."\)/);

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
