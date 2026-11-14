"""Capa global del médico: siempre activo mientras la app esté abierta.

Cada pocos segundos: anuncia recordatorios y alertas críticas nuevas, lee en voz alta las
respuestas del chat, aplica pitido y navegación, y saluda una vez al inicio.
"""
import time

import streamlit as st

import db
from . import recordatorios, voz


def _saludo(yo_nombre: str) -> str:
    h = recordatorios.ahora().hour
    momento = "Buenos días" if h < 12 else "Buenas tardes" if h < 19 else "Buenas noches"
    pendientes = db.listar_eventos(solo_pendientes=True, limite=40)
    vistos, msgs = set(), []
    for e in pendientes:
        if (e["astronauta_id"], e["parametro"]) not in vistos:
            vistos.add((e["astronauta_id"], e["parametro"]))
            msgs.append(f"{e['astronauta']}: {e['mensaje']}")
    estado = ("Hay alertas activas. " + ". ".join(msgs[:3]) + ".") if msgs else "Todos los signos están estables."
    return (f"{momento}, {yo_nombre}. Soy el médico virtual y estoy escuchando: hábleme cuando me necesite. "
            f"{estado}")


@st.fragment(run_every=8)
def capa_global(astro_id: int, yo_nombre: str) -> None:
    ss = st.session_state
    cola: list[dict] = []
    activo = ss.get("voz_on", True)

    # Saludo (una vez por sesión)
    if activo and not ss.get("saludado"):
        ss["saludado"] = True
        ss["ultimo_ev_voz"] = db.ultimo_evento_id()
        cola.append({"id": "saludo", "text": _saludo(yo_nombre)})

    # Alertas críticas nuevas (de cualquier astronauta)
    if "ultimo_ev_voz" not in ss:
        ss["ultimo_ev_voz"] = db.ultimo_evento_id()
    for e in db.eventos_desde(ss["ultimo_ev_voz"]):
        ss["ultimo_ev_voz"] = max(ss["ultimo_ev_voz"], e["id"])
        if e["severidad"] == "critica":
            cola.append({"id": f"ev{e['id']}", "text": f"Alerta crítica. {e['astronauta']}: {e['mensaje']}"})

    # Recordatorios que llegaron a su hora
    for r in recordatorios.vencidos():
        st.toast(f"⏰ {r['texto']}")
        cola.append({"id": f"rec{r['id']}", "text": f"Recordatorio: {r['texto']}"})
    hechos = ss.setdefault("recordatorios_archivo_hechos", set())
    for r in recordatorios.del_archivo():
        if r["id"] not in hechos:
            hechos.add(r["id"])
            st.toast(f"⏰ {r['texto']}")
            cola.append({"id": r["id"], "text": f"Recordatorio: {r['texto']}"})

    # Respuesta del chat para leer en voz alta
    nueva = ss.pop("voz_texto", None)
    if nueva:
        cola.append({"id": nueva[1], "text": nueva[0]})

    voz.componente(activo, cola, ss.get("sirena", False), ss.pop("nav_cmd", None) or ss.get("nav_ult"))


def contexto_extra(astro_id: int) -> str:
    """Líneas que se añaden al contexto del médico en cada pregunta."""
    ss = st.session_state
    lineas = [f"\n## Estado de la pantalla\n- Hora actual: {recordatorios.ahora().strftime('%H:%M')}",
              f"- Pitido de emergencia: {'ACTIVO' if ss.get('sirena') else 'apagado'}"]
    pend = recordatorios.pendientes(astro_id)
    if pend:
        lineas.append("- Recordatorios pendientes: " + "; ".join(f"{r['vence'][11:16]} {r['texto']}" for r in pend[:5]))
    return "\n".join(lineas)
