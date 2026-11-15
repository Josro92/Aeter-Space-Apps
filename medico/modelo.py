"""Capa de modelos: lee config/modelos.yaml y habla con el proveedor activo."""
import os
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def cargar_config() -> dict:
    return yaml.safe_load((RAIZ / "config" / "modelos.yaml").read_text(encoding="utf-8"))


def _llave(nombre_var: str) -> str:
    """Busca la llave en: variable de entorno -> st.secrets -> .env. Nunca la imprime."""
    v = os.environ.get(nombre_var, "").strip()
    if v:
        return v
    try:
        import streamlit as st
        v = str(st.secrets.get(nombre_var, "")).strip()
        if v:
            return v
    except Exception:
        pass
    try:
        from dotenv import load_dotenv
        load_dotenv(RAIZ / ".env")
        return os.environ.get(nombre_var, "").strip()
    except Exception:
        return ""


def proveedor_activo() -> tuple[str, dict, str]:
    cfg = cargar_config()
    nombre = cfg["proveedor_activo"]
    prov = cfg["proveedores"][nombre]
    return nombre, prov, _llave(prov["variable_llave"])


def hay_llave() -> bool:
    return bool(proveedor_activo()[2])


def stream(mensajes: list[dict], sistema: str):
    """Genera texto en trozos. mensajes: [{'role': 'user'|'assistant', 'content': str}]."""
    nombre, prov, llave = proveedor_activo()
    if not llave:
        raise RuntimeError("Falta la llave del proveedor")
    if nombre == "gemini":
        from google import genai
        from google.genai import types
        cliente = genai.Client(api_key=llave)
        contenido = [types.Content(role="user" if m["role"] == "user" else "model",
                                   parts=[types.Part(text=m["content"])]) for m in mensajes]
        def _conf(rapido: bool):
            extra = {}
            if rapido and hasattr(types, "ThinkingConfig"):
                extra["thinking_config"] = types.ThinkingConfig(thinking_budget=0)  # responde sin «pensar» largo
            return types.GenerateContentConfig(system_instruction=sistema,
                                               max_output_tokens=prov["max_tokens"], **extra)
        enviado = False
        for rapido in (True, False):                      # si el modelo no admite el modo rápido, reintenta normal
            try:
                for trozo in cliente.models.generate_content_stream(model=prov["modelo"],
                                                                    contents=contenido, config=_conf(rapido)):
                    if trozo.text:
                        enviado = True
                        yield trozo.text
                return
            except Exception:
                if enviado or not rapido:
                    raise
    elif nombre == "claude":
        import anthropic
        cliente = anthropic.Anthropic(api_key=llave)
        with cliente.messages.stream(model=prov["modelo"], max_tokens=prov["max_tokens"],
                                     system=sistema, messages=mensajes) as s:
            yield from s.text_stream
    else:
        raise RuntimeError(f"Proveedor desconocido: {nombre}")
