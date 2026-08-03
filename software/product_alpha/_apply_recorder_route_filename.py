#!/usr/bin/env python3
"""Include the packaged route in Product Alpha recorder download filenames."""
from pathlib import Path

PATH = Path("software/product_alpha/facilitator.html")
text = PATH.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    'function routeIdentityLabel(routeId){if(routeId==="refrigerator-v1")return"Refrigerator";if(routeId==="distributed-information-v1")return"Distributed information";throw new Error("unsupported recorder route identity")}\nfunction assertRecorderRouteIdentity',
    'function routeIdentityLabel(routeId){if(routeId==="refrigerator-v1")return"Refrigerator";if(routeId==="distributed-information-v1")return"Distributed information";throw new Error("unsupported recorder route identity")}\nfunction routeFileSlug(routeId){if(routeId==="refrigerator-v1")return"refrigerator";if(routeId==="distributed-information-v1")return"distributed-information";throw new Error("unsupported recorder route identity")}\nfunction recorderExportName(routeId,sessionId){if(!/^anonymous-[A-Za-z0-9-]+$/.test(sessionId))throw new Error("invalid anonymous session label");return`product-alpha-${routeFileSlug(routeId)}-${sessionId}.jsonl`}\nfunction assertRecorderRouteIdentity',
    "recorder filename helpers",
)
replace_once(
    'validationFocusSelector,routeIdentityLabel,assertRecorderRouteIdentity};',
    'validationFocusSelector,routeIdentityLabel,recorderExportName,assertRecorderRouteIdentity};',
    "recorder filename helper export",
)
replace_once(
    'link.download=`${value.session_id}.jsonl`;',
    'link.download=recorderExportName(value.route_id,value.session_id);',
    "recorder route-specific download",
)
replace_once(
    'The downloaded file contains one compact JSON object and can be combined with other session lines for <code>summarize.py</code>.',
    'The downloaded filename includes the bound route and anonymous session label. The file contains one compact JSON object and can be combined with other session lines for <code>summarize.py</code>.',
    "recorder filename explanation",
)

PATH.write_text(text, encoding="utf-8")
