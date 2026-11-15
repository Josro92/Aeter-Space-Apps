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
MESES = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MESES_LARGOS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
                "October", "November", "December")

TIPOS = ("Conversation", "Protocol", "Emergency", "Reminder", "Journal")
# Valores antiguos (español) -> inglés, para bases de datos que ya existían.
_ANTIGUOS = {"Conversación": "Conversation", "Protocolo": "Protocol", "Emergencia": "Emergency",
             "Recordatorio": "Reminder", "Bitácora": "Journal", "Síntoma": "Symptom", "Dolor": "Pain", "Ánimo": "Mood",
             "Sueño": "Sleep", "Ejercicio": "Exercise", "Alimentación": "Food", "Medicación": "Medication",
             "Hidratación": "Hydration", "Equipo": "Equipment", "Tarea": "Task", "Nota": "Note"}

# Palabras que la IA puede usar al clasificar una entrada de bitácora.
PALABRAS_BITACORA = ("Symptom", "Pain", "Mood", "Sleep", "Exercise", "Food",
                     "Medication", "Hydration", "Equipment", "Task", "Note")


def ahora_cr() -> datetime:
    return datetime.now(CR)


def _tabla() -> None:
    with db.conexion() as con:
        con.execute("CREATE TABLE IF NOT EXISTS registros ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, astronauta_id INTEGER NOT NULL,"
                    " tipo TEXT NOT NULL, etiqueta TEXT NOT NULL, resumen TEXT NOT NULL,"
                    " texto TEXT NOT NULL, ts TEXT NOT NULL)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_reg_astro ON registros (astronauta_id, id)")
        for es, en in _ANTIGUOS.items():
            con.execute("UPDATE registros SET tipo=? WHERE tipo=?", (en, es))
            con.execute("UPDATE registros SET etiqueta=? WHERE etiqueta=?", (en, es))


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
        filas.append({"id": f"e{e['id']}", "tipo": "Emergency", "etiqueta": "Emergency",
                      "resumen": recortar(e["mensaje"], 90),
                      "texto": e["mensaje"] + (f"\nAcknowledged by {e['reconocida_por']}." if e["reconocida"] else
                                               "\nNot acknowledged yet."),
                      "ts": e["ts"]})
    filas.sort(key=lambda r: r["ts"], reverse=True)
    for r in filas:  # en el historial cada fila lleva su tipo (Conversación, Protocolo, Bitácora...)
        r["etiqueta"] = r["tipo"]
    return filas[:limite]


def fecha_corta(ts: str) -> str:
    d = datetime.fromisoformat(ts)
    return f"{MESES[d.month - 1]} {d.day}, {d.year} · {d:%H:%M}"


def fecha_larga(ts: str) -> str:
    d = datetime.fromisoformat(ts)
    return f"{MESES_LARGOS[d.month - 1]} {d.day}, {d.year}, {d:%H:%M}"


# --------------------------------------------------------------------------- clasificación
def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


_REGLAS = (
    ("Pain", r"pain|hurts|ache|sore|cramp|dolor|duele|molest|punzada|calambre"),
    ("Symptom", r"dizz|nausea|vomit|fever|cough|short of breath|tired|palpitat|symptom|headache|mareo|fiebre|tos|falta de aire|cansanc|sintoma|cefalea"),
    ("Sleep", r"sleep|slept|insomnia|rest|dorm|sueno|desvel|insomn|descans"),
    ("Mood", r"sad|anxi|stress|happy|mood|lonely|homesick|nervous|worr|content|triste|ansied|estres|feliz|animo|solo|sola|extrano|nervios|preocup"),
    ("Exercise", r"exercise|workout|train|run|treadmill|bike|weights|strength|ejercicio|entren|correr|cinta|bicicleta|pesas|fuerza"),
    ("Food", r"ate\b|eat|meal|breakfast|lunch|dinner|appetite|hungry|comi|comida|desayun|almuerz|cena|apetito|hambre"),
    ("Hydration", r"water|hydrat|thirst|agua|hidrat|sed\b"),
    ("Medication", r"pill|medic|ibuprofen|dose|took|losartan|pastilla|medicament|ibuprofeno|dosis|tome"),
    ("Equipment", r"equipment|sensor|panel|module|failure|battery|cabin|equipo|modulo|falla|bateria|oxigeno del|cabina"),
    ("Task", r"task|experiment|mission|repair|maintenance|check-?up|eva\b|tarea|mision|reparac|mantenimiento|revision"),
)


def clasificar_simple(texto: str) -> tuple[str, str]:
    n = _norm(texto)
    for etiqueta, patron in _REGLAS:
        if re.search(patron, n):
            return etiqueta, recortar(texto, 70)
    return "Note", recortar(texto, 70)


def clasificar(texto: str) -> tuple[str, str]:
    """(palabra, resumen) de una entrada de bitácora. Usa la IA si hay llave; si no, reglas simples."""
    try:
        from medico import modelo
        if modelo.hay_llave():
            sistema = ("Classify an entry from an astronaut's personal journal. Answer with ONLY one line: "
                       "WORD | summary. WORD is ONE single word, preferably one of: "
                       + ", ".join(PALABRAS_BITACORA) + ". The summary is under 70 characters, without quotes, "
                       "in English, and adds no facts that are not in the entry. Give no advice.")
            salida = "".join(modelo.stream([{"role": "user", "content": texto[:1500]}], sistema)).strip()
            primera = salida.splitlines()[0] if salida else ""
            palabra, _, resumen = primera.partition("|")
            palabra = re.sub(r"[^A-Za-z]", "", palabra).strip().capitalize()
            if 2 <= len(palabra) <= 16 and resumen.strip():
                return palabra, recortar(resumen.strip(), 70)
    except Exception:
        pass
    return clasificar_simple(texto)


def agregar_bitacora(astro_id: int, texto: str) -> int:
    palabra, resumen = clasificar(texto)
    return agregar(astro_id, "Journal", resumen, texto.strip(), etiqueta=palabra)
