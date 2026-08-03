#!/usr/bin/env python3
"""Apply the bounded Product Alpha model-adapter and multi-route shell update."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_between(path: Path, start: str, end: str, replacement: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"{label}: boundary anchors changed")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    path.write_text(before + replacement + end + after, encoding="utf-8")


index = ROOT / "software" / "product_alpha" / "index.html"
replace_once(
    index,
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="principia-route" content="refrigerator">',
    "packaged route marker",
)
old_template = '<template id="modelT"><fieldset class="prediction" id="modelPrediction" aria-describedby="modelFeedback"><legend>Before running the model, predict the cabinet-temperature direction.</legend><label><input type="radio" name="model-prediction" value="falls"> Falls</label><label><input type="radio" name="model-prediction" value="rises"> Rises</label><label><input type="radio" name="model-prediction" value="stays nearly level"> Stays nearly level</label></fieldset><div class="controls"><label>Room temperature <output data-out="room_temperature_c"></output><input data-model="room_temperature_c" type="range" step="1"></label><label>Heat leakage, UA <output data-out="ua_w_per_k"></output><input data-model="ua_w_per_k" type="range" step=".1"></label><label>Internal load <output data-out="load_w"></output><input data-model="load_w" type="range" step="1"></label><label>Cooling capacity <output data-out="cooling_w"></output><input data-model="cooling_w" type="range" step="1"></label><label><input data-model="cooling_on" type="checkbox"> Cooling active</label></div><button class="button primary" id="runModel" type="button">Run model</button><p class="feedback" id="modelFeedback" role="status" aria-live="polite" aria-atomic="true"></p><p class="equation" id="equation"></p><div id="modelOutput" hidden><svg id="chart" viewBox="0 0 640 250" role="img" aria-labelledby="chartTitle chartDescription"><title id="chartTitle">Predicted cabinet temperature</title><desc id="chartDescription">Run the model to generate a temperature prediction.</desc></svg><p class="result" id="result"></p></div><details><summary>Model limitations</summary><ul id="limits"></ul></details></template>'
new_template = '<template id="modelT"><fieldset class="prediction" id="modelPrediction" aria-describedby="modelFeedback"><legend id="modelPredictionLegend"></legend><div id="modelPredictionOptions"></div></fieldset><div class="controls" id="modelControls"></div><button class="button primary" id="runModel" type="button">Run model</button><p class="feedback" id="modelFeedback" role="status" aria-live="polite" aria-atomic="true"></p><p class="equation" id="equation"></p><div id="modelOutput" hidden><svg id="chart" viewBox="0 0 640 250" role="img" aria-labelledby="chartTitle chartDescription"><title id="chartTitle">Predicted model response</title><desc id="chartDescription">Run the model to generate a prediction.</desc></svg><p class="result" id="result"></p></div><details><summary>Model limitations</summary><ul id="limits"></ul></details></template>'
replace_once(index, old_template, new_template, "generic model template")
replace_once(
    index,
    '<script>\n"use strict";',
    '<script src="model-adapters.js"></script>\n<script>\n"use strict";',
    "model adapter script",
)
replace_once(
    index,
    'function activity(name){const box=q("#activity");box.replaceChildren();q("#activityTitle").textContent=name==="model"?"Interactive thermal model":name==="diagnose"?"Diagnosis challenge":"Prediction prompt";if(name==="model")model(box);if(name==="diagnose")challenge(box)}',
    'function activity(name){const box=q("#activity");box.replaceChildren();q("#activityTitle").textContent=name==="model"?route.model.activity_title:name==="diagnose"?"Diagnosis challenge":"Prediction prompt";if(name==="model")model(box);if(name==="diagnose")challenge(box)}',
    "route-driven activity title",
)
new_model_block = '''function modelAdapter(){if(!globalThis.PrincipiaModelAdapters)throw new Error("Model adapters did not load.");return globalThis.PrincipiaModelAdapters.getAdapter(route.model.adapter)}
function modelValues(){const values={...route.model.defaults};document.querySelectorAll("[data-model]").forEach(input=>values[input.dataset.model]=input.type==="checkbox"?input.checked:Number(input.value));return values}
function showModelValues(values){const adapter=modelAdapter();route.model.parameters.forEach(parameter=>{const output=q(`[data-out="${parameter.id}"]`);if(output)output.textContent=adapter.formatValue(route.model,parameter.id,values[parameter.id])})}
function parameterControl(parameter,value){if(parameter.type==="checkbox")return`<label><input data-model="${esc(parameter.id)}" type="checkbox"> ${esc(parameter.label)} <output data-out="${esc(parameter.id)}"></output></label>`;return`<label>${esc(parameter.label)} <output data-out="${esc(parameter.id)}"></output><input data-model="${esc(parameter.id)}" type="range" min="${parameter.minimum}" max="${parameter.maximum}" step="${parameter.step}"></label>`}
function clearChoiceError(groupSelector,feedbackSelector){const group=q(groupSelector),feedback=q(feedbackSelector);group.removeAttribute("aria-invalid");feedback.setAttribute("aria-live","polite")}
function reportChoiceError(groupSelector,feedbackSelector,message){const group=q(groupSelector),feedback=q(feedbackSelector);group.setAttribute("aria-invalid","true");feedback.setAttribute("aria-live","assertive");feedback.textContent=message;const first=typeof group.querySelector==="function"?group.querySelector('input[type="radio"]'):q(`${groupSelector} input[type="radio"]`);if(first&&typeof first.focus==="function")first.focus()}
function hideModelResult(message){clearChoiceError("#modelPrediction","#modelFeedback");q("#modelOutput").hidden=true;q("#result").textContent="";q("#chart").replaceChildren();q("#modelFeedback").textContent=message}
function modelResultSummary(points,room,duration){return globalThis.PrincipiaModelAdapters.thermalResultSummary(points,room,duration)}
function renderModelResult(values,prediction){clearChoiceError("#modelPrediction","#modelFeedback");const adapter=modelAdapter(),result=adapter.run(route.model,values),summary=adapter.summarize(route.model,result),description=adapter.describeChart(route.model,result);adapter.draw(route.model,result,q("#chart"),description);q("#modelOutput").hidden=false;q("#result").textContent=summary.result;q("#modelFeedback").textContent=adapter.matchesPrediction(result,prediction)?"Your prediction matched this simplified model.":"Your prediction differed from this simplified model. Use the graph and equation to explain why."}
function model(box){box.append(q("#modelT").content.cloneNode(true));const config=route.model,values=session.model.values?{...session.model.values}:{...config.defaults};session.model.values={...values};q("#modelPredictionLegend").textContent=config.prediction.legend;q("#modelPredictionOptions").innerHTML=config.prediction.choices.map(choice=>`<label><input type="radio" name="model-prediction" value="${esc(choice.value)}"> ${esc(choice.label)}</label>`).join("");q("#modelControls").innerHTML=config.parameters.map(parameter=>parameterControl(parameter,values[parameter.id])).join("");q("#runModel").textContent=config.run_label||"Run model";q("#equation").textContent=config.equation;q("#limits").innerHTML=config.limitations.map(item=>`<li>${esc(item)}</li>`).join("");document.querySelectorAll("[data-model]").forEach(input=>{const key=input.dataset.model,value=values[key];if(input.type==="checkbox")input.checked=!!value;else input.value=value;input.addEventListener("input",()=>{const next=modelValues();showModelValues(next);invalidateModelState(session,next);document.querySelectorAll('[name="model-prediction"]').forEach(option=>option.checked=false);hideModelResult(config.prediction.initial_message)})});document.querySelectorAll('[name="model-prediction"]').forEach(input=>{input.checked=input.value===session.model.prediction;input.addEventListener("change",()=>{setModelPrediction(session,input.value);hideModelResult(config.prediction.ready_message)})});q("#runModel").onclick=runModel;showModelValues(values);if(session.model.ran&&session.model.prediction)renderModelResult(values,session.model.prediction);else hideModelResult(session.model.prediction?config.prediction.ready_message:config.prediction.initial_message)}
function displayedTrend(start,end){return globalThis.PrincipiaModelAdapters.displayedTrend(start,end)}
function runModel(){const picked=q('input[name="model-prediction"]:checked'),config=route.model;if(!picked){reportChoiceError("#modelPrediction","#modelFeedback",config.prediction.error);return}clearChoiceError("#modelPrediction","#modelFeedback");const values=modelValues();modelAdapter().validate(config,values);session.model.values={...values};setModelPrediction(session,picked.value);markModelRun(session);renderModelResult(values,picked.value)}
'''
replace_between(index, "function modelValues()", "function diagnosisFeedback", new_model_block, "model adapter functions")
replace_once(
    index,
    'async function init(){applyLearnerAvailability("loading");const r=await fetch("data/refrigerator.json",{cache:"no-store"});if(!r.ok)throw Error(`Unable to load route: ${r.status}`);route=await r.json();q("#title").textContent=route.title;q("#subtitle").textContent=route.subtitle;q("#sources").textContent=route.canonical_sources.length;evidence();q("#evidence").removeAttribute("aria-busy");q("#note").addEventListener("input",event=>saveNote(session,active,event.target.value));applyLearnerAvailability("ready");step(order.includes(location.hash.slice(1))?location.hash.slice(1):"observe")}',
    'async function init(){applyLearnerAvailability("loading");const marker=q(\'meta[name="principia-route"]\'),routeId=marker&&marker.content;if(!routeId||!/^[a-z0-9-]+$/.test(routeId))throw Error("Packaged route identity is missing or invalid.");const r=await fetch(`data/${routeId}.json`,{cache:"no-store"});if(!r.ok)throw Error(`Unable to load route: ${r.status}`);route=await r.json();if(route.route_id!==routeId)throw Error("Packaged route identity does not match its payload.");q("#title").textContent=route.title;q("#subtitle").textContent=route.subtitle;q("#sources").textContent=route.canonical_sources.length;evidence();q("#evidence").removeAttribute("aria-busy");q("#note").addEventListener("input",event=>saveNote(session,active,event.target.value));applyLearnerAvailability("ready");step(order.includes(location.hash.slice(1))?location.hash.slice(1):"observe")}',
    "packaged route loading",
)

build = ROOT / "software" / "product_alpha" / "build.py"
replace_once(
    build,
    'STATIC_ASSETS = ("index.html", "facilitator.html", "pilot-lab.html")',
    'STATIC_ASSETS = ("index.html", "model-adapters.js", "facilitator.html", "pilot-lab.html")',
    "adapter static asset",
)
replace_once(
    build,
    'def prepare_static_asset(relative_path: str, data: bytes) -> bytes:\n    """Apply bounded packaging repairs and reject ambiguous asset states."""\n    if relative_path == "facilitator.html":',
    'def prepare_static_asset(relative_path: str, data: bytes, route: str = DEFAULT_ROUTE) -> bytes:\n    """Apply bounded packaging repairs and reject ambiguous asset states."""\n    if relative_path == "index.html":\n        marker = b\'<meta name="principia-route" content="refrigerator">\'\n        replacement = f\'<meta name="principia-route" content="{route}">\'.encode("utf-8")\n        if data.count(marker) != 1:\n            raise ValueError("learner route marker must occur exactly once")\n        return data.replace(marker, replacement, 1)\n    if relative_path == "facilitator.html":',
    "route-bound learner asset",
)
replace_once(
    build,
    'def copy_static_files(root: Path, output: Path) -> list[dict[str, str]]:',
    'def copy_static_files(root: Path, output: Path, route: str = DEFAULT_ROUTE) -> list[dict[str, str]]:',
    "route-aware static copy signature",
)
replace_once(
    build,
    '        data = prepare_static_asset(relative_path, source.read_bytes())',
    '        data = prepare_static_asset(relative_path, source.read_bytes(), route)',
    "route-aware static preparation",
)
replace_once(
    build,
    '    files = copy_static_files(root, output)',
    '    files = copy_static_files(root, output, route)',
    "route-aware build copy",
)
replace_once(
    build,
    '    if len(config["steps"]) != 5:\n        raise ValueError("Product Alpha routes must contain exactly five learner steps")\n    return config',
    '    if len(config["steps"]) != 5:\n        raise ValueError("Product Alpha routes must contain exactly five learner steps")\n    model = config["model"]\n    if model.get("adapter") not in {"thermal-cabinet-v1", "queue-delay-fluid-v1"}:\n        raise ValueError("Product Alpha route model adapter is unsupported")\n    if not isinstance(model.get("parameters"), list) or not model["parameters"]:\n        raise ValueError("Product Alpha route model parameters are required")\n    return config',
    "model adapter config validation",
)

launcher = ROOT / "software" / "product_alpha" / "run_pilot.py"
replace_once(
    launcher,
    'DEFAULT_PORT = 8000\nREPO_ROOT',
    'DEFAULT_PORT = 8000\nDEFAULT_ROUTE = "refrigerator"\nREPO_ROOT',
    "launcher default route",
)
replace_once(
    launcher,
    '    "index.html",\n    "facilitator.html",',
    '    "index.html",\n    "model-adapters.js",\n    "facilitator.html",',
    "launcher adapter requirement",
)
replace_once(
    launcher,
    '        "/data/refrigerator.json",',
    '        "/data/{route_id}.json",',
    "dynamic smoke route path",
)
replace_once(
    launcher,
    'def run_builder(command: str, output: Path = DEFAULT_OUTPUT) -> None:\n    args = [sys.executable, str(BUILD_SCRIPT), command, "--root", str(REPO_ROOT)]\n    if command == "build":\n        args.extend(["--output", str(output)])\n    subprocess.run(args, check=True)',
    'def run_builder(command: str, output: Path = DEFAULT_OUTPUT, route: str = DEFAULT_ROUTE) -> None:\n    args = [sys.executable, str(BUILD_SCRIPT), command, "--root", str(REPO_ROOT)]\n    if route != DEFAULT_ROUTE:\n        args.extend(["--route", route])\n    if command == "build":\n        args.extend(["--output", str(output)])\n    subprocess.run(args, check=True)',
    "route-aware builder invocation",
)
replace_once(
    launcher,
    'def smoke_served_output(output: Path, build_id: str) -> dict[str, object]:',
    'def smoke_served_output(output: Path, build_id: str, route: str = DEFAULT_ROUTE) -> dict[str, object]:',
    "route-aware smoke signature",
)
replace_once(
    launcher,
    '            path = path_template.format(build_id=expected_build_id)',
    '            path = path_template.format(build_id=expected_build_id, route_id=route)',
    "route-aware smoke target",
)
replace_once(
    launcher,
    'def serve(output: Path, port: int, open_browser: bool, quiet: bool) -> None:\n    run_builder("build", output)',
    'def serve(output: Path, port: int, open_browser: bool, quiet: bool, route: str = DEFAULT_ROUTE) -> None:\n    run_builder("build", output, route)',
    "route-aware serve",
)
replace_once(
    launcher,
    '    parser.add_argument("--quiet", action="store_true", help="suppress HTTP request logs")',
    '    parser.add_argument("--quiet", action="store_true", help="suppress HTTP request logs")\n    parser.add_argument("--route", default=DEFAULT_ROUTE, choices=("refrigerator", "distributed-information"), help="learner route to package and serve")',
    "launcher route argument",
)
replace_once(
    launcher,
    '        run_builder("check", output)\n        with tempfile.TemporaryDirectory() as directory:\n            check_output = Path(directory)\n            run_builder("build", check_output)',
    '        run_builder("check", output, args.route)\n        with tempfile.TemporaryDirectory() as directory:\n            check_output = Path(directory)\n            run_builder("build", check_output, args.route)',
    "route-aware launcher check",
)
replace_once(
    launcher,
    '                report = smoke_served_output(check_output, build_id)',
    '                report = smoke_served_output(check_output, build_id, args.route)',
    "route-aware smoke call",
)
replace_once(
    launcher,
    '    serve(output, args.port, args.open_browser, args.quiet)',
    '    serve(output, args.port, args.open_browser, args.quiet, args.route)',
    "route-aware serve call",
)
