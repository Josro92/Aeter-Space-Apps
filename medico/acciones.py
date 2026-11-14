"""Acciones controladas: el médico solo puede pedir lo que está en esta lista cerrada.

Todo es de solo lectura, salvo proponer_nota, que NO guarda nada hasta que
la persona pulsa «Guardar» en pantalla. Cada acción se valida y se registra.
"""
import json
import re
from datetime import datetime
from pathlib import Path

MAX_ACCIONES = 3
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


def mostrar(acciones: list[dict], astro_id: int, yo_nombre: str, clave: str) -> None:
    """Dibuja las acciones validadas dentro del mensaje del asistente."""
    import streamlit as st
    import db
    import protocolos
    from . import conocimiento

    for i, a in enumerate(acciones):
        k, arg = a["accion"], a["arg"]
        if k == "ver_signos":
            with st.expander("📈 Últimas mediciones", expanded=True):
                filas = db.ultimas_mediciones(astro_id, 6)
                if filas:
                    st.table([{"hora": f["ts"][11:19], "FC": f["fc"], "PAS": f["pas"], "PAD": f["pad"],
                               "SpO₂": f["spo2"], "Temp": f["temp"], "FR": f["fr"]} for f in reversed(filas)])
                else:
                    st.caption("Sin mediciones todavía.")
        elif k == "ver_notas":
            with st.expander("📝 Últimas notas clínicas", expanded=True):
                notas = db.listar_notas(astro_id, 5)
                for n in notas:
                    st.markdown(f"**{n['ts'][:16]}** · {n['autor']}: {n['nota']}")
                if not notas:
                    st.caption("No hay notas registradas.")
        elif k == "ver_procedimiento":
            tipo = _claves_validas()[arg]
            md = protocolos.emergencia_md(arg) if tipo == "emergencia" else protocolos.medicion_md(arg)
            with st.expander(f"📋 Procedimiento: {arg}", expanded=True):
                st.markdown(md)
        elif k == "ver_medicamento":
            frag = next((f for f in conocimiento.fragmentos() if f["id"] == arg), None)
            with st.expander(f"💊 {arg}", expanded=True):
                st.markdown(frag["texto"].replace("## ", "### ", 1) if frag else "No encontrado.")
        elif k == "proponer_nota":
            estado = f"nota_{clave}_{i}"
            with st.container(border=True):
                st.markdown(f"📝 **Nota propuesta por el médico virtual:**\n\n> {arg}")
                actual = st.session_state.get(estado)
                if actual == "guardada":
                    st.success("Guardada en las notas clínicas.")
                elif actual == "descartada":
                    st.caption("Descartada.")
                else:
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Guardar", key=f"g_{estado}"):
                        db.insertar_nota(astro_id, f"Médico virtual (confirmado por {yo_nombre})", arg)
                        st.session_state[estado] = "guardada"
                        _registrar({"evento": "nota_guardada", "por": yo_nombre})
                        st.rerun()
                    if c2.button("✖ Descartar", key=f"d_{estado}"):
                        st.session_state[estado] = "descartada"
                        st.rerun()
