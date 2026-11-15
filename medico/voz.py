"""Voz en el navegador (Chrome/Edge): escucha, envía al chat y lee la respuesta en voz alta.

Diseño seguro (v3, solo con botón):
  Hablar -> escucha y envía al chat -> micrófono cerrado mientras Aéter responde en voz alta ->
  vuelve a escuchar unos 5 s: si no se dice nada se apaga; si se hace otra pregunta, repite el ciclo.
  Mientras Aéter habla, el botón pasa a «Silenciar» (la calla y escucha una nueva pregunta).
Usa las funciones del propio navegador (sin llaves ni costo). El código JS se instala
una sola vez en la página y sobrevive a los reruns de Streamlit.
"""
import json
import re

import streamlit.components.v1 as components

VERSION_JS = "6"

JS = r"""
window.__voz = (function(){
  const VER='6';
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const LS = {get:function(k,d){try{return localStorage.getItem(k)||d;}catch(_){return d;}}, set:function(k,v){try{localStorage.setItem(k,v);}catch(_){}}};
  function norm(s){ return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,''); }
  function limpio(s){ return ' '+s.replace(/[^a-z0-9ñ ]/g,' ').replace(/\s+/g,' ').trim()+' '; }
  const LLAMADO=/(^|[^a-z])(aeter|a eter|ae ter|aether|a ether|ayter|aiter|aider|ayder|ether|eter|ater|ahter|el eter|el ether)([^a-z]|$)/;
  const QUITAR=/^\s*(oye|hey|ok|okay|hola|buenas)?[\s,.:;!¡¿?]*(el )?(a ?[eé] ?t(?:h)?er|a[iy][td]er|[eé]t(?:h)?er|ater|ahter)(?![a-záéíóúñ])[\s,.:;!¡¿?]*/i;

  function esLlamado(w){ return w.length>=4 && w.length<=6 && /^(h|j)?a?[eiy]?(t|d)(e|a)?r$/.test(w) || w==='ether' || w==='aether' || w==='haeter'; }
  const RELLENO=/^(oye|hey|hola|ok|okay|buenas|el|a)$/;
  function hayLlamado(t){
    const n=norm(t); if(LLAMADO.test(n)) return true;
    const w=limpio(n).trim().split(' ');
    for(let i=0;i<Math.min(w.length,3);i++){ if(RELLENO.test(w[i]) && i<w.length-1) continue; return esLlamado(w[i]); }
    return false;
  }
  function sinLlamado(t){
    const w=t.trim().split(/\s+/); let i=0;
    while(i<w.length){
      const p=norm(w[i]).replace(/[^a-z0-9ñ]/g,'');
      if(RELLENO.test(p) && i<w.length-1 && hayLlamado(w.slice(i).join(' '))){ i++; continue; }
      if(esLlamado(p) || LLAMADO.test(' '+p+' ')){ i++; }
      break;
    }
    return w.slice(i).join(' ').replace(/^[\s,.:;!¡¿?]+/,'').trim();
  }
  let on=false, desbloqueado=false, ctx=null, nbeep=0;
  let rec=null, recTipo='', silencioTimer=null, busy=false, busyTimer=null;
  let speaking=false, vozToken=0, vozTimer=null, finHabla=0, hablado=[], uref=null, esRespuesta=false, hablaRespuesta=false;
  let cola=[], vistos={}, navVisto=null, sirenaOn=false, sirenaTimer=null;
  let diag=[], avisoTimer=null, ventanaHasta=0;

  function seguir(){ return true; }

  /* ---------- panel ---------- */
  function panel(){
    let el=document.getElementById('voz-panel'); if(el) return el;
    el=document.createElement('div'); el.id='voz-panel';
    el.style.cssText='position:fixed;bottom:104px;right:16px;z-index:9999;font:13px sans-serif;color:#fff;max-width:310px';
    el.innerHTML='<div id="vp-ultimo" style="text-align:right;font-size:11px;opacity:.7;margin-bottom:4px;max-width:310px"></div>'+
      '<div style="display:flex;gap:6px;align-items:center;justify-content:flex-end">'+
      '<button id="vp-hablar" style="border:1px solid rgba(255,255,255,.55);background:#0b0b7a;color:#fff;border-radius:22px;height:40px;min-width:92px;padding:0 18px;cursor:pointer;font:600 14px Poppins,sans-serif">Talk</button>'+
      '<span id="vp-estado" style="display:none;padding:6px 14px;border-radius:16px;background:rgba(15,20,45,.7);border:1px solid rgba(255,255,255,.4);backdrop-filter:blur(8px);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></span>'+
      '<button id="vp-ajustes" style="border:1px solid rgba(255,255,255,.45);background:rgba(15,20,45,.7);color:#fff;border-radius:20px;height:34px;padding:0 14px;cursor:pointer;font:600 12px Poppins,sans-serif">Settings</button></div>'+
      '<div id="vp-det" style="display:none;margin-top:8px;padding:12px;border-radius:16px;background:rgba(15,20,45,.92);border:1px solid rgba(255,255,255,.3);backdrop-filter:blur(14px)">'+
      '<div style="margin-bottom:6px"><b>Voice of Aéter</b></div>'+
      '<select id="vp-voz" style="width:100%;margin-bottom:6px;padding:4px"></select>'+
      '<div style="margin-bottom:6px">Speed <input id="vp-vel" type="range" min="0.8" max="1.5" step="0.05" style="width:130px;vertical-align:middle"></div>'+
      '<div style="display:flex;gap:6px;margin-bottom:8px"><button id="vp-probar" style="flex:1;padding:5px;cursor:pointer">Test voice</button><button id="vp-pitido" style="flex:1;padding:5px;cursor:pointer">Test beep</button></div>'+
      '<button id="vp-nivel" style="width:100%;padding:5px;margin-bottom:4px;cursor:pointer">Test microphone (6 s)</button>'+
      '<div style="height:8px;background:#333;border-radius:4px;margin-bottom:8px;overflow:hidden"><div id="vp-barra-nivel" style="height:100%;width:0;background:#2ecc71"></div></div>'+
      '<button id="vp-reset" style="width:100%;padding:6px;margin-bottom:8px;cursor:pointer;font-weight:700">Reset voice</button>'+
      '<div id="vp-diag" style="opacity:.75;font-size:11px;white-space:pre-wrap;max-height:150px;overflow:auto"></div></div>';
    document.body.appendChild(el);
    const q=function(id){return el.querySelector(id);};
    q('#vp-hablar').onclick=function(){ clicHablar(); };
    q('#vp-ajustes').onclick=function(){ const d=q('#vp-det'); d.style.display=d.style.display==='none'?'block':'none'; llenarVoces(); pintaDiag(); };
    q('#vp-voz').onchange=function(e){ LS.set('voz_nombre',e.target.value); };
    q('#vp-vel').value=LS.get('voz_vel','1'); q('#vp-vel').onchange=function(e){ LS.set('voz_vel',e.target.value); };
    q('#vp-probar').onclick=function(){ asegurarAudio(); desbloqueado=true; overlay(false); cola.length=0; esRespuesta=false; decir('Hello, I am your virtual assistant. This is how my voice sounds.'); };
    q('#vp-pitido').onclick=function(){ asegurarAudio(); for(let i=0;i<3;i++) setTimeout(beep,i*500); };
    q('#vp-nivel').onclick=function(){ probarMicrofono(); };
    q('#vp-reset').onclick=function(){ reiniciar(false); };
    return el;
  }
  function llenarVoces(){
    const sel=panel().querySelector('#vp-voz'); if(!sel) return;
    const vs=speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('en')===0;});
    const actual=LS.get('voz_nombre','');
    sel.innerHTML='<option value="">(automatic: best US English voice)</option>'+vs.map(function(v){return '<option value="'+v.name+'"'+(v.name===actual?' selected':'')+'>'+v.name+' · '+v.lang+'</option>';}).join('');
  }
  function log(m){
    const h=new Date().toLocaleTimeString('en-US',{hour12:false});
    if(diag.length && diag[diag.length-1].slice(10).trim()===m) return;
    diag.push(h+'  '+m); if(diag.length>14) diag.shift(); pintaDiag();
    const u=document.getElementById('vp-ultimo'); if(u) u.textContent=m;
  }
  function pintaDiag(){
    const d=document.getElementById('vp-diag'); if(!d) return;
    d.textContent='Audio: '+(ctx?ctx.state:'not started')+' · English voices: '+speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('en')===0;}).length+
      ' · Speech recognition: '+(SR?'yes':'NO (use Chrome/Edge)')+' · Button only\n'+diag.slice().reverse().join('\n');
  }
  function estado(t){ const e=panel().querySelector('#vp-estado'); e.style.display=t?'inline-block':'none'; e.textContent=t||''; }
  function aviso(t, ms){ clearTimeout(avisoTimer); estado(t); avisoTimer=setTimeout(refrescar, ms||3000); }
  function refrescar(){
    const b=panel().querySelector('#vp-hablar'); if(!b) return;
    if(speaking){ b.textContent='Mute'; estado('Speaking…'); }
    else if(busy){ b.textContent='Talk'; estado('Thinking…'); }
    else if(rec && recTipo==='una'){ b.textContent='Send'; estado('Listening…'); }
    else { b.textContent='Talk'; estado(''); }
  }

  /* ---------- activación de audio ---------- */
  function overlay(mostrar){
    let b=document.getElementById('voz-overlay');
    if(!mostrar){ if(b) b.remove(); return; }
    if(b) return;
    b=document.createElement('button'); b.id='voz-overlay';
    b.textContent='Tap anywhere to activate Aéter';
    b.style.cssText='position:fixed;bottom:112px;left:50%;transform:translateX(-50%);z-index:10000;padding:14px 26px;border-radius:30px;border:1px solid rgba(255,255,255,.6);background:#0b0b7a;color:#fff;font:600 16px Poppins,sans-serif;cursor:pointer;box-shadow:0 4px 20px rgba(0,0,0,.5)';
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
    sirena(sirenaOn); log('Activated'); siguiente();
  }

  /* ---------- voz de salida (el micrófono se apaga mientras habla) ---------- */
  function puntajeVoz(v){
    const n=v.name, l=v.lang.toLowerCase().replace('_','-'); let p=0;
    if(l==='en-us') p+=40; else if(l.indexOf('en')===0) p+=10; else return -1;
    if(/natural|neural/i.test(n)) p+=50;                                   // Edge: voces neuronales
    if(/\b(aria|jenny|guy|ava|andrew|emma|brian|michelle|steffan|ana)\b/i.test(n)) p+=25;
    if(/online/i.test(n)) p+=20;
    if(/google us english/i.test(n)) p+=45;                               // Chrome
    if(/samantha|ava|allison|nicky|zoe|evan|nathan|siri/i.test(n)) p+=30; // Apple
    if(/zira|david|mark/i.test(n)) p+=8;                                  // Windows clásicas
    if(/espeak|compact/i.test(n)) p-=30;
    if(v.localService===false) p+=5;
    return p;
  }
  function elegirVoz(){
    const vs=speechSynthesis.getVoices(), nombre=LS.get('voz_nombre','');
    if(nombre){ const v=vs.find(function(v){return v.name===nombre;}); if(v) return v; }
    let mejor=null, mp=-1;
    vs.forEach(function(v){ const p=puntajeVoz(v); if(p>mp){ mp=p; mejor=v; } });   // la mejor voz en inglés de EE. UU.
    return mejor;
  }
  function trozos(texto){
    const partes=texto.split(/(?<=[.!?:;])\s+/), res=[]; let acc='';
    partes.forEach(function(p){ if((acc+' '+p).length>170 && acc){res.push(acc);acc=p;} else acc=(acc?acc+' ':'')+p; });
    if(acc) res.push(acc); return res;
  }
  function cortarVoz(){ vozToken++; clearTimeout(vozTimer); try{speechSynthesis.cancel();}catch(_){} speaking=false; refrescar(); }
  function decir(texto){
    cortarVoz();
    parar();                                          // micrófono cerrado mientras habla: no se oye a sí mismo
    const lista=trozos(texto); let i=0; const tk=++vozToken;
    hablaRespuesta=esRespuesta;
    function uno(){
      if(tk!==vozToken) return;
      if(i>=lista.length){ terminarHabla(tk); return; }
      const u=new SpeechSynthesisUtterance(lista[i++]); uref=u;
      u.lang='en-US'; u.rate=parseFloat(LS.get('voz_vel','1'))||1;
      const v=elegirVoz(); if(v){ u.voice=v; u.lang=v.lang; }
      u.onend=function(){ if(tk===vozToken) uno(); };
      u.onerror=function(e){ if(tk!==vozToken||e.error==='interrupted'||e.error==='canceled') return; log('Voice: '+(e.error||'error')); uno(); };
      try{ speechSynthesis.resume(); }catch(_){}
      speechSynthesis.speak(u);
    }
    speaking=true; refrescar();
    hablado.push({n:norm(texto),ts:Date.now()}); if(hablado.length>6) hablado.shift();
    clearTimeout(vozTimer);
    vozTimer=setTimeout(function(){ if(speaking && tk===vozToken){ log('The voice did not finish: continuing'); terminarHabla(tk); } }, 6000+texto.length*110);
    setTimeout(uno, 80);
  }
  function terminarHabla(tk){
    if(tk!==vozToken) return;
    clearTimeout(vozTimer); speaking=false; finHabla=Date.now(); refrescar();
    if(cola.length){ setTimeout(siguiente, 150); return; }
    const respondio=hablaRespuesta; hablaRespuesta=false;
    if(!on) return;
    // El micrófono NO se reabre solo: para hablar de nuevo hay que tocar «Talk».
  }
  function siguiente(){
    if(speaking||!desbloqueado||!on) return;
    if(!cola.length) return;
    if(rec && recTipo==='una'){ setTimeout(siguiente, 600); return; }      // no pisar al usuario mientras habla
    const it=cola.shift(); esRespuesta=!!it.resp; decir(it.text);
  }

  /* ---------- micrófono ---------- */
  function parar(){ clearTimeout(silencioTimer); if(rec){ const r=rec; rec=null; recTipo=''; r.onend=null; r.onresult=null; r.onerror=null; try{r.abort();}catch(_){} } refrescar(); }
  function nuevoSR(continuo){
    const r=new SR(); r.lang='en-US'; r.interimResults=true; r.continuous=!!continuo; r.maxAlternatives=3; return r;
  }
  function escuchar(tipo){                                          // una sola frase: «Hablar»
    asegurarAudio();
    if(!desbloqueado){ desbloqueado=true; overlay(false); llenarVoces(); }
    if(!SR){ aviso('Use Chrome or Edge to talk'); log('This browser has no speech recognition'); return; }
    cortarVoz(); parar(); cola.length=0;
    const r=nuevoSR(false); let final='', parcial=''; rec=r; recTipo='una';
    let ventana=null;
    r.onstart=function(){
      log(tipo==='seguimiento'?'I am listening (5 s)':'Speak now'); refrescar();
      if(tipo==='seguimiento') ventana=setTimeout(function(){ if(!final.trim()&&!parcial.trim()){ log('Nothing heard: microphone off'); try{r.abort();}catch(_){} } }, 5000);
    };
    r.onresult=function(e){
      clearTimeout(ventana); parcial=''; for(let i=e.resultIndex;i<e.results.length;i++){ const x=e.results[i][0].transcript; if(e.results[i].isFinal) final+=x; else parcial+=x; }
      estado((final+parcial).trim().slice(0,40)||'Listening…');
      clearTimeout(silencioTimer);
      if(final.trim()){ try{r.stop();}catch(_){} return; }
      silencioTimer=setTimeout(function(){ try{r.stop();}catch(_){} }, 950);   // si calla casi un segundo, cierra y envía
    };
    r.onerror=function(e){
      if(e.error==='no-speech'||e.error==='aborted') return;
      log('Microphone: '+e.error);
      if(e.error==='not-allowed'||e.error==='service-not-allowed') aviso('Microphone permission denied', 6000);
    };
    r.onend=function(){
      clearTimeout(silencioTimer); clearTimeout(ventana); if(rec===r){ rec=null; recTipo=''; }
      const txt=(final||parcial).trim(); refrescar();
      if(txt){ log('Heard: '+txt); enviar(txt); } else if(tipo!=='seguimiento'){ log('Heard nothing'); aviso('I did not hear you, try again'); }
    };
    try{ r.start(); }catch(e){ rec=null; recTipo=''; log('Mic start: '+e); refrescar(); }
  }
  /* ---------- enviar al chat ---------- */
  function intencionNav(t){
    const n=norm(t);
    if(!/(muestr|ensen|\bver\b|\bveo\b|abr[ae]\b|llev|\bir\b|ve a |vamos|pasa a|cambia a|quiero ver|ponme|\bshow\b|\bopen\b|\bgo to\b|take me|\bswitch\b|i want to see|let me see|bring up)/.test(n)) return null;
    if(/alerta|alarma|recordatorio|alert|alarm|reminder/.test(n)) return ['Status'];
    if(/bitacora|diario|\bnotas?\b|anotacion|journal|diary|\bnotes?\b/.test(n)) return ['Journal'];
    if(/historial|registros?|expediente|history|records?/.test(n)) return ['History'];
    if(/monitor|grafic|signos|vitales|en vivo|tiempo real|vitals|vital signs|charts?|graphs?|live/.test(n)) return ['Vitals'];
    if(/estado|reloj|pantalla principal|inicio|status|clock|home screen|main screen/.test(n)) return ['Status'];
    if(/asistente|\bchat\b|conversacion|aeter|assistant|conversation/.test(n)) return ['Aéter'];
    return null;
  }
  function enviar(t, reintento){
    const ta=document.querySelector('[data-testid="stChatInputTextArea"]')||document.querySelector('[data-testid="stChatInput"] textarea');
    if(!ta){
      log('Chat box not found'+(reintento?'':' · opening Aéter'));
      if(!reintento){ navegar(['Aéter']); setTimeout(function(){enviar(t,true);},900); }
      return;
    }
    const dest=intencionNav(t); if(dest){ navegar(dest); log('Abro: '+dest[dest.length-1]); }
    const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
    set.call(ta,t); ta.dispatchEvent(new Event('input',{bubbles:true}));
    busy=true; ventanaHasta=Date.now()+30000; clearTimeout(busyTimer); refrescar();
    busyTimer=setTimeout(function(){ busy=false; log('No answer in 30 s'); refrescar(); siguiente(); },30000);
    setTimeout(function(){
      const b=document.querySelector('[data-testid="stChatInputSubmitButton"]');
      if(b && !b.disabled){ b.click(); log('Sent'); }
      else { ta.focus(); ['keydown','keypress','keyup'].forEach(function(tp){ ta.dispatchEvent(new KeyboardEvent(tp,{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true})); }); log('Sent with Enter'); }
    },150);
  }

  /* ---------- botón Hablar / reinicio ---------- */
  function clicHablar(){
    asegurarAudio();
    if(!desbloqueado){ desbloqueado=true; overlay(false); llenarVoces(); }
    if(speaking){ cortarVoz(); cola.length=0; return; }                              // Mute: solo la calla; para preguntar, otro toque en Talk
    if(rec && recTipo==='una'){ try{rec.stop();}catch(_){} return; }                 // enviar lo que lleva
    if(busy){ aviso('Thinking…'); return; }
    escuchar('manual');
  }
  function reiniciar(silencioso){
    clearTimeout(busyTimer); clearTimeout(avisoTimer); clearInterval(sirenaTimer); sirenaTimer=null;
    cortarVoz(); parar(); cola.length=0; busy=false; hablaRespuesta=false; esRespuesta=false; ventanaHasta=0;
    try{ speechSynthesis.cancel(); }catch(_){}
    if(ctx){ try{ ctx.close(); }catch(_){} ctx=null; }
    asegurarAudio(); if(sirenaOn) sirena(true);
    refrescar(); if(!silencioso){ log('Voice reset'); aviso('Voice reset'); }
  }
  function probarMicrofono(){
    parar(); cortarVoz();
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){ log('This browser does not allow the microphone here'); return; }
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
      const track=stream.getAudioTracks()[0]; log('Microphone in use: '+(track?track.label:'?'));
      asegurarAudio(); const an=ctx.createAnalyser(); an.fftSize=1024; ctx.createMediaStreamSource(stream).connect(an);
      const buf=new Uint8Array(an.fftSize); let max=0; const t0=Date.now(); estado('Speak now (6 s)…');
      const barra=document.getElementById('vp-barra-nivel');
      const iv=setInterval(function(){
        an.getByteTimeDomainData(buf); let m=0; for(let i=0;i<buf.length;i++){ m=Math.max(m,Math.abs(buf[i]-128)/128); }
        max=Math.max(max,m); if(barra) barra.style.width=Math.min(100,Math.round(m*300))+'%';
        if(Date.now()-t0>6000){
          clearInterval(iv); stream.getTracks().forEach(function(x){x.stop();}); if(barra) barra.style.width='0';
          log('Peak microphone level: '+max.toFixed(2)+(max<0.03?' → NOT picking up voice (muted or wrong device)':max<0.1?' → very low, raise the input volume':' → the microphone works'));
          refrescar();
        }
      },60);
    }).catch(function(e){ log('Could not open the microphone: '+(e.name||e)); refrescar(); });
  }

  /* ---------- pitido y navegación ---------- */
  function beep(){
    if(!ctx) return;
    try{ if(ctx.state!=='running') ctx.resume();
      const o=ctx.createOscillator(), g=ctx.createGain();
      o.type='square'; o.frequency.value=(nbeep++%2)?700:950; g.gain.value=0.3;
      o.connect(g); g.connect(ctx.destination); o.start(); o.stop(ctx.currentTime+0.4);
    }catch(e){ log('Beep: '+e); }
  }
  function sirena(activa){
    clearInterval(sirenaTimer); sirenaTimer=null;
    if(!activa) return;
    asegurarAudio(); beep(); sirenaTimer=setInterval(beep,650);
  }
  function pulsar(el){
    ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(function(tp){
      const Ev=tp.indexOf('pointer')===0?PointerEvent:MouseEvent;
      el.dispatchEvent(new Ev(tp,{bubbles:true,cancelable:true,view:window,button:0,pointerType:'mouse'}));
    });
  }
  function navegar(pasos){
    (function clic(i){
      const tabs=[].slice.call(document.querySelectorAll('[data-testid="stTab"], button[role="tab"]'));
      const b=tabs.find(function(x){return x.textContent.indexOf(pasos[i])>=0;});
      if(b){ pulsar(b); } else { log('Tab not found: '+pasos[i]); }
      if(i+1<pasos.length) setTimeout(function(){clic(i+1);},450);
    })(0);
  }

  panel(); refrescar();
  return {v:VER, reiniciar:reiniciar, config:function(o){
    on=!!o.on; const antes=sirenaOn; sirenaOn=!!o.sirena;
    if(!desbloqueado && hayActivacion()) desbloquear();
    if(desbloqueado && antes!==sirenaOn) sirena(sirenaOn);
    let llegoRespuesta=false;
    (o.speak||[]).forEach(function(it){ if(!vistos[it.id]){ vistos[it.id]=1; cola.push({text:it.text,resp:!!it.resp}); if(it.resp) llegoRespuesta=true; } });
    if(llegoRespuesta){ busy=false; clearTimeout(busyTimer); refrescar(); }
    if(o.nav && o.nav.id!==navVisto){ navVisto=o.nav.id; navegar(o.nav.pasos); }
    if(!on){ parar(); cortarVoz(); cola.length=0; estado(''); overlay(false); return; }
    if(!desbloqueado){ overlay(true); return; }
    siguiente();
  }};
})();
"""


