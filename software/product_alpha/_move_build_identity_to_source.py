#!/usr/bin/env python3
"""Move Product Alpha build-identity runtime behavior from packaging transforms into source assets."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


facilitator = Path("software/product_alpha/facilitator.html")
replace_once(
    facilitator,
    'const q=s=>document.querySelector(s);let rubric=null,template=null,lastRecord=null;',
    'const BUILD_ID_PATTERN=/^[0-9a-f]{64}$/,q=s=>document.querySelector(s);let rubric=null,template=null,lastRecord=null,pilotBuildId=new URLSearchParams(location.search).get("build_id")||"";',
    "facilitator build-id state",
)
replace_once(
    facilitator,
    'return{session_id:q("#sessionId").value.trim(),',
    'return{pilot_build_id:pilotBuildId,session_id:q("#sessionId").value.trim(),',
    "facilitator session build-id field",
)
replace_once(
    facilitator,
    'function validate(value){const errors=[];if(!/^anonymous-[A-Za-z0-9-]+$/.test(value.session_id))',
    'function validate(value){const errors=[];if(!BUILD_ID_PATTERN.test(value.pilot_build_id))errors.push("Pilot build ID is missing or invalid. Open the recorder from run_pilot.py.");if(!/^anonymous-[A-Za-z0-9-]+$/.test(value.session_id))',
    "facilitator build-id validation",
)
replace_once(
    facilitator,
    'q("#sessionId").value=anonymousId();[q("#sessionId")',
    'q("#sessionId").value=anonymousId();if(!BUILD_ID_PATTERN.test(pilotBuildId))setStatus("Pilot build ID is missing. Open this recorder from the launcher URL.","error");[q("#sessionId")',
    "facilitator missing-build warning",
)

pilot_lab = Path("software/product_alpha/pilot-lab.html")
replace_once(
    pilot_lab,
    '"use strict";\nconst ROUTE_ID=',
    '"use strict";\nconst BUILD_ID_PATTERN=/^[0-9a-f]{64}$/,EXPECTED_BUILD_ID=new URLSearchParams(location.search).get("build_id")||"";\nconst ROUTE_ID=',
    "Pilot Lab build-id state",
)
replace_once(
    pilot_lab,
    'if(found.length)fail(`${label}: personal-data fields are not allowed: ${found.join(", ")}.`);if(session.route_id!==ROUTE_ID)fail(',
    'if(found.length)fail(`${label}: personal-data fields are not allowed: ${found.join(", ")}.`);if(!BUILD_ID_PATTERN.test(session.pilot_build_id))fail(`${label}: pilot_build_id must be a 64-character lowercase SHA-256.`);if(EXPECTED_BUILD_ID&&session.pilot_build_id!==EXPECTED_BUILD_ID)fail(`${label}: pilot_build_id does not match the launcher build.`);if(session.route_id!==ROUTE_ID)fail(',
    "Pilot Lab build-id validation",
)
replace_once(
    pilot_lab,
    'state.duplicates=0;const seen=new Set;for(const file of state.files)',
    'state.duplicates=0;const seen=new Set;let cohortBuildId=EXPECTED_BUILD_ID||null;for(const file of state.files)',
    "Pilot Lab cohort build state",
)
replace_once(
    pilot_lab,
    'session=validateSession(parsed,label);if(seen.has(session.session_id))',
    'session=validateSession(parsed,label);if(cohortBuildId&&session.pilot_build_id!==cohortBuildId)fail(`${label}: pilot_build_id does not match the cohort build.`);cohortBuildId=session.pilot_build_id;if(seen.has(session.session_id))',
    "Pilot Lab mixed-build rejection",
)
replace_once(
    pilot_lab,
    'const summary={contract:"principia-product-alpha-pilot-summary/0.2",route_id:ROUTE_ID,',
    'const summary={contract:"principia-product-alpha-pilot-summary/0.3",pilot_build_id:sessions[0].pilot_build_id,route_id:ROUTE_ID,',
    "Pilot Lab summary build identity",
)
replace_once(
    pilot_lab,
    'box.innerHTML=`<table><caption>Cohort aggregate metrics</caption><tbody><tr><th scope="row">Started</th>',
    'box.innerHTML=`<table><caption>Cohort aggregate metrics</caption><tbody><tr><th scope="row">Build ID</th><td><code>${s.pilot_build_id.slice(0,12)}...</code></td></tr><tr><th scope="row">Started</th>',
    "Pilot Lab build-id display",
)
replace_once(
    pilot_lab,
    '"- Evidence status: **"+s.evidence_status+"**","- Route: `"+s.route_id+"`",',
    '"- Evidence status: **"+s.evidence_status+"**","- Pilot build ID: `"+s.pilot_build_id+"`","- Route: `"+s.route_id+"`",',
    "Pilot Lab Markdown build identity",
)

build = Path("software/product_alpha/build.py")
text = build.read_text(encoding="utf-8")
start = text.index("FACILITATOR_TRANSFORMS = (")
end = text.index("@dataclass(frozen=True)")
text = text[:start] + text[end:]
text = text.replace(
    '''def _replace_once(data: bytes, old: bytes, new: bytes, label: str) -> bytes:\n    old_count = data.count(old)\n    new_count = data.count(new)\n    if old_count == 1 and new_count == 0:\n        return data.replace(old, new, 1)\n    if old_count == 0 and new_count == 1:\n        return data\n    raise ValueError(f"{label} must contain exactly one canonical state")\n\n\n''',
    "",
    1,
)
text = text.replace(
    '''    if relative_path == "facilitator.html":\n        for old, new, label in FACILITATOR_TRANSFORMS:\n            data = _replace_once(data, old, new, label)\n        return data\n''',
    '''    if relative_path == "facilitator.html":\n        return data\n''',
    1,
)
text = text.replace(
    '''    for old, new, label in PILOT_LAB_TRANSFORMS:\n        data = _replace_once(data, old, new, label)\n    return data\n''',
    '''    return data\n''',
    1,
)
text = text.replace(
    '    """Apply bounded route packaging transforms and reject ambiguous asset states."""',
    '    """Apply route packaging and reject ambiguous asset states."""',
    1,
)
if "FACILITATOR_TRANSFORMS" in text or "PILOT_LAB_TRANSFORMS" in text or "def _replace_once" in text:
    raise SystemExit("build transform cleanup incomplete")
build.write_text(text, encoding="utf-8")

tests = Path("software/tests/test_product_alpha_cohort_binding.py")
replace_once(
    tests,
    '''        source_pilot_lab = (\n            ROOT / "software" / "product_alpha" / "pilot-lab.html"\n        ).read_text(encoding="utf-8")\n''',
    '''        source_root = ROOT / "software" / "product_alpha"\n        source_facilitator = (source_root / "facilitator.html").read_text(encoding="utf-8")\n        source_pilot_lab = (source_root / "pilot-lab.html").read_text(encoding="utf-8")\n''',
    "source asset fixtures",
)
replace_once(
    tests,
    '''        self.assertIn("pilot_build_id:pilotBuildId", facilitator)\n        self.assertIn('new URLSearchParams(location.search).get("build_id")', facilitator)\n        self.assertIn("Pilot build ID is missing or invalid", facilitator)\n\n        self.assertIn("EXPECTED_BUILD_ID", pilot_lab)\n''',
    '''        for asset in (source_facilitator, facilitator):\n            self.assertIn("pilot_build_id:pilotBuildId", asset)\n            self.assertIn('new URLSearchParams(location.search).get("build_id")', asset)\n            self.assertIn("Pilot build ID is missing or invalid", asset)\n\n        for asset in (source_pilot_lab, pilot_lab):\n            self.assertIn("EXPECTED_BUILD_ID", asset)\n            self.assertIn("pilot_build_id does not match the cohort build", asset)\n            self.assertIn("principia-product-alpha-pilot-summary/0.3", asset)\n\n        self.assertIn("EXPECTED_BUILD_ID", pilot_lab)\n''',
    "source and package build identity assertions",
)
replace_once(
    tests,
    '''        self.assertIn("pilot_build_id does not match the cohort build", pilot_lab)\n        self.assertIn("principia-product-alpha-pilot-summary/0.3", pilot_lab)\n        self.assertIn(",q=s=>document.querySelector(s);", source_pilot_lab)\n''',
    '''        self.assertIn(",q=s=>document.querySelector(s);", source_pilot_lab)\n''',
    "remove duplicate package assertions",
)
