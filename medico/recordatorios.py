"""Recordatorios con hora específica.

Dos orígenes:
- astronauta: los crea el médico por voz o chat (guardados en la base de datos).
- constructor: los deja Claude/el equipo en config/recordatorios.json (se suben con git).
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import db

ZONA = ZoneInfo("America/Costa_Rica")
ARCHIVO = Path(__file__).resolve().parent.parent / "config" / "recordatorios.json"


def ahora() -> datetime:
    return datetime.now(ZONA)


def _tabla() -> None:
    with db.conexion() as con:
        con.execute("CREATE TABLE IF NOT EXISTS recordatorios ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, astronauta_id INTEGER, vence TEXT NOT NULL,"
                    " texto TEXT NOT NULL, origen TEXT, hecho INTEGER NOT NULL DEFAULT 0)")


def crear(astro_id: int, hora: str, texto: str, origen: str = "astronauta") -> str:
    """hora 'HH:MM' (24 h). Si ya pasó hoy, es para mañana. Devuelve la fecha-hora ISO."""
    _tabla()
    h, m = (int(x) for x in hora.split(":"))
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError("hora inválida")
    t = ahora().replace(hour=h, minute=m, second=0, microsecond=0)
    if t <= ahora():
        t += timedelta(days=1)
    with db.conexion() as con:
        con.execute("INSERT INTO recordatorios (astronauta_id, vence, texto, origen) VALUES (?,?,?,?)",
                    (astro_id, t.isoformat(timespec="minutes"), texto, origen))
    return t.isoformat(timespec="minutes")


def pendientes(astro_id: int | None = None) -> list[dict]:
    _tabla()
    with db.conexion() as con:
        filas = con.execute("SELECT * FROM recordatorios WHERE hecho=0 ORDER BY vence").fetchall()
    return [dict(f) for f in filas if astro_id is None or f["astronauta_id"] in (None, astro_id)]


def vencidos() -> list[dict]:
    """Recordatorios de la base de datos cuya hora ya llegó; los marca como hechos."""
    _tabla()
    t = ahora().isoformat(timespec="minutes")
    with db.conexion() as con:
        filas = [dict(f) for f in con.execute(
            "SELECT * FROM recordatorios WHERE hecho=0 AND vence<=? ORDER BY vence", (t,))]
        for f in filas:
            con.execute("UPDATE recordatorios SET hecho=1 WHERE id=?", (f["id"],))
    return filas


def del_archivo() -> list[dict]:
    """Recordatorios del constructor, activos y cuya hora ya llegó (hoy o fecha indicada)."""
    try:
        datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    except Exception:
        return []
    ahora_ = ahora()
    salida = []
    for i, r in enumerate(datos):
        try:
            if not r.get("activo", True) or "hora" not in r or "texto" not in r:
                continue
            h, m = (int(x) for x in r["hora"].split(":"))
            fecha = r.get("fecha") or ahora_.strftime("%Y-%m-%d")
            vence = datetime.strptime(f"{fecha} {h:02d}:{m:02d}", "%Y-%m-%d %H:%M").replace(tzinfo=ZONA)
            if vence <= ahora_:
                salida.append({"id": f"archivo{i}_{fecha}_{r['hora']}", "texto": str(r["texto"])})
        except Exception:
            continue
    return salida
