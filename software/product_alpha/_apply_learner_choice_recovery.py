#!/usr/bin/env python3
"""Apply bounded learner choice-validation recovery semantics once."""
from pathlib import Path

HTML_PATH = Path("software/product_alpha/index.html")
TEST_PATH = Path("software/tests/test_product_alpha_learner_state.mjs")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


html = HTML_PATH.read_text(encoding="utf-8")

html = replace_once(
    html,
    '.challenge{border:0;padding:0}.challenge label{display:flex;gap:.5rem;padding:.6rem;margin:.45rem 0;border:1px solid var(--line);border-radius:.65rem}',
    '.challenge{border:0;padding:0}.prediction[aria-invalid="true"],.challenge[aria-invalid="true"]{outline:3px solid var(--warn);outline-offset:3px}.challenge label{display:flex;gap:.5rem;padding:.6rem;margin:.45rem 0;border:1px solid var(--line);border-radius:.65rem}',
    "choice-group invalid styling",
)

html = replace_once(
    html,
    '<template id="modelT"><fieldset class="prediction"><legend>Before running the model, predict the cabinet-temperature direction.</legend>',
    '<template id="modelT"><fieldset class="prediction" id="modelPrediction" aria-describedby="modelFeedback"><legend>Before running the model, predict the cabinet-temperature direction.</legend>',
    "model prediction group semantics",
)

html = replace_once(
    html,
    '<p class="feedback" id="modelFeedback" aria-live="polite"></p>',
    '<p class="feedback" id="modelFeedback" role="status" aria-live="polite" aria-atomic="true"></p>',
    "model feedback status semantics",
)

html = replace_once(
    html,
    '<template id="challengeT"><fieldset class="challenge"><legend id="question"></legend>',
    '<template id="challengeT"><fieldset class="challenge" id="diagnosisChoice" aria-describedby="feedback"><legend id="question"></legend>',
    "diagnosis group semantics",
)

html = replace_once(
    html,
    '<p class="feedback" id="feedback" aria-live="polite"></p></template>',
    '<p class="feedback" id="feedback" role="status" aria-live="polite" aria-atomic="true"></p></template>',
    "diagnosis feedback status semantics",
)

html = replace_once(
    html,
    'function hideModelResult(message){q("#modelOutput").hidden=true;q("#result").textContent="";q("#chart").replaceChildren();q("#modelFeedback").textContent=message}',
    'function clearChoiceError(groupSelector,feedbackSelector){const group=q(groupSelector),feedback=q(feedbackSelector);group.removeAttribute("aria-invalid");feedback.setAttribute("aria-live","polite")}\nfunction reportChoiceError(groupSelector,feedbackSelector,message){const group=q(groupSelector),feedback=q(feedbackSelector);group.setAttribute("aria-invalid","true");feedback.setAttribute("aria-live","assertive");feedback.textContent=message;const first=group.querySelector(\'input[type="radio"]\');if(first&&typeof first.focus==="function")first.focus()}\nfunction hideModelResult(message){clearChoiceError("#modelPrediction","#modelFeedback");q("#modelOutput").hidden=true;q("#result").textContent="";q("#chart").replaceChildren();q("#modelFeedback").textContent=message}',
    "learner choice error helpers",
)

html = replace_once(
    html,
    'function renderModelResult(values,prediction){const points=simulate(values),summary=modelResultSummary(points,values.room_temperature_c,route.model.duration_minutes);draw(points,values.room_temperature_c,summary.description);q("#modelOutput").hidden=false;q("#result").textContent=summary.result;q("#modelFeedback").textContent=prediction===summary.trend?"Your prediction matched this simplified model.":"Your prediction differed from this simplified model. Use the graph and equation to explain why."}',
    'function renderModelResult(values,prediction){clearChoiceError("#modelPrediction","#modelFeedback");const points=simulate(values),summary=modelResultSummary(points,values.room_temperature_c,route.model.duration_minutes);draw(points,values.room_temperature_c,summary.description);q("#modelOutput").hidden=false;q("#result").textContent=summary.result;q("#modelFeedback").textContent=prediction===summary.trend?"Your prediction matched this simplified model.":"Your prediction differed from this simplified model. Use the graph and equation to explain why."}',
    "model result clears choice error",
)

html = replace_once(
    html,
    'function runModel(){const picked=q(\'input[name="model-prediction"]:checked\');if(!picked){q("#modelFeedback").textContent="Choose whether the temperature will fall, rise, or stay nearly level before running the model.";return}const values=modelValues();session.model.values={...values};setModelPrediction(session,picked.value);markModelRun(session);renderModelResult(values,picked.value)}',
    'function runModel(){const picked=q(\'input[name="model-prediction"]:checked\');if(!picked){reportChoiceError("#modelPrediction","#modelFeedback","Choose whether the temperature will fall, rise, or stay nearly level before running the model.");return}clearChoiceError("#modelPrediction","#modelFeedback");const values=modelValues();session.model.values={...values};setModelPrediction(session,picked.value);markModelRun(session);renderModelResult(values,picked.value)}',
    "model choice recovery",
)

