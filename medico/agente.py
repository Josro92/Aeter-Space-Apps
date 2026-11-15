"""Arma el prompt del médico virtual (reglas + ficha + estado + inventario + conocimiento) y responde."""
from pathlib import Path

from . import conocimiento, modelo

RAIZ = Path(__file__).resolve().parent
hay_llave = modelo.hay_llave


def _reglas() -> str:
    return (RAIZ / "prompt.md").read_text(encoding="utf-8")  # se lee en cada respuesta: editable sin reiniciar


def _umbrales() -> str:
    try:
        import alertas
        return "\n".join(f"- {k}: advertencia {v['adv']}, crítico {v['crit']}" for k, v in alertas.UMBRALES.items())
    except Exception:
        return "(no disponibles)"


def construir_sistema(contexto_pagina: str, pregunta: str) -> tuple[str, list[dict]]:
    frags = conocimiento.buscar(pregunta)
    bloque = "\n\n".join(f"[{f['id']}] ({f['archivo']})\n{f['texto']}" for f in frags) or "(nothing related found)"
    sistema = (f"{_reglas()}\n\n# FICHA Y ESTADO ACTUAL (en vivo, de la pantalla)\n{contexto_pagina}\n\n"
               f"# UMBRALES DE EJEMPLO SIN VALIDAR (de la app)\n{_umbrales()}\n\n"
               f"# INVENTARIO DE MEDICAMENTOS A BORDO\n{conocimiento.inventario_compacto()}\n\n"
               f"# CONOCIMIENTO RELACIONADO CON LA PREGUNTA\n{bloque}")
    return sistema, frags


def responder_stream(mensajes: list[dict], contexto_pagina: str):
    sistema, _ = construir_sistema(contexto_pagina, mensajes[-1]["content"])
    yield from modelo.stream(mensajes, sistema)
