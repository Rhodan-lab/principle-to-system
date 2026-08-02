#!/usr/bin/env python3
"""Apply the bounded Pilot Lab replacement-confirmation patch once."""
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
    if "function stageReplacement(workspace,files)" in html:
        print("Pilot Lab replacement confirmation is already applied.")
        return 0

    html = replace_once(
        html,
        '<button class="button secondary" id="chooseReplaceFiles" type="button">Replace workspace files</button><input id="replaceFiles" type="file" accept=".jsonl,.ndjson,.json,text/plain,application/json,application/x-ndjson" multiple hidden><button class="button secondary" id="clear" type="button" aria-pressed="false" aria-describedby="workspaceStatus">Clear workspace</button>',
        '<button class="button secondary" id="chooseReplaceFiles" type="button" aria-pressed="false">Replace workspace files</button><input id="replaceFiles" type="file" accept=".jsonl,.ndjson,.json,text/plain,application/json,application/x-ndjson" multiple hidden><button class="button secondary" id="cancelReplace" type="button" hidden>Cancel replacement</button><button class="button secondary" id="clear" type="button" aria-pressed="false" aria-describedby="workspaceStatus">Clear workspace</button>',
        "Pilot Lab replacement controls",
    )
    html = replace_once(
        html,
        'const state={files:[],sessions:[],errors:[],duplicates:0,summary:null,clearArmed:false,workspaceMessage:"Workspace empty. Add the first batch of session files.",workspaceMessageKind:""};',
        'const state={files:[],sessions:[],errors:[],duplicates:0,summary:null,clearArmed:false,pendingReplacement:[],workspaceMessage:"Workspace empty. Add the first batch of session files.",workspaceMessageKind:""};',
        "Pilot Lab replacement state",
    )
    html = replace_once(
        html,
        'function clearWorkspaceState(workspace){if(!workspace.files.length){workspace.clearArmed=false;return"empty"}if(!workspace.clearArmed){workspace.clearArmed=true;return"armed"}workspace.files=[];workspace.sessions=[];workspace.errors=[];workspace.duplicates=0;workspace.summary=null;workspace.clearArmed=false;return"cleared"}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState};',
        'function clearWorkspaceState(workspace){if(!workspace.files.length){workspace.clearArmed=false;return"empty"}if(!workspace.clearArmed){workspace.clearArmed=true;return"armed"}workspace.files=[];workspace.sessions=[];workspace.errors=[];workspace.duplicates=0;workspace.summary=null;workspace.clearArmed=false;return"cleared"}\nfunction stageReplacement(workspace,files){const staged=mergeFiles([],files,true);workspace.pendingReplacement=staged;workspace.clearArmed=false;return staged.length?"staged":"empty"}\nfunction cancelReplacement(workspace){const had=workspace.pendingReplacement.length>0;workspace.pendingReplacement=[];return had}\nfunction takeReplacement(workspace){const staged=workspace.pendingReplacement;workspace.pendingReplacement=[];return staged}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState,stageReplacement,cancelReplacement,takeReplacement};',
        "Pilot Lab replacement state API",
    )
    html = replace_once(
        html,
        'async function readFiles(files,mode="add"){const incoming=[...files];if(!incoming.length)return;state.clearArmed=false;const previousCount=state.files.length,replace=mode==="replace";',
        'async function readFiles(files,mode="add"){const incoming=[...files];if(!incoming.length)return;state.clearArmed=false;state.pendingReplacement=[];const previousCount=state.files.length,replace=mode==="replace";',
        "Pilot Lab replacement disarm on load",
    )
    html = replace_once(
        html,
        'function render(){const clear=q("#clear");clear.textContent=state.clearArmed?"Confirm clear workspace":"Clear workspace";',
        'function render(){const pending=state.pendingReplacement.length,replace=q("#chooseReplaceFiles"),cancel=q("#cancelReplace");replace.textContent=pending?`Confirm replace with ${pending} file${pending===1?"":"s"}`:"Replace workspace files";replace.classList.toggle("danger",Boolean(pending));replace.setAttribute("aria-pressed",String(Boolean(pending)));cancel.hidden=!pending;const clear=q("#clear");clear.textContent=state.clearArmed?"Confirm clear workspace":"Clear workspace";',
        "Pilot Lab replacement rendering",
    )
    html = replace_once(
        html,
        'function clearWorkspace(){const outcome=clearWorkspaceState(state);',
        'function stageReplacementFiles(files){const incoming=[...files];q("#replaceFiles").value="";if(stageReplacement(state,incoming)==="empty")return;state.workspaceMessage=`Ready to replace the current ${state.files.length} file${state.files.length===1?"":"s"} with ${state.pendingReplacement.length} selected file${state.pendingReplacement.length===1?"":"s"}. The current workspace remains loaded until confirmation.`;state.workspaceMessageKind="warn";render();q("#chooseReplaceFiles").focus()}\nasync function chooseOrConfirmReplacement(){if(!state.pendingReplacement.length){q("#replaceFiles").click();return}const files=takeReplacement(state);await readFiles(files,"replace")}\nfunction cancelReplacementSelection(){if(!cancelReplacement(state))return;state.workspaceMessage="Replacement cancelled. The current workspace is unchanged.";state.workspaceMessageKind="ok";render();q("#chooseReplaceFiles").focus()}\nfunction clearWorkspace(){if(cancelReplacement(state)){state.workspaceMessage="Pending replacement cancelled. Press Clear workspace again to clear the current file set.";state.workspaceMessageKind="warn";render();q("#clear").focus();return}const outcome=clearWorkspaceState(state);',
        "Pilot Lab staged replacement handlers",
    )
    html = replace_once(
        html,
        'if(typeof document!=="undefined"){q("#chooseFiles").addEventListener("click",()=>q("#files").click());q("#chooseReplaceFiles").addEventListener("click",()=>q("#replaceFiles").click());q("#files").addEventListener("change",event=>readFiles(event.target.files,"add"));q("#replaceFiles").addEventListener("change",event=>readFiles(event.target.files,"replace"));',
        'if(typeof document!=="undefined"){q("#chooseFiles").addEventListener("click",()=>q("#files").click());q("#chooseReplaceFiles").addEventListener("click",chooseOrConfirmReplacement);q("#cancelReplace").addEventListener("click",cancelReplacementSelection);q("#files").addEventListener("change",event=>readFiles(event.target.files,"add"));q("#replaceFiles").addEventListener("change",event=>stageReplacementFiles(event.target.files));',
        "Pilot Lab replacement event handlers",
    )

    tests = replace_once(
        tests,
        "const { fileKey, mergeFiles, clearWorkspaceState } = module.exports;",
        "const {\n  fileKey,\n  mergeFiles,\n  clearWorkspaceState,\n  stageReplacement,\n  cancelReplacement,\n  takeReplacement,\n} = module.exports;",
        "Pilot Lab replacement test import",
    )
    insert_before = 'test("clear requires a deliberate second action", () => {'
    replacement_tests = '''test("replacement staging leaves the current workspace untouched", () => {
  const current = file("anonymous-a.jsonl", 120, 1);
  const replacement = file("anonymous-b.jsonl", 130, 2);
  const state = {
    files: [current],
    pendingReplacement: [],
    clearArmed: true,
  };

  assert.equal(
    stageReplacement(state, [replacement, replacement]),
    "staged",
  );
  assert.deepEqual(Array.from(state.files, fileKey), [fileKey(current)]);
  assert.deepEqual(Array.from(state.pendingReplacement, fileKey), [
    fileKey(replacement),
  ]);
  assert.equal(state.clearArmed, false);
});

test("replacement can be cancelled or consumed exactly once", () => {
  const replacement = file("anonymous-b.jsonl", 130, 2);
  const state = { pendingReplacement: [] };

  stageReplacement(state, [replacement]);
  assert.equal(cancelReplacement(state), true);
  assert.deepEqual(Array.from(state.pendingReplacement), []);
  assert.equal(cancelReplacement(state), false);

  stageReplacement(state, [replacement]);
  assert.deepEqual(Array.from(takeReplacement(state), fileKey), [
    fileKey(replacement),
  ]);
  assert.deepEqual(Array.from(state.pendingReplacement), []);
  assert.deepEqual(Array.from(takeReplacement(state)), []);
});

'''
    tests = replace_once(
        tests,
        insert_before,
        replacement_tests + insert_before,
        "Pilot Lab replacement state tests",
    )
    tests = replace_once(
        tests,
        '  assert.match(html, /id="chooseReplaceFiles" type="button">Replace workspace files/);',
        '  assert.match(html, /id="chooseReplaceFiles" type="button" aria-pressed="false">Replace workspace files/);\n  assert.match(html, /id="cancelReplace" type="button" hidden>Cancel replacement/);',
        "Pilot Lab replacement control assertion",
    )
    tests = replace_once(
        tests,
        '  assert.match(html, /q\\("#chooseReplaceFiles"\\)\\.addEventListener\\("click",\\(\\)=>q\\("#replaceFiles"\\)\\.click\\(\\)\\)/);',
        '  assert.match(html, /q\\("#chooseReplaceFiles"\\)\\.addEventListener\\("click",chooseOrConfirmReplacement\\)/);\n  assert.match(html, /q\\("#cancelReplace"\\)\\.addEventListener\\("click",cancelReplacementSelection\\)/);',
        "Pilot Lab replacement click assertions",
    )
    tests = replace_once(
        tests,
        '  assert.match(html, /readFiles\\(event\\.target\\.files,"replace"\\)/);',
        '  assert.match(html, /stageReplacementFiles\\(event\\.target\\.files\\)/);\n  assert.match(html, /takeReplacement\\(state\\)/);\n  assert.match(html, /Replacement cancelled\\. The current workspace is unchanged\\./);',
        "Pilot Lab replacement event assertions",
    )
    tests += '''\n
test("replacement confirmation is explicit and cancellable", () => {
  assert.match(html, /Confirm replace with \\${pending} file/);
  assert.match(html, /current workspace remains loaded until confirmation/);
  assert.match(html, /replace\\.classList\\.toggle\\("danger",Boolean\\(pending\\)\\)/);
  assert.match(html, /replace\\.setAttribute\\("aria-pressed",String\\(Boolean\\(pending\\)\\)\\)/);
  assert.match(html, /cancel\\.hidden=!pending/);
  assert.match(html, /Pending replacement cancelled\\. Press Clear workspace again/);
});
'''

    HTML_PATH.write_text(html, encoding="utf-8")
    TEST_PATH.write_text(tests, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
