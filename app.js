
const API_BASE = window.AGRIGUARD_API || "";
function $(id){return document.getElementById(id)}
function show(id, html){const el=$(id); if(el){el.innerHTML=html;el.style.display="block"}}
function hide(id){const el=$(id);if(el)el.style.display="none"}

async function healthCheck(){
  try{const r=await fetch(`${API_BASE}/api/health`); return await r.json();}
  catch(e){return null}
}

async function predictLeaf(file){
  const form=new FormData(); form.append("file",file);
  const r=await fetch(`${API_BASE}/api/predict`,{method:"POST",body:form});
  if(!r.ok) throw new Error("Prediction service unavailable");
  return await r.json();
}

async function loadMarket(params){
  const qs=new URLSearchParams(params).toString();
  const r=await fetch(`${API_BASE}/api/market?${qs}`);
  if(!r.ok) throw new Error("Market service unavailable");
  return await r.json();
}

function setupLanguageLinks(){
  document.querySelectorAll("[data-lang]").forEach(a=>{
    a.addEventListener("click",()=>{});
  });
}

function startVoice(lang,targetId,statusId){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){show(statusId,"Speech recognition is not supported in this browser.");return}
  const rec=new SR(); rec.lang=lang; rec.interimResults=false; rec.maxAlternatives=1;
  rec.onstart=()=>show(statusId,lang.startsWith("hi")?"सुन रहा हूँ…":"Listening…");
  rec.onerror=()=>show(statusId,lang.startsWith("hi")?"आवाज़ पहचान नहीं हो सकी।":"Could not recognize speech.");
  rec.onresult=e=>{ $(targetId).value=e.results[0][0].transcript; show(statusId,lang.startsWith("hi")?"आवाज़ दर्ज हो गई।":"Speech captured."); };
  rec.start();
}
function speak(text,lang){
  if(!("speechSynthesis" in window)){return}
  speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(text); u.lang=lang; speechSynthesis.speak(u);
}
document.addEventListener("DOMContentLoaded",setupLanguageLinks);
