import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
import test from "node:test";
import vm from "node:vm";

const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const adapters=require("../product_alpha/model-adapters.js");
const route=id=>JSON.parse(readFileSync(resolve(here,"../product_alpha/routes/"+id+".json"),"utf8"));
const html=readFileSync(resolve(here,"../product_alpha/index.html"),"utf8");
const inline=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(inline.length,1);
const context={module:{exports:{}},exports:{},PrincipiaModelAdapters:adapters};
vm.runInNewContext(inline[0][1],context);
const stateApi=context.module.exports;

function experiment(id,overrides={}){
  const model=route(id).model;
  const values={...model.defaults,...overrides};
  const result=adapters.getAdapter(model.adapter).run(model,values);
  return adapters.captureExperiment(model,result);
}

test("counterfactual lab has accessible controls and no browser persistence",()=>{
  assert.match(html,/id="saveBaseline"/);
  assert.match(html,/id="clearBaseline"/);
  assert.match(html,/id="experimentStatus"[^>]+role="status"/);
  assert.match(html,/id="experimentComparison" hidden/);
  assert.match(html,/role="region" aria-label="Comparison of simulated model results"/);
  assert.doesNotMatch(html,/localStorage|sessionStorage|indexedDB/);
});

test("refrigerator comparison exposes temperature sensitivity",()=>{
  const a=experiment("refrigerator");
  const b=experiment("refrigerator",{cooling_on:false});
  const compared=adapters.compareExperiments(a,b);
  assert.deepEqual(compared.changed,["cooling_on"]);
  assert.deepEqual(compared.metrics.map(x=>x.id),["final-temperature","temperature-change"]);
  assert.ok(compared.metrics[0].delta>0,"turning cooling off should raise modeled final temperature");
  assert.equal(a.values.cooling_on,true,"baseline must not be mutated");
});

test("queue comparison exposes retry-driven saturation",()=>{
  const a=experiment("distributed-information");
  const b=experiment("distributed-information",{retry_fraction:0.8});
  const compared=adapters.compareExperiments(a,b);
  assert.deepEqual(compared.changed,["retry_fraction"]);
  assert.deepEqual(compared.metrics.map(x=>x.id),["utilization","backlog","rejected"]);
  assert.ok(compared.metrics[0].delta>0);
  assert.ok(compared.metrics[1].delta>=0);
});

test("baseline and current results are isolated from slider edits",()=>{
  const baseline=experiment("refrigerator");
  const state=stateApi.createLearnerState();
  assert.throws(()=>stateApi.saveExperimentBaseline(state),/Run the model/);
  assert.throws(()=>stateApi.storeExperimentResult(state,baseline),/prediction-gated/);
  stateApi.setModelPrediction(state,"falls");
  stateApi.markModelRun(state);
  stateApi.storeExperimentResult(state,baseline);
  stateApi.saveExperimentBaseline(state);
  assert.equal(state.experiments.current,null);
  stateApi.invalidateModelState(state,{...baseline.values,cooling_on:false});
  assert.equal(state.experiments.baseline.values.cooling_on,true);
  assert.equal(state.experiments.current,null);
  const followUp=experiment("refrigerator",{cooling_on:false});
  stateApi.setModelPrediction(state,"rises");
  stateApi.markModelRun(state);
  stateApi.storeExperimentResult(state,followUp);
  assert.equal(adapters.compareExperiments(state.experiments.baseline,state.experiments.current).changed.length,1);
  stateApi.clearExperimentBaseline(state);
  assert.equal(state.experiments.baseline,null);
  assert.equal(state.experiments.current,followUp);
});

test("no change and mixed model adapters are handled safely",()=>{
  const a=experiment("distributed-information");
  const identical=experiment("distributed-information");
  assert.deepEqual(adapters.compareExperiments(a,identical).changed,[]);
  assert.throws(()=>adapters.compareExperiments(a,experiment("refrigerator")),/different model adapters/);
  assert.throws(()=>adapters.captureExperiment({...route("refrigerator").model,adapter:"unknown"},{values:route("refrigerator").model.defaults}),/Unsupported experiment adapter/);
});
