import assert from "node:assert/strict";
import test from "node:test";
import {createRequire} from "node:module";

const require=createRequire(import.meta.url);
const adapters=require("../product_alpha/model-adapters.js");

const thermalModel={
  adapter:"thermal-cabinet-v1",
  initial_temperature_c:8,
  duration_minutes:180,
  time_step_seconds:30,
  thermal_capacitance_j_per_k:180000,
  parameters:[
    {id:"room_temperature_c",label:"Room temperature",unit:"°C",type:"range",minimum:18,maximum:40,step:1},
    {id:"ua_w_per_k",label:"Heat leakage",unit:"W/K",type:"range",minimum:1,maximum:8,step:.1},
    {id:"load_w",label:"Internal load",unit:"W",type:"range",minimum:0,maximum:80,step:1},
    {id:"cooling_w",label:"Cooling capacity",unit:"W",type:"range",minimum:40,maximum:180,step:1},
    {id:"cooling_on",label:"Cooling active",unit:"",type:"checkbox"}
  ],
  chart:{title:"Predicted cabinet temperature"}
};

const queueModel={
  adapter:"queue-delay-fluid-v1",
  parameters:[
    {id:"external_arrival_rate_rps",label:"External arrival rate",unit:"requests/s",type:"range",minimum:1,maximum:15,step:.5},
    {id:"service_rate_rps",label:"Service capacity",unit:"requests/s",type:"range",minimum:2,maximum:20,step:.5},
    {id:"retry_fraction",label:"Retry fraction",unit:"fraction",type:"range",minimum:0,maximum:1,step:.05},
    {id:"queue_capacity_requests",label:"Queue capacity",unit:"requests",type:"range",minimum:5,maximum:200,step:5},
    {id:"observation_seconds",label:"Observation duration",unit:"s",type:"range",minimum:10,maximum:120,step:10}
  ],
  chart:{title:"Predicted queue response"}
};

test("thermal adapter preserves the refrigerator model direction and precision",()=>{
  const adapter=adapters.getAdapter("thermal-cabinet-v1");
  const result=adapter.run(thermalModel,{room_temperature_c:28,ua_w_per_k:3.2,load_w:18,cooling_w:95,cooling_on:true});
  const summary=adapter.summarize(thermalModel,result);
  assert.equal(result.points[0].t,8);
  assert.equal(result.outcome,"falls");
  assert.match(summary.result,/cabinet temperature falls to -?\d+\.\d °C after 180 minutes/);
  assert.match(summary.description,/Room temperature reference: 28\.0 °C/);
  assert.equal(adapter.matchesPrediction(result,"falls"),true);
});

test("queue adapter distinguishes comfortable capacity from near-capacity delay",()=>{
  const adapter=adapters.getAdapter("queue-delay-fluid-v1");
  const comfortable=adapter.run(queueModel,{external_arrival_rate_rps:3,service_rate_rps:10,retry_fraction:0,queue_capacity_requests:50,observation_seconds:30});
  const nearCapacity=adapter.run(queueModel,{external_arrival_rate_rps:7.5,service_rate_rps:10,retry_fraction:.1,queue_capacity_requests:50,observation_seconds:30});
  assert.equal(comfortable.outcome,"stable");
  assert.equal(nearCapacity.outcome,"sharp-growth");
  assert.equal(nearCapacity.growth,0);
  assert.ok(nearCapacity.meanTime>comfortable.meanTime);
});

test("queue adapter models overload, finite backlog, and rejected work deterministically",()=>{
  const adapter=adapters.getAdapter("queue-delay-fluid-v1");
  const values={external_arrival_rate_rps:12,service_rate_rps:10,retry_fraction:.5,queue_capacity_requests:50,observation_seconds:30};
  const first=adapter.run(queueModel,values);
  const second=adapter.run(queueModel,values);
  assert.deepEqual(first,second);
  assert.equal(first.offered,18);
  assert.equal(first.growth,8);
  assert.equal(first.backlog,50);
  assert.equal(first.rejected,190);
  assert.equal(first.meanTime,null);
  assert.equal(first.outcome,"sharp-growth");
});

test("adapter validation rejects values outside route-declared bounds",()=>{
  const adapter=adapters.getAdapter("queue-delay-fluid-v1");
  assert.throws(()=>adapter.run(queueModel,{external_arrival_rate_rps:30,service_rate_rps:10,retry_fraction:0,queue_capacity_requests:50,observation_seconds:30}),/outside its declared range/);
});

test("unknown adapter identifiers fail closed",()=>{
  assert.throws(()=>adapters.getAdapter("unknown-model"),/Unsupported model adapter/);
});
