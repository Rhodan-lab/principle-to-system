import assert from "node:assert/strict";
import test from "node:test";
import {createRequire} from "node:module";
import {readFileSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";

const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const atlas=require("../one_website/knowledge-content.js");
const reader=require("../one_website/knowledge.js");
const models=require("../one_website/exploration-models.js");
const lab=require("../one_website/exploration.js");
const file=name=>readFileSync(resolve(here,"../one_website/"+name),"utf8");

test("knowledge library has 15 original connected chapters with substantial explanations",()=>{
  assert.equal(atlas.topics.length,15);
  assert.equal(new Set(atlas.topics.map(t=>t.id)).size,15);
  const domains=new Set(atlas.domains);
  assert.ok(domains.size>=5);
  for(const t of atlas.topics){
    assert.ok(domains.has(t.domain));
    assert.equal(t.sections.length,4,t.id);
    assert.equal(t.expedition.length,3,t.id);
    assert.ok(t.expedition.every(scene=>scene.title.length>15&&scene.text.length>180),t.id);
    assert.ok(t.sections.every(s=>s.text.length>180&&s.heading.length>8&&s.thought.length>15),t.id);
    assert.ok(t.lead.length>100);
    assert.ok(t.formula.length>12);
    assert.ok(t.example.length>65);
    assert.ok(t.misconception.length>35);
    assert.match(t.source,/^https:\/\/github.com\/Rhodan-lab\/principle-to-system\/blob\/main\//);
    assert.equal(t.links.length,3);
    assert.ok(t.links.every(id=>id!==t.id&&Boolean(atlas.resolve(id))));
    assert.ok(["/explore/","/research/","/explore/rainwater/","/explore/microgrid/",
      "/learn/refrigerator/","/learn/distributed-information/"].includes(t.lab));
    assert.equal(t.check.choices.length,3);
    assert.ok(t.check.question.length>25);
    assert.ok(t.check.explanation.length>40);
  }
  const words=atlas.topics.reduce((n,t)=>n+(t.sections.map(s=>s.text).join(" ")+" "+t.expedition.map(e=>e.text).join(" ")).split(/\s+/).length,0);
  assert.ok(words>4000,"The Knowledge Atlas should contain substantive learning material");
});

test("knowledge search supports broad queries, exact topics, domains, empty results",()=>{
  assert.equal(atlas.normalize("  FOLLOW   THE   WATER "),"follow the water");
  assert.equal(atlas.search("").length,15);
  assert.equal(atlas.search("BOTTLECAP").length,0);
  assert.deepEqual(atlas.search("Heat flows; refrigerators pump it").map(x=>x.id),["heat"]);
  assert.ok(atlas.search("balance").length>=2);
  assert.ok(atlas.search("solar","Energy").some(t=>t.id==="solar"));
  assert.deepEqual(atlas.search("solar","Reasoning"),[]);
  assert.equal(atlas.resolve("toString"),null);
  assert.equal(atlas.resolve("missing"),null);
  assert.equal(reader.idFromHash("#solar",atlas),"solar");
  assert.equal(reader.idFromHash("#%73olar",atlas),"solar");
  assert.equal(reader.idFromHash("#not-a-real-topic",atlas),"systems");
  assert.equal(reader.idFromHash("#%broken",atlas),"systems");
  assert.equal(atlas.linkTo("solar"),"/knowledge/#solar");
});

test("reasoning checks reveal interpretation only when answered and vary answer positions",()=>{
  const distribution=new Set();
  for(const t of atlas.topics){
    const expected=t.check.answer;
    distribution.add(expected);
    const good=atlas.checkAnswer(t.id,expected);
    assert.equal(good.correct,true);
    assert.equal(good.expected,expected);
    assert.equal(good.explanation,t.check.explanation);
    const bad=atlas.checkAnswer(t.id,(expected+1)%3);
    assert.equal(bad.correct,false);
    assert.equal(bad.explanation,t.check.explanation);
  }
  assert.equal(distribution.size,3,"Do not put every correct option in the same position");
  assert.throws(()=>atlas.checkAnswer("unknown",0),/Unknown knowledge topic/);
  assert.throws(()=>atlas.checkAnswer("solar",8),/Invalid answer index/);
});

test("every actual simulator run can explain its numbers, not a decorative outcome",()=>{
  for(const kind of ["rainwater","microgrid"]){
    const defaults=models.defaultValues(kind);
    const result=models.simulate(kind,defaults);
    const steps=lab.interpret(kind,result,defaults);
    assert.equal(steps.length,4);
    assert.ok(steps.every(s=>s.length>80));
    assert.ok(steps.some(s=>s.includes(lab.fmt(result.servedTotal,kind==="rainwater"?1:2))));
    assert.ok(steps.some(s=>s.includes(lab.fmt(result.unmetTotal,kind==="rainwater"?1:2))));
    assert.ok(steps.some(s=>s.includes("model")||s.includes("scenario")));
    assert.ok(steps.some(s=>s.includes("Boundary")));
  }
  assert.throws(()=>lab.interpret("rainwater",{id:"microgrid"},models.defaultValues("rainwater")),/Matching model result/);
  assert.throws(()=>lab.interpret("unknown",{id:"unknown"},{}),/Unknown explanation topic/);
});

test("knowledge page is a complete original reading and retrieval workspace",()=>{
  const html=file("knowledge.html");
  for(const id of ["knowledge-main","knowledge-article","knowledge-search","knowledge-filters","knowledge-topics",
    "knowledge-check-form","knowledge-check-options","knowledge-notes","knowledge-copy-notes","knowledge-links","knowledge-scenario-cards",
    "knowledge-lab","knowledge-source","knowledge-focus","knowledge-sections"]){
    assert.match(html,new RegExp('id="'+id+'"'));
  }
  assert.match(html,/role="status" aria-live="polite"/);
  assert.match(html,/src="\/knowledge-content.js"/);
  assert.match(html,/src="\/knowledge.js"/);
  assert.match(html,/href="\/knowledge.css"/);
  assert.match(html,/no account/i);
  const src=file("knowledge.js");
  assert.match(src,/window\.addEventListener\("hashchange"/);
  assert.match(src,/textContent/);
  assert.match(src,/checkAnswer\(/);
  assert.match(src,/document\.createElement/);
  assert.doesNotMatch(src,/\binnerHTML\b|eval\s*\(|new Function\s*\(|fetch\s*\(/);
  assert.doesNotMatch(src,/\blocalStorage\b|\bsessionStorage\b|indexedDB|WebSocket|sendBeacon|XMLHttpRequest/);
});

test("knowledge paths exist on every destination and its static packaging is locked",()=>{
  const home=file("index.html");
  const library=file("explore-library.html");
  const labHtml=file("exploration.html");
  const common=file("universe.js");
  const build=file("build.py");
  assert.match(home,/id="knowledge-chapters"/);
  assert.match(home,/href="\/knowledge\/#systems"/);
  assert.match(home,/15<\/b> Connected knowledge chapters/);
  assert.match(library,/xlibrary-learn-bridge/);
  assert.match(labHtml,/lab-explain-result/);
  assert.match(labHtml,/lab-theory-links/);
  assert.match(common,/pa-knowledge-prelude/);
  assert.match(common,/href:"\/knowledge\/"/);
  assert.match(common,/pathname\.startsWith\("\/knowledge"\)/);
  assert.match(build,/knowledge\/index\.html/);
  assert.match(build,/knowledge-content\.js/);
  assert.match(build,/write_asset\(stage, "knowledge\/index\.html"/);
  assert.match(file("knowledge.css"),/@media\(max-width:680px\)/);
  assert.match(file("knowledge.css"),/prefers-reduced-motion:reduce/);
  assert.match(file("knowledge.css"),/forced-colors:active/);
});
