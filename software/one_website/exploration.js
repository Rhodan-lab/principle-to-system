"use strict";
/* Interactive educational workbench. Model source: exploration-models.js. */
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  root.PrincipiaExploration=api;
  if(typeof document!=="undefined"){
    if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",api.mount,{once:true});
    else api.mount();
  }
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  function fmt(value,precision=1){
    if(!Number.isFinite(value))throw new TypeError("Finite numerical output required");
    return Number(value).toFixed(precision);
  }
  function plotPath(values,maxValue){
    if(!Array.isArray(values)||!values.length||!Number.isFinite(maxValue)||maxValue<=0)throw new RangeError("Valid chart series required");
    return values.map((v,i)=>{
      if(!Number.isFinite(v)||v<0||v>maxValue+1e-6)throw new RangeError("Chart point outside bounds");
      const x=62+i*590/Math.max(1,values.length-1);
      const y=220-v/maxValue*172;
      return (i===0?"M":"L")+fmt(x,2)+" "+fmt(y,2);
    }).join(" ");
  }
  function metricValue(result){return fmt(result.primary,1)+"%"}
  function addSvg(node,tag,attrs,text){
    const el=document.createElementNS("http://www.w3.org/2000/svg",tag);
    for(const [key,value]of Object.entries(attrs||{}))el.setAttribute(key,String(value));
    if(text!==undefined)el.textContent=text;
    node.append(el);return el;
  }
  function mount(){
    const meta=document.querySelector('meta[name="exploration-id"]');
    if(!meta||!globalThis.PrincipiaExplorationModels)return;
    const catalog=globalThis.PrincipiaExplorationModels;
    const config=catalog.DRAFTS[meta.content];
    if(!config)return;
    const $=id=>document.getElementById(id);
    const state={baseline:null,current:null,prediction:null};
    const form=$("lab-form"),inputs=$("lab-controls"),choices=$("lab-prediction-options");
    $("lab-title").firstChild.textContent=config.label;
    $("lab-deck").textContent=config.subtitle;
    $("lab-eyebrow").textContent=config.eyebrow+" / FIELD LABORATORY";
    $("lab-crumb-name").textContent=config.label;
    $("lab-question").textContent=config.question;
    $("lab-intro").textContent=config.intro;
    $("lab-hypothesis").textContent=config.hypothesis;
    $("lab-formula").textContent=config.formula;
    $("lab-formula-explain").textContent=config.formulaExplain;
    $("lab-mode").textContent=config.mode;
    $("lab-risks").textContent=config.risks;
    $("lab-source").href=config.source;
    $("lab-source").textContent=config.sourceLabel+" ↗";
    $("lab-glyph-label").textContent=config.id==="rainwater"?"CAPTURE / STORAGE / OVERFLOW":"SUNLIGHT / BATTERY / LOAD";
    $("lab-prediction-legend").textContent=config.hypothesis;

    function create(tag,cls,text){
      const element=document.createElement(tag);if(cls)element.className=cls;
      if(text!==undefined)element.textContent=text;return element;
    }
    for(const c of config.controls){
      const row=create("div","lab-control");
      const label=create("label","lab-control-label",c.label),val=create("output","lab-control-value");
      let field;
      field=create(c.type==="select"?"select":"input","lab-control-field");
      field.id="lab-input-"+c.id;field.dataset.labControl=c.id;
      label.htmlFor=field.id;
      if(c.type==="select"){
        for(const [key,text]of c.options){const option=create("option","",text);option.value=key;field.append(option)}
        field.value=c.default;
      }else{
        field.type="range";field.min=String(c.min);field.max=String(c.max);field.step=String(c.step);field.value=String(c.default);
        field.setAttribute("aria-describedby","lab-range-"+c.id);
      }
      const help=create("span","lab-control-help",c.type==="range"?"Bounded hypothetical parameter":"Synthetic event sequence");
      help.id="lab-range-"+c.id;
      row.append(label,val,field,help);
      inputs.append(row);
      function refresh(){
        if(c.type==="select")val.textContent=field.options[field.selectedIndex]?.textContent||"";
        else val.textContent=fmt(Number(field.value),Number.isInteger(c.step)?0:2)+(c.unit?" "+c.unit:"");
      }
      field.addEventListener("input",()=>{refresh();invalidate()});
      refresh();
    }
    config.prediction.forEach((text,index)=>{
      const label=create("label","lab-prediction-option");
      const radio=create("input");radio.type="radio";radio.name="exploration-prediction";radio.value=String(index);
      const span=create("span","",text);label.append(radio,span);choices.append(label);
      radio.addEventListener("change",()=>{state.prediction=index;$("lab-prediction-group").removeAttribute("aria-invalid");$("lab-status").textContent="Prediction ready. Run your scenario to reveal the result."});
    });
    function values(){
      const obj={};
      for(const c of config.controls){
        const field=$("lab-input-"+c.id);
        obj[c.id]=c.type==="select"?field.value:Number(field.value);
      }
      return obj;
    }
    function invalidate(){
      state.current=null;
      state.prediction=null;
      choices.querySelectorAll('input[type="radio"]').forEach(r=>r.checked=false);
      $("lab-prediction-group").removeAttribute("aria-invalid");
      $("lab-output").hidden=true;$("lab-state").textContent="SCENARIO CHANGED";
      $("lab-result-intro").textContent="The inputs changed. Make a new prediction, then run the model again.";
      $("lab-status").textContent="Inputs updated. Select a prediction to run the changed scenario.";
      $("lab-save").disabled=true;
      $("lab-comparison").hidden=true;
    }
    function draw(result){
      const svg=$("lab-chart");
      while(svg.lastChild)svg.removeChild(svg.lastChild);
      addSvg(svg,"title",{id:"lab-chart-access-title"},result.chartLabel+" across "+result.steps+" modeled steps");
      addSvg(svg,"desc",{id:"lab-chart-access-desc"},"Synthetic state values, from "+fmt(result.rows[0].stored)+" to "+fmt(result.stored)+" "+result.chartUnit+", with maximum "+fmt(result.graphMax)+".");
      for(let tick=0;tick<=4;tick++){
        const y=220-tick*43;
        addSvg(svg,"line",{x1:62,y1:y,x2:658,y2:y,stroke:"#e5e5dc","stroke-width":1});
        addSvg(svg,"text",{x:48,y:y+4,"text-anchor":"end",fill:"#8e938b","font-size":11},fmt(result.graphMax*tick/4,0));
      }
      for(const [i,item]of result.rows.entries()){
        const x=62+i*590/Math.max(1,result.rows.length-1);
        addSvg(svg,"text",{x,y:243,"text-anchor":"middle",fill:"#777f73","font-size":10},String(i+1));
      }
      addSvg(svg,"line",{x1:62,y1:220-result.reference/result.graphMax*172,
        x2:658,y2:220-result.reference/result.graphMax*172,stroke:"#d09a7b",
        "stroke-dasharray":"5 5","stroke-width":1.5});
      const values=result.rows.map(x=>x.stored);
      addSvg(svg,"path",{d:plotPath(values,result.graphMax),fill:"none",stroke:"#4a7560","stroke-width":3,
        "stroke-linecap":"round","stroke-linejoin":"round"});
      for(let i=0;i<values.length;i++){
        const x=62+i*590/Math.max(1,values.length-1);
        const y=220-values[i]/result.graphMax*172;
        addSvg(svg,"circle",{cx:x,cy:y,r:4.2,fill:"#fffdfa",stroke:"#4a7560","stroke-width":2});
      }
      $("lab-chart-note").textContent=result.id==="rainwater"
        ?"Solid line: tank water after daily demand. Dashed line: tank capacity. No water-quality or installation claim."
        :"Solid line: battery stored energy at end of each hour. Dashed line: fixed 10% energy reserve. No grid or electrical-protection model.";
    }
    function table(result){
      const tbody=$("lab-table-body");tbody.replaceChildren();
      const isWater=result.id==="rainwater";
      $("lab-input-head").textContent=isWater?"Rain (mm)":"Irradiance (W/m²)";
      for(const row of result.rows){
        const tr=create("tr");
        const cells=[
          row.label,fmt(row.input,0),
          fmt(row.capture,isWater?1:2),fmt(row.served,isWater?1:2),
          fmt(row.stored,isWater?1:2),fmt(row.overflow,isWater?1:2),
          fmt(row.unmet,isWater?1:2)
        ];
        cells.forEach((value,i)=>{
          const cell=create(i===0?"th":"td","",value);
          if(i===0)cell.scope="row";
          tr.append(cell);
        });tbody.append(tr);
      }
    }
    function comparison(){
      const base=state.baseline,now=state.current;
      const panel=$("lab-comparison");
      panel.hidden=!base||!now;
      if(!base||!now)return;
      const delta=now.primary-base.primary;
      $("lab-comparison-label").textContent="Same scenario model · percentage of demand served (percentage-point difference). No measured effect or isolated causal claim.";
      $("lab-before").textContent=metricValue(base);
      $("lab-after").textContent=metricValue(now);
      $("lab-difference").textContent=(delta>=0?"+":"")+fmt(delta,1)+" pp";
    }
    form.addEventListener("submit",event=>{
      event.preventDefault();
      const checked=choices.querySelector('input[name="exploration-prediction"]:checked');
      if(!checked){
        $("lab-prediction-group").setAttribute("aria-invalid","true");
        $("lab-status").textContent="Make a prediction first so you can compare it with the model outcome.";
        choices.querySelector('input[type="radio"]')?.focus();
        return;
      }
      try{
        const prediction=Number(checked.value);
        const result=catalog.simulate(config.id,values());
        state.current=result;
        $("lab-output").hidden=false;
        $("lab-state").textContent="SCENARIO COMPUTED";
        $("lab-result-intro").textContent="This is what the bounded, synthetic scenario computes—not a measurement of a real system.";
        $("lab-primary-label").textContent=result.headline;
        $("lab-primary").textContent=metricValue(result);
        $("lab-secondary-label").textContent=result.secondaryLabel;
        $("lab-secondary").textContent=fmt(result.secondary,1)+" "+result.secondaryUnit;
        $("lab-tertiary-label").textContent=result.tertiaryLabel;
        $("lab-tertiary").textContent=fmt(result.tertiary,1)+" "+result.tertiaryUnit;
        $("lab-chart-title").textContent=result.chartLabel;
        draw(result);table(result);
        $("lab-feedback").textContent=prediction===result.prediction
          ?"Your prediction matches this simplified model. Now inspect its conditions and limits."
          :"Your prediction differs from this simplified model. Inspect the time steps to discover where the mismatch begins.";
        $("lab-status").textContent="Simulation complete. Review the results or save this run as a baseline.";
        $("lab-save").disabled=false;
        comparison();
        $("lab-result").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion:reduce)").matches?"instant":"smooth",block:"start"});
      }catch(error){
        $("lab-output").hidden=true;
        $("lab-status").textContent="The model could not calculate this input. Check the controls.";
      }
    });
    $("lab-save").addEventListener("click",()=>{
      if(!state.current)return;
      state.baseline=state.current;
      $("lab-clear").disabled=false;
      $("lab-save").disabled=true;
      $("lab-comparison").hidden=true;
      $("lab-status").textContent="Baseline saved in this tab. Change an input, predict again, then run.";
    });
    $("lab-clear").addEventListener("click",()=>{
      state.baseline=null;$("lab-clear").disabled=true;$("lab-comparison").hidden=true;
      $("lab-status").textContent="Baseline cleared. You may save a new run.";
    });
  }
  return {fmt,plotPath,mount};
});
