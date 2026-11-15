"""Aéter screens: cover, Status, Vitals, Journal, History and medical record.

Aquí no hay lógica del asistente, de la voz ni de las acciones: eso vive en medico/ y en app.py.
"""
from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

import alertas
import db
import registros
import tema
import vivo
from medico import recordatorios as med_rec

RAIZ = Path(__file__).resolve().parent
MESES = registros.MESES
E = html.escape


# --------------------------------------------------------------------------- utilidades
def hora_texto(d: datetime) -> str:
    return f"{d.hour % 12 or 12}:{d:%M} {'AM' if d.hour < 12 else 'PM'}"


def fecha_texto(d: datetime) -> str:
    return f"{MESES[d.month - 1]} {d.day}, {d.year}"


def estado_de(med: dict | None) -> tuple[str, list[dict]]:
    if not med:
        return "normal", []
    lista = alertas.evaluar_medicion(med)
    return alertas.nivel_global(lista), lista


def autoscroll(clase: str) -> None:
    """Baja la barra de una caja con desplazamiento hasta el último elemento."""
    js = f"""<script>(function(){{
      function ir(){{ try{{ const D=window.parent.document; const c=D.querySelector('.{clase}'); if(!c) return;
        const todos=[c].concat([].slice.call(c.querySelectorAll('*')));
        const s=todos.find(function(x){{return x.scrollHeight>x.clientHeight+4 && /(auto|scroll)/.test(getComputedStyle(x).overflowY);}});
        if(s) s.scrollTop=s.scrollHeight; }}catch(e){{}} }}
      function ajustar(){{ try{{ const D=window.parent.document; const c=D.querySelector('.{clase}'); if(!c) return;
        const h=Math.max(300, window.parent.innerHeight-262)+'px';   // el chat llega hasta cerca de la barra de tareas
        [c, c.parentElement].forEach(function(e){{ if(e){{ e.style.setProperty('height',h,'important'); e.style.setProperty('max-height',h,'important'); }} }}); c.parentElement.style.setProperty('flex','0 0 '+h,'important'); }}catch(e){{}} }}
      ajustar(); try{{ window.parent.addEventListener('resize', function(){{ ajustar(); ir(); }}); }}catch(e){{}}
      setTimeout(ajustar,200); setTimeout(ir,150); setTimeout(ir,600);
    }})();</script>"""
    if hasattr(st, "iframe"):
        st.iframe(js, height=1)
    else:
        components.html(js, height=0)


# --------------------------------------------------------------------------- portada
def _elegir(astro_id: int) -> None:
    st.session_state["sel_usuario"] = astro_id


def _iniciar() -> None:
    st.session_state["usuario_id"] = st.session_state["sel_usuario"]
    st.session_state["iniciado"] = True


def pantalla_inicio(astronautas: list[dict]) -> None:
    logo = RAIZ / "assets" / "logo.png"
    st.markdown(
        "<div class='portada'>" + (tema.marte_img("calma", clase="") if not logo.exists() else "")
        + "<h1>Aéter</h1><p class='sub'>Onboard health assistant for astronauts</p>"
        "<p style='opacity:.9;font-size:1.05rem;margin-bottom:.6rem'>Who are you?</p></div>",
        unsafe_allow_html=True)
    if logo.exists():
        st.image(str(logo), width=220)
    sel = st.session_state.get("sel_usuario")
    _, centro, _ = st.columns([1, 5, 1])
    with centro:
        cols = st.columns(len(astronautas), gap="medium")
        for col, a in zip(cols, astronautas):
            with col, st.container(key=f"clic_usr_{a['id']}"):
                es_sel = sel == a["id"]
                st.markdown(
                    f"<div class='tarjeta {'sel' if es_sel else ''}'>{tema.avatar_img(a['nombre'], 104)}"
                    f"<div class='nom'>{E(a['nombre'])}</div><div class='rol'>{E(a['rol'].split('(')[0].strip())}</div>"
                    f"<div class='marca'>{'Selected' if es_sel else 'Tap to choose'}</div></div>",
                    unsafe_allow_html=True)
                st.button("Choose", key=f"tapa_usr_{a['id']}", on_click=_elegir, args=(a["id"],))
        st.write("")
        _, b, _ = st.columns([1, 1.6, 1])
        quien = next((a["nombre"].split()[0] for a in astronautas if a["id"] == sel), None)
        b.button(f"Start as {quien}" if quien else "Choose an astronaut to start", key="btn_iniciar",
                 type="primary", width="stretch", disabled=sel is None, on_click=_iniciar)
        st.markdown("<p style='text-align:center;opacity:.8;font-size:.9rem;margin-top:.8rem'>"
                    "When you start, Aéter greets you. Press «Talk» to speak with it. "
                    "Allow the microphone if the browser asks.</p>", unsafe_allow_html=True)
    st.markdown("<div class='descargo'><b>Educational app.</b> Aéter is a learning prototype built for a hackathon. "
                "It does not replace formal medical care or professional medical assistance. "
                "In a real emergency, contact a qualified health professional.</div>", unsafe_allow_html=True)


