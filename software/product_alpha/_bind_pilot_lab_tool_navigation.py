#!/usr/bin/env python3
"""Preserve Product Alpha build identity across Pilot Lab tool navigation."""
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
    '<a href="facilitator.html">Recorder</a>',
    '<a id="recorderLink" href="#" aria-disabled="true" tabindex="-1">Recorder</a>',
    "Pilot Lab recorder navigation link",
)
replace_once(
    pilot_lab,
    '.button:focus-visible,a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}',
    '.button:focus-visible,a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}a[aria-disabled="true"]{pointer-events:none;opacity:.55}',
    "disabled Pilot Lab tool link styling",
)
replace_once(
    pilot_lab,
    'function pilotLabExportName(routeId,kind){const slug=routeFileSlug(routeId);if(kind==="summary-markdown")return`product-alpha-${slug}-pilot-summary.md`;if(kind==="summary-json")return`product-alpha-${slug}-pilot-summary.json`;if(kind==="sessions-jsonl")return`product-alpha-${slug}-validated-sessions.jsonl`;throw new Error("unsupported Pilot Lab export kind")}\nfunction pilotLabAvailability(buildId)',
    'function pilotLabExportName(routeId,kind){const slug=routeFileSlug(routeId);if(kind==="summary-markdown")return`product-alpha-${slug}-pilot-summary.md`;if(kind==="summary-json")return`product-alpha-${slug}-pilot-summary.json`;if(kind==="sessions-jsonl")return`product-alpha-${slug}-validated-sessions.jsonl`;throw new Error("unsupported Pilot Lab export kind")}\nfunction buildBoundToolUrl(path,buildId){if(path!=="facilitator.html")throw new Error("unsupported Product Alpha tool path");if(!BUILD_ID_PATTERN.test(buildId))throw new Error("invalid Pilot build identity");return`${path}?build_id=${buildId}`}\nfunction pilotLabAvailability(buildId)',
    "build-bound tool URL helper",
)
replace_once(
    pilot_lab,
    'function applyPilotLabAvailability(buildId){const view=pilotLabAvailability(buildId);q("#drop").setAttribute("aria-disabled",String(view.disabled));document.querySelectorAll("button,input").forEach(node=>node.disabled=view.disabled);return view.ready}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState,stageReplacement,cancelReplacement,takeReplacement,routeIdentityLabel,pilotLabExportName,pilotLabAvailability};',
    'function applyPilotLabAvailability(buildId){const view=pilotLabAvailability(buildId),link=q("#recorderLink");q("#drop").setAttribute("aria-disabled",String(view.disabled));document.querySelectorAll("button,input").forEach(node=>node.disabled=view.disabled);link.setAttribute("aria-disabled",String(view.disabled));if(view.disabled)link.setAttribute("tabindex","-1");else{link.removeAttribute("tabindex");link.href=buildBoundToolUrl("facilitator.html",buildId)}return view.ready}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState,stageReplacement,cancelReplacement,takeReplacement,routeIdentityLabel,pilotLabExportName,buildBoundToolUrl,pilotLabAvailability};',
    "build-bound Pilot Lab navigation availability",
)

tests = Path("software/tests/test_product_alpha_pilot_lab_route_identity.mjs")
replace_once(
    tests,
    'const { routeIdentityLabel, pilotLabExportName } = sandbox.module.exports;',
    'const { routeIdentityLabel, pilotLabExportName, buildBoundToolUrl } = sandbox.module.exports;',
    "build-bound navigation test import",
)
text = tests.read_text(encoding="utf-8")
addition = r'''

test("Pilot Lab recorder navigation preserves launcher build identity", () => {
  const buildId = "a".repeat(64);
  assert.equal(
    buildBoundToolUrl("facilitator.html", buildId),
    `facilitator.html?build_id=${buildId}`,
  );
  assert.throws(
    () => buildBoundToolUrl("facilitator.html", "not-a-build-id"),
    /invalid Pilot build identity/,
  );
  assert.throws(
    () => buildBoundToolUrl("unknown.html", buildId),
    /unsupported Product Alpha tool path/,
  );
  assert.match(
    html,
    /id="recorderLink" href="#" aria-disabled="true" tabindex="-1">Recorder/,
  );
  assert.match(html, /a\[aria-disabled="true"\]\{pointer-events:none;opacity:\.55\}/);
  assert.match(
    html,
    /link\.href=buildBoundToolUrl\("facilitator\.html",buildId\)/,
  );
  assert.match(html, /link\.removeAttribute\("tabindex"\)/);
  assert.match(html, /link\.setAttribute\("tabindex","-1"\)/);
});
'''
if 'test("Pilot Lab recorder navigation preserves launcher build identity"' in text:
    raise SystemExit("build-bound Pilot Lab navigation test already exists")
tests.write_text(text.rstrip() + addition, encoding="utf-8")
