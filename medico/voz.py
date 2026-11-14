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
  let interimTimer=null, marcaProc=null;
  let ultimoEstado='', oido='', diag=[], ventanaHasta=0, vozTimer=null, avisoTimer=null, vozToken=0, manual=false, bargeRec=null, hablado=[], ignorarHasta=0, interrumpidoEn=0, finHabla=0;
  function cortarVoz(){ pararBarge(); vozToken++; clearTimeout(vozTimer); try{speechSynthesis.cancel();}catch(_){} speaking=false; }
  function norm(s){ return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,''); }
  const LLAMADO=/(^|[^a-z])(aeter|a eter|aether|a ether|ayter|aiter|eter|ater)([^a-z]|$)/;
  const LS = {get:function(k,d){try{return localStorage.getItem(k)||d;}catch(_){return d;}}, set:function(k,v){try{localStorage.setItem(k,v);}catch(_){}}};

  /* ---------- panel flotante ---------- */
  function panel(){
    let el=document.getElementById('voz-panel');
    if(el) return el;
    el=document.createElement('div'); el.id='voz-panel';
    el.style.cssText='position:fixed;bottom:104px;right:16px;z-index:9999;font:13px sans-serif;color:#fff;max-width:300px';
    el.innerHTML='<div id="vp-ultimo" style="text-align:right;font-size:11px;opacity:.7;margin-bottom:4px;max-width:300px"></div>'+
      '<div id="vp-barra" style="display:flex;gap:6px;align-items:center;justify-content:flex-end">'+
      '<button id="vp-hablar" title="Hablar ahora (sin decir Aéter)" style="border:1px solid rgba(255,255,255,.55);background:#0b0b7a;color:#fff;border-radius:22px;height:38px;padding:0 18px;cursor:pointer;font:600 13px Poppins,sans-serif">Hablar</button>'+
      '<span id="vp-estado" style="padding:6px 14px;border-radius:16px;background:rgba(15,20,45,.7);border:1px solid rgba(255,255,255,.4);backdrop-filter:blur(8px)"></span>'+
      '<button id="vp-ajustes" title="Voz y diagnóstico" style="border:1px solid rgba(255,255,255,.45);background:rgba(15,20,45,.7);color:#fff;border-radius:20px;height:34px;padding:0 14px;cursor:pointer;font:600 12px Poppins,sans-serif">Ajustes</button></div>'+
      '<div id="vp-det" style="display:none;margin-top:8px;padding:12px;border-radius:16px;background:rgba(15,20,45,.9);border:1px solid rgba(255,255,255,.3);backdrop-filter:blur(14px)">'+
      '<div style="margin-bottom:6px"><b>Cuándo escucha</b></div>'+
      '<select id="vp-modo" style="width:100%;margin-bottom:10px;padding:4px"><option value="llamado">Solo cuando diga «Aéter»</option><option value="siempre">Siempre (responde a todo)</option></select>'+
      '<label style="display:block;margin-bottom:10px"><input id="vp-barge" type="checkbox"> Interrumpirlo al decir «Aéter» mientras habla</label>'+
      '<div style="margin-bottom:6px"><b>Voz de Aéter</b></div>'+
      '<select id="vp-voz" style="width:100%;margin-bottom:6px;padding:4px"></select>'+
      '<div style="margin-bottom:6px">Velocidad <input id="vp-vel" type="range" min="0.7" max="1.4" step="0.05" style="width:130px;vertical-align:middle"></div>'+
      '<div style="display:flex;gap:6px;margin-bottom:8px"><button id="vp-probar" style="flex:1;padding:5px;cursor:pointer">Probar voz</button><button id="vp-pitido" style="flex:1;padding:5px;cursor:pointer">Probar pitido</button></div>'+
      '<button id="vp-nivel" style="width:100%;padding:5px;margin-bottom:4px;cursor:pointer">Probar micrófono (6 s)</button>'+
      '<div style="height:8px;background:#333;border-radius:4px;margin-bottom:8px;overflow:hidden"><div id="vp-barra-nivel" style="height:100%;width:0;background:#2ecc71"></div></div>'+
      '<div id="vp-diag" style="opacity:.75;font-size:11px;white-space:pre-wrap"></div></div>';
    document.body.appendChild(el);
    el.querySelector('#vp-nivel').onclick=function(){ probarMicrofono(); };
    el.querySelector('#vp-hablar').onclick=function(){ hablarAhora(); };
    el.querySelector('#vp-ajustes').onclick=function(){const d=el.querySelector('#vp-det'); d.style.display=d.style.display==='none'?'block':'none'; llenarVoces(); pintaDiag();};
    const modo=el.querySelector('#vp-modo'); modo.value=LS.get('voz_modo','llamado'); modo.onchange=function(e){LS.set('voz_modo',e.target.value);};
    const bg=el.querySelector('#vp-barge'); bg.checked=LS.get('voz_barge','1')==='1'; bg.onchange=function(e){LS.set('voz_barge',e.target.checked?'1':'0'); if(!e.target.checked) pararBarge();};
    el.querySelector('#vp-voz').onchange=function(e){LS.set('voz_nombre',e.target.value);};
    const vel=el.querySelector('#vp-vel'); vel.value=LS.get('voz_vel','1'); vel.onchange=function(e){LS.set('voz_vel',e.target.value);};
    el.querySelector('#vp-probar').onclick=function(){ asegurarAudio(); decir('Hola, soy su asistente virtual. Así suena mi voz.', true); };
    el.querySelector('#vp-pitido').onclick=function(){ asegurarAudio(); for(let i=0;i<3;i++) setTimeout(beep,i*500); };
    return el;
  }
  function llenarVoces(){
    const sel=panel().querySelector('#vp-voz'); if(!sel) return;
    const vs=speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('es')===0;});
    const actual=LS.get('voz_nombre','');
    sel.innerHTML='<option value="">(automática)</option>'+vs.map(function(v){return '<option value="'+v.name+'"'+(v.name===actual?' selected':'')+'>'+v.name+' · '+v.lang+'</option>';}).join('');
  }
  function log(m){
    if(diag.length && diag[diag.length-1].slice(10)===m) return;
    const h=new Date().toLocaleTimeString('es',{hour12:false});
    diag.push(h+'  '+m); if(diag.length>14) diag.shift(); pintaDiag();
    const u=document.getElementById('vp-ultimo'); if(u) u.textContent=m;
  }
  function pintaDiag(){
    const d=document.getElementById('vp-diag'); if(!d) return;
    d.style.maxHeight='180px'; d.style.overflow='auto'; d.textContent='Audio: '+(ctx?ctx.state:'sin iniciar')+' · Voces es: '+speechSynthesis.getVoices().filter(function(v){return v.lang.toLowerCase().indexOf('es')===0;}).length+
      ' · Reconocimiento: '+(SR?'sí':'NO (use Chrome/Edge)')+'\n'+diag.slice().reverse().join('\n');
  }
  function aviso(t, ms){ clearTimeout(avisoTimer); estado(t); avisoTimer=setTimeout(function(){ if(!speaking&&!busy) estado(rec?'Escuchando…':''); }, ms||3500); }
  function estado(t){ ultimoEstado=t||''; const e=panel().querySelector('#vp-estado'); e.style.display=t?'inline-block':'none'; e.textContent=t||''; }

  /* ---------- activación ---------- */
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
    if(inmediato){ cortarVoz(); }
    const tk=++vozToken;
    function uno(){
      if(tk!==vozToken) return;
      if(i>=lista.length){ clearTimeout(vozTimer); speaking=false; finHabla=Date.now(); ignorarHasta=Date.now()+1200; if(!inmediato) siguiente(); else iniciar(); return; }
      const u=new SpeechSynthesisUtterance(lista[i++]); uref=u;      // referencia: evita que Chrome la descarte
      u.lang='es-MX'; u.rate=parseFloat(LS.get('voz_vel','1'))||1;
      const v=elegirVoz(); if(v){ u.voice=v; u.lang=v.lang; }
      u.onend=function(){ if(tk===vozToken) uno(); };
      u.onerror=function(e){ if(tk!==vozToken||e.error==='interrupted'||e.error==='canceled') return; log('Voz: '+(e.error||'error')); uno(); };
      speechSynthesis.speak(u);
    }
    speaking=true; estado('Hablando…'); hablado.push({n:norm(texto),ts:Date.now()}); if(hablado.length>6) hablado.shift();
    clearTimeout(vozTimer);
    vozTimer=setTimeout(function(){ if(speaking && tk===vozToken){ log('La voz no terminó: continúo'); cortarVoz(); if(!inmediato) siguiente(); else iniciar(); } }, 5000+texto.length*110);
    setTimeout(uno, inmediato?120:0);
  }
  function siguiente(){
    if(speaking||!desbloqueado) return;
    if(!cola.length){ busy=false; clearTimeout(busyTimer); ventanaHasta=Date.now()+25000; ignorarHasta=Math.max(ignorarHasta,Date.now()+500); estado(rec?'Escuchando…':''); iniciar(); return; }
    decir(cola.shift(), false);
  }

  /* ---------- micrófono ---------- */
  function limpio(s){ return ' '+s.replace(/[^a-z0-9ñ ]/g,' ').replace(/\s+/g,' ').trim()+' '; }
  function ecoBolsa(n){
    const w=limpio(n).trim().split(' ').filter(function(x){return x.length>2;});
    if(w.length<3) return false;
    const ahora=Date.now(), conocidas={};
    hablado.forEach(function(h){ if(ahora-h.ts<40000) limpio(h.n).trim().split(' ').forEach(function(x){conocidas[x]=1;}); });
    return w.filter(function(x){return conocidas[x];}).length/w.length>=0.6;
  }
  function eco(n){ const ahora=Date.now(), q=limpio(n); return hablado.some(function(h){ return ahora-h.ts<25000 && limpio(h.n).indexOf(q)>=0; }); }
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
  function procesar(t){
    const n=norm(t); oido=t; log('Oí: '+t);
    const llamado=LLAMADO.test(n), abierto=(LS.get('voz_modo','llamado')==='siempre')||Date.now()<ventanaHasta;
    if(!llamado && !abierto){ aviso('Oí «'+t.slice(0,40)+'». Diga «Aéter» para hablarme'); return; }
    const texto=t.replace(/^\s*(oye|hey|ok|okay|hola|buenas)?[\s,.:;!¡¿?]*(a ?[eé]ther?|a[iy]ter|[eé]ter|ater)(?![a-záéíóúñ])[\s,.:;!¡¿?]*/i,'').trim();
    ventanaHasta=Date.now()+25000;
    const palabras=texto.split(/\s+/).filter(Boolean).length;
    if(Date.now()-interrumpidoEn<5000 && palabras<=2){ log('Ya me callé'); return; }
    if(!texto || norm(texto).length<2){ cola.unshift('Dígame.'); siguiente(); return; }
    enviar(texto);
  }
  function iniciar(){
    if(!on||!desbloqueado||rec||manual) return;
    if(!SR){estado('Use Chrome o Edge para hablar');return;}
    rec=new SR(); rec.lang='es-MX'; rec.interimResults=true; rec.continuous=true; rec.maxAlternatives=1;
    const miRec=rec, t0=Date.now();
    rec.onaudiostart=function(){ log('Micrófono abierto'); };
    rec.onspeechstart=function(){ if(!speaking) log('Detecto voz…'); };
    rec.onresult=function(e){
      for(let i=e.resultIndex;i<e.results.length;i++){
        const res=e.results[i], t=(res[0].transcript||'').trim(); if(!t) continue;
        const n=norm(t);
        if(speaking){                                    // mientras habla, solo atiende la interrupción
          if(LS.get('voz_barge','1')==='1' && LLAMADO.test(n)) interrumpir();
          continue;
        }
        if(busy || Date.now()<ignorarHasta) continue;
        if(!res.isFinal){
          estado(''+t.slice(0,50)); clearTimeout(interimTimer);
          const soloLlamado=/^(oye |hey |hola |ok )?(aeter|a eter|aether|a ether|ayter|aiter|eter|ater)$/.test(limpio(n).trim());
          interimTimer=setTimeout(function(){ if(speaking||busy) return; if(Date.now()-finHabla<5000 && ecoBolsa(n)) return; marcaProc={n:n,wake:soloLlamado,ts:Date.now()}; procesar(t); }, soloLlamado?600:1100);
          continue;
        }
        clearTimeout(interimTimer);
        if(marcaProc && Date.now()-marcaProc.ts<8000){
          const m=marcaProc; marcaProc=null;
          if(n===m.n || (!m.wake && n.indexOf(m.n)===0)) continue;     // ya lo atendí con el texto parcial
        }
        if(Date.now()-finHabla<5000 && ecoBolsa(n)){ log('Ignoro el eco de mi voz'); continue; }
        procesar(t);
      }
    };
    rec.onend=function(){ if(rec===miRec) rec=null; const ms=Date.now()-t0; if(ms<1200) log('El micrófono se cerró enseguida ('+ms+' ms)'); setTimeout(iniciar,ms<1200?1500:300); };
    rec.onerror=function(e){
      if(e.error==='no-speech'||e.error==='aborted') return;
      log('Micrófono: '+e.error);
      if(e.error==='not-allowed'||e.error==='service-not-allowed'){ on=false; rec=null; estado('Permiso de micrófono denegado'); }
    };
    try{ rec.start(); if(!speaking&&!busy) estado('Escuchando…'); }catch(e){ rec=null; log('Mic start: '+e); }
  }
  function probarMicrofono(){
    manual=true; parar(); cortarVoz();
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){ log('Este navegador no permite usar el micrófono aquí'); manual=false; return; }
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
      const track=stream.getAudioTracks()[0]; log('Micrófono en uso: '+(track?track.label:'?'));
      asegurarAudio(); const an=ctx.createAnalyser(); an.fftSize=1024; ctx.createMediaStreamSource(stream).connect(an);
      const buf=new Uint8Array(an.fftSize); let max=0; const t0=Date.now(); estado('Hable ahora (6 s)…');
      const barra=document.getElementById('vp-barra-nivel');
      const iv=setInterval(function(){
        an.getByteTimeDomainData(buf); let m=0; for(let i=0;i<buf.length;i++){ m=Math.max(m,Math.abs(buf[i]-128)/128); }
        max=Math.max(max,m); if(barra) barra.style.width=Math.min(100,Math.round(m*300))+'%';
        if(Date.now()-t0>6000){
          clearInterval(iv); stream.getTracks().forEach(function(x){x.stop();}); if(barra) barra.style.width='0';
          log('Nivel máximo del micrófono: '+max.toFixed(2)+(max<0.03?' → NO capta voz (silenciado o dispositivo equivocado)':max<0.1?' → muy bajo, suba el volumen de entrada':' → el micrófono sí capta'));
          estado(''); manual=false; iniciar();
        }
      },60);
    }).catch(function(e){ log('No pude abrir el micrófono: '+(e.name||e)); manual=false; estado(''); });
  }
  function pararBarge(){}
  function interrumpir(){
    cortarVoz(); cola.length=0; busy=false; ventanaHasta=Date.now()+25000; interrumpidoEn=Date.now(); ignorarHasta=0;
    log('Interrumpido al decir «Aéter»'); estado('Lo escucho…');
  }
  function hablarAhora(){
    asegurarAudio();
    if(!desbloqueado){ desbloqueado=true; overlay(false); llenarVoces(); }
    if(!SR){ estado('Use Chrome o Edge para hablar'); log('Este navegador no tiene reconocimiento de voz'); return; }
    manual=true; cortarVoz(); cola.length=0; busy=false; parar(); estado('Preparando…');
    const r=new SR(); r.lang='es-MX'; r.interimResults=true; r.continuous=false; let final='';
    r.onstart=function(){ estado('Hable ahora…'); log('Hable ahora'); };
    r.onaudiostart=function(){ log('Micrófono abierto'); };
    r.onspeechstart=function(){ log('Detecto voz…'); };
    r.onresult=function(e){
      let parcial=''; for(let i=e.resultIndex;i<e.results.length;i++){ if(e.results[i].isFinal) final+=e.results[i][0].transcript; else parcial+=e.results[i][0].transcript; }
      estado(''+(final+parcial).slice(0,60));
    };
    r.onerror=function(e){ log('Micrófono: '+e.error); estado('Micrófono: '+e.error); manual=false; };
    const t1=Date.now();
    r.onend=function(){ manual=false; const ms=Date.now()-t1; const txt=final.trim(); if(!txt) log('Fin de escucha tras '+ms+' ms sin texto'); if(txt){ log('Oí: '+txt); ventanaHasta=Date.now()+25000; enviar(txt); } else { estado(''); log('No oí nada'); iniciar(); } };
    setTimeout(function(){ try{ r.start(); }catch(e){ manual=false; log('Mic start: '+e); estado(''); } }, 450);
  }
  function parar(){ if(rec){const r=rec; rec=null; r.onend=null; try{r.abort();}catch(_){}} }
  function enviar(t, reintento){
    const ta=document.querySelector('[data-testid="stChatInputTextArea"]')||document.querySelector('[data-testid="stChatInput"] textarea');
    if(!ta){
      log('No encuentro el cuadro de chat'+(reintento?'':' · abro el asistente'));
      if(!reintento){ navegar(['Aéter']); setTimeout(function(){enviar(t,true);},900); }
      return;
    }
    const dest=intencionNav(t); if(dest){ navegar(dest); log('Abro: '+dest[dest.length-1]); }
    const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
    set.call(ta,t); ta.dispatchEvent(new Event('input',{bubbles:true}));
    busy=true; clearTimeout(busyTimer);
    busyTimer=setTimeout(function(){busy=false;log('Sin respuesta en 30 s');iniciar();},30000);
    estado('Pensando: '+t.slice(0,40));
    setTimeout(function(){
      const b=document.querySelector('[data-testid="stChatInputSubmitButton"]');
      if(b && !b.disabled){ b.click(); log('Enviado'); }
      else { ta.focus(); ['keydown','keypress','keyup'].forEach(function(tp){ ta.dispatchEvent(new KeyboardEvent(tp,{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true})); }); log('Enviado con Enter'); }
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

  panel();
  setInterval(function(){ if(on && desbloqueado && !rec && !busy && !speaking) iniciar(); }, 2500);
  return {config:function(o){
    on=!!o.on; const antes=sirenaOn; sirenaOn=!!o.sirena;
    if(!desbloqueado && hayActivacion()) desbloquear();
    if(desbloqueado && antes!==sirenaOn) sirena(sirenaOn);
    (o.speak||[]).forEach(function(it){ if(!vistos[it.id]){vistos[it.id]=1; cola.push(it.text);} });
    if(o.nav && o.nav.id!==navVisto){ navVisto=o.nav.id; navegar(o.nav.pasos); }
    if(!on){ parar(); cortarVoz(); cola.length=0; estado(''); overlay(false); return; }
    if(!desbloqueado){ overlay(true); return; }
    siguiente();
  }};
})();
"""


def sin_palabra_de_llamado(texto: str) -> str:
    """La voz no debe decir «Aéter» ni «médico» (palabras de llamado): el micrófono las oiría."""
    t = re.sub(r"(?i)\ba?[eé]ther?\b", "su asistente", texto)
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
