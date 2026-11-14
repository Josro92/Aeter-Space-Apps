"""Búsqueda por palabras clave en knowledge/**/*.md (cualquier .md nuevo se incluye solo)."""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "knowledge"

SINONIMOS = {
    "sangrado": "hemorragia herida grave", "sangra": "hemorragia herida grave", "sangrando": "hemorragia herida grave", "sangre": "hemorragia herida grave",
    "infarto": "dolor agudo pecho", "desmayo": "perdida conciencia neurologica", "convulsiones": "convulsion", "ahogo": "dificultad respiratoria hipoxia",
    "incendio": "incendio humo cabina", "humo": "incendio humo cabina", "quemado": "quemaduras", "vomito": "nauseas vomito mareo",
    "pulso": "frecuencia cardiaca", "latidos": "frecuencia cardiaca", "taquicardia": "frecuencia cardiaca",
    "bradicardia": "frecuencia cardiaca", "presion": "presion arterial", "tension": "presion arterial",
    "oxigeno": "saturacion spo2", "respirar": "frecuencia respiratoria", "fiebre": "temperatura corporal",
    "azucar": "glucosa", "dormir": "sueno", "peso": "masa corporal", "radiacion": "dosis radiacion",
    "alergia": "antialergico antihistaminico",
    "basal": "basales valores reposo", "basales": "basal valores reposo", "amoxicilina": "penicilina antibiotico",
    "escoliosis": "columna espalda", "espalda": "columna escoliosis dolor", "infeccion": "antibiotico", "dolor": "analgesico",
}
VACIAS = set("de la el los las un una y o que en a por para con del al se me mi es lo su si no como puedo tengo".split())


def norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def tokens(t: str) -> set[str]:
    return {w[:6] for w in re.findall(r"[a-z0-9]{3,}", norm(t)) if w not in VACIAS}


OCULTAR = re.compile(r"^- (Fecha de revisión|Estado del registro):")
MARCA_PENDIENTE = "[REVISAR]"


def _limpiar(texto: str) -> tuple[str, list[str]]:
    """Quita lo que el médico no debe ver ([REVISAR], fechas y estados internos).
    Devuelve el texto limpio y los campos que estaban pendientes (para el informe del equipo)."""
    limpio, pendientes = [], []
    for linea in texto.splitlines():
        if OCULTAR.match(linea):
            continue
        m = re.match(r"^- ([^:]+): \[REVISAR\]\s*$", linea)
        if m:
            pendientes.append(m.group(1))
            continue
        limpio.append(linea)
    return "\n".join(limpio), pendientes


@lru_cache(maxsize=1)
def fragmentos() -> list[dict]:
    """Cada '## ' es un fragmento; las filas de tablas '| XXX123 |' son fragmentos propios
    (con el nombre de cada columna). Los [REVISAR] no llegan al médico."""
    res = []
    for ruta in sorted(CARPETA.rglob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        for bloque in re.split(r"(?m)^## ", texto)[1:]:
            titulo, _, cuerpo = bloque.partition("\n")
            lineas = cuerpo.splitlines()
            encabezado, filas = None, []
            for i, l in enumerate(lineas):
                if l.startswith("|") and i + 1 < len(lineas) and re.match(r"\|\s*:?-{3}", lineas[i + 1]):
                    encabezado = [c.strip() for c in l.strip().strip("|").split("|")]
                elif re.match(r"\|\s*[A-Z]{2,4}\d{2,}", l):
                    filas.append((encabezado, l))
            if filas:
                for enc, f in filas:
                    celdas = [c.strip() for c in f.strip().strip("|").split("|")]
                    nombres = enc if enc and len(enc) == len(celdas) else [f"campo{i + 1}" for i in range(len(celdas))]
                    pend = [n for n, c in zip(nombres, celdas) if c == MARCA_PENDIENTE]
                    campos = [f"- {n}: {c.replace('<br>', '; ')}" for n, c in zip(nombres, celdas)
                              if c and c != MARCA_PENDIENTE and n not in ("fecha_revision", "estado")]
                    nombre = celdas[1] if len(celdas) > 1 and celdas[1] != MARCA_PENDIENTE else ""
                    res.append({"id": celdas[0], "titulo": nombre or celdas[0],
                                "texto": f"## {celdas[0]}" + (f" — {nombre}" if nombre else "") + "\n" + "\n".join(campos),
                                "archivo": ruta.name, "pendientes": pend})
            else:
                m = re.match(r"([A-Z]{2,4}\d{2,})", titulo)
                limpio, pend = _limpiar(cuerpo.strip())
                limpio = limpio.replace(MARCA_PENDIENTE, "")
                res.append({"id": m.group(1) if m else titulo[:40], "titulo": titulo.strip(),
                            "texto": f"## {titulo}\n{limpio}", "archivo": ruta.name, "pendientes": pend})
    return res


def inventario_compacto() -> str:
    """Una línea por medicamento: así el médico siempre sabe qué hay a bordo."""
    lineas = []
    for f in fragmentos():
        if f["id"].startswith("MED"):
            g = lambda k: (re.search(rf"- {k}: (.*)", f["texto"]) or [None, "?"])[1].strip()
            lineas.append(f"{f['id']} {f['titulo'].split('—')[-1].strip()} · {g('Grupo terapéutico')} · "
                          f"vía {g('Vía de administración')} · supervisión: {g('Requiere supervisión médica')}")
    return "\n".join(lineas) if lineas else "(sin inventario cargado)"


def buscar(consulta: str, k: int = 4, max_chars: int = 2500) -> list[dict]:
    q = tokens(consulta)
    for w in re.findall(r"[a-z0-9]{3,}", norm(consulta)):   # sinónimos sobre la palabra completa
        if w in SINONIMOS:
            q |= tokens(SINONIMOS[w])
    puntuados = []
    for f in fragmentos():
        if f["id"].startswith("Hoja:") and any(x in f["id"] for x in ("LISTAS", "DICCIONARIO")):
            continue  # hojas de apoyo muy grandes: meten ruido
        t = tokens(f["titulo"])
        cuerpo = tokens(f["texto"])
        p = 3 * len(q & t) + len(q & cuerpo)
        if p >= 2:
            puntuados.append((p, f))
    puntuados.sort(key=lambda x: -x[0])
    return [dict(f, texto=f["texto"][:max_chars]) for _, f in puntuados[:k]]