def cerrar_sesion() -> None:
    for k in ("usuario_id", "sel_usuario", "saludado", "pendiente", "nav_cmd", "vt_sel"):
        st.session_state.pop(k, None)
    st.session_state["iniciado"] = False


# --------------------------------------------------------------------------- ficha médica
CAMPOS_OCULTOS = {"ID", "Source", "Review date", "Record status", "Fuente", "Fecha de revisión", "Estado del registro"}


def _datos_de_archivo(nombre: str) -> list[tuple[str, list[tuple[str, str]]]]:
    """Secciones de la ficha que ya existen en knowledge/tripulacion/ para esa persona."""
    carpeta = RAIZ / "knowledge" / "tripulacion"
    if not carpeta.exists():
        return []
    for ruta in carpeta.glob("*.md"):
        texto = ruta.read_text(encoding="utf-8")
        bajo = texto.lower()
        if not all(parte in bajo for parte in nombre.lower().split()):
            continue
        secciones = []
        for bloque in re.split(r"(?m)^## ", texto)[1:]:
            titulo, _, cuerpo = bloque.partition("\n")
            titulo = re.sub(r"^[A-Z]{3}\d{3}\s*[—-]\s*", "", titulo).replace("[REVISAR]", "").strip()
            filas = []
            for linea in cuerpo.splitlines():
                m = re.match(r"- ([^:]+): (.+)", linea.strip())
                if m and m.group(1) not in CAMPOS_OCULTOS and "[REVISAR]" not in m.group(2):
                    filas.append((m.group(1).strip(), m.group(2).strip()))
            if filas:
                secciones.append((titulo, filas))
        return secciones
    return []


def _tabla(titulo: str, filas: list[tuple[str, str]]) -> str:
    cuerpo = "".join(f"<tr><td class='k'>{E(k)}</td><td>{E(v) if v else 'No information'}</td></tr>" for k, v in filas)
    return f"<table class='ficha-tabla'><tr><th colspan='2'>{E(titulo.upper())}</th></tr>{cuerpo}</table>"


@st.cache_data(ttl=30, show_spinner=False)
def _csv_historial(astro_id: int) -> bytes:
    return pd.DataFrame(db.todas_mediciones(astro_id)).to_csv(index=False).encode("utf-8")


