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
    {href:"/explore/",title:"All laboratories",description:"Browse four interactive scientific subjects",group:"Explore"},
    {href:"/knowledge/",title:"Knowledge Atlas",description:"Read and understand 15 connected explanations about how systems work",group:"Understand"},
    {href:"/knowledge/#systems",title:"Understanding systems",description:"Boundaries, inputs, outputs and physical relationships",group:"Understand"},
    {href:"/knowledge/#conservation",title:"Conservation and balance",description:"Where energy, water and stored quantities must go",group:"Understand"},
    {href:"/knowledge/#feedback",title:"Feedback and delay",description:"How responses amplify or correct a system",group:"Understand"},
    {href:"/knowledge/#models",title:"Models versus reality",description:"The assumptions and limitations of simulations",group:"Understand"},
    {href:"/knowledge/#evidence",title:"Sources and scientific trust",description:"What a pinned source can establish",group:"Understand"},
    {href:"/learn/distributed-information/",title:"Distributed systems",description:"Queues, overload and retry dynamics",group:"Experiments"},
    {href:"/explore/rainwater/",title:"Rainwater storage",description:"Non-potable capture, storage, demand and overflow",group:"Experiments"},
    {href:"/explore/microgrid/",title:"Solar microgrid",description:"Solar power, battery capacity, reserve and critical load",group:"Experiments"},
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
    if(pathname.startsWith("/explore"))return"explore";
    if(pathname.startsWith("/knowledge"))return"knowledge";
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
      const active=link.dataset.paArea===area||(link.dataset.paArea==="explore"&&(area==="refrigerator"||area==="distributed-information"));
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
      if(event.key==="/"&&!typing&&area!=="atlas"&&area!=="knowledge"&&!dialog.open&&!event.ctrlKey&&!event.altKey&&!event.metaKey){
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
    if(!main.querySelector(".pa-knowledge-prelude")){
      const isThermal=location.pathname.includes("refrigerator");
      const guide=document.createElement("section");
      guide.className="pa-knowledge-prelude";
      guide.setAttribute("aria-label","Learn the scientific explanations behind this experiment");
      const heading=document.createElement("div");
      const marker=document.createElement("p");
      marker.textContent="UNDERSTAND / BEFORE OR AFTER EXPERIMENTING";
      const title=document.createElement("h2");title.textContent="The ideas behind this investigation.";
      const intro=document.createElement("p");intro.textContent="Every numerical outcome needs a conceptual explanation. Explore the foundations freely, then return and test your understanding in the live model.";
      heading.append(marker,title,intro);
      const links=document.createElement("div");links.className="pa-knowledge-prelude-links";
      const chapters=isThermal?[
        ["heat","Heat is a transfer, not a substance","Why moving heat out of a cabinet warms the surroundings"],
        ["conservation","Follow every joule","Account for energy crossing the chosen system boundary"],
        ["systems","Choose the right boundary","Distinguish the cabinet, appliance and whole room"]
      ]:[
        ["queue","Why retries become pressure","See how added attempts push service beyond capacity"],
        ["feedback","The loop behind the failure","Learn how a response can amplify overload"],
        ["capacity","The bottleneck is the story","Separate arrival rates, service rates and bounded queues"]
      ];
      for(const [id,name,summary]of chapters){
        const card=document.createElement("a");card.href="/knowledge/#"+id;
        const label=document.createElement("span");label.textContent="CONCEPTUAL FOUNDATION / "+id.toUpperCase();
        const title=document.createElement("strong");title.textContent=name;
        const description=document.createElement("small");description.textContent=summary;
        card.append(label,title,description);
        links.append(card);
      }
      guide.append(heading,links);frame.before(guide);
    }
    const heading=steps.querySelector(".journey-head strong");
    if(heading)heading.textContent="Field guide";
    const hero=main.querySelector(".hero");
    if(hero){
      const eyebrow=hero.querySelector(".hero-copy>.eyebrow");
      if(eyebrow)eyebrow.textContent="A FIRST-PRINCIPLES EXPEDITION";
      const brief=hero.querySelector(".hero-brief>strong");
      if(brief)brief.textContent="Your working method";
    }
    const related=main.querySelector(".stats");
    if(related&&!main.querySelector(".pa-next-labs")){
      const section=document.createElement("section");
      section.className="pa-next-labs";
      section.setAttribute("aria-label","Continue into other scientific laboratories");
      const head=document.createElement("div");
      head.className="pa-next-labs-heading";
      const overline=document.createElement("span");
      overline.textContent="FURTHER / EXPLORATION";
      const h=document.createElement("h2");
      h.textContent="The next question is yours.";
      const all=document.createElement("a");
      all.href="/explore/";all.textContent="Browse all four laboratories ↗";
      head.append(overline,h,all);section.append(head);
      const grid=document.createElement("div");grid.className="pa-next-labs-grid";
      const suggested=[
        {href:"/explore/rainwater/",tag:"WATER · NEW CONCEPTUAL LAB",title:"Where does the rain go?",desc:"A bounded tank, changing storms and everyday demand."},
        {href:"/explore/microgrid/",tag:"ENERGY · NEW CONCEPTUAL LAB",title:"What if sunlight fades?",desc:"Solar generation, limited storage and critical loads."},
        {href:location.pathname.includes("refrigerator")?"/learn/distributed-information/":"/learn/refrigerator/",
          tag:"ANOTHER PRODUCT ALPHA JOURNEY",title:location.pathname.includes("refrigerator")?"When do retries fail?":"Where does heat flow?",
          desc:"A full five-step learning investigation."}
      ];
      for(const item of suggested){
        const card=document.createElement("a");card.className="pa-next-lab";card.href=item.href;
        const kicker=document.createElement("span");kicker.className="pa-next-lab-kicker";kicker.textContent=item.tag;
        const title=document.createElement("strong");title.textContent=item.title;
        const desc=document.createElement("span");desc.className="pa-next-lab-desc";desc.textContent=item.desc;
        const arrow=document.createElement("span");arrow.className="pa-next-lab-arrow";arrow.textContent="Open investigation ↗";
        card.append(kicker,title,desc,arrow);grid.append(card);
      }
      section.append(grid);related.after(section);
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
    const sectionNav=document.querySelector(".pa3-section-index");
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
