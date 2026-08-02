#!/usr/bin/env python3
"""Apply bounded dynamic accessibility semantics to the learner route."""
from pathlib import Path

HTML_PATH = Path("software/product_alpha/index.html")
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


html = HTML_PATH.read_text(encoding="utf-8")

html = replace_once(
    html,
    '<dialog id="dialog"><form method="dialog"><div class="dialog-head"><div><p class="eyebrow">Trust and provenance</p><h2>Evidence boundary</h2></div><button class="close" value="close" aria-label="Close">×</button></div><p>References are pinned and advisory. Atlas status does not automatically become Principia publication status.</p>',
    '<dialog id="dialog" aria-labelledby="evidenceTitle" aria-describedby="evidenceBoundaryIntro"><form method="dialog"><div class="dialog-head"><div><p class="eyebrow">Trust and provenance</p><h2 id="evidenceTitle">Evidence boundary</h2></div><button class="close" value="close" aria-label="Close">×</button></div><p id="evidenceBoundaryIntro">References are pinned and advisory. Atlas status does not automatically become Principia publication status.</p>',
    "evidence dialog accessible name",
)

html = replace_once(
    html,
    '<svg id="chart" viewBox="0 0 640 250" role="img" aria-label="Predicted cabinet temperature"></svg>',
    '<svg id="chart" viewBox="0 0 640 250" role="img" aria-labelledby="chartTitle chartDescription"><title id="chartTitle">Predicted cabinet temperature</title><desc id="chartDescription">Run the model to generate a temperature prediction.</desc></svg>',
    "thermal chart accessible name",
)

html = replace_once(
    html,
    'const learnerStateApi={createLearnerState,rememberStep,saveNote,invalidateModelState,setModelPrediction,markModelRun,setDiagnosisChoice,markDiagnosisChecked,renderMarkdown:md};',
    'const learnerStateApi={createLearnerState,rememberStep,saveNote,invalidateModelState,setModelPrediction,markModelRun,setDiagnosisChoice,markDiagnosisChecked,renderMarkdown:md,modelResultSummary};',
    "dynamic accessibility test API",
)

html = replace_once(
    html,
    'function renderModelResult(values,prediction){const points=simulate(values);draw(points,values.room_temperature_c);const end=points.at(-1).t,start=points[0].t,trend=displayedTrend(start,end);q("#modelOutput").hidden=false;q("#result").textContent=`Model result: cabinet temperature ${trend} to ${end.toFixed(1)} °C after ${route.model.duration_minutes} minutes.`;q("#modelFeedback").textContent=prediction===trend?"Your prediction matched this simplified model.":"Your prediction differed from this simplified model. Use the graph and equation to explain why."}',
    'function modelResultSummary(points,room,duration){const end=points.at(-1).t,start=points[0].t,trend=displayedTrend(start,end);return{trend,result:`Model result: cabinet temperature ${trend} to ${end.toFixed(1)} °C after ${duration} minutes.`,description:`Cabinet temperature ${trend} from ${start.toFixed(1)} °C to ${end.toFixed(1)} °C over ${duration} minutes. Room temperature reference: ${Number(room).toFixed(1)} °C.`}}\nfunction renderModelResult(values,prediction){const points=simulate(values),summary=modelResultSummary(points,values.room_temperature_c,route.model.duration_minutes);draw(points,values.room_temperature_c,summary.description);q("#modelOutput").hidden=false;q("#result").textContent=summary.result;q("#modelFeedback").textContent=prediction===summary.trend?"Your prediction matched this simplified model.":"Your prediction differed from this simplified model. Use the graph and equation to explain why."}',
    "dynamic thermal result summary",
)

new_draw = '''function draw(p,room,description){const svg=q("#chart"),w=640,h=250,pad=38,temps=p.map(x=>x.t).concat(room),min=Math.floor(Math.min(...temps)-2),max=Math.ceil(Math.max(...temps)+2),x=m=>pad+m/route.model.duration_minutes*(w-pad*2),y=t=>h-pad-(t-min)/(max-min||1)*(h-pad*2),path=p.map((a,i)=>`${i?"L":"M"}${x(a.m).toFixed(1)},${y(a.t).toFixed(1)}`).join(" ");svg.innerHTML=`<title id="chartTitle">Predicted cabinet temperature</title><desc id="chartDescription">${esc(description)}</desc><line x1="${pad}" y1="${h-pad}" x2="${w-pad}" y2="${h-pad}" stroke="#a6afa9"/><line x1="${pad}" y1="${pad}" x2="${pad}" y2="${h-pad}" stroke="#a6afa9"/><line x1="${pad}" y1="${y(room)}" x2="${w-pad}" y2="${y(room)}" stroke="#8a4a14" stroke-dasharray="7 7"/><path d="${path}" fill="none" stroke="#1d5b45" stroke-width="5"/><text x="${pad}" y="${h-10}">0 min</text><text x="${w-pad-55}" y="${h-10}">${route.model.duration_minutes} min</text><text x="8" y="${pad}">${max} °C</text><text x="8" y="${h-pad}">${min} °C</text>`}
'''
html = replace_between(
    html,
    'function draw(p,room){',
    'function diagnosisFeedback(',
    new_draw,
    "thermal chart dynamic description",
)

HTML_PATH.write_text(html, encoding="utf-8")

test_text = TEST_PATH.read_text(encoding="utf-8")
addition = r'''

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
'''
if addition.strip() in test_text:
    raise SystemExit("dynamic accessibility tests already present")
TEST_PATH.write_text(test_text.rstrip() + addition, encoding="utf-8")
