"use strict";
/* Principia & Atlas / read-only, dependency-free discovery studio. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.PrincipiaHomePreview = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", api.mount, { once: true });
    else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function thermalPreview(coolingWatts) {
    const power = Number(coolingWatts);
    if (!Number.isFinite(power) || power < 0) throw new RangeError("Cooling power must be nonnegative");
    const roomTemperatureC=28, initialTemperatureC=8, conductanceWPerK=3.2, internalLoadW=18;
    const initialPowerW=conductanceWPerK*(roomTemperatureC-initialTemperatureC)+internalLoadW-power;
    const equilibriumC=roomTemperatureC+(internalLoadW-power)/conductanceWPerK;
    return {initialPowerW,equilibriumC};
  }
  function queuePreview(retryFraction) {
    const fraction=Number(retryFraction);
    if (!Number.isFinite(fraction) || fraction<0 || fraction>1) throw new RangeError("One-pass retry fraction must be 0 to 1");
    const external=7.5, service=10, duration=30, capacity=50;
    const offered=external*(1+fraction);
    const utilization=offered/service;
    const backlog=Math.min(capacity,Math.max(0,(offered-service)*duration));
    const rejected=Math.max(0,(offered-service)*duration-capacity);
    return {offered,utilization,backlog,rejected};
  }
  const mathOpen='<math xmlns="http://www.w3.org/1998/Math/MathML" display="block" ';
  const previewMath={
    thermal:mathOpen+'aria-label="Net heat input equals conductance times room minus initial temperature, plus internal load minus active cooling power"><mrow><msub><mi>P</mi><mtext>net</mtext></msub><mo>=</mo><mi>U</mi><mi>A</mi><mo>(</mo><msub><mi>T</mi><mtext>room</mtext></msub><mo>−</mo><msub><mi>T</mi><mn>0</mn></msub><mo>)</mo><mo>+</mo><msub><mi>P</mi><mtext>load</mtext></msub><mo>−</mo><msub><mi>P</mi><mtext>cool</mtext></msub></mrow></math>',
    queue:mathOpen+'aria-label="Offered requests equals external requests times one plus one-pass retry fraction, utilization equals offered rate divided by service rate"><mrow><msub><mi>λ</mi><mtext>offered</mtext></msub><mo>=</mo><msub><mi>λ</mi><mtext>external</mtext></msub><mo>(</mo><mn>1</mn><mo>+</mo><msub><mi>p</mi><mtext>retry</mtext></msub><mo>)</mo><mo>;</mo><mspace width="1em"/><mi>ρ</mi><mo>=</mo><mfrac><msub><mi>λ</mi><mtext>offered</mtext></msub><mi>μ</mi></mfrac></mrow></math>',
    evidence:mathOpen+'aria-label="Source revision identity is distinct from publication approval"><mrow><mtext>revision identity</mtext><mspace width="0.6em"/><mo>≠</mo><mspace width="0.6em"/><mtext>publication approval</mtext></mrow></math>'
  };
  const lenses={
    thermal:{
      tag:"EXPERIMENT / 01",field:"THERMAL EQUILIBRIUM",
      title:"What if the refrigerator loses cooling?",
      explanation:"Change cooling power and inspect the instant heat balance. A negative net flow means the cabinet initially tends to cool; this does not measure a real appliance.",
      label:"Cooling power",help:"Hypothetical scenario · room 28 °C · cabinet 8 °C · UA 3.2 W/K · internal load 18 W",
      min:"40",max:"180",step:"5",
      caveat:"This is an instantaneous balance, not a full trajectory. The guided lab uses a finite-time model and clearly states its limits.",
      url:"/learn/refrigerator/",action:"Investigate thermal systems"
    },
    queue:{
      tag:"EXPERIMENT / 02",field:"QUEUE CAPACITY",
      title:"When do retries overload a service?",
      explanation:"Add one retry attempt for a fraction of incoming requests. More offered work can exceed a service's processing capacity.",
      label:"Fraction retried once",help:"Hypothetical scenario · 7.5 external requests/s · 10 service slots/s · 50 queued-request limit · 30 s",
      min:"0",max:"1",step:"0.05",
      caveat:"A one-pass retry approximation with constant average rates—not a recursive retry storm or a prediction of a production service.",
      url:"/learn/distributed-information/",action:"Investigate service failures"
    },
    evidence:{
      tag:"RESEARCH / 03",field:"EXACT REVISION",
      title:"Does a connected claim become verified?",
      explanation:"A claim can be cross-referenced without inheriting approval, correctness, or human verification. Atlas keeps its own revision and review boundary.",
      caveat:"The published Atlas is a pinned accepted fixture. It is read-only and must not be confused with a live, fully reviewed knowledge corpus.",
      url:"/research/",action:"Inspect exact evidence"
    }
  };
  const signed=(value,digits)=>String((value<0?"−":"") + Math.abs(value).toFixed(digits));
  function mount(){
    const tabs=Array.from(document.querySelectorAll('[role="tab"][data-lens]'));
    const slider=document.getElementById("studio-input");
    if (!tabs.length || !slider) return;
    const q=id=>document.getElementById(id);
    const saved={thermal:95,queue:.1};
    let current="thermal";
    function output(){
      const val=Number(slider.value);
      if(current==="thermal"){
        saved.thermal=val;
        const result=thermalPreview(val);
        q("lens-slider-value").textContent=val.toFixed(0)+" W";
        q("lens-result-label").textContent="Initial net heat flow";
        q("lens-result-value").textContent=signed(result.initialPowerW,2)+" W";
        q("lens-secondary-label").textContent="Equilibrium under fixed conditions";
        q("lens-secondary-value").textContent=signed(result.equilibriumC,2)+" °C";
      }else if(current==="queue"){
        saved.queue=val;
        const result=queuePreview(val);
        q("lens-slider-value").textContent=val.toFixed(2);
        q("lens-result-label").textContent="Offered utilization";
        q("lens-result-value").textContent=(100*result.utilization).toFixed(1)+"%";
        q("lens-secondary-label").textContent="Fluid backlog after 30 s";
        q("lens-secondary-value").textContent=result.backlog.toFixed(1)+" requests";
      }
    }
    function setLens(next,focus){
      if (!lenses[next]) return;
      current=next;
      const definition=lenses[next];
      tabs.forEach(function(tab){
        const selected=tab.dataset.lens===next;
        tab.setAttribute("aria-selected",String(selected));
        tab.tabIndex=selected?0:-1;
        if(focus && selected) tab.focus();
      });
      q("lens-tag").textContent=definition.tag;
      q("lens-field").textContent=definition.field;
      q("lens-title").textContent=definition.title;
      q("lens-explanation").textContent=definition.explanation;
      q("lens-caveat").textContent=definition.caveat;
      q("lens-math").innerHTML=previewMath[next];
      q("lens-action").href=definition.url;
      q("lens-action").firstChild.textContent=definition.action+" ";
      const controls=q("studio-controls");
      controls.hidden=next==="evidence";
      if(next==="evidence"){
        q("lens-result-label").textContent="Source identity";
        q("lens-result-value").textContent="Exact revision";
        q("lens-secondary-label").textContent="Publication authority";
        q("lens-secondary-value").textContent="Independent";
        return;
      }
      slider.min=definition.min;
      slider.max=definition.max;
      slider.step=definition.step;
      slider.value=String(saved[next]);
      q("lens-slider-label").textContent=definition.label;
      q("lens-slider-help").textContent=definition.help;
      output();
    }
    tabs.forEach(function(tab,index){
      tab.addEventListener("click",function(){setLens(tab.dataset.lens,false)});
      tab.addEventListener("keydown",function(event){
        let nextIndex;
        if(event.key==="ArrowRight"||event.key==="ArrowDown")nextIndex=(index+1)%tabs.length;
        else if(event.key==="ArrowLeft"||event.key==="ArrowUp")nextIndex=(index-1+tabs.length)%tabs.length;
        else if(event.key==="Home")nextIndex=0;
        else if(event.key==="End")nextIndex=tabs.length-1;
        else return;
        event.preventDefault();
        setLens(tabs[nextIndex].dataset.lens,true);
      });
    });
    slider.addEventListener("input",output);
    setLens("thermal",false);
  }
  return {thermalPreview,queuePreview,mount};
});