@st.dialog("Medical record", width="large")
def ficha(astro_id: int) -> None:
    a = db.obtener_astronauta(astro_id)
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:18px;margin-bottom:12px'>{tema.avatar_img(a['nombre'], 78)}"
        f"<div><div style='font-family:Poppins;font-weight:700;font-size:1.5rem'>{E(a['nombre'])}</div>"
        f"<div style='opacity:.8'>{E(a['rol'])}</div></div></div>", unsafe_allow_html=True)
    st.markdown(_tabla("Medical information", [
        ("Name", a["nombre"]), ("Age", f"{a['edad']} years" if a["edad"] else ""),
        ("Weight", f"{a['peso_kg']:.0f} kg" if a["peso_kg"] else ""),
        ("Blood type", a["tipo_sangre"] or ""), ("Role", a["rol"])]), unsafe_allow_html=True)
    st.markdown(_tabla("Allergies", [("Allergies", a["alergias"] or "")]) +
                _tabla("Conditions and history", [("Conditions", a["condiciones"] or "")]) +
                _tabla("Medications", [("Current medications", a["medicamentos"] or "")]), unsafe_allow_html=True)
    for titulo, filas in _datos_de_archivo(a["nombre"]):
        st.markdown(_tabla(titulo, filas), unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.download_button("Export vital signs (CSV)", _csv_historial(astro_id), width="stretch",
                       file_name=f"vitals_{a['nombre'].replace(' ', '_')}.csv", mime="text/csv")
    if c2.button("Log out", key="btn_cerrar_sesion", type="primary", width="stretch"):
        cerrar_sesion()
        st.rerun()  # redibuja toda la app (no solo la ventana) para volver a la portada


# --------------------------------------------------------------------------- estado
def enviar_sos(astro_id: int, nombre: str) -> None:
    db.insertar_evento(astro_id, "critica", "sos", 0, f"{nombre}: requests immediate help")
    st.session_state["sos_aviso"] = True  # el aviso se muestra fuera del callback


@vivo.fragmento(3)
def marte_grande(astro_id: int) -> None:
    nivel, _ = estado_de(db.ultima_medicion(astro_id))
    sos = any(e["parametro"] == "sos" for e in db.listar_eventos(astro_id, limite=10, solo_pendientes=True))
    expresion = "critica" if (nivel == "critica" or sos) else "alerta" if nivel == "advertencia" else "calma"
    st.markdown(f"<div class='marte-grande'>{tema.marte_img(expresion)}</div>", unsafe_allow_html=True)


@vivo.fragmento(5)
def tarjeta_estado(astro_id: int, nombre: str) -> None:
    ahora = med_rec.ahora()
    with st.container(key="vidrio_estado"):
        c1, c2 = st.columns([1.5, 1], vertical_alignment="center")
        c1.markdown(f"<div class='hora'>{hora_texto(ahora)}</div><div class='fecha'>{fecha_texto(ahora)}</div>",
                    unsafe_allow_html=True)
        c2.button("SOS", key="btn_sos", on_click=enviar_sos, args=(astro_id, nombre))
        if st.session_state.pop("sos_aviso", False):
            st.toast("SOS sent to the crew")

        pendientes = db.listar_eventos(astro_id, limite=60, solo_pendientes=True)
        vistos, unicos = set(), []
        for e in pendientes:
            if e["parametro"] not in vistos:
                vistos.add(e["parametro"])
                unicos.append(e)
        items = []
        for e in unicos[:4]:
            color = tema.COLOR["critica" if e["severidad"] == "critica" else "advertencia"]
            items.append(f"<div class='alerta-item'><span class='punto' style='background:{color}'></span>"
                         f"<span>{E(e['mensaje'])}</span><span style='margin-left:auto;opacity:.7'>{e['ts'][11:16]}</span></div>")
        if len(unicos) > 4:
            items.append(f"<div class='alerta-item vacia'>and {len(unicos) - 4} more alerts</div>")
        for r in med_rec.pendientes(astro_id)[:3]:
            items.append(f"<div class='alerta-item'><span class='punto' style='background:#60a5fa'></span>"
                         f"<span>Reminder · {E(r['texto'])}</span><span style='margin-left:auto;opacity:.7'>{r['vence'][11:16]}</span></div>")
        if not items:
            items.append("<div class='alerta-item vacia'>No pending alerts or reminders</div>")
        st.markdown("<div class='zona-alertas'><h4>Alerts and Reminders:</h4>" + "".join(items) + "</div>",
                    unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        if unicos:
            b1.button("Acknowledge alerts", key="btn_reconocer", width="stretch",
                      on_click=db.reconocer_eventos, args=(nombre, astro_id))
        if st.session_state.get("sirena"):
            b2.button("Mute beep", key="btn_silenciar", width="stretch",
                      on_click=lambda: st.session_state.update(sirena=False))


def _pasos_de(texto: str) -> list[tuple[str, str]]:
    """Pasos numerados de un protocolo: (instrucción, advertencia)."""
    pasos = []
    for l in texto.splitlines():
        m = re.match(r"\s*\d+\.\s*(?:\[[^\]]+\]\s*)?(.*)", l)
        if m:
            cuerpo, _, adv = m.group(1).partition("ADVERTENCIA:")
            if not adv:
                cuerpo, _, adv = m.group(1).partition("WARNING:")
            pasos.append((cuerpo.strip(), adv.strip()))
    return pasos


def fijar_protocolo(astro_id: int, codigo: str, titulo: str, pasos: list[tuple[str, str]]) -> None:
    """Deja en la pestaña Status el protocolo que Aéter está guiando."""
    if pasos:
        st.session_state[f"proto_{astro_id}"] = {"codigo": codigo, "titulo": titulo, "pasos": pasos}


def protocolo_desde_codigo(astro_id: int, codigo: str) -> bool:
    from medico import conocimiento
    for f in conocimiento.fragmentos():
        if f["id"] == codigo:
            fijar_protocolo(astro_id, codigo, re.sub(r"^PRO\d{3}\s*[—-]\s*", "", f["titulo"]), _pasos_de(f["texto"]))
            return True
    return False


def _terminar_protocolo(astro_id: int) -> None:
    st.session_state.pop(f"proto_{astro_id}", None)


@vivo.fragmento(3)
def panel_protocolo(astro_id: int) -> None:
    proto = st.session_state.get(f"proto_{astro_id}")
    if not proto:
        st.markdown("<div class='proto'><h3>Protocol to follow</h3><p class='vacio'>When Aéter guides you with a "
                    "protocol, the steps will appear here.</p></div>", unsafe_allow_html=True)
        return
    items = []
    for i, (paso, adv) in enumerate(proto["pasos"], 1):
        extra = f"<div class='adv'>Warning: {E(adv)}</div>" if adv else ""
        items.append(f"<li><span class='n'>{i}</span><div>{E(paso)}{extra}</div></li>")
    codigo = f"{E(proto['codigo'])} · " if re.match(r"PRO\d+", proto["codigo"]) else ""
    st.markdown(f"<div class='proto'><h3>Protocol to follow</h3><div class='ptit'>{codigo}{E(proto['titulo'])}</div>"
                f"<ol>{''.join(items)}</ol></div>", unsafe_allow_html=True)
    st.button("End protocol", key="btn_fin_proto", on_click=_terminar_protocolo, args=(astro_id,))


def pantalla_estado(astro: dict) -> None:
    izq, der = st.columns([1, 1.15], gap="large", vertical_alignment="top")
    with izq:
        nombre_saludo = astro["nombre"] if len(astro["nombre"].split()) <= 2 else " ".join(astro["nombre"].split()[:2])
        with st.container(key="clic_perfil"):
            st.markdown(f"<div class='saludo'>{tema.avatar_img(astro['nombre'], 96)}"
                        f"<div class='txt'>Hello, {E(nombre_saludo)}!</div></div>", unsafe_allow_html=True)
            if st.button("View medical record", key="tapa_perfil"):
                ficha(astro["id"])
        marte_grande(astro["id"])
    with der:
        tarjeta_estado(astro["id"], astro["nombre"])
        st.write("")
        panel_protocolo(astro["id"])


# --------------------------------------------------------------------------- signos vitales
VITALES = (
    ("fc", "Heart<br>Rate", "", ("fc",), ("fc",)),
    ("pa", "Blood<br>Pressure", "systolic and diastolic", ("pas", "pad"), ("pas", "pad")),
    ("spo2", "Oxygen<br>Saturation", "", ("spo2",), ("spo2",)),
    ("temp", "Temperature", "", ("temp",), ("temp",)),
    ("fr", "Respiratory<br>Rate", "", ("fr",), ("fr",)),
)


def _valor(clave: str, med: dict) -> str:
    if clave == "fc":
        return f"{med['fc']:.0f} bpm"
    if clave == "pa":
        return f"<span class='frac'>{med['pas']:.0f}<i></i>{med['pad']:.0f}</span>"
    if clave == "spo2":
        return f"{med['spo2']:.0f}%"
    if clave == "temp":
        return f"{med['temp']:.1f} °C"
    return f"{med['fr']:.0f} rpm"


def grafica_vital(df: pd.DataFrame, param: str, key: str, color: str) -> None:
    u = alertas.UMBRALES[param]
    fig = go.Figure(go.Scatter(x=df["ts"], y=df[param], mode="lines", line=dict(width=2.5, color=color)))
    for tipo, c in (("adv", "#facc15"), ("crit", "#ef4444")):
        for limite in u[tipo]:
            if limite is not None:
                fig.add_hline(y=limite, line_dash="dot", line_color=c, line_width=1)
    lo, hi = float(df[param].min()), float(df[param].max())
    if u["adv"][0] is not None:
        lo = min(lo, u["adv"][0])
    if u["adv"][1] is not None:
        hi = max(hi, u["adv"][1])
    margen = (hi - lo) * 0.06 or 1
    fig.update_layout(
        title=dict(text=f"{u['nombre']} ({u['unidad']})", font=dict(size=13, color="#fff")),
        height=185, margin=dict(l=10, r=10, t=38, b=8), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#fff"),
        yaxis=dict(range=[lo - margen, hi + margen], gridcolor="rgba(255,255,255,.12)"),
        xaxis=dict(gridcolor="rgba(255,255,255,.08)"))
    st.plotly_chart(fig, key=key, config={"displayModeBar": False})


@vivo.fragmento(2)
def panel_signos(astro_id: int, n_puntos: int) -> None:
    recientes = db.ultimas_mediciones(astro_id, n_puntos)
    if not recientes:
        st.info("Waiting for sensor data...")
        return
    actual = recientes[-1]
    _, lista = estado_de(actual)
    por_param = {a["parametro"]: a["severidad"] for a in lista}
    orden = {"normal": 0, "advertencia": 1, "critica": 2}
    cols = st.columns(5, gap="small")
    for col, (clave, titulo, sub, params, _graf) in zip(cols, VITALES):
        nivel = max((por_param.get(p, "normal") for p in params), key=orden.get)
        with col:
            st.markdown(
                f"<div class='vital'><div class='nombre'>{titulo}" + (f"<small>{sub}</small>" if sub else "") + "</div>"
                f"{tema.icono_vital(clave, nivel, actual['fc'], actual['fr'])}<br>"
                f"<span class='dato n-{nivel}'>{_valor(clave, actual)}</span></div>", unsafe_allow_html=True)
    # Las seis gráficas siempre visibles: tres arriba y tres abajo.
    df = pd.DataFrame(recientes)
    df["ts"] = pd.to_datetime(df["ts"])
    graficas = [p for v in VITALES for p in v[4]]  # fc, pas, pad, spo2, temp, fr
    for i in range(0, len(graficas), 3):
        for col, p in zip(st.columns(3, gap="small"), graficas[i:i + 3]):
            with col:
                grafica_vital(df, p, f"graf_{astro_id}_{p}", tema.COLOR[
                    "critica" if por_param.get(p) == "critica" else "advertencia" if por_param.get(p) else "normal"])


# --------------------------------------------------------------------------- listas estilo Notion
@st.dialog("Entry")
def detalle(r: dict) -> None:
    st.markdown(tema.pill(r["etiqueta"]), unsafe_allow_html=True)
    st.markdown(f"### {r['resumen']}")
    st.caption(f"Recorded on {registros.fecha_larga(r['ts'])}")
    st.markdown(r["texto"])


def lista_registros(filas: list[dict], prefijo: str, vacio: str, alto: int = 430) -> None:
    st.markdown("<div class='cab'><span>Entry</span><span>Summary</span><span>Date</span></div>", unsafe_allow_html=True)
    with st.container(height=alto, border=False, key=f"lista_{prefijo}"):
        if not filas:
            st.markdown(f"<p style='opacity:.8;text-align:center;padding:30px'>{vacio}</p>", unsafe_allow_html=True)
        for r in filas:
            with st.container(key=f"clic_{prefijo}_{r['id']}"):
                st.markdown(
                    f"<div class='fila'><span>{tema.pill(r['etiqueta'])}</span><span class='res'>{E(r['resumen'])}</span>"
                    f"<span class='fec'>{registros.fecha_corta(r['ts'])}</span></div>", unsafe_allow_html=True)
                if st.button("Open", key=f"tapa_{prefijo}_{r['id']}"):
                    detalle(r)


def pantalla_bitacora(astro: dict, yo_nombre: str) -> None:
    with st.container(key="bit_barra"):
        with st.form("bit_form", clear_on_submit=True, border=False):
            c0, c1, c2 = st.columns([0.7, 12, 2.2], vertical_alignment="center")
            c0.markdown(tema.marte_img("calma", "46px"), unsafe_allow_html=True)
            texto = c1.text_input("Journal", placeholder="Write how you have felt today in the journal.",
                                  label_visibility="collapsed")
            enviado = c2.form_submit_button("Send", icon=":material/arrow_upward:", width="stretch")
    if enviado and texto.strip():
        with st.spinner("Aéter is reading and classifying your entry..."):
            db.insertar_nota(astro["id"], yo_nombre, texto.strip())
        st.toast("Entry saved to the journal")
    st.write("")
    lista_registros(registros.listar(astro["id"], ("Journal",), 100), "bit",
                    "No entries yet. Write above or tell Aéter: «add to the journal that…».", alto=400)


def pantalla_historial(astro: dict) -> None:
    st.markdown("<h2 style='text-align:left;margin:.2rem 0 1rem'>General History</h2>", unsafe_allow_html=True)
    lista_registros(registros.historial(astro["id"]), "his",
                    "Everything Aéter records will appear here: conversations, protocols, emergencies, "
                    "reminders and the journal.", alto=470)
