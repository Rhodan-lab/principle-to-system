#!/usr/bin/env python3
"""Apply the bounded facilitator-recorder accessibility patch once."""
from pathlib import Path

HTML_PATH = Path("software/product_alpha/facilitator.html")
TEST_PATH = Path("software/tests/test_product_alpha_facilitator_capture.mjs")


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
    '.button{border:0;border-radius:999px;padding:.72rem 1rem;cursor:pointer}.button:disabled{cursor:not-allowed;opacity:.55}',
    '.button{border:0;border-radius:999px;padding:.72rem 1rem;cursor:pointer}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.button:disabled{cursor:not-allowed;opacity:.55}',
    "facilitator visible-focus contract",
)

html = replace_once(
    html,
    '.measure{padding:1rem;margin:.75rem 0;border:1px solid var(--line);border-radius:.85rem;background:#fff}.measure h3{margin:0 0 .35rem;font-size:1rem}.measure p{margin:.25rem 0;color:var(--muted);font-size:.88rem}.score-row{display:flex;gap:.55rem;margin-top:.7rem}',
    '.measure{min-width:0;padding:1rem;margin:.75rem 0;border:1px solid var(--line);border-radius:.85rem;background:#fff}.measure legend{padding:0 .25rem;font-weight:800;font-size:1rem}.measure p{margin:.25rem 0;color:var(--muted);font-size:.88rem}.score-row{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:.7rem}',
    "facilitator measure-group styling",
)

html = replace_once(
    html,
    '<p class="status" id="status" aria-live="polite"></p>',
    '<p class="status" id="status" role="status" aria-live="polite" aria-atomic="true" tabindex="-1"></p>',
    "facilitator validation status semantics",
)

html = replace_once(
    html,
    'const captureState=createCaptureState(),captureStateApi={createCaptureState,reserveCapture,commitCapture,cancelCapture,markCaptured,startNextSession,captureView};',
    'const captureState=createCaptureState(),captureStateApi={createCaptureState,reserveCapture,commitCapture,cancelCapture,markCaptured,startNextSession,captureView,validationFocusSelector};',
    "facilitator validation test API",
)

new_render_measures = '''function renderMeasures(){const box=q("#measures");box.replaceChildren();Object.entries(rubric.measures).forEach(([key,measure])=>{const card=document.createElement("fieldset"),title=document.createElement("legend"),prompt=document.createElement("p"),evidence=document.createElement("p"),row=document.createElement("div"),promptId=`measure-${key}-prompt`,evidenceId=`measure-${key}-evidence`;card.className="measure";card.setAttribute("aria-describedby",`${promptId} ${evidenceId}`);title.textContent=key.replaceAll("_"," ").replace(/\\b\\w/g,c=>c.toUpperCase());prompt.id=promptId;prompt.textContent=measure.prompt;evidence.id=evidenceId;evidence.textContent=`Score 2 evidence: ${measure.score_2_evidence}`;row.className="score-row";[0,1,2].forEach(score=>{const label=document.createElement("label"),input=document.createElement("input"),span=document.createElement("span");input.type="radio";input.name=`score-${key}`;input.value=String(score);input.checked=score===0;input.addEventListener("change",refresh);span.textContent=String(score);label.append(input,span);row.append(label)});card.append(title,prompt,evidence,row);box.append(card)})}
'''
html = replace_between(
    html,
    'function renderMeasures(){',
    'function renderTags(){',
    new_render_measures,
    "facilitator score fieldsets",
)

