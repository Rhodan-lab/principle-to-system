import assert from "node:assert/strict";
import test from "node:test";
import {createRequire} from "node:module";
import {readFileSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";

const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const universe=require("../one_website/universe.js");
const home=require("../one_website/site.js");
const root=readFileSync(resolve(here,"../one_website/index.html"),"utf8");
const layout=readFileSync(resolve(here,"../one_website/styles.css"),"utf8");
const system=readFileSync(resolve(here,"../one_website/universe.css"),"utf8");
const logic=readFileSync(resolve(here,"../one_website/universe.js"),"utf8");
const builder=readFileSync(resolve(here,"../one_website/build.py"),"utf8");

test("every website area uses one deterministic route identity",()=>{
  assert.equal(universe.currentArea("/"),"home");
  assert.equal(universe.currentArea("/learn/refrigerator/"),"refrigerator");
  assert.equal(universe.currentArea("/learn/distributed-information/"),"distributed-information");
  assert.equal(universe.currentArea("/research/"),"atlas");
  assert.equal(universe.currentArea("/research/#overview"),"atlas");
  assert.equal(universe.currentArea("/other"),"home");
  assert.ok(universe.paths.some(x=>x.href==="/research/"));
  assert.ok(universe.paths.some(x=>x.href==="/learn/refrigerator/#model"));
  assert.ok(universe.paths.some(x=>x.href==="/learn/distributed-information/#model"));
});

test("command navigation is useful with no account or persistence",()=>{
  assert.equal(universe.findDestinations("  ").length,universe.paths.length);
  assert.deepEqual(universe.findDestinations("Thermal").map(x=>x.href),
    ["/learn/refrigerator/","/learn/refrigerator/#model"]);
  assert.deepEqual(universe.findDestinations("PROVENANCE").map(x=>x.href),["/research/"]);
  assert.ok(universe.findDestinations("  QUEUES  ").some(x=>x.href.includes("distributed-information")));
  assert.deepEqual(universe.findDestinations("unfindable"),[]);
  assert.match(logic,/showModal\(\)/);
  assert.match(logic,/aria-label","Go to another Principia and Atlas view/);
  assert.match(logic,/pa-lab-frame/);
  assert.match(logic,/pa-lab-model-brief/);
  assert.match(logic,/altKey&&event\.key\.toLowerCase\(\)==="g"/);
  assert.match(logic,/area!=="atlas"/);
  assert.doesNotMatch(logic,/fetch\s*\(|localStorage|sessionStorage|indexedDB|sendBeacon|document\.cookie/);
  assert.doesNotMatch(logic,/\beval\s*\(|\bnew Function\s*\(/);
});

test("root has connected expeditions, real model, honest evidence boundary",()=>{
  for(const anchor of ["/learn/refrigerator/","/learn/distributed-information/","/research/"]){
    assert.ok(root.includes('href="'+anchor+'"'),"Missing "+anchor);
  }
  for(const id of ["discover","explore","studio","method","evidence-boundary",
    "studio-panel","studio-input","lens-action","lens-result-label","lens-result-value","lens-math"]){
    assert.match(root,new RegExp('id="'+id+'"'));
  }
  assert.match(root,/id="pa-global-nav"/);
  assert.match(root,/aria-label="Unified Principia and Atlas navigation"/);
  assert.match(root,/src="\/universe.js"/);
  assert.match(root,/href="\/universe.css"/);
  assert.match(root,/pinned, read-only fixture/);
  assert.match(root,/Two authorities/);
  assert.match(root,/No account/);
  const routeIds=["__PRINCIPIA_COMMIT__","__ATLAS_COMMIT__","__ATLAS_WORKSPACE__","__ATLAS_REVISION__"];
  for(const token of routeIds)assert.equal(root.split(token).length-1,1,token+" must be uniquely replaced");
  assert.equal(home.thermalPreview(95).initialPowerW,-13);
  assert.equal(home.queuePreview(.1).offered,8.25);
});

test("shared design truly spans homepage, learner and evidence workspace",()=>{
  assert.match(builder,/universe\.css/);
  assert.match(builder,/universe\.js/);
  assert.match(system,/body\.pa-learner \.pa-lab-frame/);
  assert.match(system,/body\.pa-research \.atlas-toolbar/);
  assert.match(system,/#pa-global-nav/);
  assert.match(system,/\.pa-command-dialog/);
  assert.match(system,/\.pa-nav-command/);
  assert.match(layout,/\.pa3-hero/);
  assert.match(layout,/\.pa3-expedition-grid/);
  assert.match(layout,/\.pa3-studio-frame/);
  assert.match(layout,/\.pa3-boundary/);
  assert.match(system,/@media\(max-width:640px\)/);
  assert.match(layout,/@media\(max-width:540px\)/);
  assert.match(system,/prefers-reduced-motion:reduce/);
  assert.match(layout,/forced-colors:active/);
  assert.doesNotMatch(system+layout,/@import\b|url\(\s*["']?https?:/);
});

test("this release does not modify canonical source engines",()=>{
  const learner=readFileSync(resolve(here,"../product_alpha/index.html"),"utf8");
  assert.match(learner,/id="modelT"/);
  assert.match(learner,/name="model-prediction"/);
  assert.match(learner,/function runModel\(\)/);
  assert.match(learner,/id="experimentComparison"/);
  assert.match(learner,/id="note"/);
  assert.match(builder,/suite\.load_atlas/);
  assert.match(builder,/package_integrity\.load_verified_package/);
  assert.match(builder,/source = source\.replace\("<body>"/);
});
