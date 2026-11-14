import assert from "node:assert/strict";
import test from "node:test";
import {createRequire} from "node:module";
import {readFileSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";

const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const model=require("../one_website/exploration-models.js");
const app=require("../one_website/exploration.js");
const read=name=>readFileSync(resolve(here,"../one_website/"+name),"utf8");
const near=(a,b,tol=1e-7)=>assert.ok(Math.abs(a-b)<=tol,a+" not within "+tol+" of "+b);

test("two new subjects are distinct, documented and bounded",()=>{
  assert.deepEqual(Object.keys(model.DRAFTS),["rainwater","microgrid"]);
  for(const id of Object.keys(model.DRAFTS)){
    const config=model.DRAFTS[id],v=model.defaultValues(id),r=model.simulate(id,v);
    assert.equal(config.id,id);
    assert.match(config.source,/github\.com\/Rhodan-lab\/principle-to-system\/blob\/main\//);
    assert.ok(config.risks.length>150);
    assert.ok(config.formula.length>25);
    assert.ok(config.mode.length>90);
    assert.equal(r.id,id);
    assert.ok(r.rows.length>=8);
    assert.ok(r.coverage>=0&&r.coverage<=1);
    assert.ok(Math.abs(r.balanceError)<1e-7);
    assert.ok(r.rows.every(x=>Number.isFinite(x.stored)&&x.stored>=0&&x.unmet>=0));
  }
  assert.match(model.DRAFTS.rainwater.risks,/Do not drink/);
  assert.match(model.DRAFTS.microgrid.risks,/not an electrical installation/);
});

test("rainwater conserves volume within a finite tank across all weather patterns",()=>{
  const base=model.defaultValues("rainwater");
  for(const pattern of Object.keys(model.RAIN)){
    for(const area of [20,80,200]){
      for(const cap of [100,800,2500]){
        const r=model.simulateRainwater({...base,pattern,area,capacity:cap});
        assert.equal(r.rows.length,8);
        near(r.capturedTotal,r.servedTotal+r.overflowTotal+r.stored);
        near(r.unmetTotal+r.servedTotal,r.demandTotal);
        assert.ok(r.rows.every(x=>x.stored<=cap&&x.overflow>=0));
        assert.ok(r.rows.every(x=>x.served<=base.demand));
      }
    }
  }
  const dry=model.simulateRainwater({...base,pattern:"dry"});
  const wet=model.simulateRainwater({...base,pattern:"mixed"});
  assert.ok(dry.unmetTotal>wet.unmetTotal);
  near(model.simulateRainwater({...base,pattern:"dry",area:20}).rows[0].capture,3*20*base.runoff);
});

test("larger tank never serves less water for otherwise identical inputs",()=>{
  const base=model.defaultValues("rainwater");
  for(const pattern of Object.keys(model.RAIN)){
    const small=model.simulateRainwater({...base,pattern,capacity:100});
    const large=model.simulateRainwater({...base,pattern,capacity:2500});
    assert.ok(large.servedTotal+1e-7>=small.servedTotal);
  }
});

test("solar model balances stored and generated energy including conversion losses",()=>{
  const base=model.defaultValues("microgrid");
  for(const pattern of Object.keys(model.SOLAR)){
    for(const area of [6,16,40]){
      for(const cap of [2,8,24]){
        const r=model.simulateMicrogrid({...base,pattern,area,capacity:cap});
        assert.equal(r.rows.length,12);
        near(r.servedTotal+r.unmetTotal,r.demandTotal);
        assert.ok(Math.abs(r.balanceError)<1e-7);
        assert.ok(r.rows.every(x=>x.stored>=.1*cap-1e-7&&x.stored<=cap+1e-7));
        assert.ok(r.rows.every(x=>x.unmet>=0&&x.overflow>=-1e-7));
        assert.ok(r.rows.every(x=>x.served<=base.load+1e-7));
      }
    }
  }
  const full=model.simulateMicrogrid({...base,pattern:"clear",area:40,load:.5,capacity:2});
  assert.ok(full.overflowTotal>0,"High solar and tiny battery must curtail solar power");
  const overcast=model.simulateMicrogrid({...base,pattern:"overcast"});
  const clear=model.simulateMicrogrid({...base,pattern:"clear"});
  assert.ok(overcast.unmetTotal>clear.unmetTotal);
});

test("models reject out-of-domain and malformed inputs",()=>{
  assert.throws(()=>model.defaultValues("other"),/Unknown exploration/);
  assert.throws(()=>model.simulate("other",{}),/Unknown exploration/);
  const w=model.defaultValues("rainwater"),s=model.defaultValues("microgrid");
  assert.throws(()=>model.simulate("rainwater",{...w,capacity:-1}),/capacity/);
  assert.throws(()=>model.simulate("rainwater",{...w,runoff:Infinity}),/runoff/);
  assert.throws(()=>model.simulate("rainwater",{...w,pattern:"real-time forecast"}),/Unexpected scenario/);
  assert.throws(()=>model.simulate("microgrid",{...s,efficiency:1}),/efficiency/);
  assert.throws(()=>model.simulate("microgrid",{...s,area:"20"}),/area/);
  assert.throws(()=>model.simulate("microgrid",{...s,capacity:3}),/step capacity/);
});

test("new numerical UI graph is bounded and accessible",()=>{
  const r=model.simulateRainwater(model.defaultValues("rainwater"));
  const graph=app.plotPath(r.rows.map(x=>x.stored),r.graphMax);
  assert.ok(graph.startsWith("M62.00"));
  assert.match(graph,/L652\.00/);
  assert.equal(graph,app.plotPath(r.rows.map(x=>x.stored),r.graphMax));
  assert.equal(app.fmt(3.3333,2),"3.33");
  assert.throws(()=>app.plotPath([1,100],10),/outside bounds/);
  assert.throws(()=>app.plotPath([],10),/Valid chart/);
  const markup=read("exploration.html");
  for(const id of ["lab-form","lab-controls","lab-output","lab-chart",
    "lab-prediction-options","lab-result","lab-table-body","lab-save",
    "lab-clear","lab-comparison","lab-source"])assert.match(markup,new RegExp('id="'+id+'"'));
  assert.match(markup,/aria-live="polite"/);
  assert.match(markup,/aria-label="Unified Principia and Atlas navigation"/);
  assert.match(markup,/NOT PRODUCT ALPHA/);
});

test("library visibly includes all four runnable destinations",()=>{
  const library=read("explore-library.html");
  const home=read("index.html");
  for(const path of ["/learn/refrigerator/","/learn/distributed-information/",
    "/explore/rainwater/","/explore/microgrid/"]){
    assert.ok(library.includes('href="'+path+'"'),"Library missing "+path);
    assert.ok(home.includes('href="'+path+'"'),"Home missing "+path);
  }
  assert.match(library,/CONCEPTUAL LAB/);
  assert.match(home,/website-only models/);
  assert.match(read("exploration.css"),/@media\(max-width:480px\)/);
  assert.match(read("exploration.css"),/prefers-reduced-motion:reduce/);
});

test("new runtime makes no external calls or authority-promoting changes",()=>{
  for(const name of ["exploration.js","exploration-models.js"]){
    const src=read(name);
    assert.doesNotMatch(src,/\bfetch\s*\(|\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b|XMLHttpRequest|WebSocket|sendBeacon|document\.cookie/);
    assert.doesNotMatch(src,/\bnew Function\s*\(|\beval\s*\(/);
  }
  const build=read("build.py");
  assert.match(build,/EXPLORATIONS = \("rainwater", "microgrid"\)/);
  assert.match(build,/Website-only models; NOT reviewed Product Alpha routes/);
  assert.match(build,/routes": list\(ROUTES\)/);
  assert.match(build,/suite\.load_atlas/);
});
