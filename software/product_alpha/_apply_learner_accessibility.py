#!/usr/bin/env python3
"""Apply the bounded learner-route accessibility patch once."""
from pathlib import Path

INDEX_PATH = Path("software/product_alpha/index.html")
TEST_PATH = Path("software/tests/test_product_alpha_learner_state.mjs")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_between(text: str, start: str, end: str, replacement: str, label: str) -> str:
    start_count = text.count(start)
    end_count = text.count(end)
    if start_count != 1 or end_count != 1:
        raise SystemExit(
            f"{label}: expected one start/end anchor, found {start_count}/{end_count}"
        )
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[:start_index] + replacement + text[end_index:]


html = INDEX_PATH.read_text(encoding="utf-8")

html = replace_once(
    html,
    '.button{border:0;border-radius:999px;padding:.75rem 1.1rem;cursor:pointer;text-decoration:none}.button:disabled{cursor:not-allowed;opacity:.55}',
    '.button{border:0;border-radius:999px;padding:.75rem 1.1rem;cursor:pointer;text-decoration:none}a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.button:disabled{cursor:not-allowed;opacity:.55}',
    "learner visible-focus contract",
)

html = replace_once(
    html,
    '.content table{width:100%;border-collapse:collapse;font-size:.9rem}.content th,.content td{border-bottom:1px solid var(--line);padding:.5rem;text-align:left;vertical-align:top}',
    '.content .table-scroll{overflow-x:auto;border-radius:.7rem}.content .table-scroll:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.content table{width:100%;min-width:32rem;border-collapse:collapse;font-size:.9rem}.content th,.content td{border-bottom:1px solid var(--line);padding:.5rem;text-align:left;vertical-align:top}',
    "learner table-scroll styling",
)

html = replace_once(
    html,
    'const learnerStateApi={createLearnerState,rememberStep,saveNote,invalidateModelState,setModelPrediction,markModelRun,setDiagnosisChoice,markDiagnosisChecked};',
    'const learnerStateApi={createLearnerState,rememberStep,saveNote,invalidateModelState,setModelPrediction,markModelRun,setDiagnosisChoice,markDiagnosisChecked,renderMarkdown:md};',
    "learner renderer test API",
)

new_flush = '''const flushTable=()=>{if(!rows.length)return;const clean=rows.filter(r=>!r.every(c=>/^-+$/.test(c)));if(!clean.length){rows=[];return}const firstHeader=clean[0][0]||"Learner",label=`${firstHeader} reference table`;out.push(`<div class="table-scroll" role="region" aria-label="${esc(label)}" tabindex="0"><table><caption class="sr-only">${esc(label)}</caption>`);clean.forEach((r,i)=>{out.push(`<tr>${r.map((cell,j)=>i===0?`<th scope="col">${inline(cell)}</th>`:j===0?`<th scope="row">${inline(cell)}</th>`:`<td>${inline(cell)}</td>`).join("")}</tr>`)});out.push("</table></div>");rows=[]};'''
html = replace_between(
    html,
    'const flushTable=()=>{',
    'for(const raw of text.split("\\n")){',
    new_flush,
    "learner Markdown table renderer",
)

INDEX_PATH.write_text(html, encoding="utf-8")

test_text = TEST_PATH.read_text(encoding="utf-8")
addition = r'''

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
'''
if addition.strip() in test_text:
    raise SystemExit("learner accessibility tests already present")
TEST_PATH.write_text(test_text.rstrip() + addition, encoding="utf-8")
