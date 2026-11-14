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
  let vistos={}, cola=[], navVisto=null, sirenaOn=false, sirenaTimer=null, ctx=null, nbeep=0, uref=null;
  let ultimoEstado='', oido='', diag=[];
  const LS = {get:function(k,d){try{return localStorage.getItem(k)||d;}catch(_){return d;}}, set:function(k,v){try{localStorage.setItem(k,v);}catch(_){}}};

  /* ---------- panel flotante ---------- */
  function panel(){
    let el=document.getElementById('voz-panel');
    if(el) return el;
    el=document.createElement('div'); el.id='voz-panel';
    el.style.cssText='position:fixed;bottom:16px;right:16px;z-index:9999;font:13px sans-serif;color:#fff;max-width:300px';
    el.innerHTML='<div id="vp-barra" style="display:flex;gap:6px;align-items:center;justify-content:flex-end">'+
      '<span id="vp-estado" style="padding:6px 12px;border-radius:16px;background:#1B2128;border:1px solid #E4405F"></span>'+
      '<button id="vp-ajustes" title="Voz y diagnóstico" style="border:1px solid #E4405F;background:#1B2128;color:#fff;border-radius:50%;width:32px;height:32px;cursor:pointer">⚙️</button></div>'+
      '<div id="vp-det" style="display:none;margin-top:8px;padding:12px;border-radius:12px;background:#1B2128;border:1px solid #444">'+
      '<div style="margin-bottom:6px"><b>Voz del médico</b></div>'+
      '<select id="vp-voz" style="width:100%;margin-bottom:6px;padding:4px"></select>'+
      '<div style="margin-bottom:6px">Velocidad <input id="vp-vel" type="range" min="0.7" max="1.4" step="0.05" style="width:130px;vertical-align:middle"></div>'+
      '<div style="display:flex;gap:6px;margin-bottom:8px"><button id="vp-probar" style="flex:1;padding:5px;cursor:pointer">🔊 Probar voz</button><button id="vp-pitido" style="flex:1;padding:5px;cursor:pointer">🔔 Probar pitido</button></div>'+
      '<div id="vp-diag" style="opacity:.75;font-size:11px;white-space:pre-wrap"></div></div>';
    document.body.appendChild(el);
    el.querySelector('#vp-ajustes').onclick=function(){const d=el.querySelector('#vp-det'); d.style.display=d.style.display==='none'?'block':'none'; llenarVoces(); pintaDiag();};
    el.querySelector('#vp-voz').onchange=function(e){LS.set('voz_nombre',e.target.value);};
    const vel=el.querySelector('#vp-vel'); vel.value=LS.get('voz_vel','1'); vel.onchange=function(e){LS.set('voz_vel',e.target.value);};
    el.querySelector('#vp-probar').onclick=function(){ asegurarAudio(); decir('Hola, soy su médico virtual. Así suena mi voz.', true); };
    el.querySelector('#vp-pitido').onclick=function(){ asegurarAudio(); for(let i=0;i<3;i++) setTimeout(beep,i*500); };
    return el;
  }
  function llenarVoces(){
    const sel=panel().querySelector('#vp-voz'); if(!sel) return;
    const vs=speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('es')===0;});
    const actual=LS.get('voz_nombre','');
    sel.innerHTML='<option value="">(automática)</option>'+vs.map(function(v){return '<option value="'+v.name+'"'+(v.name===actual?' selected':'')+'>'+v.name+' · '+v.lang+'</option>';}).join('');
  }
  function log(m){ diag.push(m); if(diag.length>6) diag.shift(); pintaDiag(); }
  function pintaDiag(){
    const d=document.getElementById('vp-diag'); if(!d) return;
    d.textContent='Audio: '+(ctx?ctx.state:'sin iniciar')+' · Voces es: '+speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('es')===0;}).length+
      ' · Reconocimiento: '+(SR?'sí':'NO (use Chrome/Edge)')+'\n'+diag.join('\n');
  }
  function estado(t){ ultimoEstado=t||''; const e=panel().querySelector('#vp-estado'); e.style.display=t?'inline-block':'none'; e.textContent=t||''; }

  /* ---------- activación ---------- */
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
  function asegurarAudio(){
    try{ ctx=ctx||new (window.AudioContext||window.webkitAudioContext)(); if(ctx.state!=='running') ctx.resume(); }catch(e){ log('Audio: '+e); }
  }
  function desbloquear(){
    desbloqueado=true; overlay(false); asegurarAudio(); llenarVoces();
    speechSynthesis.onvoiceschanged=llenarVoces;
    sirena(sirenaOn); siguiente(); log('Activado');
  }

  /* ---------- voz de salida ---------- */
  function elegirVoz(){
    const vs=speechSynthesis.getVoices(), nombre=LS.get('voz_nombre','');
    if(nombre){ const v=vs.find(function(v){return v.name===nombre;}); if(v) return v; }
    const es=vs.filter(function(v){return v.lang.toLowerCase().indexOf('es')===0;});
    return es.find(function(v){return /natural|online|google/i.test(v.name);}) || es[0] || null;
  }
  function trozos(texto){
    const partes=texto.split(/(?<=[.!?:;])\s+/), res=[]; let acc='';
    partes.forEach(function(p){ if((acc+' '+p).length>170 && acc){res.push(acc);acc=p;} else acc=(acc?acc+' ':'')+p; });
    if(acc) res.push(acc); return res;
  }
  function decir(texto, inmediato){
    const lista=trozos(texto); let i=0;
    if(inmediato){ try{speechSynthesis.cancel();}catch(_){} }
    function uno(){
      if(i>=lista.length){ speaking=false; if(!inmediato) siguiente(); return; }
      const u=new SpeechSynthesisUtterance(lista[i++]); uref=u;      // referencia: evita que Chrome la descarte
      u.lang='es-MX'; u.rate=parseFloat(LS.get('voz_vel','1'))||1;
      const v=elegirVoz(); if(v){ u.voice=v; u.lang=v.lang; }
      u.onend=function(){ uno(); };
      u.onerror=function(e){ log('Voz: '+(e.error||'error')); uno(); };
      speechSynthesis.speak(u);
    }
    speaking=true; estado('🔊 Hablando…'); parar();
    setTimeout(uno, inmediato?120:0);
  }
  function siguiente(){
    if(speaking||!desbloqueado) return;
    if(!cola.length){ busy=false; clearTimeout(busyTimer); estado(''); iniciar(); return; }
    decir(cola.shift(), false);
  }

  /* ---------- micrófono ---------- */
  function iniciar(){
    if(!on||!desbloqueado||busy||speaking||rec) return;
    if(!SR){estado('Use Chrome o Edge para hablar');return;}
    rec=new SR(); rec.lang='es-MX'; rec.interimResults=false; rec.continuous=false; rec.maxAlternatives=1;
    rec.onresult=function(e){ const t=(e.results[0][0].transcript||'').trim(); oido=t; log('Oí: '+t); if(t) enviar(t); };
    rec.onend=function(){ rec=null; setTimeout(iniciar,300); };
    rec.onerror=function(e){
      if(e.error==='no-speech'||e.error==='aborted') return;
      log('Micrófono: '+e.error);
      if(e.error==='not-allowed'||e.error==='service-not-allowed'){ on=false; rec=null; estado('Permiso de micrófono denegado'); }
    };
    try{ rec.start(); estado('🎙️ Escuchando…'); }catch(e){ rec=null; log('Mic start: '+e); }
  }
  function parar(){ if(rec){const r=rec; rec=null; r.onend=null; try{r.abort();}catch(_){}} }
  function enviar(t, reintento){
    const ta=document.querySelector('[data-testid="stChatInputTextArea"]');
    if(!ta){
      log('No encuentro el cuadro de chat'+(reintento?'':' · abro el asistente'));
      if(!reintento){ navegar(['Detalle','Asistente IA']); setTimeout(function(){enviar(t,true);},900); }
      return;
    }
    const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
    set.call(ta,t); ta.dispatchEvent(new Event('input',{bubbles:true}));
    busy=true; clearTimeout(busyTimer);
    busyTimer=setTimeout(function(){busy=false;iniciar();},45000);
    estado('🧠 Pensando: '+t.slice(0,40));
    setTimeout(function(){
      const b=document.querySelector('[data-testid="stChatInputSubmitButton"]');
      if(b){ b.click(); log('Enviado'); } else { log('No encuentro el botón de enviar'); busy=false; }
    },250);
  }

  /* ---------- pitido ---------- */
  function beep(){
    if(!ctx) return;
    try{ if(ctx.state!=='running') ctx.resume();
      const o=ctx.createOscillator(), g=ctx.createGain();
      o.type='square'; o.frequency.value=(nbeep++%2)?700:950; g.gain.value=0.3;
      o.connect(g); g.connect(ctx.destination); o.start(); o.stop(ctx.currentTime+0.4);
    }catch(e){ log('Pitido: '+e); }
  }
  function sirena(activa){
    clearInterval(sirenaTimer); sirenaTimer=null;
    if(!activa) return;
    asegurarAudio(); beep(); sirenaTimer=setInterval(beep,650);
  }

  /* ---------- navegación ---------- */
  function navegar(pasos){
    (function clic(i){
      const b=[].slice.call(document.querySelectorAll('button[role="tab"]')).find(function(x){return x.textContent.indexOf(pasos[i])>=0;});
      if(b) b.click();
      if(i+1<pasos.length) setTimeout(function(){clic(i+1);},350);
    })(0);
  }

  panel();
  return {config:function(o){
    on=!!o.on; const antes=sirenaOn; sirenaOn=!!o.sirena;
    if(!desbloqueado && hayActivacion()) desbloquear();
    if(desbloqueado && antes!==sirenaOn) sirena(sirenaOn);
    (o.speak||[]).forEach(function(it){ if(!vistos[it.id]){vistos[it.id]=1; cola.push(it.text);} });
    if(o.nav && o.nav.id!==navVisto){ navVisto=o.nav.id; navegar(o.nav.pasos); }
    if(!on){ parar(); try{speechSynthesis.cancel();}catch(_){} speaking=false; cola.length=0; estado(''); overlay(false); return; }
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
