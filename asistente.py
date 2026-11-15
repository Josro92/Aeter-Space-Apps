
from __future__ import annotations

import os
import re
import time
from typing import Iterator

import alertas as mod_alertas
import protocolos

MODELO = os.environ.get("ASTRO_MODELO", "claude-sonnet-5-5")

SYSTEM_BASE = """You are Aéter, the onboard health assistant for a crew of astronauts.
You support the medical officer and the crew.
Rules:
- Always answer in English, clear and brief. In emergencies: short, easy steps, starting with the most urgent action.
- Keep in mind they are far from Earth and communication may be delayed.
- Use only the vital signs, medical record and alerts of the current state. Do not invent data.
- Before recommending any medication, check the patient's allergies, current medications and history and mention them explicitly.
- Say to use the dose on the kit label or in the mission protocol, confirmed by the medical officer or the flight surgeon.
- Base your answers on the emergency protocols. If something is not covered, say so and recommend consulting the flight surgeon / Mission Control.
- Do not diagnose with certainty: talk about possible causes.
- If there is a risk to life, say in order: 1) alert the crew, 2) the immediate action, 3) contact the flight surgeon.
- End emergency answers with what to measure again and when."""


def construir_contexto(astronauta: dict, recientes: list[dict], alertas_activas: list[dict],
                       notas: list[dict] | None = None) -> str:
    a = astronauta
    lineas = [
        "## Patient",
        f"- Name: {a['nombre']} ({a['rol']})",
        f"- Age: {a['edad']} years · Weight: {a['peso_kg']} kg · Blood type: {a['tipo_sangre']}",
        f"- ALLERGIES: {a['alergias'] or 'not recorded'}",
        f"- Current medications: {a['medicamentos'] or 'none'}",
        f"- History: {a['condiciones'] or 'none'}",
    ]
    if recientes:
        ult, ini = recientes[-1], recientes[0]
        lineas.append(f"\n## Current vital signs (time {ult['ts'][11:19]})")
        for p in mod_alertas.ORDEN:
            u = mod_alertas.UMBRALES[p]
            tendencia = ""
            if len(recientes) > 1 and ini[p] != ult[p]:
                tendencia = (f"  [trend: {mod_alertas.formatear(p, ini[p])} -> "
                             f"{mod_alertas.formatear(p, ult[p])} over the last {len(recientes)} samples]")
            lineas.append(f"- {u['nombre']}: {mod_alertas.formatear(p, ult[p])}{tendencia}")
    else:
        lineas.append("\n## Vital signs: no data yet")

    lineas.append("\n## Active alerts")
    if alertas_activas:
        for al in alertas_activas:
            lineas.append(f"- [{al['severidad'].upper()}] {al['mensaje']}")
    else:
        lineas.append("- None: all signs within the normal range.")

    if notas:
        lineas.append("\n## Latest clinical notes")
        for n in notas[:3]:
            lineas.append(f"- {n['ts'][:16]} ({n['autor']}): {n['nota']}")
    return "\n".join(lineas)


def construir_system(contexto: str) -> str:
    return (f"{SYSTEM_BASE}\n\n# REFERENCE PROTOCOLS\n{protocolos.texto_referencia()}"
            f"\n\n# CURRENT CONTEXT\n{contexto}")


def _mensajes_validos(historial: list[dict], maximo: int = 12) -> list[dict]:
    """Últimos mensajes, empezando por uno del usuario (requisito de la API)."""
    msgs = [{"role": m["role"], "content": m["content"]} for m in historial[-maximo:]]
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    return msgs


def _stream_texto(texto: str, pausa: float = float(os.environ.get("ASTRO_PAUSA", "0.01"))) -> Iterator[str]:
    for token in re.findall(r"\S+\s*", texto):
        yield token
        time.sleep(pausa)


