#!/usr/bin/env python3
"""Keep Product Alpha Pilot Lab inert without a valid launcher build identity."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


pilot_lab = Path("software/product_alpha/pilot-lab.html")
replace_once(
    pilot_lab,
    '<p class="workspace-message" id="workspaceStatus" role="status" aria-live="polite" aria-atomic="true">',
    '<p class="workspace-message" id="workspaceStatus" role="status" aria-live="polite" aria-atomic="true" tabindex="-1">',
    "Pilot Lab workspace status focus target",
)
replace_once(
    pilot_lab,
    'function pilotLabExportName(routeId,kind){const slug=routeFileSlug(routeId);if(kind==="summary-markdown")return`product-alpha-${slug}-pilot-summary.md`;if(kind==="summary-json")return`product-alpha-${slug}-pilot-summary.json`;if(kind==="sessions-jsonl")return`product-alpha-${slug}-validated-sessions.jsonl`;throw new Error("unsupported Pilot Lab export kind")}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState,stageReplacement,cancelReplacement,takeReplacement,routeIdentityLabel,pilotLabExportName};',
    'function pilotLabExportName(routeId,kind){const slug=routeFileSlug(routeId);if(kind==="summary-markdown")return`product-alpha-${slug}-pilot-summary.md`;if(kind==="summary-json")return`product-alpha-${slug}-pilot-summary.json`;if(kind==="sessions-jsonl")return`product-alpha-${slug}-validated-sessions.jsonl`;throw new Error("unsupported Pilot Lab export kind")}\nfunction pilotLabAvailability(buildId){const ready=BUILD_ID_PATTERN.test(buildId);return{ready,disabled:!ready}}\nfunction applyPilotLabAvailability(buildId){const view=pilotLabAvailability(buildId);q("#drop").setAttribute("aria-disabled",String(view.disabled));document.querySelectorAll("button,input").forEach(node=>node.disabled=view.disabled);return view.ready}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState,stageReplacement,cancelReplacement,takeReplacement,routeIdentityLabel,pilotLabExportName,pilotLabAvailability};',
    "Pilot Lab availability contract",
)
replace_once(
    pilot_lab,
    'if(typeof document!=="undefined"){const routeLabel=routeIdentityLabel(ROUTE_ID);q("#routeIdentity").textContent=`Bound route: ${routeLabel} (${ROUTE_ID})`;document.title=`${routeLabel} · Principia Product Alpha 0.2 Pilot Lab`;q("#chooseFiles")',
    'if(typeof document!=="undefined"){const routeLabel=routeIdentityLabel(ROUTE_ID);q("#routeIdentity").textContent=`Bound route: ${routeLabel} (${ROUTE_ID})`;document.title=`${routeLabel} · Principia Product Alpha 0.2 Pilot Lab`;if(!applyPilotLabAvailability(EXPECTED_BUILD_ID)){const status=q("#workspaceStatus");status.textContent="Pilot build ID is missing or invalid. Open Pilot Lab from the launcher URL.";status.className="workspace-message warn";status.setAttribute("aria-live","assertive");status.focus()}else{q("#chooseFiles")',
    "Pilot Lab startup build identity guard",
)
replace_once(
    pilot_lab,
    ';render()}\n</script>',
    ';render()}}\n</script>',
    "Pilot Lab guarded startup closure",
)

tests = Path("software/tests/test_product_alpha_pilot_lab_batches.mjs")
replace_once(
    tests,
    '  takeReplacement,\n} = module.exports;',
    '  takeReplacement,\n  pilotLabAvailability,\n} = module.exports;',
    "Pilot Lab availability test import",
)
text = tests.read_text(encoding="utf-8")
addition = r'''

test("Pilot Lab availability requires an exact launcher build identity", () => {
  assert.deepEqual(
    JSON.parse(JSON.stringify(pilotLabAvailability("a".repeat(64)))),
    { ready: true, disabled: false },
  );
  for (const buildId of ["", "not-a-build-id", "A".repeat(64), "a".repeat(63)]) {
    assert.deepEqual(
      JSON.parse(JSON.stringify(pilotLabAvailability(buildId))),
      { ready: false, disabled: true },
    );
  }
});

test("missing or invalid build identity keeps Pilot Lab inert", () => {
  assert.match(html, /id="workspaceStatus" role="status" aria-live="polite" aria-atomic="true" tabindex="-1"/);
  assert.match(html, /function applyPilotLabAvailability\(buildId\)/);
  assert.match(html, /document\.querySelectorAll\("button,input"\)\.forEach\(node=>node\.disabled=view\.disabled\)/);
  assert.match(html, /q\("#drop"\)\.setAttribute\("aria-disabled",String\(view\.disabled\)\)/);

  const guardAt = html.indexOf("if(!applyPilotLabAvailability(EXPECTED_BUILD_ID)){");
  const statusAt = html.indexOf("Pilot build ID is missing or invalid", guardAt);
  const assertiveAt = html.indexOf('status.setAttribute("aria-live","assertive")', statusAt);
  const focusAt = html.indexOf("status.focus()", assertiveAt);
  const elseAt = html.indexOf("}else{", focusAt);
  const handlerAt = html.indexOf('q("#chooseFiles").addEventListener', elseAt);

  assert.notEqual(guardAt, -1);
  assert.ok(guardAt < statusAt, "invalid startup must announce a specific build error");
  assert.ok(statusAt < assertiveAt, "the build error must become assertive");
  assert.ok(assertiveAt < focusAt, "the error must be announced before focus moves");
  assert.ok(focusAt < elseAt, "invalid startup must stay outside the ready branch");
  assert.ok(elseAt < handlerAt, "file handlers must only install for a valid launcher build");
});
'''
if 'test("Pilot Lab availability requires an exact launcher build identity"' in text:
    raise SystemExit("Pilot Lab build identity tests already exist")
tests.write_text(text.rstrip() + addition, encoding="utf-8")
