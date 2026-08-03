#!/usr/bin/env python3
"""Expose the packaged Product Alpha route in Pilot Lab and its exports."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


path = Path("software/product_alpha/pilot-lab.html")
replace_once(
    path,
    "<title>Principia Product Alpha — Pilot Lab</title>",
    "<title>Principia Product Alpha 0.2 — Pilot Lab</title>",
    "Pilot Lab document title",
)
replace_once(
    path,
    "<small>Product Alpha Pilot Lab</small>",
    "<small>Product Alpha 0.2 Pilot Lab</small>",
    "Pilot Lab visible version",
)
replace_once(
    path,
    '<section class="hero"><div><p class="eyebrow">Local cohort workspace</p><h1>Turn separate anonymous records into reviewable evidence.</h1>',
    '<section class="hero"><div><p class="eyebrow">Local cohort workspace</p><p class="note" id="routeIdentity" role="status" aria-live="polite" aria-atomic="true">Loading packaged route…</p><h1>Turn separate anonymous records into reviewable evidence.</h1>',
    "Pilot Lab visible route status",
)
replace_once(
    path,
    "function takeReplacement(workspace){const staged=workspace.pendingReplacement;workspace.pendingReplacement=[];return staged}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState,stageReplacement,cancelReplacement,takeReplacement};",
    "function takeReplacement(workspace){const staged=workspace.pendingReplacement;workspace.pendingReplacement=[];return staged}\nfunction routeIdentityLabel(routeId){if(routeId===\"refrigerator-v1\")return\"Refrigerator\";if(routeId===\"distributed-information-v1\")return\"Distributed information\";throw new Error(\"unsupported Pilot Lab route identity\")}\nfunction routeFileSlug(routeId){if(routeId===\"refrigerator-v1\")return\"refrigerator\";if(routeId===\"distributed-information-v1\")return\"distributed-information\";throw new Error(\"unsupported Pilot Lab route identity\")}\nfunction pilotLabExportName(routeId,kind){const slug=routeFileSlug(routeId);if(kind===\"summary-markdown\")return`product-alpha-${slug}-pilot-summary.md`;if(kind===\"summary-json\")return`product-alpha-${slug}-pilot-summary.json`;if(kind===\"sessions-jsonl\")return`product-alpha-${slug}-validated-sessions.jsonl`;throw new Error(\"unsupported Pilot Lab export kind\")}\nconst pilotLabStateApi={fileKey,mergeFiles,clearWorkspaceState,stageReplacement,cancelReplacement,takeReplacement,routeIdentityLabel,pilotLabExportName};",
    "Pilot Lab route identity helpers",
)
replace_once(
    path,
    'if(typeof document!=="undefined"){q("#chooseFiles").addEventListener("click",()=>q("#files").click());',
    'if(typeof document!=="undefined"){const routeLabel=routeIdentityLabel(ROUTE_ID);q("#routeIdentity").textContent=`Bound route: ${routeLabel} (${ROUTE_ID})`;document.title=`${routeLabel} · Principia Product Alpha 0.2 Pilot Lab`;q("#chooseFiles").addEventListener("click",()=>q("#files").click());',
    "Pilot Lab route identity initialization",
)
replace_once(
    path,
    'q("#downloadMd").addEventListener("click",()=>download("product-alpha-pilot-summary.md",markdown(state.summary),"text/markdown"));q("#downloadJson").addEventListener("click",()=>download("product-alpha-pilot-summary.json",JSON.stringify(state.summary,null,2)+"\\n","application/json"));q("#downloadJsonl").addEventListener("click",()=>download("product-alpha-validated-sessions.jsonl",state.sessions.map(item=>JSON.stringify(item)).join("\\n")+"\\n","application/x-ndjson"));',
    'q("#downloadMd").addEventListener("click",()=>download(pilotLabExportName(ROUTE_ID,"summary-markdown"),markdown(state.summary),"text/markdown"));q("#downloadJson").addEventListener("click",()=>download(pilotLabExportName(ROUTE_ID,"summary-json"),JSON.stringify(state.summary,null,2)+"\\n","application/json"));q("#downloadJsonl").addEventListener("click",()=>download(pilotLabExportName(ROUTE_ID,"sessions-jsonl"),state.sessions.map(item=>JSON.stringify(item)).join("\\n")+"\\n","application/x-ndjson"));',
    "Pilot Lab route-specific export filenames",
)
