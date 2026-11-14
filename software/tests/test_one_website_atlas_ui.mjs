import assert from "node:assert/strict";
import test from "node:test";
import {createRequire} from "node:module";
import {readFileSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";

const here=dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const atlas=require("../one_website/atlas-workspace.js");
const js=readFileSync(resolve(here,"../one_website/atlas-workspace.js"),"utf8");
const css=readFileSync(resolve(here,"../one_website/atlas-workspace.css"),"utf8");
const builder=readFileSync(resolve(here,"../one_website/build.py"),"utf8");

test("route palette matches exact accepted route names and groups",()=>{
  assert.equal(atlas.normalize("  Exact    Revision  "),"exact revision");
  const routes=[
    {hash:"#overview",kind:"overview",label:"Workspace overview",index:"01"},
    {hash:"#entry-1",kind:"entry",label:"A claim about recommendation",index:"1"},
    {hash:"#candidates",kind:"candidates",label:"Unresolved candidates",index:"07"},
    {hash:"#evidence",kind:"evidence",label:"Export evidence",index:"12"},
  ];
  assert.equal(atlas.filterRoutes(routes,"").length,4);
  assert.deepEqual(atlas.filterRoutes(routes,"recommendation").map(item=>item.hash),["#entry-1"]);
  assert.deepEqual(atlas.filterRoutes(routes,"UNRESOLVED").map(item=>item.hash),["#candidates"]);
  assert.deepEqual(atlas.filterRoutes(routes,"12").map(item=>item.hash),["#evidence"]);
  assert.equal(atlas.filterRoutes(routes,"missing").length,0);
});

test("route groups preserve exact references without creating new review states",()=>{
  assert.equal(atlas.routeCategory("overview"),"orientation");
  assert.equal(atlas.routeCategory("entry"),"entries");
  assert.equal(atlas.routeCategory("candidates"),"review");
  assert.equal(atlas.routeCategory("principia"),"review");
  assert.equal(atlas.routeCategory("warnings"),"review");
  assert.equal(atlas.routeCategory("questions"),"review");
  assert.equal(atlas.routeCategory("limitations"),"review");
  assert.equal(atlas.routeCategory("evidence"),"exports");
  assert.equal(atlas.routeCategory("summary"),"exports");
  assert.equal(atlas.routeCategory("unknown"),null);
});

test("improved research interface is useful, accessible, and does not fetch remote evidence",()=>{
  assert.match(js,/MutationObserver/);
  assert.match(js,/runtime\.classList\.contains\("ready"\)/);
  assert.match(js,/atlas-research-trail/);
  assert.match(js,/role:"search"/);
  assert.match(js,/role:"tablist"/);
  assert.match(js,/aria-selected/);
  assert.match(js,/atlas-focus-mode/);
  assert.match(js,/atlas-inspector-hidden/);
  assert.match(js,/lastValidHash|routeInfo\(\)/);
  assert.match(js,/document\.addEventListener\("keydown"/);
  assert.doesNotMatch(js,/\bfetch\s*\(/);
  assert.doesNotMatch(js,/\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b|XMLHttpRequest|WebSocket/);
  assert.doesNotMatch(js,/\binnerHTML\b|document\.cookie/);
  assert.doesNotMatch(js,/\bhistory\.pushState\b|\bhistory\.replaceState\b/);
  assert.doesNotMatch(js,/\b(?:eval|Function)\s*\(/);
  assert.doesNotMatch(js,/\bcrypto\.subtle\b/);
  assert.match(builder,/atlas-workspace\.css/);
  assert.match(builder,/atlas-workspace\.js/);
});

test("editorial three-pane interface has mobile, reduced-motion and focus fallbacks",()=>{
  assert.match(css,/\.workspace-grid/);
  assert.match(css,/grid-template-columns:minmax\(210px,262px\)/);
  assert.match(css,/#atlas-research-trail/);
  assert.match(css,/#atlas-inspector/);
  assert.match(css,/\.atlas-search-block/);
  assert.match(css,/@media\(max-width:920px\)/);
  assert.match(css,/@media\(max-width:580px\)/);
  assert.match(css,/prefers-reduced-motion:reduce/);
  assert.match(css,/forced-colors:active/);
  assert.doesNotMatch(css,/@import|url\(\s*["']?https?:/);
});
