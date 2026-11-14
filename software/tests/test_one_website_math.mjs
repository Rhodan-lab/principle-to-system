import assert from "node:assert/strict";
import test from "node:test";
import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";

const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const math=require("../one_website/experience.js");
const home=require("../one_website/site.js");
const adapters=require("../product_alpha/model-adapters.js");
const route=id=>JSON.parse(readFileSync(resolve(here,"../product_alpha/routes/"+id+".json"),"utf8"));
const near=(value,expected,tolerance=1e-8)=>assert.ok(Math.abs(value-expected)<=tolerance,
  "Expected "+value+" near "+expected);

test("thermal MathML follows same energy balance as actual deterministic model",()=>{
  const model=route("refrigerator").model;
  const values={...model.defaults};
  const result=adapters.getAdapter(model.adapter).run(model,values);
  const explanation=math.thermalQuantities(model,values,result);
  near(explanation.power,3.2*(28-8)+18-95);
  near(explanation.equilibrium,28+(18-95)/3.2);
  near(explanation.tauMinutes,180000/3.2/60);
  near(explanation.simulatedFinal,result.points.at(-1).t);
  assert.ok(Math.abs(explanation.solverError)<.005,
    "Explicit-Euler numeric result should agree with exact constant-parameter solution");
  const noCooling={...values,cooling_on:false};
  const warmer=adapters.getAdapter(model.adapter).run(model,noCooling);
  const noCoolingResult=math.thermalQuantities(model,noCooling,warmer);
  near(noCoolingResult.cooling,0);
  assert.ok(noCoolingResult.power>0);
  assert.ok(warmer.points.at(-1).t>result.points.at(-1).t);
});

test("queue formulas exactly match the bounded fluid simulation",()=>{
  const model=route("distributed-information").model;
  const scenarios=[model.defaults,{...model.defaults,retry_fraction:0},
    {...model.defaults,retry_fraction:0.8},
    {...model.defaults,external_arrival_rate_rps:15,service_rate_rps:2,retry_fraction:1}];
  for(const values of scenarios){
    const result=adapters.getAdapter(model.adapter).run(model,values);
    const explanation=math.queueQuantities(model,values,result);
    near(explanation.offered,result.offered);
    near(explanation.utilization,result.utilization);
    near(explanation.net,result.offered-values.service_rate_rps);
    near(explanation.backlog,result.backlog);
    near(explanation.rejected,result.rejected);
    if(result.meanTime===null)assert.equal(explanation.mm1Time,null);
    else near(explanation.mm1Time,result.meanTime);
  }
  const example=math.queueQuantities(model,
    {...model.defaults,retry_fraction:.8},adapters.getAdapter(model.adapter).run(model,{...model.defaults,retry_fraction:.8}));
  near(example.offered,13.5);
  near(example.backlog,50);
  near(example.rejected,55);
});

test("studio preview equations follow the same quantities",()=>{
  near(home.thermalPreview(95).initialPowerW,-13);
  near(home.thermalPreview(95).equilibriumC,3.9375);
  near(home.thermalPreview(0).initialPowerW,82);
  near(home.queuePreview(.1).offered,8.25);
  near(home.queuePreview(.1).utilization,.825);
  near(home.queuePreview(1).backlog,50);
  near(home.queuePreview(1).rejected,100);
  assert.throws(()=>home.queuePreview(2),/fraction/);
  assert.throws(()=>math.thermalQuantities({thermal_capacitance_j_per_k:0},{ua_w_per_k:2},{points:[{t:0}]}),/Positive/);
});

test("equations are accessible MathML with explicit model distinction",()=>{
  const thermal=math.makeFormulaBoard("refrigerator");
  const queue=math.makeFormulaBoard("distributed-information");
  assert.equal((thermal.match(/<math\b/g)||[]).length,1);
  assert.equal((queue.match(/<math\b/g)||[]).length,5);
  assert.match(thermal,/explicit Euler/);
  assert.match(thermal,/aria-label/);
  assert.match(queue,/separate models/);
  assert.match(queue,/one added attempt/);
  assert.match(queue,/M\/M\/1/);
  assert.equal(math.makeFormulaBoard("invalid"),"");
});

test("preview has no tracking and resources remain same-origin",()=>{
  const homepage=readFileSync(resolve(here,"../one_website/index.html"),"utf8");
  const js=readFileSync(resolve(here,"../one_website/site.js"),"utf8");
  const mathScript=readFileSync(resolve(here,"../one_website/experience.js"),"utf8");
  for(const source of [js,mathScript]){
    assert.doesNotMatch(source,/localStorage|sessionStorage|navigator\.sendBeacon|XMLHttpRequest/);
    assert.doesNotMatch(source,/https?:\/\//);
  }
  assert.match(homepage,/role="tablist"/);
  assert.match(homepage,/id="studio-panel"/);
  assert.match(homepage,/href="\/learn\/refrigerator\/"/);
  assert.match(homepage,/href="\/research\/"/);
});