html = replace_once(
    html,
    'return errors}\nfunction refresh(){if(!rubric||!template)return;lastRecord=record();q("#preview").textContent=JSON.stringify(lastRecord,null,2)}',
    'return errors}\nfunction validationFocusSelector(value,errors){if(!/^anonymous-[A-Za-z0-9-]+$/.test(value.session_id))return"#sessionId";if(value.completed_steps.length&&!value.started)return"#started";if(!Number.isFinite(value.duration_minutes)||value.duration_minutes<0||value.duration_minutes>180)return"#duration";if(PII_TEXT.some(pattern=>pattern.test(value.facilitator_notes)))return"#notes";return errors.length?"#status":null}\nfunction clearValidationState(){["#sessionId","#duration","#started","#notes"].forEach(selector=>{const node=q(selector);node.removeAttribute("aria-invalid");if(node.getAttribute("aria-describedby")==="status")node.removeAttribute("aria-describedby")})}\nfunction reportValidation(errors,value){clearValidationState();setStatus(errors.join(" "),"error");const selector=validationFocusSelector(value,errors),target=selector?q(selector):q("#status");if(selector&&selector!=="#status"){target.setAttribute("aria-invalid","true");target.setAttribute("aria-describedby","status")}target.focus()}\nfunction refresh(){if(typeof document!=="undefined"){clearValidationState();const status=q("#status");if(status.classList.contains("error"))setStatus("")}if(!rubric||!template)return;lastRecord=record();q("#preview").textContent=JSON.stringify(lastRecord,null,2)}',
    "facilitator validation focus reporting",
)

html = replace_once(
    html,
    'function setStatus(message,kind=""){const node=q("#status");node.textContent=message;node.className=`status ${kind}`}',
    'function setStatus(message,kind=""){const node=q("#status");node.textContent=message;node.className=`status ${kind}`;node.setAttribute("aria-live",kind==="error"?"assertive":"polite")}',
    "facilitator validation announcement priority",
)

error_anchor = 'if(errors.length){setStatus(errors.join(" "),"error");return}'
if html.count(error_anchor) != 2:
    raise SystemExit(
        f"facilitator validation handlers: expected two anchors, found {html.count(error_anchor)}"
    )
html = html.replace(
    error_anchor,
    'if(errors.length){reportValidation(errors,lastRecord);return}',
)

HTML_PATH.write_text(html, encoding="utf-8")

test_text = TEST_PATH.read_text(encoding="utf-8")
test_text = replace_once(
    test_text,
    '  captureView,\n} = sandbox.module.exports;',
    '  captureView,\n  validationFocusSelector,\n} = sandbox.module.exports;',
    "facilitator validation test import",
)
addition = r'''

test("validation directs facilitators to the field that needs correction", () => {
  const valid = {
    session_id: "anonymous-a1",
    completed_steps: [],
    started: true,
    duration_minutes: 10,
    facilitator_notes: "",
  };
  assert.equal(
    validationFocusSelector({ ...valid, session_id: "learner-a1" }, ["label"]),
    "#sessionId",
  );
  assert.equal(
    validationFocusSelector(
      { ...valid, completed_steps: ["observe"], started: false },
      ["started"],
    ),
    "#started",
  );
  assert.equal(
    validationFocusSelector({ ...valid, duration_minutes: 181 }, ["duration"]),
    "#duration",
  );
  assert.equal(
    validationFocusSelector(
      { ...valid, facilitator_notes: "email: learner@example.com" },
      ["identity"],
    ),
    "#notes",
  );
  assert.equal(validationFocusSelector(valid, ["Pilot build ID is invalid"]), "#status");
  assert.equal(validationFocusSelector(valid, []), null);
});

test("score controls are named fieldsets with described rubric evidence", () => {
  assert.match(html, /document\.createElement\("fieldset"\)/);
  assert.match(html, /document\.createElement\("legend"\)/);
  assert.match(html, /card\.setAttribute\("aria-describedby",`\$\{promptId\} \$\{evidenceId\}`\)/);
  assert.match(html, /\.measure legend\{/);
  assert.doesNotMatch(html, /document\.createElement\("section"\),title=document\.createElement\("h3"\)/);
});

test("validation errors are announced, marked, and focused", () => {
  assert.match(html, /id="status" role="status" aria-live="polite" aria-atomic="true" tabindex="-1"/);
  assert.equal((html.match(/reportValidation\(errors,lastRecord\)/g) || []).length, 2);
  assert.match(html, /target\.setAttribute\("aria-invalid","true"\)/);
  assert.match(html, /target\.setAttribute\("aria-describedby","status"\)/);
  assert.match(html, /target\.focus\(\)/);
  assert.match(html, /kind==="error"\?"assertive":"polite"/);
  assert.match(html, /a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible/);
});
'''
if addition.strip() in test_text:
    raise SystemExit("facilitator accessibility tests already present")
TEST_PATH.write_text(test_text.rstrip() + addition, encoding="utf-8")