def sin_palabra_de_llamado(texto: str) -> str:
    """La voz inglesa pronuncia mal «Aéter»: se cambia por «your assistant»."""
    return re.sub(r"(?i)\b(?:el\s+)?(?:a\s?)?[eé]t(?:h)?er\b", "your assistant", texto)


def limpiar_para_voz(texto: str) -> str:
    texto = sin_palabra_de_llamado(texto)
    t = re.sub(r"\([A-Z]{2,4}\d{2,}\)", "", texto)      # códigos (MED014) no se leen
    t = re.sub(r"\[\[.*?\]\]", "", t)
    t = re.sub(r"[*_#>`|]+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def resumen_hablado(texto: str, max_frases: int = 2, max_chars: int = 260) -> str:
    """Lo que Aéter dice en voz alta de una respuesta larga: las primeras frases; el resto se lee en pantalla."""
    t = limpiar_para_voz(texto)
    frases = re.split(r"(?<=[.!?])\s+", t)
    salida, largo = [], 0
    for f in frases:
        if salida and (len(salida) >= max_frases or largo + len(f) > max_chars):
            break
        salida.append(f)
        largo += len(f)
    hablado = " ".join(salida)
    if len(hablado) > max_chars + 80:                      # una sola frase enorme
        hablado = hablado[:max_chars].rsplit(" ", 1)[0] + "."
    return hablado


def componente(activo: bool, hablar: list[dict] | None = None, sirena: bool = False,
               nav: dict | None = None) -> None:
    """Se llama en cada ejecución. hablar: [{'id','text','resp'}]; nav: {'id','pasos'}.
    resp=True marca una respuesta del chat (se resume y luego Aéter vuelve a escuchar)."""
    habla = []
    for h in (hablar or []):
        resp = bool(h.get("resp"))
        habla.append({"id": h["id"], "resp": resp,
                      "text": (limpiar_para_voz(h["text"]) if re.search(r"\bPRO\d{3}\b", h["text"])
                               else resumen_hablado(h["text"])) if resp else limpiar_para_voz(h["text"])})
    cfg = {"on": activo, "sirena": sirena, "nav": nav, "speak": habla}
    html = f"""<script>
    (function(){{
      try {{
        const P = window.parent, D = P.document;
        if (P.__voz && P.__voz.v !== {json.dumps(VERSION_JS)}) {{      // había una versión vieja de la voz: recarga una vez
          if (!P.sessionStorage.getItem('voz_recarga_{VERSION_JS}')) {{ P.sessionStorage.setItem('voz_recarga_{VERSION_JS}', '1'); P.location.reload(); }}
          return;
        }}
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
