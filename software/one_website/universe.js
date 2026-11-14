"use strict";
/*
 * Principia & Atlas — Shared interaction shell.
 * Single-origin routing + ephemeral command search. No analytics, persistence,
 * account, remote fetch or modification of verified research/source documents.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  root.PrincipiaUniverse=api;
  if(typeof document!=="undefined"){
    if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",api.mount,{once:true});
    else api.mount();
  }
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  const paths=[
    {href:"/",title:"Discover",description:"Return to the knowledge observatory",group:"Explore"},
    {href:"/learn/refrigerator/",title:"Thermal laboratory",description:"Heat, energy balance and counterfactual models",group:"Experiments"},
    {href:"/learn/distributed-information/",title:"Distributed systems",description:"Queues, overload and retry dynamics",group:"Experiments"},
    {href:"/research/",title:"Research Atlas",description:"Accepted evidence, revisions, provenance and review boundaries",group:"Evidence"},
    {href:"/research/#overview",title:"Atlas overview",description:"Accepted workspace identity and source boundary",group:"Evidence"},
    {href:"/learn/refrigerator/#model",title:"Thermal model",description:"Predict and experiment with the heat-balance model",group:"Experiments"},
    {href:"/learn/distributed-information/#model",title:"Queue model",description:"Predict and test capacity and retries",group:"Experiments"}
  ];
  const stepNames=["observe","map","model","diagnose","redesign"];
  function normalized(text){
    return String(text==null?"":text).normalize("NFKD").toLowerCase().replace(/\s+/g," ").trim();
  }
  function findDestinations(query,items=paths){
    const term=normalized(query);
    if(!term)return items;
    return items.filter(item=>normalized(item.title+" "+item.description+" "+item.group).includes(term));
  }
  function currentArea(pathname){
    if(pathname.startsWith("/research"))return"atlas";
    if(pathname.startsWith("/learn/refrigerator"))return"refrigerator";
    if(pathname.startsWith("/learn/distributed-information"))return"distributed-information";
    return"home";
  }
  function mount(){
    const navigation=document.querySelector("#pa-global-nav");
    if(!navigation||navigation.dataset.universeMounted==="true")return;
    navigation.dataset.universeMounted="true";
    const body=document.body;
    const area=currentArea(location.pathname);
    body.dataset.paArea=area;
    const links=[...navigation.querySelectorAll(".pa-nav-link")];
    links.forEach(link=>{
      const active=link.dataset.paArea===area;
      if(active)link.setAttribute("aria-current","page");
      else link.removeAttribute("aria-current");
    });
    const commandButton=navigation.querySelector(".pa-nav-command");
    const dialog=document.createElement("dialog");
    dialog.className="pa-command-dialog";
    dialog.id="pa-command-dialog";
    dialog.setAttribute("aria-label","Go to another Principia and Atlas view");
    const top=document.createElement("div");top.className="pa-cmd-top";
    const symbol=document.createElement("span");symbol.className="pa-cmd-symbol";symbol.textContent="⌕";symbol.setAttribute("aria-hidden","true");
    const input=document.createElement("input");input.className="pa-cmd-input";input.type="search";
    input.id="pa-command-search";input.placeholder="Jump to an experiment, view, or topic…";
    input.setAttribute("aria-label","Search website destinations");
    input.setAttribute("autocomplete","off");
    const close=document.createElement("button");close.type="button";close.className="pa-cmd-close";close.textContent="Esc";close.setAttribute("aria-label","Close navigation search");
    top.append(symbol,input,close);
    const list=document.createElement("ul");list.className="pa-cmd-list";list.id="pa-command-results";list.setAttribute("aria-label","Available destinations");
    const empty=document.createElement("p");empty.className="pa-cmd-empty";empty.textContent="No matching destination. Try a system, model, or Atlas.";
    empty.hidden=true;
    const foot=document.createElement("div");foot.className="pa-cmd-bottom";
    const hint=document.createElement("span");hint.textContent="↑ ↓ to choose  ·  Enter to open  ·  Esc to close";
    const boundary=document.createElement("span");boundary.textContent="Local navigation only · no search history";
    foot.append(hint,boundary);
    dialog.append(top,list,empty,foot);
    document.body.append(dialog);
    let activeIndex=0;
    const menuLinks=()=>[...list.querySelectorAll("a")];
    function highlight(index){
      const buttons=menuLinks();
      if(!buttons.length)return;
      activeIndex=((index%buttons.length)+buttons.length)%buttons.length;
      buttons.forEach((a,i)=>{
        a.dataset.active=String(i===activeIndex);
        if(i===activeIndex)a.setAttribute("aria-selected","true");else a.removeAttribute("aria-selected");
      });
    }
    function render(){
      list.replaceChildren();
      const matches=findDestinations(input.value);
      empty.hidden=matches.length!==0;
      matches.forEach((route,index)=>{
        const li=document.createElement("li");
        const anchor=document.createElement("a");anchor.href=route.href;
        anchor.setAttribute("aria-label",route.title+" — "+route.description);
        const number=document.createElement("span");number.className="pa-cmd-index";number.textContent=String(index+1).padStart(2,"0");
        const info=document.createElement("span");
        const title=document.createElement("span");title.className="pa-cmd-label";title.textContent=route.title;
        const desc=document.createElement("span");desc.className="pa-cmd-desc";desc.textContent=route.description;
        info.append(title,desc);anchor.append(number,info);
        li.append(anchor);list.append(li);
      });
      highlight(0);
    }
    function openMenu(){
      if(dialog.open)return;
      input.value="";render();
      dialog.showModal();input.focus();
    }
    function closeMenu(){
      if(dialog.open)dialog.close();
      commandButton?.focus();
    }
    if(commandButton)commandButton.addEventListener("click",openMenu);
    close.addEventListener("click",closeMenu);
    input.addEventListener("input",render);
    input.addEventListener("keydown",event=>{
      if(event.key==="ArrowDown"){event.preventDefault();highlight(activeIndex+1);}
      else if(event.key==="ArrowUp"){event.preventDefault();highlight(activeIndex-1);}
      else if(event.key==="Enter"){
        const active=menuLinks()[activeIndex];
        if(active){event.preventDefault();location.assign(active.href);}
      }
    });
    document.addEventListener("keydown",event=>{
      const typing=event.target instanceof HTMLElement&&(
        event.target.matches("input,textarea,select")||event.target.isContentEditable);
      const globalShortcut=(event.altKey&&event.key.toLowerCase()==="g") ||
        (area!=="atlas"&&(event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==="k");
      if(globalShortcut){event.preventDefault();openMenu();}
      if(event.key==="/"&&!typing&&area!=="atlas"&&!dialog.open&&!event.ctrlKey&&!event.altKey&&!event.metaKey){
        event.preventDefault();openMenu();
      }
    });
    // Outside-click close is explicit; the native dialog controls Escape.
    dialog.addEventListener("click",event=>{
      if(event.target===dialog)closeMenu();
    });
    if(area==="refrigerator"||area==="distributed-information")enhanceLearner();
    if(area==="home")enhanceHome();
  }
  function enhanceLearner(){
    const main=document.querySelector("body.pa-learner main");
    const steps=main?.querySelector(".journey-shell");
    const workspace=main?.querySelector(".workspace");
    if(!main||!steps||!workspace||main.querySelector(".pa-lab-frame"))return;
    const frame=document.createElement("div");
    frame.className="pa-lab-frame";
    frame.setAttribute("aria-label","Three-pane learning workspace");
    steps.before(frame);frame.append(steps,workspace);
    const heading=steps.querySelector(".journey-head strong");
    if(heading)heading.textContent="Field guide";
    const hero=main.querySelector(".hero");
    if(hero){
      const eyebrow=hero.querySelector(".hero-copy>.eyebrow");
      if(eyebrow)eyebrow.textContent="A FIRST-PRINCIPLES EXPEDITION";
      const brief=hero.querySelector(".hero-brief>strong");
      if(brief)brief.textContent="Your working method";
    }
    const note=document.querySelector("#note");
    if(note)note.setAttribute("aria-label","In-tab working explanation for this lesson");
    const nav=steps.querySelector('nav[aria-label="Learner journey"]');
    if(nav){
      nav.setAttribute("aria-label","Five-step investigation index");
      const progress=document.createElement("p");
      progress.className="pa-lab-aside-note";
      progress.textContent="Choose any step. Your local notes and predictions stay in this tab.";
      steps.append(progress);
      const observer=new MutationObserver(()=>{
        const current=nav.querySelector('a[aria-current="step"]');
        if(current)document.body.dataset.paStep=current.dataset.step||"observe";
      });
      observer.observe(nav,{subtree:true,attributes:true,attributeFilter:["aria-current"]});
      const current=nav.querySelector('a[aria-current="step"]');
      if(current)document.body.dataset.paStep=current.dataset.step;
    }
    const modelHelp=document.querySelector("#modelT");
    if(modelHelp){
      // Source templates are deliberately left unmodified. This header
      // appears above their cloned model controls only after Model is opened.
      const activity=document.querySelector("#activity");
      const observer=new MutationObserver(()=>{
        if(!activity?.querySelector("#modelControls")||activity.querySelector(".pa-lab-model-brief"))return;
        const block=document.createElement("div");
        block.className="pa-lab-model-brief";
        block.setAttribute("role","note");
        block.textContent="Prediction first · run the deterministic model · inspect the equation · compare a saved baseline.";
        const target=activity.querySelector("#modelControls");
        target.before(block);
      });
      if(activity)observer.observe(activity,{childList:true});
    }
  }
  function enhanceHome(){
    const sectionNav=document.querySelector(".pa-section-index");
    if(!sectionNav)return;
    const anchors=[...sectionNav.querySelectorAll('a[href^="#"]')];
    if(typeof IntersectionObserver!=="function")return;
    const entries=anchors.map(a=>document.querySelector(a.getAttribute("href"))).filter(Boolean);
    if(!entries.length)return;
    const observer=new IntersectionObserver(records=>{
      const visible=records.filter(r=>r.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio);
      if(!visible.length)return;
      anchors.forEach(a=>{
        const selected=a.getAttribute("href")==="#"+visible[0].target.id;
        if(selected)a.setAttribute("aria-current","location");else a.removeAttribute("aria-current");
      });
    },{rootMargin:"-30% 0px -56% 0px",threshold:[0,.1,.5]});
    entries.forEach(s=>observer.observe(s));
  }
  return {paths,normalized,findDestinations,currentArea,mount};
});
