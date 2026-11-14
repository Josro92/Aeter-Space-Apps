"""Búsqueda por palabras clave en knowledge/**/*.md (cualquier .md nuevo se incluye solo)."""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "knowledge"

SINONIMOS = {
    "pulso": "frecuencia cardiaca", "latidos": "frecuencia cardiaca", "taquicardia": "frecuencia cardiaca",
    "bradicardia": "frecuencia cardiaca", "presion": "presion arterial", "tension": "presion arterial",
    "oxigeno": "saturacion spo2", "respirar": "frecuencia respiratoria", "fiebre": "temperatura corporal",
    "azucar": "glucosa", "dormir": "sueno", "peso": "masa corporal", "radiacion": "dosis radiacion",
    "alergia": "antialergico antihistaminico", "infeccion": "antibiotico", "dolor": "analgesico",
}
VACIAS = set("de la el los las un una y o que en a por para con del al se me mi es lo su si no como puedo tengo".split())


def norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def tokens(t: str) -> set[str]:
    return {w[:6] for w in re.findall(r"[a-z0-9]{3,}", norm(t)) if w not in VACIAS}


@lru_cache(maxsize=1)
def fragmentos() -> list[dict]:
    """Cada '## ' es un fragmento; las filas de tablas '| XXX123 |' son fragmentos propios."""
    res = []
    for ruta in sorted(CARPETA.rglob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        for bloque in re.split(r"(?m)^## ", texto)[1:]:
            titulo, _, cuerpo = bloque.partition("\n")
            filas = [l for l in cuerpo.splitlines() if re.match(r"\|\s*[A-Z]{2,4}\d{2,}", l)]
            if filas:
                for f in filas:
                    celdas = [c.strip() for c in f.strip("|").split("|")]
                    res.append({"id": celdas[0], "titulo": celdas[1] if len(celdas) > 1 else celdas[0],
                                "texto": f"{celdas[0]}: " + " | ".join(celdas[1:]), "archivo": ruta.name})
            else:
                m = re.match(r"([A-Z]{2,4}\d{2,})", titulo)
                res.append({"id": m.group(1) if m else titulo[:40], "titulo": titulo.strip(),
                            "texto": f"## {titulo}\n{cuerpo.strip()}", "archivo": ruta.name})
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


def buscar(consulta: str, k: int = 4, max_chars: int = 1400) -> list[dict]:
    q = tokens(consulta)
    for w in list(q):
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
