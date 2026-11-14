"use strict";
/* Static website enhancement only: never mutates canonical Principia/Atlas sources. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.PrincipiaWebsiteMath = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", api.mount, { once: true });
    else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const round = (number, places) => Number(number).toFixed(places);
  const finite = (number, label) => {
    if (!Number.isFinite(number)) throw new Error("Non-finite quantity: " + label);
    return number;
  };
  function thermalQuantities(model, values, result) {
    if (!model || !values || !result || !Array.isArray(result.points)) throw new Error("Thermal run required");
    const c = finite(model.thermal_capacitance_j_per_k, "C");
    const ua = finite(values.ua_w_per_k, "UA");
    if (!(c > 0 && ua > 0)) throw new Error("Positive heat capacity and conductance required");
    const cooling = values.cooling_on ? finite(values.cooling_w, "cooling") : 0;
    const power = ua * (values.room_temperature_c - model.initial_temperature_c) + values.load_w - cooling;
    const equilibrium = values.room_temperature_c + (values.load_w - cooling) / ua;
    const tauSeconds = c / ua;
    const tSeconds = model.duration_minutes * 60;
    const analyticFinal = equilibrium + (model.initial_temperature_c - equilibrium) * Math.exp(-tSeconds / tauSeconds);
    const simulatedFinal = result.points[result.points.length - 1].t;
    return {
      cooling, power: finite(power, "initial net power"),
      equilibrium: finite(equilibrium, "equilibrium"),
      tauMinutes: finite(tauSeconds / 60, "time constant"),
      analyticFinal: finite(analyticFinal, "analytic solution"),
      simulatedFinal: finite(simulatedFinal, "Euler result"),
      solverError: finite(simulatedFinal - analyticFinal, "numerical error")
    };
  }
  function queueQuantities(model, values, result) {
    if (!values || !result) throw new Error("Queue run required");
    const offered = finite(values.external_arrival_rate_rps * (1 + values.retry_fraction), "offered");
    const mu = finite(values.service_rate_rps, "capacity");
    const k = finite(values.queue_capacity_requests, "queue capacity");
    const time = finite(values.observation_seconds, "observation");
    if (!(mu > 0 && k > 0 && time > 0)) throw new Error("Positive queue quantities required");
    const net = offered - mu;
    const backlog = Math.min(k, Math.max(0, net * time));
    const rejected = Math.max(0, net * time - k);
    const utilization = offered / mu;
    const mm1Time = offered < mu ? 1 / (mu - offered) : null;
    return {offered, utilization, net, backlog, rejected, mm1Time};
  }
  const MATH_START = '<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"';
  const thermalMath = MATH_START + ' aria-label="Thermal capacitance times temperature rate equals conductive heat input plus internal load minus active cooling power"><mrow><mi>C</mi><mfrac><mrow><mi>d</mi><mi>T</mi></mrow><mrow><mi>d</mi><mi>t</mi></mrow></mfrac><mo>=</mo><mi>U</mi><mi>A</mi><mo>(</mo><msub><mi>T</mi><mtext>room</mtext></msub><mo>−</mo><mi>T</mi><mo>)</mo><mo>+</mo><msub><mi>P</mi><mtext>load</mtext></msub><mo>−</mo><msub><mi>I</mi><mtext>on</mtext></msub><msub><mi>P</mi><mtext>cool</mtext></msub></mrow></math>';
  const queueMath =
    MATH_START + ' aria-label="Offered rate equals external arrival rate times one plus one-pass retry fraction"><mrow><msub><mi>λ</mi><mtext>offered</mtext></msub><mo>=</mo><msub><mi>λ</mi><mtext>external</mtext></msub><mo>(</mo><mn>1</mn><mo>+</mo><msub><mi>p</mi><mtext>retry</mtext></msub><mo>)</mo></mrow></math>' +
    MATH_START + ' aria-label="Utilization equals offered arrival rate divided by service rate"><mrow><mi>ρ</mi><mo>=</mo><mfrac><msub><mi>λ</mi><mtext>offered</mtext></msub><mi>μ</mi></mfrac></mrow></math>' +
    MATH_START + ' aria-label="Backlog equals the minimum of queue capacity and the maximum of zero and excess arrival rate times elapsed time"><mrow><mi>B</mi><mo>(</mo><mi>t</mi><mo>)</mo><mo>=</mo><mi mathvariant="normal">min</mi><mo>(</mo><mi>K</mi><mo>,</mo><mi mathvariant="normal">max</mi><mo>(</mo><mn>0</mn><mo>,</mo><mo>(</mo><msub><mi>λ</mi><mtext>offered</mtext></msub><mo>−</mo><mi>μ</mi><mo>)</mo><mi>t</mi><mo>)</mo><mo>)</mo></mrow></math>' +
    MATH_START + ' aria-label="Rejected requests equals the maximum of zero and excess arrivals over the queue capacity"><mrow><mi>R</mi><mo>(</mo><mi>t</mi><mo>)</mo><mo>=</mo><mi mathvariant="normal">max</mi><mo>(</mo><mn>0</mn><mo>,</mo><mo>(</mo><msub><mi>λ</mi><mtext>offered</mtext></msub><mo>−</mo><mi>μ</mi><mo>)</mo><mi>t</mi><mo>−</mo><mi>K</mi><mo>)</mo></mrow></math>' +
    MATH_START + ' aria-label="Separately, the stationary M M one mean time in system equals one over service rate minus offered arrival rate when offered rate is less than service rate"><mrow><msub><mi>W</mi><mtext>M/M/1</mtext></msub><mo>=</mo><mfrac><mn>1</mn><mrow><mi>μ</mi><mo>−</mo><msub><mi>λ</mi><mtext>offered</mtext></msub></mrow></mfrac><mspace width="0.7em"/><mtext>if </mtext><msub><mi>λ</mi><mtext>offered</mtext></msub><mo>&lt;</mo><mi>μ</mi></mrow></math>';
  const config = {
    refrigerator: {
      title:"Energy balance",
      kicker:"01 / THERMAL DYNAMICS",
      prose:"Heat moves across the cabinet boundary while cooling extracts energy. Every term in the balance is power (watts); C is heat capacity in joules per kelvin.",
      markup:thermalMath,
      reading:"C times dT/dt equals UA times (room temperature minus cabinet temperature), plus internal load, minus cooling power when cooling is enabled.",
      definitions:"C · J/K: thermal capacitance. UA · W/K: heat conductance. T · °C: cabinet temperature. t · seconds. P · W: power. I_on · 0 or 1.",
      caution:"The displayed graph uses explicit Euler steps of 30 seconds. The analytic constant-parameter solution is used only as a cross-check, not as a measured appliance temperature."
    },
    "distributed-information":{
      title:"Capacity and queue balance",
      kicker:"02 / REQUEST DYNAMICS",
      prose:"Two separate models are shown: a bounded, constant-rate fluid queue for backlog and rejected work; and an illustrative stationary M/M/1 formula for mean time in system only below capacity.",
      markup:queueMath,
      reading:"Offered rate is external rate times one plus one-pass retry fraction. Utilization is offered rate divided by service rate. Backlog is the smaller of queue capacity and positive excess requests. Rejected work is overflow beyond that capacity. M/M/1 mean time is one divided by spare service rate only when offered rate is below service rate.",
      definitions:"λ · requests/s: average arrival rate. μ · requests/s: service capacity. p_retry: fraction of external requests retried once. K · requests: queue capacity. B and R · requests. W · seconds.",
      caution:"The fluid queue begins empty and uses constant average rates. The M/M/1 delay relation assumes a different, stochastic steady-state system. A retry here means at most one added attempt per external request; this is not a recursive retry-storm simulation."
    }
  };
  function makeFormulaBoard(routeId) {
    const data = config[routeId];
    if (!data) return "";
    return '<div class="pa-math-heading"><span class="pa-math-tag">' + data.kicker +
      '</span><strong>' + data.title + '</strong><p>' + data.prose + '</p></div>' +
      '<div class="pa-math-typeset">' + data.markup + '</div>' +
      '<div class="pa-math-inspection"><span class="pa-inspection-label">YOUR CURRENT SCENARIO</span><div id="pa-worked" role="status" aria-live="polite" aria-atomic="true">Predict and run the model to reveal the worked calculation.</div></div>' +
      '<details class="pa-math-definitions"><summary>Symbols, units, and assumptions</summary><p>' + data.definitions +
      '</p><p>' + data.caution + '</p><p><strong>Read aloud:</strong> ' + data.reading + '</p></details>';
  }
  function mount() {
    const routeMarker = document.querySelector('meta[name="principia-route"]');
    if (!routeMarker || !config[routeMarker.content]) return;
    const routeId = routeMarker.content;
    const target = document.getElementById("activity");
    if (!target) return;
    let modelPromise = null;
    function getModel() {
      if (!modelPromise) modelPromise = fetch("data/" + routeId + ".json", {cache:"no-store"}).then(function(response) {
        if (!response.ok) throw new Error("Model route unavailable");
        return response.json();
      }).then(function(data) {
        if (data.route_id !== routeId) throw new Error("Model route identity mismatch");
        return data.model;
      });
      return modelPromise;
    }
    async function update() {
      const slot=document.getElementById("pa-worked");
      if (!slot) return;
      const resultView=document.getElementById("modelOutput");
      if (!resultView || resultView.hidden) {
        slot.textContent="Make a prediction and run the model to reveal the numerical result. Your controls can be adjusted first.";
        return;
      }
      try {
        const model=await getModel();
        if (!document.contains(slot) || resultView.hidden) return;
        const values=Object.assign({},model.defaults);
        document.querySelectorAll("[data-model]").forEach(function(input) {
          values[input.dataset.model]=input.type==="checkbox"?input.checked:Number(input.value);
        });
        const adapter=globalThis.PrincipiaModelAdapters.getAdapter(model.adapter);
        const run=adapter.run(model,values);
        const lines=[];
        if(routeId==="refrigerator"){
          const q=thermalQuantities(model,values,run);
          lines.push(["Initial heat-flow balance",round(q.power,2)+" W"]);
          lines.push(["Predicted cabinet after "+model.duration_minutes+" minutes",round(q.simulatedFinal,2)+" °C"]);
          lines.push(["Constant-parameter equilibrium",round(q.equilibrium,2)+" °C"]);
          lines.push(["Characteristic response time",round(q.tauMinutes,1)+" min"]);
          lines.push(["Analytic vs numeric difference",round(Math.abs(q.solverError),4)+" °C"]);
        }else{
          const q=queueQuantities(model,values,run);
          lines.push(["Offered request rate",round(q.offered,2)+" requests/s"]);
          lines.push(["Offered utilization",round(q.utilization*100,1)+"%"]);
          lines.push(["Net input minus capacity",round(q.net,2)+" requests/s"]);
          lines.push(["Fluid backlog at end",round(q.backlog,1)+" requests"]);
          lines.push(["Rejected work at end",round(q.rejected,1)+" requests"]);
          lines.push(["M/M/1 illustrative mean time",q.mm1Time===null?"No finite stationary mean":round(q.mm1Time,3)+" s"]);
        }
        if (!document.contains(slot) || resultView.hidden) return;
        const dl=document.createElement("dl");
        dl.className="pa-math-results";
        lines.forEach(function(line) {
          const row=document.createElement("div");
          const dt=document.createElement("dt"); dt.textContent=line[0];
          const dd=document.createElement("dd"); dd.textContent=line[1];
          row.append(dt,dd);dl.append(row);
        });
        slot.replaceChildren(dl);
      } catch (err) {
        if (document.contains(slot)) slot.textContent="The mathematical inspection is unavailable; the original model and chart remain usable.";
      }
    }
    function enhance() {
      const original=document.getElementById("equation");
      if (!original || original.dataset.paMathEnhanced === "true") return;
      const board=document.createElement("section");
      board.id="equation";
      board.className="pa-math-board";
      board.dataset.paMathEnhanced="true";
      board.setAttribute("aria-label","Mathematical model and worked solution");
      board.innerHTML=makeFormulaBoard(routeId);
      original.replaceWith(board);
      update();
    }
    const observer=new MutationObserver(enhance);
    observer.observe(target,{childList:true});
    enhance();
    document.addEventListener("input",function(event){
      if(event.target && event.target.matches("[data-model]")) queueMicrotask(update);
    });
    document.addEventListener("change",function(event){
      if(event.target && event.target.matches('[name="model-prediction"],[data-model]')) queueMicrotask(update);
    });
    document.addEventListener("click",function(event){
      if(event.target && event.target.closest("#runModel")) queueMicrotask(update);
    });
  }
  return {thermalQuantities,queueQuantities,makeFormulaBoard,mount};
});
