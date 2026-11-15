"""Voz en el navegador (Chrome/Edge): escucha, envía al chat y lee la respuesta en voz alta.

Diseño seguro (v2):
  - Modo «Con botón» (por defecto): se pulsa Hablar, se dice la frase y Aéter responde. Mientras Aéter
    habla el micrófono está apagado, así que no se oye a sí mismo ni se contesta.
  - Modo «Manos libres»: escucha «Aéter» de forma continua (pensado para audífonos).
  - Las respuestas habladas son cortas (el texto completo queda en pantalla).
  - Ajustes > «Reiniciar voz» limpia todo y vuelve a empezar.
Usa las funciones del propio navegador (sin llaves ni costo). El código JS se instala
una sola vez en la página y sobrevive a los reruns de Streamlit.
"""
import json
import re

import streamlit.components.v1 as components

VERSION_JS = "2"

JS = r"""
window.__voz = (function(){
  const VER='2';
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const LS = {get:function(k,d){try{return localStorage.getItem(k)||d;}catch(_){return d;}}, set:function(k,v){try{localStorage.setItem(k,v);}catch(_){}}};
  function norm(s){ return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,''); }
  function limpio(s){ return ' '+s.replace(/[^a-z0-9ñ ]/g,' ').replace(/\s+/g,' ').trim()+' '; }
  const LLAMADO=/(^|[^a-z])(aeter|a eter|ae ter|aether|a ether|ayter|aiter|aider|ayder|ether|eter|ater|ahter|el eter|el ether)([^a-z]|$)/;
  const QUITAR=/^\s*(oye|hey|ok|okay|hola|buenas)?[\s,.:;!¡¿?]*(el )?(a ?[eé] ?t(?:h)?er|a[iy][td]er|[eé]t(?:h)?er|ater|ahter)(?![a-záéíóúñ])[\s,.:;!¡¿?]*/i;

  let on=false, desbloqueado=false, ctx=null, nbeep=0;
  let rec=null, recTipo='', silencioTimer=null, busy=false, busyTimer=null;
  let speaking=false, vozToken=0, vozTimer=null, finHabla=0, hablado=[], uref=null, esRespuesta=false, hablaRespuesta=false;
  let cola=[], vistos={}, navVisto=null, sirenaOn=false, sirenaTimer=null;
  let diag=[], avisoTimer=null, ventanaHasta=0;

  function modo(){ return LS.get('v2_modo','boton'); }
  function seguir(){ return LS.get('v2_seguir','1')==='1'; }

  /* ---------- panel ---------- */
  function panel(){
    let el=document.getElementById('voz-panel'); if(el) return el;
    el=document.createElement('div'); el.id='voz-panel';
    el.style.cssText='position:fixed;bottom:104px;right:16px;z-index:9999;font:13px sans-serif;color:#fff;max-width:310px';
    el.innerHTML='<div id="vp-ultimo" style="text-align:right;font-size:11px;opacity:.7;margin-bottom:4px;max-width:310px"></div>'+
      '<div style="display:flex;gap:6px;align-items:center;justify-content:flex-end">'+
      '<button id="vp-hablar" style="border:1px solid rgba(255,255,255,.55);background:#0b0b7a;color:#fff;border-radius:22px;height:40px;min-width:92px;padding:0 18px;cursor:pointer;font:600 14px Poppins,sans-serif">Hablar</button>'+
      '<span id="vp-estado" style="display:none;padding:6px 14px;border-radius:16px;background:rgba(15,20,45,.7);border:1px solid rgba(255,255,255,.4);backdrop-filter:blur(8px);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></span>'+
      '<button id="vp-ajustes" style="border:1px solid rgba(255,255,255,.45);background:rgba(15,20,45,.7);color:#fff;border-radius:20px;height:34px;padding:0 14px;cursor:pointer;font:600 12px Poppins,sans-serif">Ajustes</button></div>'+
      '<div id="vp-det" style="display:none;margin-top:8px;padding:12px;border-radius:16px;background:rgba(15,20,45,.92);border:1px solid rgba(255,255,255,.3);backdrop-filter:blur(14px)">'+
      '<div style="margin-bottom:6px"><b>Cómo hablar con Aéter</b></div>'+
      '<select id="vp-modo" style="width:100%;margin-bottom:8px;padding:4px"><option value="boton">Con botón (recomendado, sin eco)</option><option value="manos">Manos libres, di «Aéter» (usa audífonos)</option></select>'+
      '<label style="display:block;margin-bottom:10px"><input id="vp-seguir" type="checkbox"> Escuchar de nuevo cuando termine de responder</label>'+
      '<div style="margin-bottom:6px"><b>Voz de Aéter</b></div>'+
      '<select id="vp-voz" style="width:100%;margin-bottom:6px;padding:4px"></select>'+
      '<div style="margin-bottom:6px">Velocidad <input id="vp-vel" type="range" min="0.8" max="1.5" step="0.05" style="width:130px;vertical-align:middle"></div>'+
      '<div style="display:flex;gap:6px;margin-bottom:8px"><button id="vp-probar" style="flex:1;padding:5px;cursor:pointer">Probar voz</button><button id="vp-pitido" style="flex:1;padding:5px;cursor:pointer">Probar pitido</button></div>'+
      '<button id="vp-nivel" style="width:100%;padding:5px;margin-bottom:4px;cursor:pointer">Probar micrófono (6 s)</button>'+
      '<div style="height:8px;background:#333;border-radius:4px;margin-bottom:8px;overflow:hidden"><div id="vp-barra-nivel" style="height:100%;width:0;background:#2ecc71"></div></div>'+
      '<button id="vp-reset" style="width:100%;padding:6px;margin-bottom:8px;cursor:pointer;font-weight:700">Reiniciar voz</button>'+
      '<div id="vp-diag" style="opacity:.75;font-size:11px;white-space:pre-wrap;max-height:150px;overflow:auto"></div></div>';
    document.body.appendChild(el);
    const q=function(id){return el.querySelector(id);};
    q('#vp-hablar').onclick=function(){ clicHablar(); };
    q('#vp-ajustes').onclick=function(){ const d=q('#vp-det'); d.style.display=d.style.display==='none'?'block':'none'; llenarVoces(); pintaDiag(); };
    q('#vp-modo').value=modo(); q('#vp-modo').onchange=function(e){ LS.set('v2_modo',e.target.value); reiniciar(true); };
    q('#vp-seguir').checked=seguir(); q('#vp-seguir').onchange=function(e){ LS.set('v2_seguir',e.target.checked?'1':'0'); };
    q('#vp-voz').onchange=function(e){ LS.set('voz_nombre',e.target.value); };
    q('#vp-vel').value=LS.get('voz_vel','1'); q('#vp-vel').onchange=function(e){ LS.set('voz_vel',e.target.value); };
    q('#vp-probar').onclick=function(){ asegurarAudio(); desbloqueado=true; overlay(false); cola.length=0; esRespuesta=false; decir('Hola, soy su asistente virtual. Así suena mi voz.'); };
    q('#vp-pitido').onclick=function(){ asegurarAudio(); for(let i=0;i<3;i++) setTimeout(beep,i*500); };
    q('#vp-nivel').onclick=function(){ probarMicrofono(); };
    q('#vp-reset').onclick=function(){ reiniciar(false); };
    return el;
  }
  function llenarVoces(){
    const sel=panel().querySelector('#vp-voz'); if(!sel) return;
    const vs=speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('es')===0;});
    const actual=LS.get('voz_nombre','');
    sel.innerHTML='<option value="">(automática)</option>'+vs.map(function(v){return '<option value="'+v.name+'"'+(v.name===actual?' selected':'')+'>'+v.name+' · '+v.lang+'</option>';}).join('');
  }
  function log(m){
    const h=new Date().toLocaleTimeString('es',{hour12:false});
    if(diag.length && diag[diag.length-1].slice(10).trim()===m) return;
    diag.push(h+'  '+m); if(diag.length>14) diag.shift(); pintaDiag();
    const u=document.getElementById('vp-ultimo'); if(u) u.textContent=m;
  }
  function pintaDiag(){
    const d=document.getElementById('vp-diag'); if(!d) return;
    d.textContent='Audio: '+(ctx?ctx.state:'sin iniciar')+' · Voces es: '+speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('es')===0;}).length+
      ' · Reconocimiento: '+(SR?'sí':'NO (use Chrome/Edge)')+' · Modo: '+modo()+'\n'+diag.slice().reverse().join('\n');
  }
  function estado(t){ const e=panel().querySelector('#vp-estado'); e.style.display=t?'inline-block':'none'; e.textContent=t||''; }
  function aviso(t, ms){ clearTimeout(avisoTimer); estado(t); avisoTimer=setTimeout(refrescar, ms||3000); }
  function refrescar(){
    const b=panel().querySelector('#vp-hablar'); if(!b) return;
    if(speaking){ b.textContent='Callar'; estado('Hablando…'); }
    else if(busy){ b.textContent='Hablar'; estado('Pensando…'); }
    else if(rec && recTipo==='una'){ b.textContent='Enviar'; estado('Escuchando…'); }
    else if(rec){ b.textContent='Hablar'; estado('Escuchando: di «Aéter»'); }
    else { b.textContent='Hablar'; estado(''); }
  }

  /* ---------- activación de audio ---------- */
  function overlay(mostrar){
    let b=document.getElementById('voz-overlay');
    if(!mostrar){ if(b) b.remove(); return; }
    if(b) return;
    b=document.createElement('button'); b.id='voz-overlay';
    b.textContent='Toque en cualquier parte para activar a Aéter';
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
    sirena(sirenaOn); log('Activado'); siguiente();
  }

  /* ---------- voz de salida (el micrófono se apaga mientras habla) ---------- */
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
  function cortarVoz(){ vozToken++; clearTimeout(vozTimer); try{speechSynthesis.cancel();}catch(_){} speaking=false; refrescar(); }
  function decir(texto){
    cortarVoz();
    if(modo()==='boton') parar();                     // sin micrófono mientras habla: no se oye a sí mismo
    const lista=trozos(texto); let i=0; const tk=++vozToken;
    hablaRespuesta=esRespuesta;
    function uno(){
      if(tk!==vozToken) return;
      if(i>=lista.length){ terminarHabla(tk); return; }
      const u=new SpeechSynthesisUtterance(lista[i++]); uref=u;
      u.lang='es-MX'; u.rate=parseFloat(LS.get('voz_vel','1'))||1;
      const v=elegirVoz(); if(v){ u.voice=v; u.lang=v.lang; }
      u.onend=function(){ if(tk===vozToken) uno(); };
      u.onerror=function(e){ if(tk!==vozToken||e.error==='interrupted'||e.error==='canceled') return; log('Voz: '+(e.error||'error')); uno(); };
      try{ speechSynthesis.resume(); }catch(_){}
      speechSynthesis.speak(u);
    }
    speaking=true; refrescar();
    hablado.push({n:norm(texto),ts:Date.now()}); if(hablado.length>6) hablado.shift();
    clearTimeout(vozTimer);
    vozTimer=setTimeout(function(){ if(speaking && tk===vozToken){ log('La voz no terminó: continúo'); terminarHabla(tk); } }, 6000+texto.length*110);
    setTimeout(uno, 80);
  }
  function terminarHabla(tk){
    if(tk!==vozToken) return;
    clearTimeout(vozTimer); speaking=false; finHabla=Date.now(); refrescar();
    if(cola.length){ setTimeout(siguiente, 150); return; }
    const respondio=hablaRespuesta; hablaRespuesta=false;
    if(!on) return;
    if(modo()==='boton' && respondio && seguir() && SR){ setTimeout(function(){ if(!speaking&&!busy&&!rec) escuchar('seguimiento'); }, 700); }   // deja morir el eco
    else if(modo()==='manos'){ setTimeout(asegurarContinuo, 500); }
  }
  function siguiente(){
    if(speaking||!desbloqueado||!on) return;
    if(!cola.length){ if(modo()==='manos') asegurarContinuo(); return; }
    if(rec && recTipo==='una'){ setTimeout(siguiente, 600); return; }      // no pisar al usuario mientras habla
    const it=cola.shift(); esRespuesta=!!it.resp; decir(it.text);
  }

  /* ---------- micrófono ---------- */
  function parar(){ clearTimeout(silencioTimer); if(rec){ const r=rec; rec=null; recTipo=''; r.onend=null; r.onresult=null; r.onerror=null; try{r.abort();}catch(_){} } refrescar(); }
  function nuevoSR(continuo){
    const r=new SR(); r.lang='es-MX'; r.interimResults=true; r.continuous=!!continuo; r.maxAlternatives=3; return r;
  }
  function escuchar(tipo){                                          // una sola frase: «Hablar»
    asegurarAudio();
    if(!desbloqueado){ desbloqueado=true; overlay(false); llenarVoces(); }
    if(!SR){ aviso('Use Chrome o Edge para hablar'); log('Este navegador no tiene reconocimiento de voz'); return; }
    cortarVoz(); parar(); cola.length=0;
    const r=nuevoSR(false); let final='', parcial=''; rec=r; recTipo='una';
    r.onstart=function(){ log(tipo==='seguimiento'?'Te escucho':'Hable ahora'); refrescar(); };
    r.onresult=function(e){
      parcial=''; for(let i=e.resultIndex;i<e.results.length;i++){ const x=e.results[i][0].transcript; if(e.results[i].isFinal) final+=x; else parcial+=x; }
      estado((final+parcial).trim().slice(0,40)||'Escuchando…');
      clearTimeout(silencioTimer);
      if(final.trim()){ try{r.stop();}catch(_){} return; }
      silencioTimer=setTimeout(function(){ try{r.stop();}catch(_){} }, 950);   // si calla casi un segundo, cierra y envía
    };
    r.onerror=function(e){
      if(e.error==='no-speech'||e.error==='aborted') return;
      log('Micrófono: '+e.error);
      if(e.error==='not-allowed'||e.error==='service-not-allowed') aviso('Permiso de micrófono denegado', 6000);
    };
    r.onend=function(){
      clearTimeout(silencioTimer); if(rec===r){ rec=null; recTipo=''; }
      const txt=(final||parcial).trim(); refrescar();
      if(txt){ log('Oí: '+txt); enviar(txt); } else if(tipo!=='seguimiento'){ log('No oí nada'); aviso('No te oí, prueba de nuevo'); }
    };
    try{ r.start(); }catch(e){ rec=null; recTipo=''; log('Mic start: '+e); refrescar(); }
  }
  function asegurarContinuo(){                                       // modo manos libres: espera «Aéter»
    if(modo()!=='manos'||!on||!desbloqueado||rec||busy||!SR) return;
    const r=nuevoSR(true); rec=r; recTipo='continuo';
    r.onstart=function(){ refrescar(); };
    r.onresult=function(e){
      for(let i=e.resultIndex;i<e.results.length;i++){
        const res=e.results[i]; let t=(res[0].transcript||'').trim(); if(!t) continue;
        if(!LLAMADO.test(norm(t))){ for(let k=1;k<res.length;k++){ const a=(res[k].transcript||'').trim(); if(a&&LLAMADO.test(norm(a))){ t=a; break; } } }
        const n=norm(t);
        if(speaking){                                                // con audífonos: la voz del usuario la interrumpe
          if(Date.now()-hablado[hablado.length-1].ts<900 || eco(n)) continue;
          if(LLAMADO.test(n) || n.replace(/\s/g,'').length>=3){ cortarVoz(); cola.length=0; ventanaHasta=Date.now()+30000; log('Te oí hablar: me callo'); }
          else continue;
        }
        if(busy || Date.now()-finHabla<1200 || eco(n)) continue;
        if(res.isFinal){ procesar(t); }
        else { clearTimeout(silencioTimer); silencioTimer=setTimeout(function(){ try{r.stop();}catch(_){} }, 900); estado(t.slice(0,40)); }
      }
    };
    r.onerror=function(e){ if(e.error==='no-speech'||e.error==='aborted') return; log('Micrófono: '+e.error); if(e.error==='not-allowed'||e.error==='service-not-allowed'){ on=false; aviso('Permiso de micrófono denegado', 6000); } };
    r.onend=function(){ clearTimeout(silencioTimer); if(rec===r){ rec=null; recTipo=''; refrescar(); setTimeout(asegurarContinuo, 350); } };
    try{ r.start(); }catch(e){ rec=null; recTipo=''; log('Mic start: '+e); }
  }
  function eco(n){ const q=limpio(n), ahora=Date.now(); return hablado.some(function(h){ return ahora-h.ts<30000 && limpio(h.n).indexOf(q)>=0; }); }
  function procesar(t){
    const n=norm(t), llamado=LLAMADO.test(n), abierto=Date.now()<ventanaHasta;
    log('Oí: '+t);
    if(!llamado && !abierto){ aviso('Oí «'+t.slice(0,30)+'». Di «Aéter»'); return; }
    const texto=t.replace(QUITAR,'').trim();
    if(!texto||norm(texto).length<2){ ventanaHasta=Date.now()+30000; aviso('Dime'); return; }
    enviar(texto);
  }

  /* ---------- enviar al chat ---------- */
  function intencionNav(t){
    const n=norm(t);
    if(!/(muestr|ensen|\bver\b|\bveo\b|abr[ae]\b|llev|\bir\b|ve a |vamos|pasa a|cambia a|quiero ver|ponme)/.test(n)) return null;
    if(/alerta|alarma|recordatorio/.test(n)) return ['Estado'];
    if(/bitacora|diario|\bnotas?\b|anotacion/.test(n)) return ['Bitácora'];
    if(/historial|registros?|expediente/.test(n)) return ['Historial'];
    if(/monitor|grafic|signos|vitales|en vivo|tiempo real/.test(n)) return ['Signos Vitales'];
    if(/estado|reloj|pantalla principal|inicio/.test(n)) return ['Estado'];
    if(/asistente|\bchat\b|conversacion|aeter/.test(n)) return ['Aéter'];
    return null;
  }
  function enviar(t, reintento){
    const ta=document.querySelector('[data-testid="stChatInputTextArea"]')||document.querySelector('[data-testid="stChatInput"] textarea');
    if(!ta){
      log('No encuentro el cuadro de chat'+(reintento?'':' · abro Aéter'));
      if(!reintento){ navegar(['Aéter']); setTimeout(function(){enviar(t,true);},900); }
      return;
    }
    const dest=intencionNav(t); if(dest){ navegar(dest); log('Abro: '+dest[dest.length-1]); }
    const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
    set.call(ta,t); ta.dispatchEvent(new Event('input',{bubbles:true}));
    busy=true; ventanaHasta=Date.now()+30000; clearTimeout(busyTimer); refrescar();
    busyTimer=setTimeout(function(){ busy=false; log('Sin respuesta en 30 s'); refrescar(); siguiente(); },30000);
    setTimeout(function(){
      const b=document.querySelector('[data-testid="stChatInputSubmitButton"]');
      if(b && !b.disabled){ b.click(); log('Enviado'); }
      else { ta.focus(); ['keydown','keypress','keyup'].forEach(function(tp){ ta.dispatchEvent(new KeyboardEvent(tp,{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true})); }); log('Enviado con Enter'); }
    },150);
  }

  /* ---------- botón Hablar / reinicio ---------- */
  function clicHablar(){
    asegurarAudio();
    if(!desbloqueado){ desbloqueado=true; overlay(false); llenarVoces(); }
    if(speaking){ cortarVoz(); cola.length=0; escuchar('manual'); return; }          // la interrumpe y la escucha ya
    if(rec && recTipo==='una'){ try{rec.stop();}catch(_){} return; }                 // enviar lo que lleva
    if(busy){ aviso('Estoy pensando…'); return; }
    escuchar('manual');
  }
  function reiniciar(silencioso){
    clearTimeout(busyTimer); clearTimeout(avisoTimer); clearInterval(sirenaTimer); sirenaTimer=null;
    cortarVoz(); parar(); cola.length=0; busy=false; hablaRespuesta=false; esRespuesta=false; ventanaHasta=0;
    try{ speechSynthesis.cancel(); }catch(_){}
    if(ctx){ try{ ctx.close(); }catch(_){} ctx=null; }
    asegurarAudio(); if(sirenaOn) sirena(true);
    refrescar(); if(!silencioso){ log('Voz reiniciada'); aviso('Voz reiniciada'); }
    if(on&&desbloqueado&&modo()==='manos') setTimeout(asegurarContinuo, 400);
  }
  function probarMicrofono(){
    parar(); cortarVoz();
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){ log('Este navegador no permite usar el micrófono aquí'); return; }
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
      const track=stream.getAudioTracks()[0]; log('Micrófono en uso: '+(track?track.label:'?'));
      asegurarAudio(); const an=ctx.createAnalyser(); an.fftSize=1024; ctx.createMediaStreamSource(stream).connect(an);
      const buf=new Uint8Array(an.fftSize); let max=0; const t0=Date.now(); estado('Habla ahora (6 s)…');
      const barra=document.getElementById('vp-barra-nivel');
      const iv=setInterval(function(){
        an.getByteTimeDomainData(buf); let m=0; for(let i=0;i<buf.length;i++){ m=Math.max(m,Math.abs(buf[i]-128)/128); }
        max=Math.max(max,m); if(barra) barra.style.width=Math.min(100,Math.round(m*300))+'%';
        if(Date.now()-t0>6000){
          clearInterval(iv); stream.getTracks().forEach(function(x){x.stop();}); if(barra) barra.style.width='0';
          log('Nivel máximo del micrófono: '+max.toFixed(2)+(max<0.03?' → NO capta voz (silenciado o dispositivo equivocado)':max<0.1?' → muy bajo, sube el volumen de entrada':' → el micrófono sí capta'));
          refrescar();
        }
      },60);
    }).catch(function(e){ log('No pude abrir el micrófono: '+(e.name||e)); refrescar(); });
  }

  /* ---------- pitido y navegación ---------- */
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
      if(b){ pulsar(b); } else { log('No encuentro la pestaña «'+pasos[i]+'»'); }
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
    """La voz no debe decir «Aéter» ni «médico» (palabras de llamado): el micrófono las oiría."""
    t = re.sub(r"(?i)\b(?:el\s+)?(?:a\s?)?[eé]t(?:h)?er\b", "su asistente", texto)
    t = re.sub(r"(?i)\bm[eé]dic[oa]s? virtual(es)?\b", "asistente virtual", t)
    t = re.sub(r"(?i)\bm[eé]dic[oa]s\b", "profesionales de salud", t)
    t = re.sub(r"(?i)\bm[eé]dic[oa]\b", "profesional de salud", t)
    t = re.sub(r"(?i)\bdoctor(es)?\b|\bdoctora(s)?\b", "profesional de salud", t)
    return t


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
    if len(salida) < len(frases) or len(hablado) < len(t) - 2:
        hablado += " El resto está en pantalla."
    return hablado


def componente(activo: bool, hablar: list[dict] | None = None, sirena: bool = False,
               nav: dict | None = None) -> None:
    """Se llama en cada ejecución. hablar: [{'id','text','resp'}]; nav: {'id','pasos'}.
    resp=True marca una respuesta del chat (se resume y luego Aéter vuelve a escuchar)."""
    habla = []
    for h in (hablar or []):
        resp = bool(h.get("resp"))
        habla.append({"id": h["id"], "resp": resp,
                      "text": resumen_hablado(h["text"]) if resp else limpiar_para_voz(h["text"])})
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
