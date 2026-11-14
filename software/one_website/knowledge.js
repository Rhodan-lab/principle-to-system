"use strict";
/* Accessible, evidence-aware Knowledge Atlas UI. All content is first party. */
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  root.PrincipiaKnowledgeApp=api;
  if(typeof document!=="undefined"){
    if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",api.mount,{once:true});
    else api.mount();
  }
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  function fragment(tag,className,content){
    const e=document.createElement(tag);
    if(className)e.className=className;
    if(content!==undefined)e.textContent=String(content);
    return e;
  }
  function idFromHash(hash,api){
    const raw=String(hash||"").replace(/^#/,"");
    let value;
    try{value=decodeURIComponent(raw)}catch{return "systems"}
    return api.resolve(value)?value:"systems";
  }
  function mount(){
    const api=globalThis.PrincipiaKnowledge;
    const root=document.getElementById("knowledge-main");
    if(!api||!root||root.dataset.knowledgeMounted)return;
    root.dataset.knowledgeMounted="true";
    const $=id=>document.getElementById(id);
    let active="systems",domain="All",notesByTopic=new Map();
    let visited=new Set();
    let focus=false;
    const all=api.topics;
    const search=$("knowledge-search"),topics=$("knowledge-topics"),filters=$("knowledge-filters");

    function makeIndex(){
      const items=api.search(search.value,domain);
      topics.replaceChildren();
      items.forEach(item=>{
        const i=all.indexOf(item)+1;
        const li=fragment("li","knowledge-topic-item");
        const a=fragment("a","knowledge-topic-link");
        a.href=api.linkTo(item.id);
        a.dataset.topic=item.id;
        if(item.id===active)a.setAttribute("aria-current","location");
        const num=fragment("span","knowledge-topic-index",String(i).padStart(2,"0"));
        const content=fragment("span","knowledge-topic-text");
        content.append(fragment("strong","",item.title),fragment("small","",item.domain));
        const arrow=fragment("span","knowledge-topic-arrow","↗");arrow.setAttribute("aria-hidden","true");
        a.append(num,content,arrow);li.append(a);topics.append(li);
      });
      $("knowledge-search-status").textContent=items.length+" of "+all.length+" chapters shown";
      if(items.length===0)topics.append(fragment("li","knowledge-topic-empty","No match yet. Try a broader idea or clear the filter."));
      for(const button of filters.querySelectorAll("button")){
        button.setAttribute("aria-pressed",String(button.dataset.domain===domain));
      }
    }
    for(const value of ["All",...api.domains]){
      const button=fragment("button","knowledge-filter",value);
      button.type="button";button.dataset.domain=value;button.setAttribute("aria-pressed",String(value===domain));
      button.addEventListener("click",()=>{domain=value;makeIndex();});
      filters.append(button);
    }
    search.addEventListener("input",makeIndex);
    search.addEventListener("keydown",event=>{
      if(event.key==="Escape"){search.value="";makeIndex();}
      else if(event.key==="Enter"){
        const first=topics.querySelector("a");
        if(first){event.preventDefault();window.location.hash=first.hash;}
      }
    });
    const notes=$("knowledge-notes");
    function saveNotes(){
      const text=notes.value;
      if(text)notesByTopic.set(active,text);
      else notesByTopic.delete(active);
    }
    notes.addEventListener("input",saveNotes);
    $("knowledge-copy-notes").addEventListener("click",()=>{
      if(!notes.value.trim()){
        $("knowledge-copy-status").textContent="Write a few sentences first.";
        notes.focus();return;
      }
      const text=notes.value;
      if(!navigator.clipboard?.writeText){
        $("knowledge-copy-status").textContent="Select the text above and copy it manually.";
        notes.select();return;
      }
      navigator.clipboard.writeText(text).then(()=>{
        $("knowledge-copy-status").textContent="Copied to clipboard.";
      }).catch(()=>{
        $("knowledge-copy-status").textContent="Clipboard unavailable. Select the text and copy.";
        notes.select();
      });
    });

    function resetCheck(item){
      $("knowledge-check-question").textContent=item.check.question;
      const options=$("knowledge-check-options");
      options.replaceChildren();
      item.check.choices.forEach((choice,index)=>{
        const label=fragment("label","knowledge-check-option");
        const radio=fragment("input");
        radio.type="radio";radio.name="knowledge-answer";radio.value=String(index);
        const text=fragment("span","",choice);
        label.append(radio,text);options.append(label);
      });
      const feedback=$("knowledge-check-feedback");
      feedback.hidden=true;feedback.replaceChildren();
      $("knowledge-check-submit").disabled=false;
    }

    function fillArticle(id){
      const item=api.resolve(id);
      if(!item)return;
      saveNotes();
      active=id;
      visited.add(id);
      $("knowledge-visited").textContent=String(visited.size);
      const order=all.indexOf(item);
      $("knowledge-domain").textContent=item.domain.toUpperCase();
      $("knowledge-chapter-index").textContent="CHAPTER / "+String(order+1).padStart(2,"0")+" OF "+all.length;
      $("knowledge-question").textContent=item.question;
      $("knowledge-article-title").textContent=item.title;
      $("knowledge-lead").textContent=item.lead;
      $("knowledge-guiding").textContent=item.question;
      const sections=$("knowledge-sections");
      sections.replaceChildren();
      item.sections.forEach((s,index)=>{
        const section=fragment("section","knowledge-section");
        section.id="knowledge-section-"+(index+1);
        section.append(fragment("p","knowledge-small","THE EXPLANATION / "+String(index+1).padStart(2,"0")),
          fragment("h4","",s.heading),fragment("p","knowledge-section-body",s.text));
        const question=fragment("div","knowledge-section-ponder");
        question.append(fragment("span","","THINK ABOUT IT"),fragment("p","",s.thought));
        section.append(question);sections.append(section);
      });
      $("knowledge-formula").textContent=item.formula;
      $("knowledge-example").textContent=item.example;
      $("knowledge-mistake").textContent=item.misconception;
      $("knowledge-source").href=item.source;
      const next=all[(order+1)%all.length];
      $("knowledge-next").href=api.linkTo(next.id);
      $("knowledge-next").textContent=next.title+" ↗";
      const links=$("knowledge-links");links.replaceChildren();
      for(const targetId of item.links){
        const target=api.resolve(targetId);
        if(!target)continue;
        const a=fragment("a","knowledge-related");
        a.href=api.linkTo(target.id);
        a.append(fragment("span","",target.domain),fragment("strong","",target.title),
          fragment("span","knowledge-related-arrow","↗"));
        links.append(a);
      }
      $("knowledge-lab").href=item.lab;
      $("knowledge-lab").textContent=item.lab==="/research/"?"Inspect accepted Atlas evidence ↗":
        item.lab==="/explore/"?"Browse the four scientific labs ↗":"Open the related interactive lab ↗";
      notes.value=notesByTopic.get(id)||"";
      $("knowledge-copy-status").textContent="";
      resetCheck(item);
      makeIndex();
    }
    $("knowledge-check-form").addEventListener("submit",event=>{
      event.preventDefault();
      const checked=$("knowledge-check-options").querySelector('input[name="knowledge-answer"]:checked');
      const output=$("knowledge-check-feedback");
      output.replaceChildren();
      output.hidden=false;
      if(!checked){
        output.className="knowledge-check-feedback knowledge-check-hint";
        output.textContent="Choose the explanation that best fits the mechanism before revealing the answer.";
        $("knowledge-check-options").querySelector("input")?.focus();
        return;
      }
      const result=api.checkAnswer(active,Number(checked.value));
      output.className="knowledge-check-feedback "+(result.correct?"knowledge-check-correct":"knowledge-check-revise");
      output.append(fragment("strong","",result.correct?"Your reasoning fits the model.":"A useful point to reconsider."),
        fragment("p","",result.explanation));
      for(const radio of $("knowledge-check-options").querySelectorAll("input")){
        radio.disabled=true;
        if(Number(radio.value)===result.expected)radio.closest("label")?.classList.add("knowledge-option-answer");
      }
      $("knowledge-check-submit").disabled=true;
    });
    function sync(){
      const id=idFromHash(location.hash,api);
      if(id!==active||!$("knowledge-lead").textContent){
        fillArticle(id);
      }
    }
    window.addEventListener("hashchange",sync);
    $("knowledge-focus").addEventListener("click",()=>{
      focus=!focus;
      document.body.classList.toggle("knowledge-focus-mode",focus);
      $("knowledge-focus").setAttribute("aria-pressed",String(focus));
      $("knowledge-focus").firstChild.textContent=focus?"Exit focus ":"Focus reading ";
    });
    document.addEventListener("keydown",event=>{
      const target=event.target;
      const editing=target instanceof HTMLElement&&(target.matches("input,textarea,select")||target.isContentEditable);
      if(event.key==="/"&&!editing&&!event.ctrlKey&&!event.metaKey&&!event.altKey){
        event.preventDefault();
        if(focus){
          focus=false;document.body.classList.remove("knowledge-focus-mode");
          $("knowledge-focus").setAttribute("aria-pressed","false");
          $("knowledge-focus").firstChild.textContent="Focus reading ";
        }
        search.focus();
      }
      if(event.key==="Escape"&&focus&&!editing){
        $("knowledge-focus").click();$("knowledge-focus").focus();
      }
    });
    sync();
  }
  return {idFromHash,mount};
});
