"""Acciones controladas: el médico solo puede pedir lo que está en esta lista cerrada.

Todo es de solo lectura, salvo proponer_nota, que NO guarda nada hasta que
la persona pulsa «Guardar» en pantalla. Cada acción se valida y se registra.
"""
import json
import re
import time
from datetime import datetime
from pathlib import Path

MAX_ACCIONES = 3
CONFIRMAR_SEG = 120          # tiempo para confirmar SOS / normalizar
PENDIENTES = ("sos", "normalizar_emergencia")   # piden confirmación explícita
# sección -> pestañas que hay que pulsar (en orden)
SECCIONES = {"estado": ["Status"], "alertas": ["Status"], "monitoreo": ["Vitals"], "signos": ["Vitals"],
             "asistente": ["Aéter"], "bitacora": ["Journal"], "historial": ["History"]}
RAIZ = Path(__file__).resolve().parent.parent
LOG = RAIZ / "logs" / "acciones.jsonl"


def _registrar(evento: dict) -> None:
    try:
        LOG.parent.mkdir(exist_ok=True)
        evento["ts"] = datetime.now().isoformat(timespec="seconds")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    except Exception:
        pass  # el registro nunca debe romper la app


def _norm(t: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFD", t.lower().strip())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


VISUALES = ("ver_signos", "ver_notas", "ver_procedimiento", "ver_medicamento", "ver_fuente", "proponer_nota",
            "sos", "normalizar_emergencia")


def intencion_navegacion(texto: str) -> str | None:
    """Si la persona pide ir a una pantalla («muéstrame las alertas»), devuelve la sección."""
    n = _norm(texto)
    if not re.search(r"(muestr|ensen|\bver\b|\bveo\b|abr[ae]\b|llev|\bir\b|ve a |vamos|pasa a|cambia a|quiero ver|ponme|\bshow\b|\bopen\b|\bgo to\b|take me|\bswitch\b|i want to see|let me see|bring up)", n):
        return None
    if re.search(r"alerta|alarma|recordatorio|alert|alarm|reminder", n):
        return "alertas"
    if re.search(r"bitacora|diario|\bnotas?\b|anotacion|journal|diary|\bnotes?\b", n):
        return "bitacora"
    if re.search(r"historial|registros?|expediente|history|records?", n):
        return "historial"
    if re.search(r"monitor|grafic|signos|vitales|en vivo|tiempo real|vitals|vital signs|charts?|graphs?|live", n):
        return "monitoreo"
    if re.search(r"estado|reloj|pantalla principal|inicio|status|clock|home screen|main screen", n):
        return "estado"
    if re.search(r"asistente|\bchat\b|conversacion|aeter|assistant|conversation", n):
        return "asistente"
    return None


def _claves_validas() -> dict:
    import protocolos
    return {**{k: "emergencia" for k in protocolos.EMERGENCIAS},
            **{k: "medicion" for k in protocolos.MEDICIONES}}


def validar(nombre: str, arg: str) -> dict | None:
    """Devuelve la acción limpia o None si no está permitida."""
    nombre, arg = nombre.strip().lower(), arg.strip()
    if nombre in ("ver_signos", "ver_notas") and not arg:
        return {"accion": nombre, "arg": ""}
    if nombre == "ver_procedimiento" and arg.lower() in _claves_validas():
        return {"accion": nombre, "arg": arg.lower()}
    if nombre == "ver_medicamento" and re.fullmatch(r"MED\d{3}", arg.upper()):
        from . import conocimiento
        if any(f["id"] == arg.upper() for f in conocimiento.fragmentos()):
            return {"accion": nombre, "arg": arg.upper()}
    if nombre == "proponer_nota" and 3 <= len(arg) <= 300:
        return {"accion": nombre, "arg": arg}
    if nombre == "ir_a" and arg.lower() in SECCIONES:
        return {"accion": nombre, "arg": arg.lower()}
    if nombre == "pitido" and arg.lower() in ("activar", "desactivar"):
        return {"accion": nombre, "arg": arg.lower()}
    if nombre == "ver_fuente" and re.fullmatch(r"(MED|IND|SRC)\d{3}", arg.upper()):
        return {"accion": nombre, "arg": arg.upper()}
    if nombre == "recordar":
        m = re.fullmatch(r"(\d{1,2}):(\d{2})\|(.{3,150})", arg)
        if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
            return {"accion": nombre, "arg": f"{int(m.group(1)):02d}:{m.group(2)}|{m.group(3).strip()}"}
    if nombre == "cambiar_astronauta" and 2 <= len(arg) <= 40:
        import db
        q = _norm(arg)
        for a in db.listar_astronautas():
            n = _norm(a["nombre"])
            if q == n or q in n.split() or n.split()[0] == q.split()[0]:
                return {"accion": nombre, "arg": a["nombre"], "id": a["id"]}
        return None
    if nombre == "sos" and 3 <= len(arg) <= 200:
        return {"accion": nombre, "arg": arg, "ts": time.time()}
    if nombre == "normalizar_emergencia" and not arg:
        return {"accion": nombre, "arg": "", "ts": time.time()}
    return None


class Filtro:
    """Quita las etiquetas [[...]] del texto que se muestra y las junta en self.acciones."""

    def __init__(self):
        self.acciones: list[dict] = []

    def _tag(self, tag: str) -> None:
        nombre, _, arg = tag.partition(":")
        ok = validar(nombre, arg) if len(self.acciones) < MAX_ACCIONES else None
        _registrar({"evento": "aceptada" if ok else "rechazada", "tag": tag[:120]})
        if ok:
            self.acciones.append(ok)

    def filtrar(self, trozos):
        buf = ""
        for t in trozos:
            buf += t
            while True:
                if "[[" in buf:
                    antes, _, resto = buf.partition("[[")
                    if antes:
                        yield antes
                    if "]]" in resto:
                        tag, _, buf = resto.partition("]]")
                        self._tag(tag)
                        continue
                    buf = "[[" + resto
                    break
                if buf.endswith("["):
                    if buf[:-1]:
                        yield buf[:-1]
                    buf = "["
                else:
                    if buf:
                        yield buf
                    buf = ""
                break
        if buf and not buf.startswith("["):
            yield buf


def ejecutar_pendiente(a: dict, astro_id: int, yo_nombre: str, servicio) -> str:
    """Ejecuta SOS o normalizar. Solo se llama tras confirmación (botón o 'confirmo')."""
    import db
    nombre = db.obtener_astronauta(astro_id)["nombre"]
    if time.time() - a.get("ts", 0) > CONFIRMAR_SEG:
        return "Too much time has passed: please ask me again."
    if a["accion"] == "sos":
        db.insertar_evento(astro_id, "critica", "sos", 1, f"SOS from {nombre}: {a['arg']}")
        _registrar({"evento": "sos_enviado", "por": yo_nombre, "astro": astro_id})
        return "SOS sent to the whole crew."
    if a["accion"] == "normalizar_emergencia":
        servicio.set_escenario(astro_id, "normal")
        db.reconocer_eventos(yo_nombre, astro_id)
        _registrar({"evento": "emergencia_normalizada", "por": yo_nombre, "astro": astro_id})
        return "Emergency stopped: normal scenario and alerts acknowledged."
    return "Action not recognized."


def aplicar_inmediatas(acciones: list[dict], astro_id: int, yo_nombre: str) -> None:
    """Acciones seguras que se ejecutan al llegar la respuesta (una sola vez)."""
    import streamlit as st
    from . import recordatorios
    # Si hay algo que ver en el chat y la persona no pidió otra pantalla, se la lleva al asistente.
    if (any(a["accion"] in VISUALES for a in acciones)
            and not any(a["accion"] == "ir_a" for a in acciones)
            and not st.session_state.get("nav_intent")):
        st.session_state["nav_cmd"] = {"id": f"{time.time()}", "pasos": SECCIONES["asistente"]}
    for a in acciones:
        k, arg = a["accion"], a["arg"]
        if k == "ir_a":
            st.session_state["nav_cmd"] = {"id": f"{time.time()}", "pasos": SECCIONES[arg]}
        elif k == "pitido":
            st.session_state["sirena"] = (arg == "activar")
        elif k == "cambiar_astronauta":
            st.session_state["astro_cambiar"] = a["id"]
        elif k == "recordar":
            hora, _, texto = arg.partition("|")
            try:
                recordatorios.crear(astro_id, hora, texto)
                _registrar({"evento": "recordatorio", "hora": hora})
            except Exception:
                pass
        if k in ("ir_a", "pitido", "recordar", "cambiar_astronauta"):
            _registrar({"evento": "ejecutada", "accion": k, "arg": arg[:80], "por": yo_nombre})


def pendiente_de(acciones: list[dict]) -> dict | None:
    return next((a for a in acciones if a["accion"] in PENDIENTES), None)


def mostrar(acciones: list[dict], astro_id: int, yo_nombre: str, clave: str, servicio=None) -> None:
    """Dibuja las acciones validadas dentro del mensaje del asistente."""
    import streamlit as st
    import db
    import protocolos
    from . import conocimiento

    for i, a in enumerate(acciones):
        k, arg = a["accion"], a["arg"]
        if k == "ver_signos":
            with st.expander("Latest measurements", expanded=True):
                filas = db.ultimas_mediciones(astro_id, 6)
                if filas:
                    st.table([{"time": f["ts"][11:19], "HR": f["fc"], "SBP": f["pas"], "DBP": f["pad"],
                               "SpO₂": f["spo2"], "Temp": f["temp"], "RR": f["fr"]} for f in reversed(filas)])
                else:
                    st.caption("No measurements yet.")
        elif k == "ver_notas":
            with st.expander("Latest clinical notes", expanded=True):
                notas = db.listar_notas(astro_id, 5)
                for n in notas:
                    st.markdown(f"**{n['ts'][:16]}** · {n['autor']}: {n['nota']}")
                if not notas:
                    st.caption("No notes recorded.")
        elif k == "ver_procedimiento":
            tipo = _claves_validas()[arg]
            md = protocolos.emergencia_md(arg) if tipo == "emergencia" else protocolos.medicion_md(arg)
            with st.expander(f"Procedure: {arg}", expanded=True):
                st.markdown(md)
        elif k == "ver_medicamento":
            frag = next((f for f in conocimiento.fragmentos() if f["id"] == arg), None)
            with st.expander(f"{arg}", expanded=True):
                st.markdown(frag["texto"].replace("## ", "### ", 1) if frag else "Not found.")
        elif k == "ir_a":
            st.caption(f"Opening: {SECCIONES[arg][-1]}")
        elif k == "cambiar_astronauta":
            st.caption(f"Switching to astronaut: {arg}")
        elif k == "pitido":
            st.caption("Emergency beep " + ("on" if arg == "activar" else "off"))
        elif k == "recordar":
            hora, _, texto = arg.partition("|")
            st.caption(f"Reminder at {hora}: {texto}")
        elif k == "ver_fuente":
            frag = next((f for f in conocimiento.fragmentos() if f["id"] == arg), None)
            with st.expander(f"Source: {arg}", expanded=True):
                if not frag:
                    st.caption("Not found.")
                else:
                    st.markdown(frag["texto"].replace("## ", "### ", 1))
                    st.caption(f"File: {frag['archivo']}")
                    for src in sorted(set(re.findall(r"SRC\d{3}", frag["texto"])) - {arg}):
                        s = next((f for f in conocimiento.fragmentos() if f["id"] == src), None)
                        if s:
                            titulo = (re.search(r"- titulo: (.*)", s["texto"]) or [None, "(no title recorded)"])[1]
                            url = (re.search(r"https?://\S+", s["texto"]) or [None])[0]
                            st.markdown(f"**{src}** · {titulo}" + (f" · [open source]({url})" if url else ""))
                        else:
                            st.markdown(f"**{src}** · no source data recorded yet")
                    for url in re.findall(r"https?://\S+", frag["texto"]):
                        st.markdown(f"[Open original source]({url.rstrip('|)')})")
        elif k in PENDIENTES:
            estado = f"pend_{clave}_{i}"
            etiqueta = "SOS to the crew" if k == "sos" else "Stop the emergency state"
            with st.container(border=True):
                st.markdown(f"**{etiqueta}**" + (f"\n\n> {arg}" if arg else ""))
                actual = st.session_state.get(estado)
                vigente = time.time() - a.get("ts", 0) <= CONFIRMAR_SEG
                if actual:
                    st.caption(actual)
                elif not vigente:
                    st.caption("Expired without confirmation.")
                else:
                    st.info("To run it, say «confirm» or press the button.", icon="")
                    c1, c2 = st.columns(2)
                    if c1.button("Confirm", key=f"c_{estado}", type="primary"):
                        st.session_state[estado] = "" + ejecutar_pendiente(a, astro_id, yo_nombre, servicio)
                        st.session_state.pop("pendiente", None)
                        st.rerun()
                    if c2.button("Cancel", key=f"x_{estado}"):
                        st.session_state[estado] = "Cancelled."
                        st.session_state.pop("pendiente", None)
                        st.rerun()
        elif k == "proponer_nota":
            estado = f"nota_{clave}_{i}"
            with st.container(border=True):
                st.markdown(f"**Note proposed by Aéter:**\n\n> {arg}")
                actual = st.session_state.get(estado)
                if actual == "guardada":
                    st.success("Saved to the clinical notes.")
                elif actual == "descartada":
                    st.caption("Discarded.")
                else:
                    c1, c2 = st.columns(2)
                    if c1.button("Save", key=f"g_{estado}"):
                        db.insertar_nota(astro_id, f"Aéter (confirmed by {yo_nombre})", arg)
                        st.session_state[estado] = "guardada"
                        _registrar({"evento": "nota_guardada", "por": yo_nombre})
                        st.rerun()
                    if c2.button("Discard", key=f"d_{estado}"):
                        st.session_state[estado] = "descartada"
                        st.rerun()
