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
