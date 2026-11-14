"use strict";
/*
 * Atlas Evidence Studio · presentation-only enhancement to the verified,
 * source-owned Atlas Phase 4 research workspace. No network access, persistence,
 * writes, evidence substitution or review-state changes.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.AtlasEvidenceStudio = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", api.mount, {once:true});
    else api.mount();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const groups = [
    {id:"orientation",label:"01 / ORIENTATION",kinds:["overview"]},
    {id:"entries",label:"02 / ACCEPTED ENTRIES",kinds:["entry"]},
    {id:"review",label:"03 / REVIEW & BOUNDARIES",kinds:["candidates","principia","warnings","questions","limitations"]},
    {id:"exports",label:"04 / EXPORT & RECORD",kinds:["evidence","summary"]}
  ];
  const descriptions = {
    overview:"A guided overview of the accepted, immutable research package and its decision order.",
    entry:"An exact-revision research entry. Its existing decision, metadata and provenance stay unchanged.",
    candidates:"Potential contradiction or duplication is advisory and unresolved, not automatically resolved.",
    principia:"An offline cross-repository reference; Principia status stays independent from Atlas.",
    warnings:"Unavailable exact references remain visible. Missing evidence is never silently replaced.",
    questions:"Research questions invite further investigation; they are not publication decisions.",
    limitations:"The evidence boundary states what this accepted package cannot establish.",
    evidence:"Package provenance, byte identity and the verified local export.",
    summary:"A non-graph reading path through the five accepted entries in preserved order."
  };
  function normalize(query) {
    return String(query ?? "").normalize("NFKD").toLocaleLowerCase("en").trim().replace(/\s+/g," ");
  }
  function routeCategory(kind) {
    const group = groups.find(section => section.kinds.includes(kind));
    return group ? group.id : null;
  }
  function filterRoutes(routes,query) {
    const term=normalize(query);
    return routes.filter(route => normalize(route.label+" "+route.kind+" "+(route.index||"")).includes(term));
  }
  function element(tag,attrs={},children=[]) {
    const node=document.createElement(tag);
    for(const [key,value] of Object.entries(attrs)) {
      if(key==="text")node.textContent=String(value);
      else if(key==="className")node.className=value;
      else if(key==="dataset")Object.assign(node.dataset,value);
      else if(key.startsWith("aria-"))node.setAttribute(key,String(value));
      else if(key==="hidden")node.hidden=Boolean(value);
      else if(key==="type"||key==="href"||key==="id"||key==="role"||key==="title"||key==="placeholder"||key==="htmlFor")node[key]=value;
      else node.setAttribute(key,String(value));
    }
    for(const child of children)node.append(child instanceof Node?child:document.createTextNode(String(child)));
    return node;
  }
  function link(target,text,className="") {
    return element("a",{href:target,className,text});
  }
  function mount() {
    const grid=document.querySelector(".workspace-grid");
    const sidebar=document.querySelector(".sidebar");
    const header=document.querySelector(".masthead");
    const nav=document.querySelector("#route-list");
    const runtime=document.querySelector(".runtime-card");
    const panel=document.querySelector("#content-panel");
    const main=document.querySelector("#main-content");
    if(!grid||!sidebar||!header||!nav||!runtime||!panel||!main)return;
    const body=document.body;
    if(body.dataset.atlasStudioMounted==="true")return;
    body.dataset.atlasStudioMounted="true";

    // Give the authority-bound export an editorial entry point, without
    // altering a byte of the accepted data or its original rendering engine.
    const copy=header.querySelector(".masthead-copy");
    if(copy){
      const eyebrow=copy.querySelector(".eyebrow");
      const heading=copy.querySelector("h1");
      const lede=copy.querySelector(".lede");
      if(eyebrow)eyebrow.textContent="ATLAS / EVIDENCE STUDIO · READ ONLY";
      if(heading)heading.textContent="Follow the evidence.";
      if(lede)lede.textContent="A serious research desk for examining exact revisions, decisions, provenance and unresolved questions. Every record comes from a verified, pinned workspace export.";
      copy.prepend(element("div",{className:"atlas-overline",text:"INDEPENDENT KNOWLEDGE / ACCEPTED FIXTURE / NO WRITES"}));
    }
    const toolbar=element("div",{className:"atlas-toolbar"});
    const breadcrumb=element("div",{className:"atlas-breadcrumb","aria-label":"Current research view"});
    breadcrumb.append(link("/","Principia & Atlas"),element("span",{"aria-hidden":"true",text:"/"}),link("#overview","Research desk"),element("span",{"aria-hidden":"true",text:"/"}),element("strong",{id:"atlas-current-view",text:"Overview"}));
    const tools=element("div",{className:"atlas-toolbar-actions"});
    const searchShortcut=element("button",{className:"atlas-toolbar-button",type:"button","aria-label":"Search Atlas views, shortcut Control K",text:"Search views  ⌘ K"});
    const focusButton=element("button",{id:"atlas-focus-button",className:"atlas-toolbar-button",type:"button","aria-pressed":"false",text:"Focus reading"});
    const inspectorButton=element("button",{id:"atlas-inspector-button",className:"atlas-toolbar-button",type:"button","aria-pressed":"true",text:"Hide inspector"});
    tools.append(searchShortcut,focusButton,inspectorButton);
    toolbar.append(breadcrumb,tools);
    header.after(toolbar);

    const searchBox=element("div",{className:"atlas-search-block",role:"search","aria-label":"Find research views"});
    const searchLabel=element("label",{htmlFor:"atlas-route-filter",text:"FIND IN THE WORKSPACE"});
    const searchRow=element("div",{className:"atlas-search-row"});
    const searchInput=element("input",{type:"search",id:"atlas-route-filter",placeholder:"Search 13 views…","aria-controls":"route-list","aria-describedby":"atlas-search-status",autocomplete:"off",spellcheck:"false"});
    const hint=element("kbd",{text:"/"});
    searchRow.append(searchInput,hint);
    const searchStatus=element("p",{id:"atlas-search-status",className:"atlas-search-status",role:"status","aria-live":"polite",text:"Loading verified routes…"});
    searchBox.append(searchLabel,searchRow,searchStatus);
    sidebar.querySelector(".sidebar-heading")?.after(searchBox);

    const sidebarNote=element("p",{className:"atlas-sidebar-note",text:"Each view is an exact-revision lens, not an independent verdict."});
    sidebar.querySelector("nav")?.after(sidebarNote);

    const inspector=element("aside",{id:"atlas-inspector",className:"atlas-inspector","aria-label":"Contextual research inspector"});
    const inspectorHead=element("div",{className:"atlas-inspector-head"});
    inspectorHead.append(element("div",{className:"atlas-inspector-mark",text:"∴"}),
      element("div",{},[
        element("p",{className:"atlas-inspector-eyebrow",text:"CONTEXT / RESEARCH LENS"}),
        element("h2",{text:"Inspector"})
      ]));
    const inspectorTabs=element("div",{className:"atlas-inspector-tabs",role:"tablist","aria-label":"Inspector information"});
    const contextTab=element("button",{type:"button",role:"tab",id:"atlas-tab-context","aria-controls":"atlas-inspector-content","aria-selected":"true",text:"Context"});
    const integrityTab=element("button",{type:"button",role:"tab",id:"atlas-tab-integrity","aria-controls":"atlas-inspector-content","aria-selected":"false",tabindex:"-1",text:"Integrity"});
    inspectorTabs.append(contextTab,integrityTab);
    const inspectorContent=element("section",{id:"atlas-inspector-content",role:"tabpanel","aria-label":"Inspector detail",tabindex:"0"});
    inspector.append(inspectorHead,inspectorTabs,inspectorContent);
    grid.append(inspector);
    let inspectorMode="context",lastRoute=null;
    const navLinks=()=>Array.from(nav.querySelectorAll("a.route-link")).filter(a=>a.dataset.routeKind);
    const routeInfo=()=>navLinks().map(a=>({
      hash:a.getAttribute("href"),kind:a.dataset.routeKind,label:a.querySelector(".route-label")?.textContent?.trim()||a.textContent.trim(),
      index:a.querySelector(".route-index")?.textContent?.trim()||""
    }));
    function groupNavigation(){
      if(nav.dataset.atlasGrouped==="true")return;
      const links=Array.from(nav.children).filter(li=>li.querySelector("a[data-route-kind]"));
      if(!links.length)return;
      for(const group of groups){
        const belonging=links.filter(li=>group.kinds.includes(li.querySelector("a")?.dataset.routeKind));
        if(!belonging.length)continue;
        const heading=element("li",{className:"atlas-route-group",role:"presentation",dataset:{group:group.id}});
        heading.append(element("span",{text:group.label}));
        nav.append(heading);
        for(const li of belonging){
          li.dataset.atlasRouteGroup=group.id;
          nav.append(li);
        }
      }
      nav.dataset.atlasGrouped="true";
    }
    function applyFilter(){
      const all=routeInfo();
      const matching=new Set(filterRoutes(all,searchInput.value).map(route=>route.hash));
      let shown=0;
      for(const li of Array.from(nav.children)){
        const a=li.querySelector("a.route-link");
        if(!a)continue;
        li.hidden=!matching.has(a.getAttribute("href"));
        if(!li.hidden)shown++;
      }
      for(const heading of nav.querySelectorAll(".atlas-route-group")){
        heading.hidden=!Array.from(nav.children).some(li=>li.dataset.atlasRouteGroup===heading.dataset.group&&!li.hidden);
      }
      searchStatus.textContent=normalize(searchInput.value)
        ? (shown===0?"No matching views. Try a different term.":shown+" matching view"+(shown===1?"":"s"))
        : (all.length+" views · "+all.filter(r=>r.kind==="entry").length+" accepted entries");
    }
    function openSearch(){
      if(!runtime.classList.contains("ready"))return;
      if(body.classList.contains("atlas-focus-mode"))setFocus(false);
      searchInput.focus();searchInput.select();
    }
    function setFocus(value){
      body.classList.toggle("atlas-focus-mode",value);
      focusButton.setAttribute("aria-pressed",String(value));
      focusButton.textContent=value?"Exit focus":"Focus reading";
    }
    function setInspectorVisible(value){
      body.classList.toggle("atlas-inspector-hidden",!value);
      inspectorButton.setAttribute("aria-pressed",String(value));
      inspectorButton.textContent=value?"Hide inspector":"Show inspector";
      if(!value&&inspector.contains(document.activeElement))inspectorButton.focus();
    }
    function viewInfo(){
      const route=routeInfo().find(item=>item.hash===(location.hash||"#overview"));
      return route||{hash:"#overview",kind:"overview",label:"Workspace overview",index:""};
    }
    function fillInspector(){
      if(!runtime.classList.contains("ready"))return;
      const current=viewInfo();
      lastRoute=current;
      inspectorContent.replaceChildren();
      const exactStatus=document.querySelector("#runtime-status")?.textContent||"Verification pending";
      if(inspectorMode==="integrity"){
        inspectorContent.append(
          element("p",{className:"atlas-aside-overline",text:"PACKAGE / IDENTITY"}),
          element("h3",{className:"atlas-aside-title",text:"Verified, not promoted."}),
          element("p",{className:"atlas-inspector-body",text:"The original workspace verified its accepted export's SHA-256 and byte length before opening the research views. This presentation does not grant publication or human-review authority."}),
          element("div",{className:"atlas-context-kv"},[
            element("span",{text:"Export verification"}),
            element("strong",{text:exactStatus}),
            element("span",{text:"Canonical writes"}),
            element("strong",{text:"Disabled"}),
            element("span",{text:"Automatic promotion"}),
            element("strong",{text:"Not available"}),
            element("span",{text:"Principia inheritance"}),
            element("strong",{text:"Separate"})
          ]),
          link(routeInfo().find(r=>r.kind==="evidence")?.hash||"#overview","Inspect export evidence ↗","atlas-aside-link")
        );
      }else{
        inspectorContent.append(
          element("p",{className:"atlas-aside-overline",text:"NOW INSPECTING / "+current.kind.toUpperCase()}),
          element("h3",{className:"atlas-aside-title",text:current.label}),
          element("p",{className:"atlas-inspector-body",text:descriptions[current.kind]||"Browse the accepted workspace without modifying source state."}),
          element("div",{className:"atlas-context-rule"}),
          element("p",{className:"atlas-aside-overline",text:"NEXT TO EXPLORE"})
        );
        const related=current.kind==="entry"?["overview","candidates","evidence"]:
          current.kind==="overview"?["entry","candidates","evidence"]:
          ["overview","entry","limitations"];
        for(const kind of related){
          const next=routeInfo().find(r=>r.kind===kind&&r.hash!==current.hash);
          if(next)inspectorContent.append(link(next.hash,next.label+" ↗","atlas-aside-link"));
        }
        inspectorContent.append(
          element("div",{className:"atlas-inspector-tip"},[
            element("strong",{text:"Reading rule"}),
            element("p",{text:"An exact reference names a version; it does not itself prove a claim correct. Check provenance, review level and limitations together."})
          ])
        );
      }
    }
    function setInspectorTab(mode,focus){
      inspectorMode=mode;
      for(const tab of [contextTab,integrityTab]){
        const selected=tab===(mode==="context"?contextTab:integrityTab);
        tab.setAttribute("aria-selected",String(selected));
        tab.tabIndex=selected?0:-1;
        if(selected&&focus)tab.focus();
      }
      fillInspector();
    }
    for(const [tab,mode] of [[contextTab,"context"],[integrityTab,"integrity"]]){
      tab.addEventListener("click",()=>setInspectorTab(mode,false));
      tab.addEventListener("keydown",event=>{
        if(!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;
        event.preventDefault();
        const next=event.key==="Home"?"context":event.key==="End"?"integrity":
          mode==="context"?"integrity":"context";
        setInspectorTab(next,true);
      });
    }
    function makeResearchTrail(){
      if(!runtime.classList.contains("ready") || location.hash!=="#overview")return;
      if(panel.querySelector("#atlas-research-trail"))return;
      const entries=routeInfo().filter(route=>route.kind==="entry");
      if(!entries.length)return;
      const canvas=element("section",{id:"atlas-research-trail",className:"atlas-research-trail","aria-labelledby":"atlas-research-trail-title"});
      const head=element("div",{className:"atlas-trail-head"});
      head.append(element("div",{},[
          element("p",{className:"atlas-overline",text:"THE ACCEPTED RESEARCH TRAIL"}),
          element("h3",{id:"atlas-research-trail-title",text:"Five entries. One inspectable sequence."})
        ]),element("p",{text:"These cards follow accepted entry order; the connecting rule is navigational, not a claim of causal dependency."}));
      const ordered=element("ol",{className:"atlas-trail-list"});
      for(const route of entries){
        ordered.append(element("li",{},[
          link(route.hash,"", "atlas-trail-link")
        ]));
        const a=ordered.lastChild.querySelector("a");
        a.append(
          element("span",{className:"atlas-trail-index",text:String(route.index).padStart(2,"0")}),
          element("span",{className:"atlas-trail-name",text:route.label}),
          element("span",{className:"atlas-trail-arrow","aria-hidden":"true",text:"↗"})
        );
      }
      canvas.append(head,ordered);
      const before=panel.querySelector(".meta-row");
      if(before)before.before(canvas);else panel.append(canvas);
    }
    function sync(){
      if(runtime.classList.contains("failed")){
        body.classList.add("atlas-verification-failed");
        toolbar.querySelector("#atlas-current-view").textContent="Package unavailable";
        return;
      }
      if(!runtime.classList.contains("ready"))return;
      groupNavigation();
      applyFilter();
      const current=viewInfo();
      body.dataset.atlasRoute=current.kind;
      toolbar.querySelector("#atlas-current-view").textContent=current.label;
      fillInspector();
      makeResearchTrail();
    }
    searchShortcut.addEventListener("click",openSearch);
    focusButton.addEventListener("click",()=>setFocus(!body.classList.contains("atlas-focus-mode")));
    inspectorButton.addEventListener("click",()=>setInspectorVisible(body.classList.contains("atlas-inspector-hidden")));
    searchInput.addEventListener("input",applyFilter);
    searchInput.addEventListener("keydown",event=>{
      if(event.key==="Escape"){
        if(searchInput.value){searchInput.value="";applyFilter();}
        else searchInput.blur();
      }else if(event.key==="Enter"){
        const first=navLinks().find(a=>!a.closest("li")?.hidden);
        if(first){event.preventDefault();searchInput.value="";applyFilter();first.click();}
      }
    });
    document.addEventListener("keydown",event=>{
      const target=event.target;
      const typing=target instanceof HTMLElement&&(
        target.matches("input,textarea,select")||target.isContentEditable
      );
      if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="k"){
        event.preventDefault();openSearch();
      }else if(event.key==="/"&&!typing&&!event.ctrlKey&&!event.metaKey&&!event.altKey){
        event.preventDefault();openSearch();
      }else if(event.key==="Escape"&&body.classList.contains("atlas-focus-mode")){
        setFocus(false);focusButton.focus();
      }
    });
    window.addEventListener("hashchange",()=>{
      if(searchInput.value){searchInput.value="";applyFilter();}
      queueMicrotask(sync);
    });
    const observer=new MutationObserver(sync);
    observer.observe(runtime,{attributes:true,attributeFilter:["class"]});
    observer.observe(nav,{childList:true});
    observer.observe(panel,{childList:true});
    sync();
  }
  return {normalize,routeCategory,filterRoutes,mount};
});