html = replace_once(
    html,
    'function challenge(box){const c=route.learner_steps.diagnose.challenge;box.append(q("#challengeT").content.cloneNode(true));q("#question").textContent=c.question;const options=q("#options");options.innerHTML=c.options.map((x,i)=>`<label><input type="radio" name="d" value="${i}"><span>${esc(x)}</span></label>`).join("");document.querySelectorAll(\'input[name="d"]\').forEach(i=>i.checked=Number(i.value)===session.diagnosis.choice);options.addEventListener("change",()=>{const picked=q(\'input[name="d"]:checked\');if(picked)setDiagnosisChoice(session,Number(picked.value));q("#feedback").textContent=""});if(session.diagnosis.checked)q("#feedback").textContent=diagnosisFeedback(c,session.diagnosis.choice);q("#check").onclick=()=>{const picked=q(\'input[name="d"]:checked\');if(picked)setDiagnosisChoice(session,Number(picked.value));markDiagnosisChecked(session);q("#feedback").textContent=diagnosisFeedback(c,session.diagnosis.choice)}}',
    'function challenge(box){const c=route.learner_steps.diagnose.challenge;box.append(q("#challengeT").content.cloneNode(true));q("#question").textContent=c.question;const options=q("#options");options.innerHTML=c.options.map((x,i)=>`<label><input type="radio" name="d" value="${i}"><span>${esc(x)}</span></label>`).join("");document.querySelectorAll(\'input[name="d"]\').forEach(i=>i.checked=Number(i.value)===session.diagnosis.choice);options.addEventListener("change",()=>{const picked=q(\'input[name="d"]:checked\');if(picked)setDiagnosisChoice(session,Number(picked.value));clearChoiceError("#diagnosisChoice","#feedback");q("#feedback").textContent=""});if(session.diagnosis.checked)q("#feedback").textContent=diagnosisFeedback(c,session.diagnosis.choice);q("#check").onclick=()=>{const picked=q(\'input[name="d"]:checked\');if(!picked){reportChoiceError("#diagnosisChoice","#feedback","Choose a diagnosis first.");return}clearChoiceError("#diagnosisChoice","#feedback");setDiagnosisChoice(session,Number(picked.value));markDiagnosisChecked(session);q("#feedback").textContent=diagnosisFeedback(c,session.diagnosis.choice)}}',
    "diagnosis choice recovery",
)

HTML_PATH.write_text(html, encoding="utf-8")

test_text = TEST_PATH.read_text(encoding="utf-8")
addition = r'''

test("model and diagnosis groups expose validation relationships",()=>{
  assert.match(html,/<fieldset class="prediction" id="modelPrediction" aria-describedby="modelFeedback">/);
  assert.match(html,/id="modelFeedback" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html,/<fieldset class="challenge" id="diagnosisChoice" aria-describedby="feedback">/);
  assert.match(html,/id="feedback" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html,/\.prediction\[aria-invalid="true"\],\.challenge\[aria-invalid="true"\]/);
});

test("choice validation marks the group and focuses its first radio",()=>{
  assert.match(html,/function reportChoiceError\(groupSelector,feedbackSelector,message\)/);
  assert.match(html,/group\.setAttribute\("aria-invalid","true"\)/);
  assert.match(html,/feedback\.setAttribute\("aria-live","assertive"\)/);
  assert.match(html,/group\.querySelector\('input\[type="radio"\]'\)/);
  assert.match(html,/first&&typeof first\.focus==="function"\)first\.focus\(\)/);
  assert.match(html,/function clearChoiceError\(groupSelector,feedbackSelector\)/);
  assert.match(html,/group\.removeAttribute\("aria-invalid"\)/);
  assert.match(html,/feedback\.setAttribute\("aria-live","polite"\)/);
});

test("model and diagnosis reject empty choices before recording completion",()=>{
  const runModelSource=html.match(/function runModel\(\)\{([\s\S]*?)\}\nfunction simulate/);
  assert.ok(runModelSource,"runModel source must be testable");
  assert.match(runModelSource[1],/if\(!picked\)\{reportChoiceError\("#modelPrediction","#modelFeedback"/);
  assert.ok(runModelSource[1].indexOf("reportChoiceError(")<runModelSource[1].indexOf("markModelRun(session)"));

  const challengeSource=html.match(/function challenge\(box\)\{([\s\S]*?)\}\nfunction evidence/);
  assert.ok(challengeSource,"challenge source must be testable");
  assert.match(challengeSource[1],/if\(!picked\)\{reportChoiceError\("#diagnosisChoice","#feedback","Choose a diagnosis first\."\);return\}/);
  assert.ok(challengeSource[1].indexOf("reportChoiceError(")<challengeSource[1].indexOf("markDiagnosisChecked(session)"));
  assert.match(challengeSource[1],/clearChoiceError\("#diagnosisChoice","#feedback"\)/);
});
'''
if addition.strip() in test_text:
    raise SystemExit("learner choice recovery tests already present")
TEST_PATH.write_text(test_text.rstrip() + addition, encoding="utf-8")
