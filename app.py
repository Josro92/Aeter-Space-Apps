"""AstroMonitor · monitoreo de signos vitales de astronautas + asistente médico con IA.

Ejecutar:   streamlit run app.py
"""
from __future__ import annotations
import base64
import html
import os
from datetime import datetime, timedelta
import time
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import alertas
import asistente
import db
import protocolos
from servicio import ServicioSensores
from simulador import ESCENARIOS, ETIQUETAS_ESCENARIO

st.set_page_config(page_title="Aéter", page_icon="🚀", layout="wide")

ICONO = {"normal": "🟢", "advertencia": "🟡", "critica": "🔴"}
ETIQUETA_NIVEL = {"normal": "Estable", "advertencia": "Precaución", "critica": "CRÍTICO"}


# --------------------------------------------------------------------------- arranque
@st.cache_resource
def iniciar_servicio() -> ServicioSensores:
    """Crea la BD y arranca el hilo de sensores UNA sola vez por proceso."""
    db.init_db()
    db.sembrar_astronautas()
    servicio = ServicioSensores(intervalo=1.0)
    servicio.iniciar()
    return servicio


servicio = iniciar_servicio()


# --------------------------------------------------------------------------- pantalla de inicio
def pantalla_inicio() -> None:
    """Portada con un solo botón. Ese toque activa el audio y el micrófono del médico."""
    st.markdown("""<style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stHeader"]{display:none}
    .portada{text-align:center;padding-top:14vh}
    .portada h1{font-size:3.4rem;letter-spacing:.06em;margin-bottom:.2rem}
    .portada p{opacity:.75;font-size:1.1rem;margin-bottom:2.2rem}
    </style>""", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        logo = Path(__file__).with_name("assets") / "logo.png"
        if logo.exists():
            st.image(str(logo), width="stretch")
        else:
            st.markdown("<div class='portada'><div style='font-size:5rem'>🚀</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='portada' style='padding-top:0'><h1>Aéter</h1>"
                    "<p>Monitoreo de signos vitales y médico virtual de a bordo</p></div>",
                    unsafe_allow_html=True)
        st.button("▶  Iniciar", type="primary", width="stretch", key="btn_iniciar",
                  on_click=lambda: st.session_state.update(iniciado=True))
        st.caption("Al iniciar, el médico virtual saluda y queda escuchando: diga «médico» para hablarle. Permita el micrófono si el navegador lo pide.")


if not st.session_state.get("iniciado"):
    pantalla_inicio()
    st.stop()

astronautas = db.listar_astronautas()
por_id = {a["id"]: a for a in astronautas}


# --------------------------------------------------------------------------- componentes
def grafica_vital(df: pd.DataFrame, param: str, key: str) -> None:
    u = alertas.UMBRALES[param]
    fig = go.Figure(go.Scatter(x=df["ts"], y=df[param], mode="lines", line=dict(width=2)))
    for tipo, color in (("adv", "#d97706"), ("crit", "#dc2626")):
        for limite in u[tipo]:
            if limite is not None:
                fig.add_hline(y=limite, line_dash="dot", line_color=color, line_width=1)
    # El eje siempre incluye el rango de advertencia, para ver "qué tan cerca" está el valor.
    lo, hi = float(df[param].min()), float(df[param].max())
    if u["adv"][0] is not None:
        lo = min(lo, u["adv"][0])
    if u["adv"][1] is not None:
        hi = max(hi, u["adv"][1])
    margen = (hi - lo) * 0.06 or 1
    fig.update_layout(
        title=dict(text=f"{u['nombre']} ({u['unidad']})", font=dict(size=14)),
        height=230, margin=dict(l=10, r=10, t=40, b=10), showlegend=False,
        yaxis_range=[lo - margen, hi + margen],
    )
    st.plotly_chart(fig, key=key)


def estado_de(med: dict | None) -> tuple[str, list[dict]]:
    if not med:
        return "normal", []
    lista = alertas.evaluar_medicion(med)
    return alertas.nivel_global(lista), lista


def avisar_nuevos_eventos() -> None:
    """Muestra un aviso emergente (toast) por cada alerta nueva registrada."""
    actual = db.ultimo_evento_id()
    visto = st.session_state.get("ultimo_evento_visto")
    if visto is None:  # primera carga: no avisar de lo antiguo
        st.session_state["ultimo_evento_visto"] = actual
        return
    if actual > visto:
        nuevos = db.eventos_desde(visto)
        for e in nuevos[-3:]:
            st.toast(f"{e['astronauta']}: {e['mensaje']}",
                     icon="🚨" if e["severidad"] == "critica" else "⚠️")
        st.session_state["ultimo_evento_visto"] = actual


# --------------------------------------------------------------------------- banner de alertas
@st.fragment(run_every=2)
def banner_alertas(yo_nombre: str) -> None:
    avisar_nuevos_eventos()
    pendientes = db.listar_eventos(solo_pendientes=True, limite=80)
    if not pendientes:
        st.success("Tripulación estable · sin alertas pendientes", icon="✅")
        return

    vistos, unicos = set(), []  # una línea por astronauta + parámetro
    for e in pendientes:
        clave = (e["astronauta_id"], e["parametro"])
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(e)

    if any(e["severidad"] == "critica" for e in unicos):
        st.markdown("### 📢 ALERTA A TODA LA TRIPULACIÓN")
    for e in unicos[:5]:
        texto = f"**{e['astronauta']}** · {e['mensaje']} · {e['ts'][11:19]}"
        if e["severidad"] == "critica":
            st.error(texto, icon="🚨")
        else:
            st.warning(texto, icon="⚠️")
    if len(unicos) > 5:
        st.caption(f"... y {len(unicos) - 5} alertas más (ver pestaña Alertas)")
    # on_click se ejecuta antes de redibujar, así que el banner ya sale actualizado.
    st.button(f"✔ Reconocer alertas (como {yo_nombre})", key="btn_reconocer",
              on_click=db.reconocer_eventos, args=(yo_nombre,))


# --------------------------------------------------------------------------- pestaña principal: estado actual
ESTILO_RELOJ = """<style>
.reloj-wrap{display:flex;justify-content:center;padding:4px 0 16px}
.reloj{--c:#2ecc71;--glow:rgba(46,204,113,.40);width:min(320px,100%);aspect-ratio:1/1;box-sizing:border-box;
border-radius:50%;border:10px solid var(--c);background:#0f1729;color:#e8eefc;box-shadow:0 0 30px var(--glow);
display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:28px;text-align:center}
.reloj.nivel-advertencia{--c:#f5b301;--glow:rgba(245,179,1,.40)}
.reloj.nivel-critica{--c:#ff3b30;--glow:rgba(255,59,48,.60)}
.reloj-hora{font-size:44px;font-weight:700;line-height:1}
.reloj-nombre{font-size:14px;color:#8fa0c4}
.reloj-estado{font-size:20px;font-weight:600;color:var(--c)}
.reloj-vitales{display:flex;gap:14px;font-size:15px;flex-wrap:wrap;justify-content:center}
button[data-baseweb="tab"] p{font-size:22px}
button[data-baseweb="tab"]{height:56px}
.reloj.con-svg{position:relative;border:none;background:none;box-shadow:none}
.reloj-img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 0 18px var(--glow))}
.reloj.con-svg > div{position:relative}
.corazon-svg {
  width: 18px;
  height: 18px;
  vertical-align: middle;
  margin-right: 4px;
}
#corazon-path {
  fill: var(--c-corazon, #047f00);
  stroke: var(--c-corazon, #047f00);
  transform-box: fill-box;
  transform-origin: center;
  animation: latir var(--duracion, 0.85s) infinite ease-in-out;
}
@keyframes latir {
  0%, 100% { transform: scale(1); }
  15% { transform: scale(1.25); }
  30% { transform: scale(1); }
  45% { transform: scale(1.18); }
  60% { transform: scale(1); }
}
</style>"""
RUTA_SVG = Path(__file__).with_name("dinosa.svg")
SVG_B64 = base64.b64encode(RUTA_SVG.read_bytes()).decode() if RUTA_SVG.exists() else ""
TEXTO_ESTADO = {"normal": "Todo en orden", "advertencia": "Atención", "critica": "Emergencia"}


def reloj_html(nivel: str, nombre: str, estado: str, med: dict | None) -> str:
    def v(clave: str, formato: str = "{:.0f}") -> str:
        return formato.format(med[clave]) if med else "--"

    # Cálculo dinámico de velocidad y color según la frecuencia cardíaca (fc)
    fc = med["fc"] if (med and med.get("fc")) else 70
    duracion = 60.0 / max(fc, 30)  # Evita división por cero si hay fallo de sensor
    color_corazon = "#ff3b30" if fc > 100 else "#2ecc71"
   
    svg_corazon = (
        f'<svg class="corazon-svg" viewBox="100 50 200 180" xmlns="http://w3.org">'
        f'<path id="corazon-path" stroke-width="8" '
        f'style="--c-corazon:{color_corazon}; --duracion:{duracion:.2f}s;" '
        f'd="m200.04,112.01c24.5,-70.29 120.49,0 0,90.37c-120.49,-90.37 -24.5,-160.66 0,-90.37z"/>'
        f'</svg>'
    )



def enviar_sos(astro_id: int) -> None:
    """Botón SOS: registra una alerta crítica que ve toda la tripulación."""
    a = por_id[astro_id]
    db.insertar_evento(astro_id, "critica", "sos", 0,
                       f"{a['nombre']}: solicita ayuda inmediata")


@st.fragment(run_every=2)
def panel_estado_actual(astro_id: int) -> None:
    a = por_id[astro_id]
    med = db.ultima_medicion(astro_id)
    nivel, lista = estado_de(med)
    estado = TEXTO_ESTADO[nivel]
    sos = [e for e in db.listar_eventos(astro_id, limite=20, solo_pendientes=True)
           if e["parametro"] == "sos"]
    if sos:  # un SOS pendiente pone el reloj en rojo aunque los signos estén normales
        nivel, estado = "critica", "SOS enviado"

    col_reloj, col_info = st.columns([1, 1.3], gap="large")
    with col_reloj:
        st.markdown(reloj_html(nivel, a["nombre"], estado, med), unsafe_allow_html=True)
        st.button("🆘 SOS: avisar a la tripulación", key="btn_sos", type="primary",
                  on_click=enviar_sos, args=(astro_id,))

    with col_info:
        st.subheader("Qué hacer ahora")
        if sos:
            st.error(f"SOS enviado a la tripulación a las {sos[0]['ts'][11:19]}. "
                     "Esperando que alguien lo reconozca.", icon="🆘")
        if not lista:
            st.success("Todos los signos vitales están dentro del rango normal. "
                       "Sigue con tu rutina.", icon="✅")
        for al in lista:
            if al["severidad"] == "critica":
                st.error(al["mensaje"], icon="🚨")
            else:
                st.warning(al["mensaje"], icon="⚠️")
        for clave in protocolos.protocolos_para_alertas(lista)[:2]:
            e = protocolos.EMERGENCIAS[clave]
            with st.container(border=True):
                st.markdown(f"**{e['titulo']}**")
                st.markdown(protocolos.lista_numerada(e["pasos"][:3]))
                st.caption(f"Escalar si: {e['escalar']}")

    if med:
        por_param = {al["parametro"]: al["severidad"] for al in lista}

        def sev(*params: str) -> str:
            niveles = [por_param.get(p, "normal") for p in params]
            return ("critica" if "critica" in niveles
                    else "advertencia" if "advertencia" in niveles else "normal")

        datos = [
            ("Pulso", alertas.formatear("fc", med["fc"]), sev("fc")),
            ("Presión", f"{med['pas']:.0f}/{med['pad']:.0f} mmHg", sev("pas", "pad")),
            ("SpO₂", alertas.formatear("spo2", med["spo2"]), sev("spo2")),
            ("Temperatura", alertas.formatear("temp", med["temp"]), sev("temp")),
            ("Respiración", alertas.formatear("fr", med["fr"]), sev("fr")),
        ]
        for col, (titulo, valor, s) in zip(st.columns(5), datos):
            col.metric(f"{ICONO[s]} {titulo}", valor)

    st.caption("Tripulación")
    for col, x in zip(st.columns(len(astronautas)), astronautas):
        n, _ = estado_de(db.ultima_medicion(x["id"]))
        col.markdown(f"{ICONO[n]} **{x['nombre']}**  \n{x['rol']} · {ETIQUETA_NIVEL[n]}")
   


# --------------------------------------------------------------------------- pestaña 1
@st.fragment(run_every=2)
def panel_monitoreo(astro_id: int, n_puntos: int) -> None:
    st.subheader("Tripulación")
    columnas = st.columns(len(astronautas))
    for col, a in zip(columnas, astronautas):
        med = db.ultima_medicion(a["id"])
        with col, st.container(border=True):
            nivel, _ = estado_de(med)
            st.markdown(f"**{ICONO[nivel]} {a['nombre']}**")
            st.caption(f"{a['rol']} · {ETIQUETA_NIVEL[nivel]}")
            if med:
                st.markdown(f"❤️ {med['fc']:.0f} lpm  \n🫁 SpO₂ {med['spo2']:.0f} %  \n"
                            f"🩸 {med['pas']:.0f}/{med['pad']:.0f} mmHg")

    recientes = db.ultimas_mediciones(astro_id, n_puntos)
    if not recientes:
        st.info("Esperando datos de los sensores...")
        return
    df = pd.DataFrame(recientes)
    df["ts"] = pd.to_datetime(df["ts"])
    actual = recientes[-1]
    _, lista = estado_de(actual)
    por_param = {a["parametro"]: a for a in lista}

    st.subheader(f"Signos vitales · {por_id[astro_id]['nombre']}")
    st.caption(f"Última medición: {actual['ts'][11:19]} · escenario del simulador: "
               f"{ETIQUETAS_ESCENARIO[servicio.escenario(astro_id)]}")
    for fila in (alertas.ORDEN[:3], alertas.ORDEN[3:]):
        cols = st.columns(3)
        for col, p in zip(cols, fila):
            sev = por_param.get(p, {}).get("severidad", "normal")
            col.metric(f"{ICONO[sev]} {alertas.UMBRALES[p]['nombre']}",
                       alertas.formatear(p, actual[p]))
        cols = st.columns(3)
        for col, p in zip(cols, fila):
            with col:
                grafica_vital(df, p, key=f"graf_{astro_id}_{p}")


# --------------------------------------------------------------------------- pestaña 2
@st.fragment(run_every=3)
def panel_alertas(astro_id: int) -> None:
    c1, c2 = st.columns(2)
    solo_sel = c1.toggle("Solo el astronauta seleccionado", value=False, key="solo_sel")
    solo_pend = c2.toggle("Solo pendientes", value=False, key="solo_pend")
    eventos = db.listar_eventos(astro_id if solo_sel else None, limite=300, solo_pendientes=solo_pend)
    if not eventos:
        st.info("No hay alertas registradas todavía. Activa un escenario en el simulador de la barra lateral.")
        return
    df = pd.DataFrame(eventos)
    m1, m2, m3 = st.columns(3)
    m1.metric("Alertas mostradas", len(df))
    m2.metric("Críticas", int((df["severidad"] == "critica").sum()))
    m3.metric("Pendientes", int((df["reconocida"] == 0).sum()))
    tabla = pd.DataFrame({
        "Hora": df["ts"].str[11:19],
        "Astronauta": df["astronauta"],
        "Nivel": df["severidad"].map({"critica": "🔴 Crítica", "advertencia": "🟡 Advertencia"}),
        "Detalle": df["mensaje"],
        "Estado": df.apply(lambda r: f"Reconocida por {r['reconocida_por']}" if r["reconocida"] else "Pendiente", axis=1),
    })
    st.dataframe(tabla, hide_index=True)


# --------------------------------------------------------------------------- pestaña 3
@st.cache_data(ttl=30, show_spinner=False)
def csv_historial(astro_id: int) -> bytes:
    return pd.DataFrame(db.todas_mediciones(astro_id)).to_csv(index=False).encode("utf-8")


def tab_historial(astro_id: int, yo_nombre: str) -> None:
    a = db.obtener_astronauta(astro_id)
    st.subheader(f"Ficha médica · {a['nombre']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rol", a["rol"])
    c2.metric("Edad", f"{a['edad']} años")
    c3.metric("Peso", f"{a['peso_kg']:.0f} kg")
    c4.metric("Grupo sanguíneo", a["tipo_sangre"])

    with st.form(f"ficha_{astro_id}"):
        f1, f2, f3 = st.columns(3)
        alergias = f1.text_area("Alergias", a["alergias"], key=f"alergias_{astro_id}")
        medicamentos = f2.text_area("Medicamentos actuales", a["medicamentos"], key=f"meds_{astro_id}")
        condiciones = f3.text_area("Antecedentes / condiciones", a["condiciones"], key=f"cond_{astro_id}")
        if st.form_submit_button("💾 Guardar ficha"):
            db.actualizar_astronauta(astro_id, alergias=alergias, medicamentos=medicamentos,
                                     condiciones=condiciones)
            st.success("Ficha actualizada")

    st.subheader("Bitácora clínica")
    with st.form(f"nota_{astro_id}", clear_on_submit=True):
        texto = st.text_area("Nueva nota (síntomas, tratamiento aplicado, evolución...)",
                             key=f"nota_txt_{astro_id}")
        if st.form_submit_button(f"➕ Agregar nota (como {yo_nombre})") and texto.strip():
            db.insertar_nota(astro_id, yo_nombre, texto.strip())
            st.success("Nota guardada")
    for n in db.listar_notas(astro_id, limite=10):
        st.markdown(f"**{n['ts'].replace('T', ' ')}** · {n['autor']}  \n{n['nota']}")

    st.subheader("Historial de signos vitales")
    rangos = {"Últimos 5 minutos": 5, "Última hora": 60, "Todo el registro": None}
    c1, c2 = st.columns(2)
    rango = c1.selectbox("Período", list(rangos), index=1, key="rango_hist")
    variable = c2.selectbox("Gráfica de tendencia", list(alertas.ORDEN),
                            format_func=lambda p: alertas.UMBRALES[p]["nombre"], key="var_hist")
    minutos = rangos[rango]
    desde = (datetime.now() - timedelta(minutes=minutos)).isoformat(timespec="seconds") if minutos else None

    res = db.resumen_mediciones(astro_id, desde)
    if not res["n"]:
        st.info("Aún no hay mediciones en este período.")
        return
    tabla = pd.DataFrame(
        {alertas.UMBRALES[p]["nombre"]: [res[f"{p}_min"], res[f"{p}_prom"], res[f"{p}_max"]]
         for p in alertas.ORDEN},
        index=["Mínimo", "Promedio", "Máximo"],
    ).round(1)
    st.caption(f"{res['n']} mediciones en el período")
    st.dataframe(tabla)

    datos = db.mediciones(astro_id, desde, max_puntos=1500)
    df = pd.DataFrame(datos)
    df["ts"] = pd.to_datetime(df["ts"])
    grafica_vital(df, variable, key=f"hist_{astro_id}_{variable}")

    eventos = db.listar_eventos(astro_id, limite=20)
    if eventos:
        st.markdown("**Últimas alertas de este astronauta**")
        st.dataframe(pd.DataFrame({
            "Hora": [e["ts"].replace("T", " ") for e in eventos],
            "Nivel": [e["severidad"] for e in eventos],
            "Detalle": [e["mensaje"] for e in eventos],
        }), hide_index=True)

    st.download_button("📥 Exportar historial completo (CSV)", csv_historial(astro_id),
                       file_name=f"historial_{a['nombre'].replace(' ', '_')}.csv", mime="text/csv")


# --------------------------------------------------------------------------- pestaña 4
ATAJOS = {
    "🚨 Guíame en la emergencia actual": "Guíame paso a paso en la emergencia actual de este astronauta.",
    "🩺 ¿Cómo mido la presión?": "¿Cómo mido la presión arterial correctamente?",
    "🫁 ¿Cómo mido la SpO₂?": "¿Cómo mido la saturación de oxígeno?",
    "💊 ¿Qué medicamentos puedo usar?": "¿Qué medicamentos del botiquín puedo usar con este astronauta y qué debo revisar antes?",
}


def tab_asistente(astro_id: int, api_key: str, yo_nombre: str) -> None:
    astro = db.obtener_astronauta(astro_id)
    st.subheader(f"Asistente de a bordo · paciente: {astro['nombre']}")
    import medico
    if medico.hay_llave():
        st.caption("🟢 Médico virtual conectado (Gemini + base de conocimiento)")
    elif api_key:
        st.caption("🟢 Conectado a Claude")
    else:
        st.caption("🟠 Modo offline: responde con los protocolos locales (falta la llave GEMINI_API_KEY)")

    historial = st.session_state.setdefault(f"chat_{astro_id}", [])
    from medico import acciones as med_acciones

    with st.expander("🔎 Contexto que recibe el asistente en este momento"):
        recientes = db.ultimas_mediciones(astro_id, 30)
        _, lista = estado_de(recientes[-1] if recientes else None)
        st.code(asistente.construir_contexto(astro, recientes, lista, db.listar_notas(astro_id, 3)),
                language="markdown")

    cols = st.columns(len(ATAJOS))
    for col, (etiqueta, texto) in zip(cols, ATAJOS.items()):
        if col.button(etiqueta, key=f"atajo_{astro_id}_{etiqueta}"):
            st.session_state["pregunta_pendiente"] = texto

    for i, m in enumerate(historial):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("acciones"):
                med_acciones.mostrar(m["acciones"], astro_id, yo_nombre, f"{astro_id}_{i}", servicio)

    prompt = st.chat_input("Describe la emergencia o haz una pregunta...", key=f"chat_in_{astro_id}")
    if not prompt:
        prompt = st.session_state.pop("pregunta_pendiente", None)
    if prompt:
        historial.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # Si pidió ir a una pantalla («muéstrame las alertas»), se navega sin depender del modelo.
        destino = med_acciones.intencion_navegacion(prompt)
        st.session_state["nav_intent"] = destino
        if destino:
            st.session_state["nav_cmd"] = {"id": f"{time.time()}", "pasos": med_acciones.SECCIONES[destino]}
        # Confirmación por voz de SOS / detener emergencia: la decide la página, no el modelo.
        pend = st.session_state.get("pendiente")
        palabras = protocolos.normalizar(prompt).split()
        if pend and len(palabras) <= 6:
            if time.time() - pend.get("ts", 0) > med_acciones.CONFIRMAR_SEG:
                st.session_state.pop("pendiente", None)
            elif any(p in ("confirmo", "confirmado", "adelante", "envialo", "hazlo") for p in palabras):
                resultado = med_acciones.ejecutar_pendiente(pend, astro_id, yo_nombre, servicio)
                st.session_state.pop("pendiente", None)
                with st.chat_message("assistant"):
                    st.markdown(resultado)
                historial.append({"role": "assistant", "content": resultado, "acciones": []})
                st.session_state["voz_texto"] = (resultado, f"{astro_id}_{len(historial)}")
                prompt = None
            elif any(p in ("cancela", "cancelar", "cancelalo", "olvidalo") for p in palabras):
                st.session_state.pop("pendiente", None)
                with st.chat_message("assistant"):
                    st.markdown("Cancelado.")
                historial.append({"role": "assistant", "content": "Cancelado.", "acciones": []})
                st.session_state["voz_texto"] = ("Cancelado.", f"{astro_id}_{len(historial)}")
                prompt = None
    if prompt:
        recientes = db.ultimas_mediciones(astro_id, 30)  # datos frescos al momento de preguntar
        _, lista = estado_de(recientes[-1] if recientes else None)
        filtro = med_acciones.Filtro()
        with st.chat_message("assistant"):
            respuesta = st.write_stream(filtro.filtrar(asistente.responder_stream(
                historial, astro, recientes, lista, db.listar_notas(astro_id, 3), api_key)))
            med_acciones.aplicar_inmediatas(filtro.acciones, astro_id, yo_nombre)
            med_acciones.mostrar(filtro.acciones, astro_id, yo_nombre, f"{astro_id}_{len(historial)}", servicio)
        nueva_pend = med_acciones.pendiente_de(filtro.acciones)
        if nueva_pend:
            st.session_state["pendiente"] = nueva_pend
        historial.append({"role": "assistant", "content": respuesta, "acciones": filtro.acciones})
        st.session_state["voz_texto"] = (respuesta, f"{astro_id}_{len(historial)}")
        if "astro_cambiar" in st.session_state:
            st.rerun()  # redibuja ya con el otro astronauta seleccionado

    if historial and st.button("🧹 Limpiar conversación", key=f"limpiar_{astro_id}"):
        historial.clear()
        st.rerun()


# --------------------------------------------------------------------------- barra lateral
# El médico pide cambiar de astronauta: se aplica antes de crear el selector.
if "astro_cambiar" in st.session_state:
    st.session_state["astro"] = st.session_state.pop("astro_cambiar")

with st.sidebar:
    st.title("🚀 AstroMonitor")
    st.caption("Monitoreo de signos vitales y asistente médico de a bordo")

    yo_id = st.selectbox("Sesión iniciada como", list(por_id),
                         format_func=lambda i: por_id[i]["nombre"], key="yo")
    astro_id = st.selectbox("Astronauta a monitorear", list(por_id),
                            format_func=lambda i: f"{por_id[i]['nombre']} · {por_id[i]['rol']}", key="astro")
    ventana = st.slider("Ventana de las gráficas (segundos)", 30, 600, 120, step=30)

    with st.expander("🧪 Simulador de emergencias", expanded=True):
        escenario = st.selectbox("Escenario", list(ESCENARIOS),
                                 format_func=ETIQUETAS_ESCENARIO.get, key="esc_sel")
        b1, b2 = st.columns(2)
        if b1.button("▶ Activar", type="primary"):
            servicio.set_escenario(astro_id, escenario)
            st.toast(f"Escenario «{ETIQUETAS_ESCENARIO[escenario]}» activado para {por_id[astro_id]['nombre']}")
        if b2.button("↺ Normalizar"):
            servicio.set_escenario(astro_id, "normal")
        st.caption(f"Escenario actual: **{ETIQUETAS_ESCENARIO[servicio.escenario(astro_id)]}**")

    with st.expander("🩺 Médico virtual", expanded=True):
        st.toggle("🎙️ Siempre activo (voz)", value=True, key="voz_on",
                  help="El médico saluda, escucha sin botones y responde en voz alta. Use Chrome o Edge y permita el micrófono.")
        s1, s2 = st.columns(2)
        s1.button("🔔 Pitido", on_click=lambda: st.session_state.update(sirena=True), use_container_width=True)
        s2.button("🔕 Silenciar", on_click=lambda: st.session_state.update(sirena=False), use_container_width=True)
        if st.session_state.get("sirena"):
            st.error("Pitido de emergencia ACTIVO", icon="🔔")
        from medico import recordatorios as med_rec
        for r in med_rec.pendientes(astro_id)[:4]:
            st.caption(f"⏰ {r['vence'][11:16]} · {r['texto']}")

    with st.expander("🤖 Asistente con IA"):
        api_key = st.text_input("API key de Anthropic (opcional)", type="password",
                                value=os.environ.get("ANTHROPIC_API_KEY", ""),
                                help="Sin key, el asistente responde con los protocolos locales.")
    st.caption(protocolos.DESCARGO)

# --------------------------------------------------------------------------- pantalla principal
yo_nombre = por_id[yo_id]["nombre"]
banner_alertas(yo_nombre)

st.markdown(ESTILO_RELOJ, unsafe_allow_html=True)
tab_estado, tab_detalle = st.tabs(["⌚ Estado actual", "📊 Detalle"])
with tab_estado:
    panel_estado_actual(astro_id)
with tab_detalle:
    sub1, sub2, sub3, sub4 = st.tabs(["📡 Monitoreo en vivo", "🚨 Alertas", "🗂️ Historial médico", "🤖 Asistente IA"])
    with sub1:
        panel_monitoreo(astro_id, int(ventana / servicio.intervalo))
    with sub2:
        panel_alertas(astro_id)
    with sub3:
        tab_historial(astro_id, yo_nombre)
    with sub4:
        tab_asistente(astro_id, api_key, yo_nombre)

from medico.capa import capa_global
capa_global(astro_id, yo_nombre)