# --------------------------------------------------------------------------- modo offline
def respuesta_offline(pregunta: str, astronauta: dict, alertas_activas: list[dict]) -> str:
    q = protocolos.normalizar(pregunta)
    partes: list[str] = []

    quiere_medir = bool(re.search(r"\b(measure|measuring|take|taking|check|medir|mido|medicion|mediciones|tomar|tomo|mide|se mide)\b", q))
    pide_guia = any(p in q for p in ("emergency", "guide", "what do i do", "what should i do", "help", "urgent", "step by step", "current situation", "current",
                                      "emergencia", "guia", "guiame", "que hago", "ayuda",
                                      "urgente", "paso a paso", "situacion actual", "actual"))

    if alertas_activas:
        resumen = "; ".join(a["mensaje"] for a in alertas_activas)
        partes.append(f" **Current status of {astronauta['nombre']}:** {resumen}.\n"
                      "**First: alert the crew.**")

    if protocolos.detectar(q, {"med": protocolos.MEDICAMENTOS}):
        partes.append(f"**Record of {astronauta['nombre']}** · Allergies: {astronauta['alergias'] or 'not recorded'} · "
                      f"Current medications: {astronauta['medicamentos'] or 'none'} · "
                      f"History: {astronauta['condiciones'] or 'none'}")
        partes.append(protocolos.medicamentos_md())
    elif quiere_medir:
        claves = protocolos.detectar(q, protocolos.MEDICIONES)
        if claves:
            partes.extend(protocolos.medicion_md(c) for c in claves)
        else:
            opciones = ", ".join(m["titulo"].replace("How to measure ", "") for m in protocolos.MEDICIONES.values())
            partes.append(f"I can guide you to measure: {opciones}. Which one do you need?")
    else:
        claves = protocolos.detectar(q, protocolos.EMERGENCIAS)
        if pide_guia and alertas_activas:
            claves = protocolos.protocolos_para_alertas(alertas_activas)
        elif not claves and alertas_activas:
            claves = protocolos.protocolos_para_alertas(alertas_activas)
        if claves:
            partes.extend(protocolos.emergencia_md(c) for c in claves)
        elif not alertas_activas:
            partes.append(
                "There are no active alerts and I did not understand the request. I can help with:\n"
                "- How to measure blood pressure, SpO₂, pulse, temperature or breathing\n"
                "- Guides for hypoxia, tachycardia/bradycardia, hypertension/hypotension, fever or hypothermia\n"
                "- Safe use of medications from the kit"
            )

    partes.append("_Offline mode: answer based on the app's local protocols. "
                  "Confirm with the medical officer / flight surgeon._")
    return "\n\n".join(partes)


# --------------------------------------------------------------------------- función principal
def responder_stream(historial: list[dict], astronauta: dict, recientes: list[dict],
                     alertas_activas: list[dict], notas: list[dict] | None = None,
                     api_key: str | None = None) -> Iterator[str]:
    """Genera la respuesta del asistente en trozos de texto."""
    pregunta = historial[-1]["content"] if historial else ""
    clave = (api_key or os.environ.get("ANTHROPIC_API_KEY") or "").strip()

    # 1) Médico virtual (Gemini + conocimiento). Si falla, se cae al camino anterior.
    try:
        import medico
        if medico.hay_llave():
            contexto = construir_contexto(astronauta, recientes, alertas_activas, notas)
            try:
                from medico.capa import contexto_extra
                contexto += contexto_extra(astronauta["id"])
            except Exception:
                pass
            yield from medico.responder_stream(_mensajes_validos(historial), contexto)
            return
    except Exception as e:
        yield f"I could not reach Aéter ({type(e).__name__}). Using the backup.\n\n"

    if clave:
        try:
            import anthropic

            cliente = anthropic.Anthropic(api_key=clave)
            system = construir_system(construir_contexto(astronauta, recientes, alertas_activas, notas))
            with cliente.messages.stream(
                model=MODELO,
                max_tokens=1000,
                system=system,
                messages=_mensajes_validos(historial),
            ) as stream:
                for texto in stream.text_stream:
                    yield texto
            return
        except Exception as e:  # sin internet, key inválida, límite de uso...
            yield f"I could not reach the AI ({type(e).__name__}). Answering in offline mode.\n\n"

    yield from _stream_texto(respuesta_offline(pregunta, astronauta, alertas_activas))
