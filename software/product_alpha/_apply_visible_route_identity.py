#!/usr/bin/env python3
"""Expose Product Alpha 0.2 and the recorder's packaged route identity."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


learner = Path("software/product_alpha/index.html")
replace_once(
    learner,
    "<small>Product Alpha 0.1</small>",
    "<small>Product Alpha 0.2</small>",
    "learner visible product version",
)

facilitator = Path("software/product_alpha/facilitator.html")
replace_once(
    facilitator,
    "<title>Principia Product Alpha — Pilot Recorder</title>",
    "<title>Principia Product Alpha 0.2 — Pilot Recorder</title>",
    "recorder document title",
)
replace_once(
    facilitator,
    '<section class="hero"><p class="eyebrow">Product Alpha 0.1</p><h1>Record a learner session without collecting identity.</h1>',
    '<section class="hero"><p class="eyebrow">Product Alpha 0.2</p><p class="hint" id="routeIdentity" role="status" aria-live="polite" aria-atomic="true">Loading packaged route…</p><h1>Record a learner session without collecting identity.</h1>',
    "recorder visible version and route status",
)
replace_once(
    facilitator,
    'function recorderAvailability(state){if(!["loading","ready","error"].includes(state))throw new Error("invalid recorder availability");return{busy:state==="loading",disabled:state!=="ready"}}\nconst captureState=createCaptureState(),captureStateApi={createCaptureState,reserveCapture,commitCapture,cancelCapture,markCaptured,startNextSession,captureView,recorderAvailability,validationFocusSelector};',
    'function recorderAvailability(state){if(!["loading","ready","error"].includes(state))throw new Error("invalid recorder availability");return{busy:state==="loading",disabled:state!=="ready"}}\nfunction routeIdentityLabel(routeId){if(routeId==="refrigerator-v1")return"Refrigerator";if(routeId==="distributed-information-v1")return"Distributed information";throw new Error("unsupported recorder route identity")}\nfunction assertRecorderRouteIdentity(rubricValue,templateValue){const routeId=templateValue&&templateValue.route_id,supported=templateValue&&templateValue.supported_route_ids;if(!Array.isArray(supported)||!supported.includes(routeId))throw new Error("unsupported recorder route identity");if(!rubricValue||rubricValue.route_id!==routeId)throw new Error("recorder route assets do not match");return routeId}\nconst captureState=createCaptureState(),captureStateApi={createCaptureState,reserveCapture,commitCapture,cancelCapture,markCaptured,startNextSession,captureView,recorderAvailability,validationFocusSelector,routeIdentityLabel,assertRecorderRouteIdentity};',
    "recorder route identity helpers",
)
replace_once(
    facilitator,
    'async function init(){applyRecorderAvailability("loading");try{[rubric,template]=await Promise.all([fetch("evaluation/rubric.json").then(r=>{if(!r.ok)throw new Error("rubric");return r.json()}),fetch("evaluation/session-template.json").then(r=>{if(!r.ok)throw new Error("template");return r.json()})]);renderSteps();',
    'async function init(){applyRecorderAvailability("loading");try{[rubric,template]=await Promise.all([fetch("evaluation/rubric.json").then(r=>{if(!r.ok)throw new Error("rubric");return r.json()}),fetch("evaluation/session-template.json").then(r=>{if(!r.ok)throw new Error("template");return r.json()})]);const routeId=assertRecorderRouteIdentity(rubric,template),routeLabel=routeIdentityLabel(routeId);q("#routeIdentity").textContent=`Bound route: ${routeLabel} (${routeId})`;document.title=`${routeLabel} · Principia Product Alpha 0.2 Recorder`;renderSteps();',
    "recorder route identity initialization",
)
replace_once(
    facilitator,
    'applyCaptureState();refresh()}catch{applyRecorderAvailability("error");q("#preview").textContent="Recorder assets could not be loaded.";setStatus("Serve the Product Alpha build through a local HTTP server before using the recorder.","error");q("#status").focus()}}',
    'applyCaptureState();refresh()}catch{applyRecorderAvailability("error");q("#routeIdentity").textContent="Route identity unavailable.";q("#preview").textContent="Recorder assets could not be loaded or did not match.";setStatus("Serve the Product Alpha build through a local HTTP server and confirm its route assets match before using the recorder.","error");q("#status").focus()}}',
    "recorder route identity failure",
)
