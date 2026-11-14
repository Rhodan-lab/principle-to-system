"use strict";
/* Pure educational, synthetic models. Not Product Alpha routes. */
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  root.PrincipiaExplorationModels=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  const RAIN={
    mixed:[0,4,15,0,9,3,0,12],
    dry:[3,0,0,0,0,0,0,0],
    storm:[0,0,8,46,65,0,0,5]
  };
  const SOLAR={
    clear:[0,100,300,520,730,870,940,900,740,500,210,0],
    overcast:[0,60,145,300,400,360,500,340,280,120,30,0],
    shaded:[0,100,300,230,170,340,480,400,270,500,210,0]
  };
  const DRAFTS={
    rainwater:{
      id:"rainwater",label:"The rainwater buffer",subtitle:"How much can a finite reservoir really save?",
      eyebrow:"WATER / FLOWS & STORAGE",tag:"Conceptual design lab",
      intro:"Storms arrive in bursts. Demand arrives every day. Explore what happens between them through a simple non-potable storage model.",
      question:"Can a smaller tank meet demand during a dry spell?",
      hypothesis:"Predict whether the scenario meets every day's demand, then run the model.",
      formula:"S(next) = min(K, max(0, S + captured − served))",
      formulaExplain:"Captured = rainfall in millimeters × area in square meters × runoff fraction, giving liters. Served = min(demand, storage + capture). Overflow is anything exceeding tank capacity after demand.",
      mode:"A synthetic eight-day sequence. An initially empty, sealed non-potable tank, with daily rainfall arriving before daily demand. No evaporation, leakage or first-flush loss is included.",
      risks:"Conceptual simulation only. Do not drink or use this water for food or connect to potable plumbing. Real catchment, drainage, contamination, mosquito protection, structure and local rules require qualified review.",
      source:"https://github.com/Rhodan-lab/principle-to-system/blob/main/design-challenges/nonpotable-rainwater-buffer.md",
      sourceLabel:"Read Principia's non-potable rainwater challenge",
      prediction:["Every day's non-potable demand is served","At least one day has unmet demand"],
      controls:[
        {id:"pattern",label:"Rainfall sequence",type:"select",options:[["mixed","Intermittent rain"],["dry","Dry spell"],["storm","Intense storm"]],default:"mixed"},
        {id:"area",label:"Catchment area",type:"range",min:20,max:200,step:10,unit:"m²",default:80},
        {id:"runoff",label:"Capture fraction",type:"range",min:.5,max:.95,step:.05,unit:"",default:.8},
        {id:"capacity",label:"Tank capacity",type:"range",min:100,max:2500,step:100,unit:"L",default:800},
        {id:"demand",label:"Daily demand",type:"range",min:20,max:250,step:10,unit:"L/day",default:90}
      ]
    },
    microgrid:{
      id:"microgrid",label:"The solar microgrid",subtitle:"Can a battery carry an islanded system through low sunlight?",
      eyebrow:"ENERGY / POWER & RESERVES",tag:"Conceptual design lab",
      intro:"Sunlight changes by the hour while loads continue. Test how panel area, battery size and demand change energy that can be served.",
      question:"Can stored energy protect critical demand?",
      hypothesis:"Predict whether any demand goes unserved before running the synthetic scenario.",
      formula:"E(next) = E + ηc · Echarge,input − Edelivered / ηd",
      formulaExplain:"PV power = irradiance (W/m²) × panel area (m²) × efficiency ÷ 1000, in kW. Energy in each one-hour step is kWh. Storage is bounded between a fixed 10% reserve and full capacity.",
      mode:"Synthetic 12-hour, one-hour steps. Islanded operation, constant critical load, 50% initial battery charge, 10% untouchable reserve, 92% charge and discharge efficiencies. No grid, inverter constraints or overnight service claim.",
      risks:"An educational energy-balance approximation, not an electrical installation or safety design. It does not model protection, switching, AC frequency, voltage, weather forecasts or safe islanding/reconnection.",
      source:"https://github.com/Rhodan-lab/principle-to-system/blob/main/system-dossiers/solar-battery-microgrid.md",
      sourceLabel:"Read Principia's solar–battery system dossier",
      prediction:["Every hour's critical load is served","Some critical-load energy remains unserved"],
      controls:[
        {id:"pattern",label:"Sunlight",type:"select",options:[["clear","Clear-sky profile"],["overcast","Overcast profile"],["shaded","Partial shade profile"]],default:"clear"},
        {id:"area",label:"Panel area",type:"range",min:6,max:40,step:2,unit:"m²",default:16},
        {id:"efficiency",label:"PV conversion efficiency",type:"range",min:.12,max:.24,step:.02,unit:"",default:.18},
        {id:"capacity",label:"Battery capacity",type:"range",min:2,max:24,step:2,unit:"kWh",default:8},
        {id:"load",label:"Constant critical load",type:"range",min:.5,max:4,step:.25,unit:"kW",default:1.5}
      ]
    }
  };
  const safety=(value,label,min,max)=>{
    if(typeof value!=="number"||!Number.isFinite(value)||value<min||value>max)throw new RangeError(label+" must be finite and between "+min+" and "+max);
    return value;
  };
  function checkedValues(config,values){
    if(!config||!values||!Array.isArray(config.controls))throw new TypeError("Valid controls required");
    const clean={};
    for(const c of config.controls){
      const val=values[c.id];
      if(c.type==="select"){
        if(!c.options.some(x=>x[0]===val))throw new RangeError("Unexpected scenario "+c.id);
        clean[c.id]=val;
      }else{
        clean[c.id]=safety(val,c.id,c.min,c.max);
        const ticks=(val-c.min)/c.step;
        if(Math.abs(ticks-Math.round(ticks))>1e-7)throw new RangeError("Unexpected parameter step "+c.id);
      }
    }
    return clean;
  }
  function simulateRainwater(values){
    const v=checkedValues(DRAFTS.rainwater,values);
    const rain=RAIN[v.pattern],rows=[];
    let stored=0,capturedTotal=0,servedTotal=0,overflowTotal=0,unmetTotal=0;
    for(let day=0;day<rain.length;day++){
      // 1 mm over 1 square meter is exactly 1 liter.
      const captured=rain[day]*v.area*v.runoff;
      const available=stored+captured;
      const served=Math.min(v.demand,available);
      const afterUse=available-served;
      const overflow=Math.max(0,afterUse-v.capacity);
      const next=Math.min(v.capacity,Math.max(0,afterUse));
      const unmet=v.demand-served;
      rows.push({label:"Day "+(day+1),input:rain[day],capture:captured,served,stored:next,overflow,unmet});
      stored=next;capturedTotal+=captured;servedTotal+=served;overflowTotal+=overflow;unmetTotal+=unmet;
    }
    const balanceError=capturedTotal-(servedTotal+overflowTotal+stored);
    if(Math.abs(balanceError)>1e-7)throw new Error("Water volume balance mismatch");
    return {
      id:"rainwater",rows,stored,capturedTotal,servedTotal,overflowTotal,unmetTotal,
      demandTotal:v.demand*rain.length,coverage:servedTotal/(v.demand*rain.length),
      prediction:unmetTotal<1e-9?0:1,balanceError,
      headline:"Daily demand served",primary:100*servedTotal/(v.demand*rain.length),primaryUnit:"%",
      secondaryLabel:"Unmet non-potable demand",secondary:unmetTotal,secondaryUnit:"L",
      tertiaryLabel:"Total overflow",tertiary:overflowTotal,tertiaryUnit:"L",
      chartLabel:"Stored non-potable water",chartUnit:"L",
      graphMax:v.capacity,reference:v.capacity,steps:rain.length
    };
  }
  function simulateMicrogrid(values){
    const v=checkedValues(DRAFTS.microgrid,values);
    const sunlight=SOLAR[v.pattern],rows=[];
    const eta=.92,reserve=v.capacity*.1;
    let stored=v.capacity*.5,pvTotal=0,servedTotal=0,unmetTotal=0,curtailedTotal=0,chargeLoss=0,dischargeLoss=0;
    for(let hour=0;hour<sunlight.length;hour++){
      const pv=sunlight[hour]*v.area*v.efficiency/1000; // kWh in a 1h step
      const load=v.load; // kWh in one step
      let direct=Math.min(load,pv),served=direct,curtailed=0,chargeInput=0,dischargeDelivered=0;
      if(pv>=load){
        chargeInput=Math.min(pv-load,(v.capacity-stored)/eta);
        stored+=chargeInput*eta;
        chargeLoss+=chargeInput*(1-eta);
        curtailed=pv-load-chargeInput;
      }else{
        const need=load-pv;
        dischargeDelivered=Math.min(need,Math.max(0,stored-reserve)*eta);
        stored-=dischargeDelivered/eta;
        served+=dischargeDelivered;
        dischargeLoss+=dischargeDelivered*(1/eta-1);
      }
      stored=Math.max(reserve,Math.min(v.capacity,stored));
      const unmet=Math.max(0,load-served);
      const incidentBalance=pv+dischargeDelivered-served-chargeInput-curtailed;
      if(Math.abs(incidentBalance)>1e-8)throw new Error("PV-to-load energy balance mismatch");
      rows.push({label:"Hour "+(hour+1),input:sunlight[hour],capture:pv,served,stored,overflow:curtailed,unmet});
      pvTotal+=pv;servedTotal+=served;unmetTotal+=unmet;curtailedTotal+=curtailed;
    }
    const batteryDelta=stored-v.capacity*.5;
    const balanceError=(pvTotal+v.capacity*.5)-(servedTotal+curtailedTotal+stored+chargeLoss+dischargeLoss);
    if(Math.abs(balanceError)>1e-7)throw new Error("Battery+PV energy balance mismatch");
    return {
      id:"microgrid",rows,stored,capturedTotal:pvTotal,servedTotal,unmetTotal,overflowTotal:curtailedTotal,
      demandTotal:v.load*sunlight.length,coverage:servedTotal/(v.load*sunlight.length),
      prediction:unmetTotal<1e-9?0:1,balanceError,batteryDelta,
      headline:"Critical demand served",primary:100*servedTotal/(v.load*sunlight.length),primaryUnit:"%",
      secondaryLabel:"Unserved critical energy",secondary:unmetTotal,secondaryUnit:"kWh",
      tertiaryLabel:"Curtailed solar energy",tertiary:curtailedTotal,tertiaryUnit:"kWh",
      chartLabel:"Energy remaining in battery",chartUnit:"kWh",
      graphMax:v.capacity,reference:reserve,steps:sunlight.length
    };
  }
  function defaultValues(id){
    const draft=DRAFTS[id];if(!draft)throw new RangeError("Unknown exploration");
    return Object.fromEntries(draft.controls.map(c=>[c.id,c.default]));
  }
  function simulate(id,values){
    if(id==="rainwater")return simulateRainwater(values);
    if(id==="microgrid")return simulateMicrogrid(values);
    throw new RangeError("Unknown exploration");
  }
  return {RAIN,SOLAR,DRAFTS,defaultValues,checkedValues,simulateRainwater,simulateMicrogrid,simulate};
});
