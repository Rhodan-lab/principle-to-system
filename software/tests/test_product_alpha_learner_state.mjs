import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import vm from "node:vm";
import {fileURLToPath} from "node:url";
import {dirname, resolve} from "node:path";

const here=dirname(fileURLToPath(import.meta.url));
const html=readFileSync(resolve(here,"../product_alpha/index.html"),"utf8");
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,1,"index.html must contain one inline script");
const context={module:{exports:{}},exports:{}};
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

test("thermal chart summary describes the simulated result",()=>{
  const summary=JSON.parse(JSON.stringify(api.modelResultSummary(
    [{m:0,t:8.04},{m:60,t:4.96}],
    24,
    60,
  )));
  assert.deepEqual(summary,{
    trend:"falls",
    result:"Model result: cabinet temperature falls to 5.0 °C after 60 minutes.",
    description:"Cabinet temperature falls from 8.0 °C to 5.0 °C over 60 minutes. Room temperature reference: 24.0 °C.",
  });
});

test("thermal chart exposes a dynamic title and description",()=>{
  assert.match(html,/id="chart"[^>]+aria-labelledby="chartTitle chartDescription"/);
  assert.match(html,/<title id="chartTitle">Predicted cabinet temperature<\/title>/);
  assert.match(html,/<desc id="chartDescription">\$\{esc\(description\)\}<\/desc>/);
  assert.match(html,/draw\(points,values\.room_temperature_c,summary\.description\)/);
  assert.doesNotMatch(html,/id="chart"[^>]+aria-label="Predicted cabinet temperature"/);
});

test("evidence dialog has an explicit accessible name and description",()=>{
  assert.match(html,/<dialog id="dialog" aria-labelledby="evidenceTitle" aria-describedby="evidenceBoundaryIntro">/);
  assert.match(html,/<h2 id="evidenceTitle">Evidence boundary<\/h2>/);
  assert.match(html,/<p id="evidenceBoundaryIntro">References are pinned and advisory\./);
});
