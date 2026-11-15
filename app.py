"""Aéter · monitoreo de signos vitales y asistente de salud con IA para astronautas.

Ejecutar:   streamlit run app.py

Estructura:
  tema.py      estilos y dibujos (glassmorfismo)
  vistas.py    pantallas: portada, Estado, Signos Vitales, Bitácora, Historial y ficha médica
  registros.py bitácora e historial
  medico/      cerebro de Aéter (IA, conocimiento, voz, acciones)
"""
from __future__ import annotations

import os
import re
import time

import streamlit as st

st.set_page_config(page_title="Aéter", page_icon=":material/public:", layout="wide",
                   initial_sidebar_state="collapsed")

import alertas
import asistente
import db
import protocolos
import registros
import tema
import vistas
from servicio import ServicioSensores
from simulador import ESCENARIOS, ETIQUETAS_ESCENARIO

tema.aplicar_tema()


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
astronautas = db.listar_astronautas()
por_id = {a["id"]: a for a in astronautas}

# Aéter puede pedir (por voz o chat) cambiar de astronauta: se aplica antes de dibujar nada.
if "astro_cambiar" in st.session_state:
    nuevo = st.session_state.pop("astro_cambiar")
    if st.session_state.get("iniciado") and nuevo in por_id:
        st.session_state["usuario_id"] = nuevo

if not (st.session_state.get("iniciado") and st.session_state.get("usuario_id") in por_id):
    vistas.pantalla_inicio(astronautas)
    st.stop()

astro_id = st.session_state["usuario_id"]
astro = por_id[astro_id]
yo_nombre = astro["nombre"]
nombre_corto = astro["nombre"].split()[0]
api_key = os.environ.get("ANTHROPIC_API_KEY", "")

