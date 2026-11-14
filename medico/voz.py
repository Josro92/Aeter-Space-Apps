"""Voz en el navegador (Chrome/Edge): escucha, envía al chat y lee la respuesta en voz alta.

Usa las funciones del propio navegador (sin llaves ni costo). El código JS se instala
una sola vez en la página y sobrevive a los reruns de Streamlit.
"""
import json
import re

import streamlit.components.v1 as components

JS = r"""
window.__voz = (function(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  let rec=null, on=false, busy=false, speaking=false, busyTimer=null, desbloqueado=false;
  let vistos={}, cola=[], navVisto=null, sirenaOn=false, sirenaTimer=null, ctx=null, nbeep=0;
  function estado(t){
    let el=document.getElementById('voz-estado');
    if(!el){el=document.createElement('div');el.id='voz-estado';
      el.style.cssText='position:fixed;bottom:80px;right:16px;z-index:9999;padding:6px 14px;border-radius:16px;background:#1B2128;color:#fff;font:13px sans-serif;border:1px solid #E4405F;display:none';
      document.body.appendChild(el);}
    el.style.display=t?'block':'none'; el.textContent=t||'';
  }
  function overlay(mostrar){
    let b=document.getElementById('voz-overlay');
    if(!mostrar){ if(b) b.remove(); return; }
    if(b) return;
    b=document.createElement('button'); b.id='voz-overlay';
    b.textContent='🎙️ Toque en cualquier parte para activar al médico virtual';
    b.style.cssText='position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:10000;padding:14px 26px;border-radius:30px;border:2px solid #E4405F;background:#E4405F;color:#fff;font:600 16px sans-serif;cursor:pointer;box-shadow:0 4px 20px rgba(0,0,0,.5)';
    b.onclick=desbloquear; document.body.appendChild(b);
    document.addEventListener('pointerdown', function f(){ document.removeEventListener('pointerdown', f); if(!desbloqueado) desbloquear(); }, true);
  }
  function hayActivacion(){ return !!(navigator.userActivation && navigator.userActivation.hasBeenActive); }
  function desbloquear(){
    desbloqueado=true; overlay(false);
    try{ ctx=ctx||new (window.AudioContext||window.webkitAudioContext)(); ctx.resume(); }catch(_){}
    sirena(sirenaOn); siguiente();
  }
  function iniciar(){
    if(!on||!desbloqueado||busy||speaking||rec) return;
    if(!SR){estado('Este navegador no tiene reconocimiento de voz: use Chrome o Edge');return;}
    rec=new SR(); rec.lang='es-MX'; rec.interimResults=false; rec.continuous=false;
    rec.onresult=function(e){const t=(e.results[0][0].transcript||'').trim(); if(t) enviar(t);};
    rec.onend=function(){rec=null; setTimeout(iniciar,300);};
    rec.onerror=function(e){ if(e.error==='not-allowed'||e.error==='service-not-allowed'){on=false;rec=null;estado('Permiso de micrófono denegado');} };
    try{rec.start(); estado('🎙️ Escuchando…');}catch(_){rec=null;}
  }
  function parar(){ if(rec){const r=rec; rec=null; r.onend=null; try{r.abort();}catch(_){}} }
  function enviar(t){
    const ta=document.querySelector('[data-testid="stChatInputTextArea"]');
    if(!ta) return;
    const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
    set.call(ta,t); ta.dispatchEvent(new Event('input',{bubbles:true}));
    busy=true; clearTimeout(busyTimer);
    busyTimer=setTimeout(function(){busy=false;iniciar();},45000);
    estado('🧠 Pensando…');
    setTimeout(function(){const b=document.querySelector('[data-testid="stChatInputSubmitButton"]'); if(b) b.click();},200);
  }
  function siguiente(){
    if(speaking||!desbloqueado) return;
    if(!cola.length){ busy=false; clearTimeout(busyTimer); estado(''); iniciar(); return; }
    const texto=cola.shift();
    speechSynthesis.cancel(); parar(); speaking=true; estado('🔊 Hablando…');
    const u=new SpeechSynthesisUtterance(texto); u.lang='es-MX';
    const v=speechSynthesis.getVoices().find(function(v){return v.lang.toLowerCase().indexOf('es')===0;});
    if(v) u.voice=v;
    u.onend=u.onerror=function(){speaking=false; siguiente();};
    speechSynthesis.speak(u);
  }
  function sirena(activa){
    clearInterval(sirenaTimer); sirenaTimer=null;
    if(!activa||!ctx) return;
    sirenaTimer=setInterval(function(){
      try{ const o=ctx.createOscillator(), g=ctx.createGain();
        o.type='square'; o.frequency.value=(nbeep++%2)?660:880; g.gain.value=0.08;
        o.connect(g); g.connect(ctx.destination); o.start(); o.stop(ctx.currentTime+0.35); }catch(_){}
    },600);
  }
  function navegar(pasos){
    (function clic(i){
      const b=[].slice.call(document.querySelectorAll('button[role="tab"]')).find(function(x){return x.textContent.indexOf(pasos[i])>=0;});
      if(b) b.click();
      if(i+1<pasos.length) setTimeout(function(){clic(i+1);},350);
    })(0);
  }
  return {config:function(o){
    on=!!o.on; sirenaOn=!!o.sirena;
    if(!desbloqueado && hayActivacion()) desbloquear();
    if(desbloqueado) sirena(sirenaOn);
    (o.speak||[]).forEach(function(it){ if(!vistos[it.id]){vistos[it.id]=1; cola.push(it.text);} });
    if(o.nav && o.nav.id!==navVisto){ navVisto=o.nav.id; navegar(o.nav.pasos); }
    if(!on){ parar(); speechSynthesis.cancel(); speaking=false; cola.length=0; estado(''); overlay(false); return; }
    if(!desbloqueado){ overlay(true); return; }
    siguiente();
  }};
})();
"""


def limpiar_para_voz(texto: str) -> str:
    t = re.sub(r"\([A-Z]{2,4}\d{2,}\)", "", texto)      # códigos (MED014) no se leen
    t = re.sub(r"\[\[.*?\]\]", "", t)
    t = re.sub(r"[*_#>`|]+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def componente(activo: bool, hablar: list[dict] | None = None, sirena: bool = False,
               nav: dict | None = None) -> None:
    """Se llama en cada ejecución. hablar: [{'id','text'}]; nav: {'id','pasos'}."""
    cfg = {"on": activo, "sirena": sirena, "nav": nav,
           "speak": [{"id": h["id"], "text": limpiar_para_voz(h["text"])} for h in (hablar or [])]}
    html = f"""<script>
    (function(){{
      try {{
        const P = window.parent, D = P.document;
        if (!P.__voz) {{ const s = D.createElement('script'); s.textContent = {json.dumps(JS)}; D.head.appendChild(s); }}
        P.__voz.config({json.dumps(cfg)});
      }} catch (e) {{ console.log('voz no disponible', e); }}
    }})();
    </script>"""
    import streamlit as st
    if hasattr(st, "iframe"):          # versiones nuevas de Streamlit
        st.iframe(html, height=1)
    else:
        components.html(html, height=0)
