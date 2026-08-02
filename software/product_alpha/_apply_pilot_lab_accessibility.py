#!/usr/bin/env python3
"""Apply the bounded Pilot Lab keyboard and clear-safety patch once."""
from pathlib import Path

HTML_PATH = Path("software/product_alpha/pilot-lab.html")
TEST_PATH = Path("software/tests/test_product_alpha_pilot_lab_batches.mjs")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    html = HTML_PATH.read_text(encoding="utf-8")
    tests = TEST_PATH.read_text(encoding="utf-8")

    complete = all(
        marker in html
        for marker in (
            'id="chooseFiles" type="button"',
            "function clearWorkspaceState(workspace)",
            'role="status" aria-live="polite" aria-atomic="true"',
        )
    ) and "clearWorkspaceState } = module.exports" in tests
    if complete:
        print("Pilot Lab accessibility patch is already applied.")
        return 0

    partial_markers = (
        'id="chooseFiles" type="button"',
        "function clearWorkspaceState(workspace)",
        "clearWorkspaceState } = module.exports",
    )
    if any(marker in html or marker in tests for marker in partial_markers):
        raise SystemExit("Pilot Lab accessibility patch is partial; refusing to continue")

    replacements = [
        (
            '.button{display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:999px;padding:.75rem 1rem;cursor:pointer;text-decoration:none;font-weight:760}.primary{background:var(--accent);color:#fff}.secondary{background:transparent;box-shadow:inset 0 0 0 1px var(--line);color:var(--ink)}input[type=file]{position:absolute;inline-size:1px;block-size:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}',
            '.button{display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:999px;padding:.75rem 1rem;cursor:pointer;text-decoration:none;font-weight:760}.button:focus-visible,a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.primary{background:var(--accent);color:#fff}.secondary{background:transparent;box-shadow:inset 0 0 0 1px var(--line);color:var(--ink)}.danger{background:#fff0f0;color:var(--danger);box-shadow:inset 0 0 0 1px #dfb4b4}input[type=file][hidden]{display:none}',
            "Pilot Lab focus and hidden-input styles",
        ),
        (
            '<div class="actions"><label class="button primary" for="files">Add session files</label><input id="files" type="file" accept=".jsonl,.ndjson,.json,text/plain,application/json,application/x-ndjson" multiple><label class="button secondary" for="replaceFiles">Replace workspace files</label><input id="replaceFiles" type="file" accept=".jsonl,.ndjson,.json,text/plain,application/json,application/x-ndjson" multiple><button class="button secondary" id="clear" type="button">Clear workspace</button></div><p class="workspace-message" id="workspaceStatus" aria-live="polite">Workspace empty. Add the first batch of session files.</p>',
            '<div class="actions"><button class="button primary" id="chooseFiles" type="button">Add session files</button><input id="files" type="file" accept=".jsonl,.ndjson,.json,text/plain,application/json,application/x-ndjson" multiple hidden><button class="button secondary" id="chooseReplaceFiles" type="button">Replace workspace files</button><input id="replaceFiles" type="file" accept=".jsonl,.ndjson,.json,text/plain,application/json,application/x-ndjson" multiple hidden><button class="button secondary" id="clear" type="button" aria-pressed="false" aria-describedby="workspaceStatus">Clear workspace</button></div><p class="workspace-message" id="workspaceStatus" role="status" aria-live="polite" aria-atomic="true">Workspace empty. Add the first batch of session files.</p>',
            "Pilot Lab accessible file-picker and clear controls",
        ),
        (
            '<h3>Validation errors</h3><div class="errors" id="errors"><p class="empty">No validation errors.</p></div>',
            '<h3 id="validationErrorsTitle">Validation errors</h3><div class="errors" id="errors" role="region" aria-labelledby="validationErrorsTitle" aria-live="polite"><p class="empty">No validation errors.</p></div>',
            "Pilot Lab live validation errors",
        ),
        (
            '<div class="status incomplete" id="status">Evidence gate incomplete: 0 of 5 valid sessions.</div>',
            '<div class="status incomplete" id="status" role="status" aria-live="polite" aria-atomic="true">Evidence gate incomplete: 0 of 5 valid sessions.</div>',
            "Pilot Lab live cohort status",
        ),
        (
            'const state={files:[],sessions:[],errors:[],duplicates:0,summary:null,workspaceMessage:"Workspace empty. Add the first batch of session files.",workspaceMessageKind:""};',
            'const state={files:[],sessions:[],errors:[],duplicates:0,summary:null,clearArmed:false,workspaceMessage:"Workspace empty. Add the first batch of session files.",workspaceMessageKind:""};',
            "Pilot Lab clear confirmation state",
        ),
        (
            "const pilotLabStateApi={fileKey,mergeFiles};",
            'function clearWorkspaceState(workspace){if(!workspace.files.length){workspace.clearArmed=false;return"empty"}if(!workspace.clearArmed){workspace.clearArmed=true;return"armed"}workspace.files=[];workspace.sessions=[];workspace.errors=[];workspace.duplicates=0;workspace.summary=null;workspace.clearArmed=false;return"cleared"}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState};',
            "Pilot Lab clear state API",
        ),
        (
            'async function readFiles(files,mode="add"){const incoming=[...files];if(!incoming.length)return;const previousCount=state.files.length,replace=mode==="replace";',
            'async function readFiles(files,mode="add"){const incoming=[...files];if(!incoming.length)return;state.clearArmed=false;const previousCount=state.files.length,replace=mode==="replace";',
            "Pilot Lab disarm clear on file load",
        ),
        (
            'function render(){q("#validCount").textContent=state.sessions.length;',
            'function render(){const clear=q("#clear");clear.textContent=state.clearArmed?"Confirm clear workspace":"Clear workspace";clear.classList.toggle("danger",state.clearArmed);clear.setAttribute("aria-pressed",String(state.clearArmed));q("#validCount").textContent=state.sessions.length;',
            "Pilot Lab clear button rendering",
        ),
        (
            'function clearWorkspace(){state.files=[];state.sessions=[];state.errors=[];state.duplicates=0;state.summary=null;state.workspaceMessage="Workspace cleared. Add the first batch of session files.";state.workspaceMessageKind="";q("#files").value="";q("#replaceFiles").value="";render()}',
            'function clearWorkspace(){const outcome=clearWorkspaceState(state);if(outcome==="empty"){state.workspaceMessage="Workspace is already empty. Add the first batch of session files.";state.workspaceMessageKind="";render();return}if(outcome==="armed"){state.workspaceMessage=`Clear ${state.files.length} selected file${state.files.length===1?"":"s"}? Press Confirm clear workspace to erase this in-memory set.`;state.workspaceMessageKind="warn";render();q("#clear").focus();return}state.workspaceMessage="Workspace cleared. Add the first batch of session files.";state.workspaceMessageKind="";q("#files").value="";q("#replaceFiles").value="";render();q("#chooseFiles").focus()}',
            "Pilot Lab two-step clear behavior",
        ),
        (
            'if(typeof document!=="undefined"){q("#files").addEventListener("change",event=>readFiles(event.target.files,"add"));',
            'if(typeof document!=="undefined"){q("#chooseFiles").addEventListener("click",()=>q("#files").click());q("#chooseReplaceFiles").addEventListener("click",()=>q("#replaceFiles").click());q("#files").addEventListener("change",event=>readFiles(event.target.files,"add"));',
            "Pilot Lab keyboard file-picker buttons",
        ),
    ]
    for old, new, label in replacements:
        html = replace_once(html, old, new, label)

    tests = replace_once(
        tests,
        "const { fileKey, mergeFiles } = module.exports;",
        "const { fileKey, mergeFiles, clearWorkspaceState } = module.exports;",
        "Pilot Lab test import",
    )
    old_test = '''test("interface exposes explicit add and replace controls", () => {
  assert.match(html, /for="files">Add session files/);
  assert.match(html, /for="replaceFiles">Replace workspace files/);
  assert.match(html, /readFiles\\(event\\.target\\.files,"add"\\)/);
  assert.match(html, /readFiles\\(event\\.target\\.files,"replace"\\)/);
  assert.match(html, /readFiles\\(event\\.dataTransfer\\.files,"add"\\)/);
  assert.match(html, /id="workspaceStatus" aria-live="polite"/);
});
'''
    new_test = '''test("clear requires a deliberate second action", () => {
  const state = {
    files: [file("anonymous-a.jsonl", 120, 1)],
    sessions: [{ session_id: "anonymous-a" }],
    errors: ["example"],
    duplicates: 1,
    summary: { sessions: 1 },
    clearArmed: false,
  };

  assert.equal(clearWorkspaceState(state), "armed");
  assert.equal(state.clearArmed, true);
  assert.equal(state.files.length, 1);
  assert.equal(clearWorkspaceState(state), "cleared");
  assert.deepEqual(state.files, []);
  assert.deepEqual(state.sessions, []);
  assert.deepEqual(state.errors, []);
  assert.equal(state.duplicates, 0);
  assert.equal(state.summary, null);
  assert.equal(state.clearArmed, false);
});

test("empty workspaces do not arm destructive clear", () => {
  const state = { files: [], clearArmed: true };
  assert.equal(clearWorkspaceState(state), "empty");
  assert.equal(state.clearArmed, false);
});

test("interface exposes keyboard file pickers and live status", () => {
  assert.match(html, /id="chooseFiles" type="button">Add session files/);
  assert.match(html, /id="files"[^>]+multiple hidden/);
  assert.match(html, /id="chooseReplaceFiles" type="button">Replace workspace files/);
  assert.match(html, /id="replaceFiles"[^>]+multiple hidden/);
  assert.match(html, /q\\("#chooseFiles"\\)\\.addEventListener\\("click",\\(\\)=>q\\("#files"\\)\\.click\\(\\)\\)/);
  assert.match(html, /q\\("#chooseReplaceFiles"\\)\\.addEventListener\\("click",\\(\\)=>q\\("#replaceFiles"\\)\\.click\\(\\)\\)/);
  assert.match(html, /readFiles\\(event\\.target\\.files,"add"\\)/);
  assert.match(html, /readFiles\\(event\\.target\\.files,"replace"\\)/);
  assert.match(html, /readFiles\\(event\\.dataTransfer\\.files,"add"\\)/);
  assert.match(html, /id="workspaceStatus" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html, /id="status" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html, /id="errors" role="region"[^>]+aria-live="polite"/);
  assert.match(html, /\\.button:focus-visible,a:focus-visible/);
  assert.doesNotMatch(html, /<label class="button [^"]+" for="(?:files|replaceFiles)"/);
});

test("clear control is announced and visually changes when armed", () => {
  assert.match(html, /id="clear" type="button" aria-pressed="false" aria-describedby="workspaceStatus"/);
  assert.match(html, /Confirm clear workspace/);
  assert.match(html, /clear\\.classList\\.toggle\\("danger",state\\.clearArmed\\)/);
  assert.match(html, /q\\("#chooseFiles"\\)\\.focus\\(\\)/);
});
'''
    tests = replace_once(
        tests,
        old_test,
        new_test,
        "Pilot Lab interface tests",
    )

    HTML_PATH.write_text(html, encoding="utf-8")
    TEST_PATH.write_text(tests, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