# Icono de Aéter a la izquierda de la barra de escritura del chat.
_marte_uri = "data:image/svg+xml;base64," + __import__("base64").b64encode(tema.marte_svg("calma").encode()).decode()
st.markdown(f"""<style>
[data-testid="stChatInput"]{{padding-left:64px!important;background-image:url("{_marte_uri}")!important;
background-repeat:no-repeat!important;background-size:46px!important;background-position:12px center!important}}
</style>""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- Aéter (chat)
def _registrar_intercambio(prompt: str, respuesta: str, acciones: list[dict]) -> None:
    """Deja la conversación (y los protocolos que usó) en el historial de la persona."""
    try:
        registros.agregar(astro_id, "Conversación", prompt,
                          f"Pregunta: {prompt}\n\nRespuesta de Aéter: {respuesta}")
        from medico import conocimiento
        cods = sorted(set(re.findall(r"PRO\d{3}", respuesta)))
        titulos = {f["id"]: f["titulo"] for f in conocimiento.fragmentos() if f["id"] in cods}
        for c in cods:
            nombre_pro = re.sub(r"^PRO\d{3}\s*[—-]\s*", "", titulos.get(c, c))
            registros.agregar(astro_id, "Protocolo", f"{c} · {nombre_pro}",
                              f"Aéter aplicó el protocolo {c} durante una conversación.\n\nPregunta: {prompt}")
        for a in acciones:
            if a["accion"] == "ver_procedimiento":
                titulo = protocolos.EMERGENCIAS.get(a["arg"], {}).get("titulo", a["arg"])
                registros.agregar(astro_id, "Protocolo", f"Guía mostrada: {titulo}",
                                  f"Aéter mostró la guía «{titulo}».\n\nPregunta: {prompt}")
    except Exception:
        pass  # el historial nunca debe romper el chat


def pantalla_aeter() -> None:
    from medico import acciones as med_acciones
    historial = st.session_state.setdefault(f"chat_{astro_id}", [])

    caja = st.container(height=545, border=False, key="chat_caja")
    with caja:
        bienvenida = st.empty()
        if not historial:
            bienvenida.markdown("<p class='bienvenida'>Escribe o di «Aéter» y cuéntame qué necesitas. "
                                "Puedo ayudarte con tu salud, la misión o lo que quieras conversar.</p>",
                                unsafe_allow_html=True)
        for i, m in enumerate(historial):
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m.get("acciones"):
                    med_acciones.mostrar(m["acciones"], astro_id, yo_nombre, f"{astro_id}_{i}", servicio)

    prompt = st.chat_input(f"Hola, {nombre_corto}. ¿En qué te puedo ayudar?", key=f"chat_in_{astro_id}")
    if prompt:
        bienvenida.empty()
        with caja:
            _atender(prompt, historial, med_acciones)
    vistas.autoscroll("st-key-chat_caja")


def _atender(prompt: str, historial: list, med_acciones) -> None:
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
            return
        elif any(p in ("cancela", "cancelar", "cancelalo", "olvidalo") for p in palabras):
            st.session_state.pop("pendiente", None)
            with st.chat_message("assistant"):
                st.markdown("Cancelado.")
            historial.append({"role": "assistant", "content": "Cancelado.", "acciones": []})
            st.session_state["voz_texto"] = ("Cancelado.", f"{astro_id}_{len(historial)}")
            return

    recientes = db.ultimas_mediciones(astro_id, 30)  # datos frescos al momento de preguntar
    _, lista = vistas.estado_de(recientes[-1] if recientes else None)
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
    _registrar_intercambio(prompt, respuesta, filtro.acciones)
    if "astro_cambiar" in st.session_state:
        st.rerun()  # redibuja ya con el otro astronauta


# --------------------------------------------------------------------------- barra lateral: modo demostración
with st.sidebar:
    st.markdown("### Modo demostración")
    st.caption("Panel para quien presenta. Aquí se activan emergencias simuladas y se ajusta la voz.")
    escenario = st.selectbox("Escenario simulado", list(ESCENARIOS), format_func=ETIQUETAS_ESCENARIO.get, key="esc_sel")
    b1, b2 = st.columns(2)
    if b1.button("Activar", type="primary", width="stretch"):
        servicio.set_escenario(astro_id, escenario)
        st.toast(f"Escenario «{ETIQUETAS_ESCENARIO[escenario]}» activado")
    if b2.button("Normalizar", width="stretch"):
        servicio.set_escenario(astro_id, "normal")
    st.caption(f"Escenario actual: {ETIQUETAS_ESCENARIO[servicio.escenario(astro_id)]}")
    st.toggle("Voz siempre activa", value=True, key="voz_on",
              help="Aéter saluda, escucha sin botones y responde en voz alta. Use Chrome o Edge y permita el micrófono.")
    s1, s2 = st.columns(2)
    s1.button("Pitido", on_click=lambda: st.session_state.update(sirena=True), width="stretch")
    s2.button("Silenciar", on_click=lambda: st.session_state.update(sirena=False), width="stretch")
    ventana = st.slider("Ventana de las gráficas (segundos)", 30, 600, 120, step=30)
    if st.button("Limpiar conversación", width="stretch"):
        st.session_state.get(f"chat_{astro_id}", []).clear()
        st.rerun()
    st.caption(protocolos.DESCARGO)

# --------------------------------------------------------------------------- pantalla principal
tab_estado, tab_signos, tab_aeter, tab_bitacora, tab_historial = st.tabs(
    ["Estado", "Signos Vitales", "Aéter", "Bitácora", "Historial"])
with tab_estado:
    vistas.pantalla_estado(astro)
with tab_signos:
    vistas.panel_signos(astro_id, int(ventana / servicio.intervalo))
with tab_aeter:
    pantalla_aeter()
with tab_bitacora:
    vistas.pantalla_bitacora(astro, yo_nombre)
with tab_historial:
    vistas.pantalla_historial(astro)

from medico.capa import capa_global
capa_global(astro_id, yo_nombre)
