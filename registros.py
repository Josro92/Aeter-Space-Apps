"""Registros de Aéter: bitácora, conversaciones, protocolos, recordatorios y emergencias.

Una sola tabla alimenta las pestañas Bitácora e Historial. Cada registro tiene:
  tipo      Bitácora | Conversación | Protocolo | Recordatorio | Emergencia
  etiqueta  una palabra que lo describe (en la bitácora la elige la IA)
  resumen   menos de una línea
  texto     el contenido completo
  ts        fecha y hora de Costa Rica
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import db

CR = ZoneInfo("America/Costa_Rica")
MESES = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
MESES_LARGOS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
                "octubre", "noviembre", "diciembre")

TIPOS = ("Conversación", "Protocolo", "Emergencia", "Recordatorio", "Bitácora")

# Palabras que la IA puede usar al clasificar una entrada de bitácora.
PALABRAS_BITACORA = ("Síntoma", "Dolor", "Ánimo", "Sueño", "Ejercicio", "Alimentación",
                     "Medicación", "Hidratación", "Equipo", "Tarea", "Nota")


def ahora_cr() -> datetime:
    return datetime.now(CR)


def _tabla() -> None:
    with db.conexion() as con:
        con.execute("CREATE TABLE IF NOT EXISTS registros ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, astronauta_id INTEGER NOT NULL,"
                    " tipo TEXT NOT NULL, etiqueta TEXT NOT NULL, resumen TEXT NOT NULL,"
                    " texto TEXT NOT NULL, ts TEXT NOT NULL)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_reg_astro ON registros (astronauta_id, id)")


def recortar(texto: str, n: int = 70) -> str:
    t = re.sub(r"\s+", " ", (texto or "").strip())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def agregar(astro_id: int, tipo: str, resumen: str, texto: str = "", etiqueta: str | None = None) -> int:
    _tabla()
    with db.conexion() as con:
        cur = con.execute(
            "INSERT INTO registros (astronauta_id, tipo, etiqueta, resumen, texto, ts) VALUES (?,?,?,?,?,?)",
            (astro_id, tipo, etiqueta or tipo, recortar(resumen, 90), texto or resumen,
             ahora_cr().replace(tzinfo=None).isoformat(timespec="seconds")))
        return cur.lastrowid


def listar(astro_id: int, tipos: tuple[str, ...] | None = None, limite: int = 120) -> list[dict]:
    """Registros del astronauta, del más nuevo al más antiguo. Solo de esa persona."""
    _tabla()
    sql, params = "SELECT * FROM registros WHERE astronauta_id=?", [astro_id]
    if tipos:
        sql += " AND tipo IN (%s)" % ",".join("?" * len(tipos))
        params += list(tipos)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limite)
    with db.conexion() as con:
        return [dict(f) for f in con.execute(sql, params)]


def historial(astro_id: int, limite: int = 150) -> list[dict]:
    """Todo lo que Aéter registró, más las emergencias (SOS y alertas críticas) de ese astronauta."""
    filas = listar(astro_id, limite=limite)
    for e in db.listar_eventos(astro_id, limite=40):
        if e["severidad"] != "critica":
            continue
        filas.append({"id": f"e{e['id']}", "tipo": "Emergencia", "etiqueta": "Emergencia",
                      "resumen": recortar(e["mensaje"].replace("SOS de", "SOS:"), 90),
                      "texto": e["mensaje"] + (f"\nReconocida por {e['reconocida_por']}." if e["reconocida"] else
                                               "\nAún sin reconocer."),
                      "ts": e["ts"]})
    filas.sort(key=lambda r: r["ts"], reverse=True)
    for r in filas:  # en el historial cada fila lleva su tipo (Conversación, Protocolo, Bitácora...)
        r["etiqueta"] = r["tipo"]
    return filas[:limite]


def fecha_corta(ts: str) -> str:
    d = datetime.fromisoformat(ts)
    return f"{d.day} {MESES[d.month - 1]} {d.year} · {d:%H:%M}"


def fecha_larga(ts: str) -> str:
    d = datetime.fromisoformat(ts)
    return f"{d.day} de {MESES_LARGOS[d.month - 1]} de {d.year}, {d:%H:%M}"


# --------------------------------------------------------------------------- clasificación
def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


_REGLAS = (
    ("Dolor", r"dolor|duele|molest|punzada|calambre"),
    ("Síntoma", r"mareo|nausea|vomit|fiebre|tos|falta de aire|cansanc|palpita|sintoma|dolor de cabeza|cefalea"),
    ("Sueño", r"dorm|sueno|desvel|insomn|descans"),
    ("Ánimo", r"triste|ansied|estres|feliz|animo|solo|sola|extrano|nervios|preocup|contento|content"),
    ("Ejercicio", r"ejercicio|entren|correr|cinta|bicicleta|pesas|fuerza"),
    ("Alimentación", r"comi|comida|desayun|almuerz|cena|apetito|hambre"),
    ("Hidratación", r"agua|hidrat|sed\b"),
    ("Medicación", r"pastilla|medicament|ibuprofeno|dosis|tomé|tome|losartan"),
    ("Equipo", r"equipo|sensor|panel|modulo|falla|bateria|oxigeno del|cabina"),
    ("Tarea", r"tarea|experimento|mision|reparac|mantenimiento|revision|eva\b"),
)


def clasificar_simple(texto: str) -> tuple[str, str]:
    n = _norm(texto)
    for etiqueta, patron in _REGLAS:
        if re.search(patron, n):
            return etiqueta, recortar(texto, 70)
    return "Nota", recortar(texto, 70)


def clasificar(texto: str) -> tuple[str, str]:
    """(palabra, resumen) de una entrada de bitácora. Usa la IA si hay llave; si no, reglas simples."""
    try:
        from medico import modelo
        if modelo.hay_llave():
            sistema = ("Clasifica una anotación de la bitácora personal de un astronauta. Responde SOLO con una línea: "
                       "PALABRA | resumen. PALABRA es UNA sola palabra, preferiblemente una de: "
                       + ", ".join(PALABRAS_BITACORA) + ". El resumen tiene menos de 70 caracteres, sin comillas, "
                       "en español, y no añade datos que no estén en la anotación. No des consejos.")
            salida = "".join(modelo.stream([{"role": "user", "content": texto[:1500]}], sistema)).strip()
            primera = salida.splitlines()[0] if salida else ""
            palabra, _, resumen = primera.partition("|")
            palabra = re.sub(r"[^A-Za-zÁÉÍÓÚáéíóúÑñ]", "", palabra).strip().capitalize()
            if 2 <= len(palabra) <= 16 and resumen.strip():
                return palabra, recortar(resumen.strip(), 70)
    except Exception:
        pass
    return clasificar_simple(texto)


def agregar_bitacora(astro_id: int, texto: str) -> int:
    palabra, resumen = clasificar(texto)
    return agregar(astro_id, "Bitácora", resumen, texto.strip(), etiqueta=palabra)
