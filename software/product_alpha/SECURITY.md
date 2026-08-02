# Product Alpha loopback security boundary

Product Alpha pilot evidence must be collected only through the supported launchers. A bare static server is useful for inspection, but it does not enforce this boundary and must not collect pilot records.

## Supported server contract

`run_pilot.py` and `launch_workspace.py` serve the deterministic build with these controls:

- bind only to `127.0.0.1`;
- accept only the exact `127.0.0.1` Host value, optionally followed by the server's actual port;
- reject a missing or foreign Host value with HTTP `421` before serving a file;
- apply the Host rule to both `GET` and `HEAD`;
- return no response body for a trusted `HEAD` request;
- store no session data;
- bind the facilitator recorder and Pilot Lab to the exact SHA-256 Pilot build ID.

Every accepted and rejected response includes the required policy headers:

- `Cache-Control: no-store`
- `Pragma: no-cache`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: no-referrer`
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: same-origin`
- `X-Frame-Options: DENY`
- `Content-Security-Policy`
- `Permissions-Policy`

The Content Security Policy allows only the existing same-origin static package and its packaged inline scripts and styles. It denies framing, form submission, object loading, and non-local fetches. The Permissions Policy disables unrelated camera, display-capture, geolocation, microphone, payment, serial, and USB capabilities. Clipboard write is intentionally still available because the facilitator recorder can copy one validated JSONL record.

## Pilot-day verification

Run the complete served-output check before preparing or launching a cohort:

```bash
python3 software/product_alpha/run_pilot.py smoke
```

A successful deterministic line includes:

```text
head_verified=true
foreign_host_methods_rejected=GET+HEAD
session_data_stored=false
```

The smoke verifies five accepted `GET` assets, one accepted `HEAD` request, and rejected foreign-Host `GET` and `HEAD` requests. It checks the exact build manifest, packaged markers, all required response headers, and the absence of the learner-page marker in rejected responses.

## Limits

This boundary is local containment, not authentication, encryption, signing, sandboxing, malware protection, or external notarization. It does not protect against a compromised operating system, browser, browser extension, or facilitator account. Keep raw exports and private workspaces outside the repository and under facilitator control.
