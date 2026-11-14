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
  let rec=null, on=false, busy=false, speaking=false, lastId=null, busyTimer=null;
  function estado(t){
    let el=document.getElementById('voz-estado');
    if(!el){el=document.createElement('div');el.id='voz-estado';
      el.style.cssText='position:fixed;bottom:80px;right:16px;z-index:9999;padding:6px 14px;border-radius:16px;background:#1B2128;color:#fff;font:13px sans-serif;border:1px solid #E4405F;display:none';
      document.body.appendChild(el);}
    el.style.display=t?'block':'none'; el.textContent=t||'';
  }
  function iniciar(){
    if(!on||busy||speaking||rec) return;
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
  function hablar(texto){
    speechSynthesis.cancel(); parar(); speaking=true; estado('🔊 Hablando…');
    const u=new SpeechSynthesisUtterance(texto); u.lang='es-MX';
    const v=speechSynthesis.getVoices().find(function(v){return v.lang.toLowerCase().indexOf('es')===0;});
    if(v) u.voice=v;
    u.onend=u.onerror=function(){speaking=false;busy=false;clearTimeout(busyTimer);estado('');iniciar();};
    speechSynthesis.speak(u);
  }
  return {config:function(o){
    on=!!o.on;
    if(!on){parar();speechSynthesis.cancel();speaking=false;busy=false;estado('');return;}
    if(o.speak && o.id!==lastId){lastId=o.id;hablar(o.speak);} else {iniciar();}
  }};
})();
"""


def limpiar_para_voz(texto: str) -> str:
    t = re.sub(r"\([A-Z]{2,4}\d{2,}\)", "", texto)      # códigos (MED014) no se leen
    t = re.sub(r"\[\[.*?\]\]", "", t)
    t = re.sub(r"[*_#>`|]+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def componente(activo: bool, hablar: str | None = None, id_mensaje: str | None = None) -> None:
    """Se llama en cada ejecución. hablar solo viene con texto cuando hay respuesta nueva."""
    cfg = {"on": activo, "speak": limpiar_para_voz(hablar) if hablar else None, "id": id_mensaje}
    components.html(f"""<script>
    (function(){{
      try {{
        const P = window.parent, D = P.document;
        if (!P.__voz) {{ const s = D.createElement('script'); s.textContent = {json.dumps(JS)}; D.head.appendChild(s); }}
        P.__voz.config({json.dumps(cfg)});
      }} catch (e) {{ console.log('voz no disponible', e); }}
    }})();
    </script>""", height=0)
