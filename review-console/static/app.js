const state={projects:[],selected:null,pipeline:[],poller:null,health:null,selectedStage:null,decisionSummary:null,feedbackConfig:null,feedbacks:[]};
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmtSize=n=>n>1048576?`${(n/1048576).toFixed(1)} MB`:n>1024?`${Math.round(n/1024)} KB`:`${n} B`;
const fmtDate=s=>s?new Date(s).toLocaleString("zh-CN",{month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}):"—";
const inlineMarkdown=text=>esc(text)
  .replace(/`([^`]+)`/g,"<code>$1</code>")
  .replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>")
  .replace(/__([^_]+)__/g,"<strong>$1</strong>")
  .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g,"<em>$1</em>");
function markdownToSafeHtml(markdown){
  const lines=String(markdown??"").replace(/\r\n?/g,"\n").split("\n");
  const html=[];
  const isTableDivider=line=>/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
  const cells=line=>line.trim().replace(/^\||\|$/g,"").split("|").map(cell=>cell.trim());
  let index=0;
  while(index<lines.length){
    const line=lines[index];
    if(!line.trim()){index+=1;continue}
    if(/^```/.test(line.trim())){
      const language=line.trim().slice(3).trim();
      const code=[];
      index+=1;
      while(index<lines.length&&!/^```/.test(lines[index].trim())){code.push(lines[index]);index+=1}
      if(index<lines.length)index+=1;
      html.push(`<pre><code${language?` data-language="${esc(language)}"`:""}>${esc(code.join("\n"))}</code></pre>`);
      continue;
    }
    if(line.includes("|")&&index+1<lines.length&&isTableDivider(lines[index+1])){
      const headers=cells(line);
      index+=2;
      const rows=[];
      while(index<lines.length&&lines[index].includes("|")&&lines[index].trim()){
        rows.push(cells(lines[index]));index+=1;
      }
      html.push(`<div class="markdown-table-wrap"><table><thead><tr>${headers.map(cell=>`<th>${inlineMarkdown(cell)}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${headers.map((_,cellIndex)=>`<td>${inlineMarkdown(row[cellIndex]??"")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }
    const heading=line.match(/^(#{1,6})\s+(.+)$/);
    if(heading){
      const level=heading[1].length;
      html.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      index+=1;continue;
    }
    if(/^\s*[-*_]{3,}\s*$/.test(line)){html.push("<hr>");index+=1;continue}
    if(/^\s*>\s?/.test(line)){
      const quote=[];
      while(index<lines.length&&/^\s*>\s?/.test(lines[index])){
        quote.push(lines[index].replace(/^\s*>\s?/,""));index+=1;
      }
      html.push(`<blockquote>${quote.map(inlineMarkdown).join("<br>")}</blockquote>`);
      continue;
    }
    const listMatch=line.match(/^\s*([-+*]|\d+\.)\s+(.+)$/);
    if(listMatch){
      const ordered=/\d+\./.test(listMatch[1]);
      const tag=ordered?"ol":"ul";
      const items=[];
      while(index<lines.length){
        const match=lines[index].match(/^\s*([-+*]|\d+\.)\s+(.+)$/);
        if(!match||(/\d+\./.test(match[1]))!==ordered)break;
        items.push(match[2]);index+=1;
      }
      html.push(`<${tag}>${items.map(item=>`<li>${inlineMarkdown(item)}</li>`).join("")}</${tag}>`);
      continue;
    }
    const paragraph=[line.trim()];
    index+=1;
    while(index<lines.length&&lines[index].trim()&&!/^(#{1,6})\s+/.test(lines[index])&&!/^```/.test(lines[index].trim())&&!/^\s*(>|[-+*]\s+|\d+\.\s+)/.test(lines[index])){
      if(lines[index].includes("|")&&index+1<lines.length&&isTableDivider(lines[index+1]))break;
      paragraph.push(lines[index].trim());index+=1;
    }
    html.push(`<p>${paragraph.map(inlineMarkdown).join("<br>")}</p>`);
  }
  return html.join("");
}
function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2500)}
async function api(path,options={}){
  const res=await fetch(path,{headers:{"Content-Type":"application/json",...(options.headers||{})},...options});
  const contentType=res.headers.get("content-type")||"";
  const data=contentType.includes("application/json")?await res.json():null;
  if(!res.ok)throw new Error(data?.error||`请求失败（${res.status}）`);
  if(!data)throw new Error("服务器返回了无法识别的响应");
  return data;
}

async function init(){
  [state.projects,state.pipeline,state.health,state.feedbackConfig]=await Promise.all([
    api("/api/projects"),
    api("/api/pipeline"),
    api("/api/health"),
    api("/api/knowledge-feedback-config")
  ]);
  const status=$("#serviceStatus");
  status.innerHTML=state.health.api_key_configured
    ?`<i></i> ${esc(state.health.ai_model)} / READY`
    :`<i class="offline"></i> AI API 未配置`;
  status.title=state.health.api_key_configured
    ?`${state.health.ai_provider} · ${state.health.ai_base_url}`
    :"请双击“设置智谱API.cmd”完成配置";
  populateFeedbackConfig();
  renderProjects();
  const first=state.projects[0];
  if(first)selectProject(first.id);
}
function renderProjects(filter=""){
  const q=filter.trim().toLowerCase();
  const list=state.projects.filter(p=>(p.project_key+" "+p.name).toLowerCase().includes(q));
  $("#projectCount").textContent=state.projects.length;
  $("#projectList").innerHTML=list.map(p=>`<div class="project-item ${state.selected?.id===p.id?"active":""}" data-id="${p.id}">
    <button class="project-select" type="button">
      <strong>${esc(p.project_key.toUpperCase())}</strong><small>${esc(p.name)}</small>
    </button>
    <button class="project-edit" type="button" title="编辑项目号和项目名" aria-label="编辑 ${esc(p.project_key)}">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4l11-11-4-4L4 16v4Zm12.2-16.2 4 4 1.1-1.1a1.4 1.4 0 0 0 0-2l-2-2a1.4 1.4 0 0 0-2 0l-1.1 1.1Z"/></svg>
    </button>
    <button class="project-delete" type="button" title="删除项目" aria-label="删除 ${esc(p.project_key)}">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4h8l1 2h4v2H3V6h4l1-2Zm-2 6h12l-1 10H7L6 10Zm4 2v6h2v-6h-2Zm4 0v6h2v-6h-2Z"/></svg>
    </button>
  </div>`).join("");
  document.querySelectorAll(".project-select").forEach(x=>x.onclick=()=>selectProject(x.closest(".project-item").dataset.id));
  document.querySelectorAll(".project-edit").forEach(x=>x.onclick=()=>openEditProject(x.closest(".project-item").dataset.id));
  document.querySelectorAll(".project-delete").forEach(x=>x.onclick=()=>openDeleteProject(x.closest(".project-item").dataset.id));
}
function openEditProject(id){
  const project=state.projects.find(p=>p.id===id);
  if(!project)return;
  const form=$("#editProjectForm");
  form.dataset.projectId=id;
  form.elements.project_key.value=project.project_key;
  form.elements.name.value=project.name;
  $("#editProjectDialog").showModal();
  requestAnimationFrame(()=>form.elements.project_key.focus());
}
function openDeleteProject(id){
  const project=state.projects.find(p=>p.id===id);
  if(!project)return;
  const dialog=$("#deleteProjectDialog");
  dialog.dataset.projectId=id;
  $("#deleteProjectName").textContent=`${project.project_key.toUpperCase()} · ${project.name}`;
  if(!dialog.open)dialog.showModal();
}
async function refreshProjects(){
  state.projects=await api("/api/projects");
  renderProjects($("#searchInput").value);
}
async function selectProject(id){
  [state.selected,state.decisionSummary,state.feedbacks]=await Promise.all([
    api(`/api/projects/${id}`),
    api(`/api/projects/${id}/decision-summary`),
    api(`/api/projects/${id}/knowledge-feedback`)
  ]);
  state.selectedStage=null;
  $("#emptyState").hidden=true;$("#projectView").hidden=false;
  renderProjects($("#searchInput").value);renderProject();
}
function renderProject(){
  const p=state.selected;const run=p.runs[0];
  $("#projectKey").textContent=p.project_key.toUpperCase();
  $("#projectStatus").textContent=p.status;
  $("#projectName").textContent=p.name;
  $("#projectMeta").textContent=[p.customer&&`客户：${p.customer}`,p.owner&&`负责人：${p.owner}`,`更新：${fmtDate(p.updated_at)}`].filter(Boolean).join(" · ");
  $("#fileCount").textContent=p.files.length;$("#artifactCount").textContent=p.artifacts.length;$("#riskLevel").textContent=p.risk_level;
  $("#nonstandardItems").textContent=p.nonstandard_items||"待评估";
  $("#runStatus").textContent=run?.status||"未运行";$("#runTime").textContent=run?fmtDate(run.created_at):"—";
  $("#runNote").textContent=run?.message||"点击“启动方案评审”后，这里会实时显示进度";
  const runActive=run?.status==="运行中"||run?.status==="排队中";
  $("#startRunBtn").hidden=Boolean(run);
  $("#startRunBtn").disabled=runActive;
  $("#rerunBtn").hidden=!run;
  $("#rerunBtn").disabled=runActive;
  renderDecisionSummary();renderPipeline(run);renderFiles();renderEvents(run);renderKnowledgeFeedback();
  if(run&&["运行中","排队中"].includes(run.status))startPolling(run.id);else stopPolling();
}
function renderDecisionSummary(){
  const items=state.decisionSummary?.items||{};
  const order=["recommended_version","risk_items","custom_development","effort_estimation"];
  $("#decisionSummaryGrid").innerHTML=order.map(key=>{
    const item=items[key]||{key,label:key,content:"",source:""};
    const content=item.content?.trim()||"暂无输出，点击编辑可补充。";
    return `<article class="decision-summary-card">
      <header><strong>${esc(item.label)}</strong><button type="button" class="decision-edit-btn" data-key="${esc(key)}">编辑</button></header>
      <div class="decision-summary-markdown">${markdownToSafeHtml(content)}</div>
      <footer>${item.source?`来源：${esc(item.source)}`:"尚未生成对应 Markdown，首次保存时自动创建"}</footer>
    </article>`;
  }).join("");
  document.querySelectorAll(".decision-edit-btn").forEach(button=>button.onclick=()=>openDecisionEditor(button.dataset.key));
}
function openDecisionEditor(key){
  const item=state.decisionSummary?.items?.[key];
  if(!item)return;
  const dialog=$("#decisionEditDialog");
  dialog.dataset.key=key;
  $("#decisionEditTitle").textContent=`编辑${item.label}`;
  $("#decisionEditSource").textContent=item.source?`当前文件：${item.source}`:"当前没有对应文档，保存后将自动创建。";
  $("#decisionEditContent").value=item.content||"";
  dialog.showModal();
  requestAnimationFrame(()=>$("#decisionEditContent").focus());
}
function renderPipeline(run){
  const artifacts=state.selected?.artifacts||[];
  $("#pipeline").innerHTML=state.pipeline.map(s=>{
    let cls="";if(run){if(s.index<run.current_stage||run.status==="已完成")cls="done";else if(s.index===run.current_stage&&run.status==="运行中")cls="active"}
    const selected=state.selectedStage===s.index?"selected":"";
    return `<button class="stage ${cls} ${selected}" data-stage="${s.index}" aria-expanded="${selected?"true":"false"}" aria-controls="pipelineDetails" aria-label="查看${esc(s.name)}详细说明"><div class="stage-dot">${s.index+1}</div><strong>${esc(s.name)}</strong><small>${esc(s.agent)}</small></button>`
  }).join("");

  const renderSelectedStage=()=>{
    const s=state.pipeline.find(item=>item.index===state.selectedStage);
    const hasSelection=Boolean(s);
    $("#processExplainer").hidden=!hasSelection;
    $("#eventDrawer").hidden=!hasSelection;
    if(!s){
      $("#pipelineDetails").innerHTML=`<div class="stage-detail-empty"><span>选择一个步骤</span><p>点击上方 1–7 中的任意节点，查看该步骤的处理说明和现有输出。</p></div>`;
      return;
    }
    const stageItems=artifacts.filter(a=>Number(a.stage_index)===s.index);
    const registered=s.index===0?(state.selected?.files||[]):[];
    const outputs=s.index===0?registered:stageItems;
    const stageMessages=(run?.agent_messages||[]).filter(message=>Number(message.stage_index)===s.index);
    const communicationMarkup=stageMessages.length?`<section class="agent-communication">
      <div class="communication-head"><strong>TPM 协作交流</strong><span>${stageMessages.length} MESSAGES</span></div>
      <div class="communication-list">${stageMessages.map(message=>`<article class="communication-item">
        <div class="communication-route"><b>第 ${message.round_no} 轮</b><strong>${esc(message.from_agent)}</strong><i>→</i><strong>${esc(message.to_agent)}</strong><span class="communication-status ${message.status==="已回答"?"resolved":""}">${esc(message.status)}</span></div>
        <p><em>问</em>${esc(message.question)}</p>
        ${message.related_requirement?`<small>关联：${esc(message.related_requirement)}${message.evidence?` · 证据：${esc(message.evidence)}`:""}</small>`:""}
        ${message.answer?`<p class="communication-answer"><em>答</em>${esc(message.answer)}</p>`:""}
        ${message.confidence?`<small>置信度：${esc(message.confidence)}${message.follow_up?` · 后续：${esc(message.follow_up)}`:""}</small>`:""}
      </article>`).join("")}</div>
    </section>`:"";
    const outputMarkup=outputs.length?outputs.map(a=>{
      const isSource=s.index===0;
      const fileName=isSource?a.name:a.title;
      const ext=(fileName.split(".").pop()||"DATA").slice(0,5).toUpperCase();
      const url=isSource?`/api/files/${a.id}`:`/api/artifacts/${a.id}`;
      const finalBadge=!isSource&&Number(a.is_final)===1?`<b class="final-badge">FINAL</b>`:"";
      return `<button class="stage-output file-location-trigger" data-kind="${isSource?"file":"artifact"}" data-id="${a.id}"><span class="output-ext">${esc(ext)}</span><div><strong>${esc(fileName)}</strong><small>${esc(isSource?"初始上传":a.artifact_type)} · ${fmtDate(a.created_at)}</small></div>${finalBadge}<i>⌖</i></button>`;
    }).join(""):`<div class="no-stage-output"><span>NO FILE</span><p>当前评审目录没有为此步骤单独保存产物。</p></div>`;
    $("#pipelineDetails").innerHTML=`<section class="detail-card selected-detail" aria-live="polite">
    <header class="detail-heading"><span class="detail-index">${String(s.index+1).padStart(2,"0")}</span><div><strong>${esc(s.name)}</strong><small>${esc(s.agent)} · ${esc(s.description)}</small></div><button class="detail-close" type="button" aria-label="收起步骤说明">×</button></header>
    <div class="detail-body">
      <p class="purpose">${esc(s.purpose)}</p>
      <dl>
        <div><dt>输入</dt><dd>${esc(s.input)}</dd></div>
        <div><dt>处理内容</dt><dd>${esc(s.processing)}</dd></div>
        <div><dt>输出</dt><dd>${esc(s.output)}</dd></div>
        <div><dt>完成标准</dt><dd>${esc(s.done)}</dd></div>
      </dl>
      ${communicationMarkup}
      <div class="stage-output-head"><strong>本步骤现有输出</strong><span>${outputs.length} FILES</span></div>
      <div class="stage-output-list">${outputMarkup}</div>
    </div>
  </section>`;
    $(".detail-close").onclick=()=>{
      state.selectedStage=null;
      renderPipeline(run);
    };
    bindFileLocationButtons();
  };
  renderSelectedStage();

  document.querySelectorAll(".stage").forEach(button=>button.onclick=()=>{
    const index=Number(button.dataset.stage);
    state.selectedStage=state.selectedStage===index?null:index;
    renderPipeline(run);
    if(state.selectedStage!==null)$("#pipelineDetails").scrollIntoView({behavior:"smooth",block:"nearest"});
  });
}
function renderFiles(){
  const files=state.selected.files;
  const filesMarkup=files.length?files.map((f,index)=>`<button class="file-row file-location-trigger" data-kind="file" data-id="${f.id}"><div class="file-index">${String(index+1).padStart(2,"0")}</div><div class="file-icon">${esc(f.name.split(".").pop().slice(0,4).toUpperCase())}</div><div><strong>${esc(f.display_name||f.name)}</strong><small>${esc(f.content_summary||"项目原始资料")} · 原文件：${esc(f.name)} · ${fmtSize(f.size)} · ${fmtDate(f.created_at)}</small></div><span class="tag">${esc(f.kind)}</span><i>⌖</i></button>`).join(""):`<div class="empty-list">没有识别到初始上传资料</div>`;
  $("#fileList").innerHTML=filesMarkup;
  const finalOutputs=selectLatestFinalOutputs(state.selected.artifacts,state.selected.runs);
  $("#finalOutputList").innerHTML=finalOutputs.length?finalOutputs.map((a,index)=>{
    const ext=(a.title.split(".").pop()||"DATA").slice(0,5).toUpperCase();
    const outputKind=a.artifact_type==="方案评审主报告"?"主报告":"正式附件";
    return `<button class="final-output-row file-location-trigger" data-kind="artifact" data-id="${a.id}"><div class="file-index">${String(index+1).padStart(2,"0")}</div><div class="final-output-icon">${esc(ext)}</div><div><strong>${esc(a.artifact_type)}</strong><small>最新一轮 · ${fmtDate(a.created_at)}</small></div><b>${outputKind}</b><i>⌖</i></button>`;
  }).join(""):`<div class="empty-list">当前项目还没有最终输出</div>`;
  bindFileLocationButtons();
}
function populateFeedbackConfig(){
  const config=state.feedbackConfig||{targets:[],source_types:[]};
  $("#feedbackTarget").innerHTML=config.targets.map(item=>
    `<option value="${esc(item.key)}">${esc(item.label)} · ${esc(item.relative_path)}</option>`
  ).join("");
  $("#feedbackSourceType").innerHTML=config.source_types.map(item=>
    `<option value="${esc(item)}">${esc(item)}</option>`
  ).join("");
}
function renderKnowledgeFeedback(){
  const items=state.feedbacks||[];
  $("#knowledgeFeedbackList").innerHTML=items.length?items.map(item=>{
    const error=item.last_error?`<p class="feedback-item-error">${esc(item.last_error)}</p>`:"";
    const actions=[
      `<button type="button" class="ghost feedback-raw-btn" data-id="${item.id}">查看原始 MD</button>`,
      item.can_edit_raw?`<button type="button" class="ghost feedback-edit-btn" data-id="${item.id}">编辑反馈</button>`:"",
      item.can_analyze?`<button type="button" class="primary feedback-analyze-btn" data-id="${item.id}">${item.status==="待确认"?"重新 AI 分析":"开始 AI 分析"}</button>`:"",
      item.analysis_md_path?`<button type="button" class="ghost feedback-analysis-btn" data-id="${item.id}">查看分析</button>`:""
    ].filter(Boolean).join("");
    return `<article class="knowledge-feedback-item">
      <div class="feedback-item-main">
        <header><strong>${esc(item.feedback_no)} · ${esc(item.title)}</strong><span class="feedback-status status-${esc(item.status)}">${esc(item.status)}</span></header>
        <p>${esc(item.summary||"未填写摘要")}</p>
        <small>${esc(item.target_label)} · ${esc(item.source_type)} · ${fmtDate(item.updated_at)}</small>
        ${error}
      </div>
      <div class="feedback-item-actions">${actions}</div>
    </article>`;
  }).join(""):`<div class="empty-list">当前项目还没有 TPM 知识反馈</div>`;
  document.querySelectorAll(".feedback-edit-btn").forEach(button=>button.onclick=()=>openFeedbackEditor(button.dataset.id));
  document.querySelectorAll(".feedback-analyze-btn").forEach(button=>button.onclick=()=>runFeedbackAnalysis(button.dataset.id,button));
  document.querySelectorAll(".feedback-analysis-btn").forEach(button=>button.onclick=()=>openFeedbackAnalysis(button.dataset.id));
  document.querySelectorAll(".feedback-raw-btn").forEach(button=>button.onclick=()=>openFeedbackRaw(button.dataset.id));
}
async function refreshFeedbacks(){
  if(!state.selected)return;
  state.feedbacks=await api(`/api/projects/${state.selected.id}/knowledge-feedback`);
  renderKnowledgeFeedback();
}
function renderFeedbackAttachmentOptions(selected=[]){
  const selectedIds=new Set(selected);
  const files=state.selected?.files||[];
  $("#feedbackAttachmentOptions").innerHTML=files.length?files.map(file=>
    `<label class="feedback-attachment-option">
      <input type="checkbox" value="${file.id}" ${selectedIds.has(file.id)?"checked":""}>
      <span><strong>${esc(file.display_name||file.name)}</strong><small>${esc(file.name)} · ${fmtSize(file.size)}</small></span>
    </label>`
  ).join(""):`<div class="feedback-no-attachment">当前项目没有可引用的已上传资料</div>`;
  document.querySelectorAll("#feedbackAttachmentOptions input").forEach(input=>input.onchange=event=>{
    const checked=[...document.querySelectorAll("#feedbackAttachmentOptions input:checked")];
    if(checked.length>3){
      event.target.checked=false;
      toast("一次反馈最多引用 3 份项目资料");
    }
  });
}
function populateFeedbackForm(item=null){
  const form=$("#feedbackForm");
  form.reset();
  form.dataset.feedbackId=item?.id||"";
  $("#feedbackDialogTitle").textContent=item?`编辑 ${item.feedback_no}`:"新增 TPM 知识反馈";
  $("#saveFeedbackBtn").textContent=item?"保存原始反馈 MD":"保存原始反馈 MD";
  const value=item?.form||{};
  form.elements.title.value=value.title||"";
  form.elements.source_type.value=value.source_type||state.feedbackConfig?.source_types?.[0]||"TPM复核";
  form.elements.target_key.value=item?.target_key||state.feedbackConfig?.targets?.[0]?.key||"";
  form.elements.version_info.value=value.version_info||"";
  form.elements.vehicle_info.value=value.vehicle_info||"";
  form.elements.scenario.value=value.scenario||"";
  form.elements.exclusions.value=value.exclusions||"";
  form.elements.raw_content.value=value.raw_content||"";
  const calculation=value.calculation||{};
  form.elements.calculation_parameters.value=calculation.parameters||"";
  form.elements.calculation_measured_value.value=calculation.measured_value||"";
  form.elements.calculation_unit.value=calculation.unit||"";
  form.elements.calculation_data_source.value=calculation.data_source||"";
  form.elements.calculation_method.value=calculation.method||"";
  form.elements.calculation_formula.value=calculation.formula||"";
  form.elements.calculation_result.value=calculation.result||"";
  form.elements.calculation_threshold.value=calculation.threshold||"";
  form.elements.calculation_conclusion.value=calculation.conclusion||"";
  renderFeedbackAttachmentOptions(item?.attachment_ids||[]);
}
async function openFeedbackEditor(id=null){
  try{
    const item=id?await api(`/api/knowledge-feedback/${id}`):null;
    if(item&&!item.can_edit_raw){toast("AI 分析完成后原始反馈已锁定");return}
    populateFeedbackForm(item);
    $("#feedbackDialog").showModal();
    requestAnimationFrame(()=>$("#feedbackForm").elements.title.focus());
  }catch(err){toast(err.message)}
}
function feedbackFormPayload(){
  const form=$("#feedbackForm");
  return {
    title:form.elements.title.value,
    source_type:form.elements.source_type.value,
    target_key:form.elements.target_key.value,
    version_info:form.elements.version_info.value,
    vehicle_info:form.elements.vehicle_info.value,
    scenario:form.elements.scenario.value,
    exclusions:form.elements.exclusions.value,
    raw_content:form.elements.raw_content.value,
    attachment_ids:[...document.querySelectorAll("#feedbackAttachmentOptions input:checked")].map(input=>input.value),
    calculation:{
      parameters:form.elements.calculation_parameters.value,
      measured_value:form.elements.calculation_measured_value.value,
      unit:form.elements.calculation_unit.value,
      data_source:form.elements.calculation_data_source.value,
      method:form.elements.calculation_method.value,
      formula:form.elements.calculation_formula.value,
      result:form.elements.calculation_result.value,
      threshold:form.elements.calculation_threshold.value,
      conclusion:form.elements.calculation_conclusion.value
    }
  };
}
async function runFeedbackAnalysis(id,button=null){
  if(!state.health?.api_key_configured){toast("请先配置 DeepSeek API Key");return}
  const originalText=button?.textContent||"";
  if(button){button.disabled=true;button.textContent="AI 分析中…"}
  try{
    const item=await api(`/api/knowledge-feedback/${id}/analyze`,{method:"POST",body:"{}"});
    await refreshFeedbacks();
    openFeedbackAnalysisDialog(item);
    toast("AI 分析已完成，等待 TPM 确认");
  }catch(err){
    await refreshFeedbacks();
    toast(err.message);
  }finally{
    if(button){button.disabled=false;button.textContent=originalText}
  }
}
async function openFeedbackAnalysis(id){
  try{
    const item=await api(`/api/knowledge-feedback/${id}`);
    openFeedbackAnalysisDialog(item);
  }catch(err){toast(err.message)}
}
function openFeedbackAnalysisDialog(item){
  const dialog=$("#feedbackAnalysisDialog");
  dialog.dataset.feedbackId=item.id;
  dialog.dataset.targetLabel=item.target_label||"";
  dialog.dataset.targetPath=item.target_relative_path||"";
  $("#feedbackAnalysisTitle").textContent=`${item.feedback_no} AI 知识分析`;
  $("#feedbackAnalysisMeta").textContent=`${item.target_label} · ${item.target_relative_path} · 状态：${item.status}`;
  $("#feedbackAnalysisContent").value=item.analysis_content||"";
  $("#feedbackAnalysisContent").readOnly=!item.can_publish;
  $("#saveFeedbackAnalysisBtn").hidden=!item.can_publish;
  $("#publishFeedbackBtn").hidden=!item.can_publish;
  $("#reanalyzeFeedbackBtn").hidden=!item.can_analyze;
  const error=$("#feedbackAnalysisError");
  error.hidden=!item.last_error;
  error.textContent=item.last_error||"";
  if(!dialog.open)dialog.showModal();
}
async function openFeedbackRaw(id){
  try{
    const item=await api(`/api/knowledge-feedback/${id}`);
    const dialog=$("#previewDialog");
    dialog.dataset.kind="feedback";
    dialog.dataset.id=item.id;
    $("#previewName").textContent=`${item.feedback_no}_raw.md`;
    $("#previewType").textContent="MD · TPM RAW FEEDBACK";
    $("#previewMeta").textContent="原始反馈证据 · AI 分析后不可改写";
    const container=$("#previewContent");
    container.innerHTML=`<article class="preview-markdown">${markdownToSafeHtml(item.raw_markdown||"")}</article>`;
    $("#previewLocationBtn").hidden=true;
    dialog.showModal();
  }catch(err){toast(err.message)}
}
const FINAL_OUTPUT_TYPES=[
  "方案评审主报告",
  "版本适配建议",
  "定制化开发清单",
  "非标判定清单",
  "人时估算清单",
  "方案未决项清单"
];
function selectLatestFinalOutputs(artifacts=[],runs=[]){
  const candidates=artifacts.filter(a=>
    Number(a.is_final)===1&&
    (
      Number(a.stage_index)===6||
      (Number(a.stage_index)===5&&a.artifact_type==="方案未决项清单")
    )&&
    FINAL_OUTPUT_TYPES.includes(a.artifact_type)
  );
  const latestRunId=runs.map(r=>r.id).find(runId=>candidates.some(a=>a.run_id===runId));
  const scoped=latestRunId
    ?candidates.filter(a=>a.run_id===latestRunId)
    :candidates.filter(a=>!a.run_id);
  return FINAL_OUTPUT_TYPES
    .map(type=>scoped.find(a=>a.artifact_type===type))
    .filter(Boolean);
}
function bindFileLocationButtons(){
  document.querySelectorAll(".file-location-trigger").forEach(button=>button.onclick=()=>{
    const kind=button.dataset.kind;const id=button.dataset.id;
    const item=kind==="file"?state.selected.files.find(x=>x.id===id):state.selected.artifacts.find(x=>x.id===id);
    if(item)showPreview(kind,item);
  });
}
async function showPreview(kind,item){
  try{
    const data=await api(`/api/previews/${kind}/${item.id}`);
    const dialog=$("#previewDialog");
    dialog.dataset.kind=kind;dialog.dataset.id=item.id;
    $("#previewLocationBtn").hidden=false;
    $("#previewName").textContent=data.name;
    $("#previewType").textContent=`${data.extension} · FILE PREVIEW`;
    $("#previewMeta").textContent=`${fmtSize(data.size)} · 工作台内预览，不会下载文件`;
    const container=$("#previewContent");
    container.innerHTML="";
    if(data.preview_type==="text"&&data.extension==="MD"){
      const article=document.createElement("article");article.className="preview-markdown";article.innerHTML=markdownToSafeHtml(data.content);container.appendChild(article);
      $("#previewType").textContent="MD · RENDERED PREVIEW";
    }else if(data.preview_type==="text"){
      const pre=document.createElement("pre");pre.className="preview-text";pre.textContent=data.content;container.appendChild(pre);
    }else if(data.preview_type==="image"){
      const image=document.createElement("img");image.className="preview-image";image.src=data.url;image.alt=data.name;container.appendChild(image);
    }else if(data.preview_type==="pdf"){
      const frame=document.createElement("iframe");frame.className="preview-frame";frame.src=data.url;frame.title=data.name;container.appendChild(frame);
    }else{
      const message=document.createElement("div");message.className="preview-message";message.textContent=data.content;container.appendChild(message);
    }
    dialog.showModal();
  }catch(err){toast(err.message)}
}
function showFileLocation(kind,item){
  const name=kind==="file"?item.name:item.title;
  const path=kind==="file"?item.stored_path:item.path;
  const meta=kind==="file"
    ?`${item.kind} · ${fmtSize(item.size)} · ${fmtDate(item.created_at)}`
    :`${item.artifact_type} · 阶段 ${Number(item.stage_index)+1} · ${fmtDate(item.created_at)}`;
  $("#fileDialogName").textContent=name;$("#fileDialogPath").value=path;$("#fileDialogMeta").textContent=meta;
  $("#fileDialog").dataset.kind=kind;$("#fileDialog").dataset.id=item.id;$("#fileDialog").showModal();
}
function renderEvents(run){
  const events=run?.events||[];
  $("#eventList").innerHTML=events.length?events.map(e=>`<div class="event"><time>${fmtDate(e.created_at)}</time><span>${esc(e.agent)}</span><div>${esc(e.summary)}</div></div>`).join(""):`<div class="empty-list">暂无运行记录</div>`;
}
async function openKnowledgeBase(){
  try{
    const data=await api("/api/knowledge-base");
    $("#knowledgeFileCount").textContent=data.file_count;
    $("#knowledgeRootPath").value=data.root;
    const libraryMarkup=(data.libraries||[]).map(library=>`<button class="knowledge-library-row" data-library="${esc(library.id)}" ${library.exists?"":"disabled"}>
      <span class="knowledge-kind">${library.id==="mingmou"?"MM":"KB"}</span>
      <span><strong>${esc(library.label)}</strong><small>${esc(library.scope)} · ${esc(library.root)}</small></span>
      <span>${library.exists?`${library.file_count} FILES`:"目录未就绪"}</span><i>${library.exists?"→":"—"}</i>
    </button>`).join("");
    const itemMarkup=data.items.length?data.items.map(item=>`<button class="knowledge-row" data-library="${esc(item.library)}" data-path="${esc(item.relative_path)}">
        <span class="knowledge-kind">${esc(item.kind==="folder"?"DIR":item.extension||"FILE")}</span>
        <span><strong>${esc(item.name)}</strong><small>${esc(item.library_label)} · ${esc(item.relative_path)}</small></span>
        <span>${item.kind==="folder"?"文件夹":fmtSize(item.size)}</span><i>⌖</i>
      </button>`).join(""):`<div class="knowledge-empty">知识库目录目前为空</div>`;
    $("#knowledgeList").innerHTML=libraryMarkup+itemMarkup;
    document.querySelectorAll(".knowledge-library-row:not([disabled])").forEach(button=>button.onclick=async()=>{
      try{
        await api("/api/reveal",{method:"POST",body:JSON.stringify({kind:"knowledge",library:button.dataset.library,relative_path:""})});
        toast("已打开知识库目录");
      }catch(err){toast(err.message)}
    });
    document.querySelectorAll(".knowledge-row").forEach(button=>button.onclick=async()=>{
      try{
        await api("/api/reveal",{method:"POST",body:JSON.stringify({kind:"knowledge",library:button.dataset.library,relative_path:button.dataset.path})});
        toast("已在资源管理器中定位");
      }catch(err){toast(err.message)}
    });
    $("#knowledgeDialog").showModal();
  }catch(err){toast(err.message)}
}
function startPolling(runId){
  if(state.poller)return;
  state.poller=setInterval(async()=>{
    const data=await api(`/api/runs/${runId}`);
    const run=state.selected.runs.find(r=>r.id===runId)||{};
    Object.assign(run,data.run,{events:data.events,agent_messages:data.agent_messages||[],agent_results:data.agent_results||[]});
    if(!state.selected.runs.some(r=>r.id===runId))state.selected.runs.unshift(run);
    renderProject();
    if(!["运行中","排队中"].includes(run.status)){stopPolling();await refreshProjects();await selectProject(state.selected.id);toast("本次流程已结束")}
  },900);
}
function stopPolling(){if(state.poller){clearInterval(state.poller);state.poller=null}}

$("#searchInput").addEventListener("input",e=>renderProjects(e.target.value));
$("#newProjectBtn").onclick=()=>$("#projectDialog").showModal();
document.querySelectorAll("[data-close-dialog]").forEach(button=>{
  button.onclick=()=>document.getElementById(button.dataset.closeDialog)?.close();
});
$("#knowledgeBaseBtn").onclick=openKnowledgeBase;
$("#newFeedbackBtn").onclick=()=>openFeedbackEditor();
$("#closeKnowledgeDialog").onclick=()=>$("#knowledgeDialog").close();
$("#copyKnowledgeRootBtn").onclick=async()=>{
  try{await navigator.clipboard.writeText($("#knowledgeRootPath").value);toast("知识库根目录已复制")}
  catch{toast("无法自动复制，请在路径框中手动复制")}
};
$("#revealKnowledgeRootBtn").onclick=async()=>{
  try{
    await api("/api/reveal",{method:"POST",body:JSON.stringify({kind:"knowledge",relative_path:""})});
    toast("已打开知识库目录");
  }catch(err){toast(err.message)}
};
$("#projectForm").onsubmit=async e=>{
  e.preventDefault();const form=new FormData(e.target);const body=Object.fromEntries(form);
  try{const p=await api("/api/projects",{method:"POST",body:JSON.stringify(body)});$("#projectDialog").close();e.target.reset();await refreshProjects();await selectProject(p.id);toast("项目已创建")}
  catch(err){toast(err.message)}
};
$("#editProjectForm").onsubmit=async e=>{
  e.preventDefault();
  const id=e.target.dataset.projectId;
  const body=Object.fromEntries(new FormData(e.target));
  try{
    await api(`/api/projects/${id}`,{method:"PATCH",body:JSON.stringify(body)});
    $("#editProjectDialog").close();
    await refreshProjects();
    if(state.selected?.id===id)await selectProject(id);
    toast("项目信息已更新");
  }catch(err){toast(err.message)}
};
$("#decisionEditForm").onsubmit=async e=>{
  e.preventDefault();
  if(!state.selected)return;
  const dialog=$("#decisionEditDialog");
  const key=dialog.dataset.key;
  const button=e.target.querySelector('button[type="submit"]');
  button.disabled=true;
  try{
    const item=await api(`/api/projects/${state.selected.id}/decision-summary`,{
      method:"PATCH",
      body:JSON.stringify({key,content:$("#decisionEditContent").value})
    });
    state.decisionSummary.items[key]=item;
    dialog.close();
    renderDecisionSummary();
    await refreshProjects();
    toast("已保存并更新 Markdown");
  }catch(err){toast(err.message)}
  finally{button.disabled=false}
};
$("#feedbackForm").onsubmit=async e=>{
  e.preventDefault();
  if(!state.selected)return;
  const form=e.target;
  const feedbackId=form.dataset.feedbackId;
  const button=$("#saveFeedbackBtn");
  button.disabled=true;
  try{
    const item=await api(
      feedbackId?`/api/knowledge-feedback/${feedbackId}/raw`:`/api/projects/${state.selected.id}/knowledge-feedback`,
      {method:feedbackId?"PATCH":"POST",body:JSON.stringify(feedbackFormPayload())}
    );
    $("#feedbackDialog").close();
    await refreshFeedbacks();
    toast(`${item.feedback_no} 原始反馈 MD 已保存`);
  }catch(err){toast(err.message)}
  finally{button.disabled=false}
};
async function saveCurrentFeedbackAnalysis(){
  const dialog=$("#feedbackAnalysisDialog");
  const id=dialog.dataset.feedbackId;
  if(!id)return null;
  return api(`/api/knowledge-feedback/${id}/analysis`,{
    method:"PATCH",
    body:JSON.stringify({content:$("#feedbackAnalysisContent").value})
  });
}
$("#saveFeedbackAnalysisBtn").onclick=async()=>{
  const button=$("#saveFeedbackAnalysisBtn");
  button.disabled=true;
  try{
    const item=await saveCurrentFeedbackAnalysis();
    await refreshFeedbacks();
    openFeedbackAnalysisDialog(item);
    toast("分析修改已保存，尚未写入正式知识库");
  }catch(err){toast(err.message)}
  finally{button.disabled=false}
};
$("#reanalyzeFeedbackBtn").onclick=async()=>{
  const dialog=$("#feedbackAnalysisDialog");
  const id=dialog.dataset.feedbackId;
  dialog.close();
  await runFeedbackAnalysis(id);
};
$("#publishFeedbackBtn").onclick=async()=>{
  const dialog=$("#feedbackAnalysisDialog");
  const id=dialog.dataset.feedbackId;
  const target=`${dialog.dataset.targetLabel}（${dialog.dataset.targetPath}）`;
  if(!window.confirm(`确认将标记区间内的内容写入 ${target}？\n\n该操作会生成写入前备份和差异记录，不会重新运行项目评审。`))return;
  const button=$("#publishFeedbackBtn");
  button.disabled=true;
  try{
    await saveCurrentFeedbackAnalysis();
    const item=await api(`/api/knowledge-feedback/${id}/publish`,{
      method:"POST",
      body:JSON.stringify({confirmed:true})
    });
    dialog.close();
    await refreshFeedbacks();
    toast(item.status==="已归档"?"已确认无需修改知识库":"知识条目已由 TPM 确认并发布");
  }catch(err){toast(err.message)}
  finally{button.disabled=false}
};
$("#confirmDeleteProjectBtn").onclick=async()=>{
  const dialog=$("#deleteProjectDialog");
  const id=dialog.dataset.projectId;
  if(!id)return;
  const button=$("#confirmDeleteProjectBtn");
  button.disabled=true;
  try{
    await api(`/api/projects/${id}`,{method:"DELETE"});
    dialog.close();
    if(state.selected?.id===id){
      stopPolling();
      state.selected=null;
      state.selectedStage=null;
      $("#projectView").hidden=true;
      $("#emptyState").hidden=false;
    }
    await refreshProjects();
    if(!state.selected&&state.projects[0])await selectProject(state.projects[0].id);
    toast("项目及本地文件已删除");
  }catch(err){toast(err.message)}
  finally{button.disabled=false}
};
$("#fileInput").onchange=async e=>{
  if(!state.selected||!e.target.files.length)return;
  const files=[...e.target.files];
  const chunkSize=4*1024*1024;
  const buttonText=$("#uploadButtonText");
  let uploadedCount=0;
  e.target.disabled=true;
  try{
    for(let fileIndex=0;fileIndex<files.length;fileIndex++){
      const file=files[fileIndex];
      if(file.size===0){toast(`${file.name} 是空文件`);continue}
      if(file.size>500*1024*1024){toast(`${file.name} 超过 500 MB`);continue}
      const totalChunks=Math.ceil(file.size/chunkSize);
      const uploadId=crypto.randomUUID();
      for(let chunkIndex=0;chunkIndex<totalChunks;chunkIndex++){
        const start=chunkIndex*chunkSize;
        const blob=file.slice(start,Math.min(start+chunkSize,file.size));
        const content=await new Promise((resolve,reject)=>{
          const reader=new FileReader();
          reader.onload=()=>resolve(reader.result.split(",")[1]);
          reader.onerror=()=>reject(new Error(`读取 ${file.name} 失败`));
          reader.readAsDataURL(blob);
        });
        const fileProgress=(chunkIndex+1)/totalChunks;
        const totalProgress=Math.round(((fileIndex+fileProgress)/files.length)*100);
        buttonText.textContent=`上传中 ${totalProgress}%`;
        await api(`/api/projects/${state.selected.id}/files/chunks`,{
          method:"POST",
          body:JSON.stringify({
            upload_id:uploadId,name:file.name,mime_type:file.type,file_size:file.size,
            chunk_index:chunkIndex,total_chunks:totalChunks,content_base64:content
          })
        });
      }
      uploadedCount++;
    }
    if(uploadedCount){
      await selectProject(state.selected.id);
      toast(`${uploadedCount} 份资料已上传并完成校验`);
    }else{
      toast("没有文件完成上传");
    }
  }catch(err){
    toast(err.message);
  }finally{
    buttonText.textContent="上传资料";
    e.target.disabled=false;
    e.target.value="";
  }
};
$("#startRunBtn").onclick=async()=>{
  if(!state.selected)return;
  if(!state.health?.executor_configured){toast("请先双击“设置智谱API.cmd”配置 API Key");return}
  try{const data=await api(`/api/projects/${state.selected.id}/runs`,{method:"POST",body:"{}"});await selectProject(state.selected.id);startPolling(data.run_id);toast("评审任务已进入队列")}
  catch(err){toast(err.message)}
};
$("#rerunBtn").onclick=()=>{
  if(!state.selected)return;
  const run=state.selected.runs?.[0];
  if(!run||["运行中","排队中"].includes(run.status))return;
  $("#rerunProjectName").textContent=`${state.selected.project_key.toUpperCase()} · ${state.selected.name}`;
  $("#rerunDialog").showModal();
};
async function submitRerun(mode,button){
  if(!state.selected)return;
  if(!state.health?.executor_configured){toast("请先双击“设置智谱API.cmd”配置 API Key");return}
  const originalText=button.textContent;
  button.disabled=true;
  button.textContent="正在准备重新评审…";
  try{
    const projectId=state.selected.id;
    const data=await api(`/api/projects/${projectId}/rerun`,{
      method:"POST",
      body:JSON.stringify({confirmed:true,mode})
    });
    $("#rerunDialog").close();
    await selectProject(projectId);
    startPolling(data.run_id);
    const summary=mode==="preserve_history"
      ?`已归档 ${data.archived_outputs} 份当前输出，新结果版本为 V${String(data.output_version).padStart(3,"0")}`
      :`已清空 ${data.removed_artifacts} 份历史产物，新结果从 V001 开始`;
    toast(`${summary}，评审已进入队列`);
  }catch(err){
    toast(err.message);
  }finally{
    button.disabled=false;
    button.textContent=originalText;
  }
}
$("#preserveHistoryRerunBtn").onclick=()=>submitRerun("preserve_history",$("#preserveHistoryRerunBtn"));
$("#replaceAllRerunBtn").onclick=()=>submitRerun("replace_all",$("#replaceAllRerunBtn"));
$("#closeFileDialog").onclick=()=>$("#fileDialog").close();
$("#closePreviewDialog").onclick=()=>$("#previewDialog").close();
$("#previewDoneBtn").onclick=()=>$("#previewDialog").close();
$("#previewLocationBtn").onclick=()=>{
  const dialog=$("#previewDialog");const kind=dialog.dataset.kind;const id=dialog.dataset.id;
  if(kind==="feedback")return;
  const item=kind==="file"?state.selected.files.find(x=>x.id===id):state.selected.artifacts.find(x=>x.id===id);
  dialog.close();if(item)showFileLocation(kind,item);
};
$("#copyPathBtn").onclick=async()=>{
  try{await navigator.clipboard.writeText($("#fileDialogPath").value);toast("路径已复制")}
  catch{toast("无法自动复制，请在路径框中手动复制")}
};
$("#revealFileBtn").onclick=async()=>{
  const dialog=$("#fileDialog");
  try{await api("/api/reveal",{method:"POST",body:JSON.stringify({kind:dialog.dataset.kind,id:dialog.dataset.id})});toast("已在资源管理器中定位")}
  catch(err){toast(err.message)}
};
init().catch(err=>toast(err.message));
