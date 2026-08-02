#!/usr/bin/env python3
"""Apply bounded accessible table semantics to Product Alpha Pilot Lab."""
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
    if 'class="table-scroll" role="region"' in html:
        print("Pilot Lab table semantics are already applied.")
        return 0

    html = replace_once(
        html,
        'table{width:100%;border-collapse:collapse;font-size:.9rem}th,td{',
        '.table-scroll{max-width:100%;overflow-x:auto}.table-scroll:focus-visible{outline:3px solid var(--accent);outline-offset:3px}table{width:100%;border-collapse:collapse;font-size:.9rem}caption{caption-side:top;text-align:left;padding:0 0 .5rem;color:var(--muted);font-weight:760}th,td{',
        "Pilot Lab table overflow and caption styles",
    )
    html = replace_once(
        html,
        'box.innerHTML=`<table><thead><tr><th>Session</th><th>Progress</th><th>Duration</th><th>Continue</th></tr></thead><tbody>${state.sessions.map(item=>`<tr><td><code>${escapeHtml(item.session_id)}</code></td><td>${item.completed_steps.length}/5</td><td>${Number(item.duration_minutes).toFixed(1)} min</td><td>${item.voluntary_continue===null?"unknown":item.voluntary_continue?"yes":"no"}</td></tr>`).join("")}</tbody></table>`}',
        'box.innerHTML=`<div class="table-scroll" role="region" aria-label="Loaded session validation ledger" tabindex="0"><table><caption>Loaded anonymous sessions</caption><thead><tr><th scope="col">Session</th><th scope="col">Progress</th><th scope="col">Duration</th><th scope="col">Continue</th></tr></thead><tbody>${state.sessions.map(item=>`<tr><td><code>${escapeHtml(item.session_id)}</code></td><td>${item.completed_steps.length}/5</td><td>${Number(item.duration_minutes).toFixed(1)} min</td><td>${item.voluntary_continue===null?"unknown":item.voluntary_continue?"yes":"no"}</td></tr>`).join("")}</tbody></table></div>`}',
        "Pilot Lab validation ledger semantics",
    )
    html = replace_once(
        html,
        'box.innerHTML=`<table><tbody><tr><th>Started</th><td>${s.started}</td></tr><tr><th>Finished</th><td>${s.finished}</td></tr><tr><th>Completion</th><td>${percent(s.completion_rate)}</td></tr><tr><th>Average duration</th><td>${s.average_duration_minutes.toFixed(2)} min</td></tr>${SCORE_KEYS.map(key=>`<tr><th>${title(key)}</th><td>${s.score_averages[key].toFixed(2)} / 2</td></tr>`).join("")}<tr><th>Continue yes</th><td>${s.voluntary_continue.yes} / ${s.voluntary_continue.answered} answered</td></tr></tbody></table>`;',
        'box.innerHTML=`<table><caption>Cohort aggregate metrics</caption><tbody><tr><th scope="row">Started</th><td>${s.started}</td></tr><tr><th scope="row">Finished</th><td>${s.finished}</td></tr><tr><th scope="row">Completion</th><td>${percent(s.completion_rate)}</td></tr><tr><th scope="row">Average duration</th><td>${s.average_duration_minutes.toFixed(2)} min</td></tr>${SCORE_KEYS.map(key=>`<tr><th scope="row">${title(key)}</th><td>${s.score_averages[key].toFixed(2)} / 2</td></tr>`).join("")}<tr><th scope="row">Continue yes</th><td>${s.voluntary_continue.yes} / ${s.voluntary_continue.answered} answered</td></tr></tbody></table>`;',
        "Pilot Lab aggregate table semantics",
    )

    tests += '''\n
test("dynamic tables expose captions and header relationships", () => {
  assert.match(html, /<caption>Loaded anonymous sessions<\\/caption>/);
  assert.match(html, /<th scope="col">Session<\\/th>/);
  assert.match(html, /<th scope="col">Progress<\\/th>/);
  assert.match(html, /<th scope="col">Duration<\\/th>/);
  assert.match(html, /<th scope="col">Continue<\\/th>/);
  assert.match(html, /<caption>Cohort aggregate metrics<\\/caption>/);
  assert.match(html, /<th scope="row">Started<\\/th>/);
  assert.match(html, /<th scope="row">\\${title\\(key\\)}<\\/th>/);
  assert.match(html, /<th scope="row">Continue yes<\\/th>/);
});

test("wide validation ledger is a keyboard-scrollable named region", () => {
  assert.match(html, /class="table-scroll" role="region" aria-label="Loaded session validation ledger" tabindex="0"/);
  assert.match(html, /\\.table-scroll\\{max-width:100%;overflow-x:auto\\}/);
  assert.match(html, /\\.table-scroll:focus-visible\\{outline:3px solid var\\(--accent\\)/);
});
'''

    HTML_PATH.write_text(html, encoding="utf-8")
    TEST_PATH.write_text(tests, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
