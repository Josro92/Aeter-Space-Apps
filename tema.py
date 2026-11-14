"""Tema visual de Aéter (borrador): glassmorfismo, ilustraciones SVG y piezas de HTML.

No contiene lógica de la aplicación: solo estilos e imágenes. Cuando llegue el diseño
final de Canva, bastará con reemplazar este archivo (y la carpeta assets/).
"""
from __future__ import annotations

import base64
import hashlib

import streamlit as st

COLOR = {"normal": "#34d399", "advertencia": "#facc15", "critica": "#ef4444"}
NIVEL_TEXTO = {"normal": "Estable", "advertencia": "Atención", "critica": "Emergencia"}

# Colores de las etiquetas del historial (una palabra, un color)
COLORES_TIPO = {
    "Protocolo": "#34d399", "Conversación": "#60a5fa", "Recordatorio": "#fbbf24",
    "Emergencia": "#f87171", "Bitácora": "#a78bfa",
}
COLORES_PALABRA = {
    "Síntoma": "#fb7185", "Dolor": "#f87171", "Ánimo": "#f472b6", "Sueño": "#818cf8",
    "Ejercicio": "#34d399", "Alimentación": "#fbbf24", "Medicación": "#2dd4bf",
    "Hidratación": "#38bdf8", "Equipo": "#94a3b8", "Tarea": "#fb923c", "Nota": "#a78bfa",
}
_PALETA = ("#f472b6", "#38bdf8", "#fb923c", "#a3e635", "#c084fc", "#2dd4bf", "#fda4af", "#fcd34d")


def color_etiqueta(palabra: str) -> str:
    if palabra in COLORES_TIPO:
        return COLORES_TIPO[palabra]
    if palabra in COLORES_PALABRA:
        return COLORES_PALABRA[palabra]
    h = int(hashlib.md5(palabra.encode("utf-8")).hexdigest(), 16)
    return _PALETA[h % len(_PALETA)]


def _uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


# --------------------------------------------------------------------------- Marte con cara
def marte_svg(expresion: str = "calma") -> str:
    """Planeta Marte con cara. expresion: calma | alerta | critica."""
    oscuro = "#3a2a2a"
    if expresion == "critica":
        cara = (f'<ellipse cx="140" cy="190" rx="19" ry="22" fill="#fff"/><circle cx="140" cy="194" r="8" fill="{oscuro}"/>'
                f'<ellipse cx="260" cy="190" rx="19" ry="22" fill="#fff"/><circle cx="260" cy="194" r="8" fill="{oscuro}"/>'
                f'<path d="M110 150 L165 165 M290 150 L235 165" stroke="{oscuro}" stroke-width="7" stroke-linecap="round"/>'
                f'<ellipse cx="200" cy="268" rx="22" ry="26" fill="{oscuro}"/>')
    elif expresion == "alerta":
        cara = (f'<circle cx="140" cy="192" r="17" fill="#fff"/><circle cx="142" cy="194" r="7" fill="{oscuro}"/>'
                f'<circle cx="260" cy="192" r="17" fill="#fff"/><circle cx="258" cy="194" r="7" fill="{oscuro}"/>'
                f'<path d="M115 165 Q140 152 165 168 M285 165 Q260 152 235 168" stroke="{oscuro}" stroke-width="6" '
                f'fill="none" stroke-linecap="round"/>'
                f'<path d="M172 268 Q200 258 228 268" stroke="{oscuro}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    else:
        cara = (f'<path d="M112 196 Q140 218 168 196" stroke="{oscuro}" stroke-width="7" fill="none" stroke-linecap="round"/>'
                f'<path d="M232 196 Q260 218 288 196" stroke="{oscuro}" stroke-width="7" fill="none" stroke-linecap="round"/>'
                f'<path d="M168 262 Q200 290 232 262" stroke="{oscuro}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">'
        '<defs><radialGradient id="g" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#f8b998"/>'
        '<stop offset="0.6" stop-color="#ee8f6c"/><stop offset="1" stop-color="#d9694f"/></radialGradient>'
        '<clipPath id="c"><circle cx="200" cy="200" r="190"/></clipPath></defs>'
        '<circle cx="200" cy="200" r="190" fill="url(#g)"/>'
        '<g clip-path="url(#c)" opacity="0.55">'
        '<path d="M0 120 Q90 70 190 110 T400 90 L400 140 Q300 160 200 140 T0 170Z" fill="#e0775a"/>'
        '<path d="M0 300 Q110 250 200 290 T400 270 L400 330 Q290 350 200 330 T0 350Z" fill="#cf6048"/>'
        '<ellipse cx="300" cy="300" rx="70" ry="48" fill="#c9553f" transform="rotate(-25 300 300)"/>'
        '<ellipse cx="90" cy="250" rx="38" ry="24" fill="#f5b392" transform="rotate(20 90 250)"/>'
        '<ellipse cx="320" cy="110" rx="46" ry="26" fill="#f7c0a0" transform="rotate(-18 320 110)"/></g>'
        '<ellipse cx="200" cy="232" rx="14" ry="8" fill="#d9694f"/>'
        f'{cara}</svg>'
    )


def marte_img(expresion: str = "calma", ancho: str | None = None, clase: str = "") -> str:
    estilo = f' style="width:{ancho}"' if ancho else ""
    return f'<img class="marte {clase}"{estilo} src="{_uri(marte_svg(expresion))}" alt="Aéter">'


# --------------------------------------------------------------------------- avatares de la tripulación
_AVATAR = {"Ana Rojas": "#e63946", "Jason": "#3b82f6", "María Quesada Antonelli": "#14b8a6"}


def avatar_svg(nombre: str) -> str:
    color = _AVATAR.get(nombre) or _PALETA[int(hashlib.md5(nombre.encode()).hexdigest(), 16) % len(_PALETA)]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs>'
        f'<radialGradient id="a" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="{color}"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".35"/></radialGradient>'
        '<clipPath id="k"><circle cx="100" cy="100" r="100"/></clipPath></defs>'
        f'<circle cx="100" cy="100" r="100" fill="{color}"/>'
        '<g clip-path="url(#k)"><ellipse cx="45" cy="60" rx="45" ry="32" fill="#fff" opacity=".18"/>'
        '<ellipse cx="160" cy="150" rx="55" ry="38" fill="#000" opacity=".16"/>'
        '<ellipse cx="150" cy="40" rx="30" ry="20" fill="#000" opacity=".12"/></g>'
        '<circle cx="100" cy="100" r="100" fill="url(#a)" opacity=".55"/>'
        '<ellipse cx="72" cy="92" rx="10" ry="14" fill="#111"/><ellipse cx="128" cy="92" rx="10" ry="14" fill="#111"/>'
        '<circle cx="76" cy="86" r="4" fill="#fff"/><circle cx="132" cy="86" r="4" fill="#fff"/>'
        '<ellipse cx="52" cy="116" rx="12" ry="7" fill="#fff" opacity=".35"/>'
        '<ellipse cx="148" cy="116" rx="12" ry="7" fill="#fff" opacity=".35"/>'
        '<path d="M88 118 Q100 130 112 118" stroke="#f9a8d4" stroke-width="6" fill="none" stroke-linecap="round"/></svg>'
    )


def avatar_img(nombre: str, tam: int = 64) -> str:
    return (f'<img class="avatar" style="width:{tam}px;height:{tam}px" src="{_uri(avatar_svg(nombre))}" '
            f'alt="{nombre}">')


# --------------------------------------------------------------------------- iconos de signos vitales
def _svg(cuerpo: str, estilo: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">'
            f'<style>{estilo}</style>{cuerpo}</svg>')


def icono_vital(clave: str, nivel: str, fc: float = 70, fr: float = 15) -> str:
    """Icono animado del signo vital, coloreado según su estado (verde, amarillo o rojo)."""
    c = COLOR.get(nivel, COLOR["normal"])
    g = f"filter:drop-shadow(0 0 6px {c}aa);"
    if clave == "fc":
        d = 60 / max(30, min(fc or 70, 200))
        s = _svg(
            f'<g class="h"><path d="M60 106 C20 76 8 54 8 38 C8 22 20 12 34 12 C45 12 55 17 60 27 C65 17 75 12 86 12 '
            f'C100 12 112 22 112 38 C112 54 100 76 60 106Z" fill="{c}" fill-opacity=".92"/>'
            f'<polyline points="14,58 40,58 50,38 62,80 72,52 80,58 106,58" fill="none" stroke="#0f1a2e" '
            f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></g>',
            f".h{{transform-box:fill-box;transform-origin:center;animation:l {d:.2f}s infinite ease-in-out;{g}}}"
            "@keyframes l{0%,100%{transform:scale(1)}15%{transform:scale(1.14)}30%{transform:scale(1)}"
            "45%{transform:scale(1.09)}60%{transform:scale(1)}}")
    elif clave == "pa":
        s = _svg(
            f'<g class="b"><rect x="8" y="14" width="42" height="58" rx="9" fill="none" stroke="{c}" stroke-width="7"/>'
            f'<path d="M20 30 H38 M20 44 H38 M20 58 H38" stroke="{c}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M30 72 C30 104 74 108 84 86" fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round"/>'
            f'<circle cx="92" cy="84" r="11" fill="{c}"/>'
            f'<circle cx="84" cy="38" r="27" fill="none" stroke="{c}" stroke-width="7"/>'
            f'<g class="n"><line x1="84" y1="38" x2="84" y2="18" stroke="{c}" stroke-width="5" stroke-linecap="round"/></g>'
            f'<circle cx="84" cy="38" r="4" fill="{c}"/></g>',
            f".b{{{g}}}.n{{transform-box:view-box;transform-origin:84px 38px;animation:a 3.2s infinite ease-in-out}}"
            "@keyframes a{0%,100%{transform:rotate(-40deg)}50%{transform:rotate(55deg)}}")
    elif clave == "spo2":
        s = _svg(
            f'<g class="gt"><path d="M38 10 C27 30 18 40 18 54 A20 20 0 0 0 58 54 C58 40 49 30 38 10Z" fill="{c}"/>'
            f'<path d="M72 8 C64 22 58 28 58 38 A14 14 0 0 0 86 38 C86 28 80 22 72 8Z" fill="{c}" fill-opacity=".8"/></g>'
            f'<g class="o"><circle cx="84" cy="84" r="27" fill="{c}"/>'
            f'<text x="84" y="92" text-anchor="middle" font-family="Arial" font-weight="700" font-size="24" fill="#0f1a2e">O2</text></g>',
            f".gt{{animation:v 2.4s infinite ease-in-out;{g}}}.o{{transform-box:fill-box;transform-origin:center;"
            f"animation:p 2.4s infinite ease-in-out;{g}}}"
            "@keyframes v{0%,100%{transform:translateY(0)}50%{transform:translateY(5px)}}"
            "@keyframes p{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}")
    elif clave == "temp":
        s = _svg(
            f'<g class="t"><rect x="46" y="8" width="28" height="74" rx="14" fill="none" stroke="{c}" stroke-width="7"/>'
            f'<circle cx="60" cy="94" r="19" fill="{c}"/>'
            f'<rect class="m" x="54" y="26" width="12" height="62" rx="6" fill="{c}"/>'
            f'<path d="M86 24 H104 M86 40 H98 M86 56 H104 M86 72 H98" stroke="{c}" stroke-width="5" stroke-linecap="round"/></g>',
            f".t{{{g}}}.m{{transform-box:fill-box;transform-origin:bottom;animation:m 3s infinite ease-in-out}}"
            "@keyframes m{0%,100%{transform:scaleY(.82)}50%{transform:scaleY(1)}}")
    else:  # fr
        d = 60 / max(6, min(fr or 15, 40))
        s = _svg(
            f'<g class="p"><path d="M60 8 V52" stroke="{c}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M60 40 C50 40 44 52 38 60 M60 40 C70 40 76 52 82 60" stroke="{c}" stroke-width="6" '
            f'fill="none" stroke-linecap="round"/>'
            f'<path d="M52 42 C28 42 10 72 10 100 C10 110 20 112 31 106 C45 98 52 82 52 60Z" fill="{c}" fill-opacity=".92"/>'
            f'<path d="M68 42 C92 42 110 72 110 100 C110 110 100 112 89 106 C75 98 68 82 68 60Z" fill="{c}" fill-opacity=".92"/></g>',
            f".p{{transform-box:fill-box;transform-origin:50% 60%;animation:r {d:.2f}s infinite ease-in-out;{g}}}"
            "@keyframes r{0%,100%{transform:scale(.95)}50%{transform:scale(1.08)}}")
    return f'<img class="icono" src="{_uri(s)}" alt="">'


# --------------------------------------------------------------------------- estilos
FONTS = ("@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&"
         "family=Poppins:wght@500;600;700;800&display=swap');")

CSS = FONTS + """
:root{--navy:#0b0b7a;--vidrio:rgba(255,255,255,.16);--borde:rgba(255,255,255,.30);--texto:#fff}
.stApp{
  background:
    radial-gradient(rgba(0,0,0,.20) 1px, transparent 1.3px) 0 0/4px 4px,
    radial-gradient(circle at 12% 18%, rgba(30,50,90,.9), transparent 45%),
    linear-gradient(100deg,#0d1424 0%,#17213a 34%,#9a3b2b 56%,#e2582c 74%,#f3893a 90%,#f7b94c 100%);
  background-attachment:fixed;color:var(--texto);font-family:'Open Sans',sans-serif}
[data-testid="stHeader"]{background:transparent}
[data-testid="stAppDeployButton"],[data-testid="stMainMenu"],[data-testid="stToolbarActions"],[data-testid="stDecoration"],footer,#MainMenu{display:none!important}
.block-container{max-width:1320px;padding:1.4rem 2.2rem 8.5rem!important}
h1,h2,h3,h4{font-family:'Poppins',sans-serif;color:#fff}
p,span,label,li,div{color:inherit}
.stApp,.stApp p,.stApp li,.stApp label{color:#fff}

/* ---- barra de pestañas fija abajo ---- */
[data-baseweb="tab-list"],[data-testid="stTabs"]>div>[role="tablist"]{position:fixed!important;left:0;right:0;bottom:0;z-index:999;
  height:92px;display:flex!important;align-items:center;justify-content:space-around;gap:6px;padding:0 18px!important;
  background:rgba(235,225,225,.30)!important;backdrop-filter:blur(22px) saturate(1.3);-webkit-backdrop-filter:blur(22px) saturate(1.3);
  border-top:1px solid rgba(255,255,255,.35);border-bottom:none!important;overflow:visible!important}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"],.react-aria-SelectionIndicator{display:none!important}
button[data-baseweb="tab"],[data-testid="stTab"]{flex:1;max-width:260px;height:62px!important;border-radius:40px!important;
  display:flex!important;align-items:center;justify-content:center;background:transparent!important;transition:all .25s;
  cursor:pointer;padding:0 10px!important}
[data-testid="stTab"] p,button[data-baseweb="tab"] p{font-family:'Poppins',sans-serif;font-weight:700;
  font-size:1.2rem!important;color:#191a4a!important;margin:0}
[data-testid="stTab"][aria-selected="true"],button[data-baseweb="tab"][aria-selected="true"]{background:var(--navy)!important;
  box-shadow:0 6px 18px rgba(5,5,80,.45)}
[data-testid="stTab"][aria-selected="true"] p,button[data-baseweb="tab"][aria-selected="true"] p{color:#fff!important}
[data-testid="stTab"]:hover,button[data-baseweb="tab"]:hover{background:rgba(255,255,255,.25)!important}
[data-testid="stTab"][aria-selected="true"]:hover{background:var(--navy)!important}

body:has([data-testid="stSidebar"][aria-expanded="true"]) [data-baseweb="tab-list"],body:has([data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stTabs"]>div>[role="tablist"]{left:300px!important}

/* ---- vidrio ---- */
.vidrio,[class*="st-key-vidrio_"]{background:var(--vidrio);backdrop-filter:blur(18px) saturate(1.2);
  -webkit-backdrop-filter:blur(18px) saturate(1.2);border:1px solid var(--borde);border-radius:30px;
  box-shadow:0 10px 36px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.35)}
[class*="st-key-vidrio_"]{padding:22px 26px}

/* ---- botones ---- */
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{border-radius:40px;font-family:'Poppins',sans-serif;
  font-weight:600;color:#fff;background:var(--vidrio);border:1px solid var(--borde);backdrop-filter:blur(14px)}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:rgba(255,255,255,.28);border-color:#fff;color:#fff}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:var(--navy);border-color:var(--navy)}

/* ---- botón invisible encima de una tarjeta (tarjeta clicable) ---- */
[class*="st-key-clic_"]{position:relative}
[class*="st-key-tapa_"]{position:absolute!important;inset:0;z-index:5;margin:0!important}
[class*="st-key-tapa_"] button{width:100%!important;height:100%!important;min-height:0;opacity:0;cursor:pointer;border-radius:30px}
[class*="st-key-tapa_"] [data-testid="stButton"],[class*="st-key-tapa_"] [data-testid="stElementContainer"]{height:100%}
[class*="st-key-clic_"]:hover .tarjeta,[class*="st-key-clic_"]:hover .fila{filter:brightness(1.12)}

/* ---- portada ---- */
.portada{text-align:center;padding-top:3vh}
.portada .marte{width:min(230px,40vw)!important;animation:flota 6s ease-in-out infinite;filter:drop-shadow(0 14px 30px rgba(0,0,0,.35))}
.portada h1{font-size:4.2rem;font-weight:800;letter-spacing:.08em;margin:.2rem 0 0}
.portada p.sub{font-size:1.15rem;opacity:.85;margin:.2rem 0 1.4rem}
.tarjeta{display:flex;flex-direction:column;align-items:center;gap:10px;padding:22px 12px;border-radius:30px;
  background:var(--vidrio);border:1px solid var(--borde);backdrop-filter:blur(16px);transition:all .2s}
.tarjeta .avatar{width:96px;height:96px}
.tarjeta .nom{font-family:'Poppins',sans-serif;font-weight:700;font-size:1.05rem;text-align:center}
.tarjeta .rol{font-size:.8rem;opacity:.75;text-align:center}
.tarjeta.sel{background:rgba(255,255,255,.34);border-color:#fff;box-shadow:0 0 0 3px rgba(255,255,255,.55),0 12px 34px rgba(0,0,0,.3)}
.avatar{border-radius:50%;object-fit:cover;box-shadow:0 4px 14px rgba(0,0,0,.3)}
@keyframes flota{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}

/* ---- estado ---- */
.marte-grande{display:flex;align-items:center;justify-content:center;padding:1rem}
.marte-grande .marte{width:min(470px,100%)!important;animation:flota 7s ease-in-out infinite;filter:drop-shadow(0 18px 34px rgba(0,0,0,.4))}
.saludo{display:flex;align-items:center;gap:26px;padding:14px 40px 14px 16px;border-radius:70px;
  background:var(--vidrio);border:1px solid var(--borde);backdrop-filter:blur(18px)}
.saludo .avatar{width:112px;height:112px}
.saludo .txt{font-family:'Poppins',sans-serif;font-weight:700;font-size:2.05rem;flex:1;text-align:center}
.hora{font-family:'Poppins',sans-serif;font-weight:800;font-size:4.2rem;line-height:1;letter-spacing:-.03em}
.fecha{font-family:'Open Sans',sans-serif;font-weight:700;font-size:1.5rem;margin-top:.3rem;padding-left:.4rem}
.zona-alertas h4{text-align:center;font-family:'Open Sans',sans-serif;font-weight:700;font-size:1.7rem;margin:.6rem 0 .8rem}
.alerta-item{display:flex;gap:12px;align-items:center;padding:9px 14px;border-radius:16px;margin-bottom:8px;
  background:rgba(255,255,255,.14);font-size:1rem}
.alerta-item .punto{width:12px;height:12px;border-radius:50%;flex:none}
.alerta-item.vacia{opacity:.8;justify-content:center}
.st-key-btn_sos button{width:170px;height:170px;border-radius:50%!important;font-family:'Poppins',sans-serif;
  background:rgba(255,255,255,.70)!important;border:1px solid #fff!important;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.st-key-btn_sos button p{font-size:2.4rem!important;font-weight:800;color:#d62839!important}
.st-key-btn_sos button:hover{background:#fff!important;transform:scale(1.04)}
.st-key-btn_sos{display:flex;justify-content:center}

/* ---- signos vitales ---- */
.vital{text-align:center}
.vital .nombre{font-family:'Open Sans',sans-serif;font-weight:700;font-size:1.65rem;line-height:1.12;min-height:3.8rem;
  display:flex;flex-direction:column;justify-content:flex-end;align-items:center}
.vital .nombre small{font-size:.8rem;font-weight:600;opacity:.9}
.vital .icono{width:128px;height:128px;margin:14px 0 20px;transition:transform .2s}
[class*="st-key-clic_"]:hover .vital .icono{transform:scale(1.07)}
.dato{display:inline-flex;align-items:center;justify-content:center;min-width:150px;padding:14px 22px;border-radius:18px;
  background:rgba(255,255,255,.12);border:1px solid var(--borde);backdrop-filter:blur(10px);
  font-family:'Poppins',sans-serif;font-weight:700;font-size:1.9rem}
.dato.n-advertencia{border-color:#facc15;box-shadow:0 0 14px rgba(250,204,21,.5)}
.dato.n-critica{border-color:#ef4444;box-shadow:0 0 16px rgba(239,68,68,.65)}
.frac{display:inline-flex;flex-direction:column;align-items:center;line-height:1.05;font-size:1.7rem}
.frac i{display:block;width:100%;height:2px;background:#fff;margin:2px 0}
.aviso-vital{opacity:.85;font-size:.9rem;margin-top:8px}

/* ---- tablas tipo Notion ---- */
.cab{display:grid;grid-template-columns:19% 55% 26%;gap:10px;padding:6px 16px;font-size:.85rem;font-weight:700;opacity:.8}
.fila{display:grid;grid-template-columns:19% 55% 26%;gap:10px;align-items:center;padding:12px 16px;border-radius:16px;
  background:rgba(12,14,28,.55);border:1px solid rgba(255,255,255,.12);margin-bottom:6px;font-size:.95rem}
.fila .res{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fila .fec{opacity:.8;font-size:.88rem;white-space:nowrap}
.pill{display:inline-block;padding:3px 12px;border-radius:8px;font-weight:700;font-size:.82rem;color:#fff;
  white-space:nowrap}

/* ---- barra de escritura (chat y bitácora) ---- */
[data-testid="stChatInput"],.st-key-bit_barra{background:#17174a!important;border-radius:20px!important;
  border:1px solid rgba(255,255,255,.18)!important;box-shadow:0 10px 30px rgba(0,0,0,.35)}
[data-testid="stChatInput"]>div{background:transparent!important;border:none!important}
[data-testid="stChatInput"] textarea{color:#fff!important}
.st-key-bit_barra{padding:10px 16px}
.st-key-bit_barra [data-testid="stForm"]{border:none!important;padding:0!important;background:transparent!important}
.st-key-bit_barra input{background:transparent!important;color:#fff!important;font-size:1.05rem}
.st-key-bit_barra [data-baseweb="input"],.st-key-bit_barra [data-baseweb="base-input"],
.st-key-bit_barra [data-testid="stTextInputRootElement"]{background:transparent!important;border:none!important;box-shadow:none!important}
.st-key-bit_barra .stFormSubmitButton>button,.st-key-bit_barra [data-testid="stFormSubmitButton"]>button{
  background:var(--navy)!important;border-color:#3b3bb5!important;border-radius:14px!important}
.barra-aeter{display:flex;align-items:center;gap:12px}
.barra-aeter .marte{width:50px!important;flex:none}

[data-testid="InputInstructions"]{display:none!important}
.vital.sel .dato{background:rgba(255,255,255,.30);border-color:#fff}

/* ---- conversación ---- */
[data-testid="stChatMessage"]{background:transparent!important;padding:0!important;margin-bottom:14px}
[data-testid="stChatMessageAvatarUser"],[data-testid="stChatMessageAvatarAssistant"]{display:none!important}
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"]{border-radius:28px;padding:16px 22px;
  backdrop-filter:blur(16px);background:rgba(255,255,255,.17);border:1px solid rgba(255,255,255,.3);max-width:78%;width:fit-content}
[data-testid="stChatMessage"]{justify-content:flex-start}
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"]{flex:0 1 auto!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){flex-direction:row-reverse;justify-content:flex-start}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"]{
  margin-left:auto;border-radius:34px;background:rgba(255,255,255,.24)}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"]{
  background:rgba(20,24,52,.55);border-color:rgba(255,255,255,.5)}

/* ---- barra lateral (modo demostración) ---- */
[data-testid="stSidebar"]{background:rgba(14,18,38,.82);backdrop-filter:blur(22px)}
[data-testid="stSidebar"] *{color:#fff}

/* ---- ventanas emergentes ---- */
[data-testid="stDialog"] [role="dialog"]{background:rgba(24,28,58,.94)!important;backdrop-filter:blur(24px);
  border:1px solid rgba(255,255,255,.3);border-radius:28px;color:#fff}
.ficha-tabla{width:100%;border-collapse:collapse;margin-bottom:14px;font-size:.95rem}
.ficha-tabla th{background:rgba(255,255,255,.2);text-align:left;padding:8px 12px;font-family:'Poppins',sans-serif;
  letter-spacing:.04em;font-size:.85rem}
.ficha-tabla td{padding:8px 12px;border:1px solid rgba(255,255,255,.18);vertical-align:top}
.ficha-tabla td.k{width:34%;font-weight:700;background:rgba(255,255,255,.07)}

/* ---- gráficas y varios ---- */
[data-testid="stPlotlyChart"]{background:rgba(12,14,28,.5);border-radius:22px;padding:6px;border:1px solid rgba(255,255,255,.14)}
[data-testid="stAlert"]{border-radius:18px}
@media (max-width:900px){.hora{font-size:3rem}.saludo .txt{font-size:1.4rem}.vital .nombre{font-size:1.2rem}
  .cab,.fila{grid-template-columns:28% 40% 32%}[data-testid="stTab"] p{font-size:.9rem!important}}
"""


def aplicar_tema() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def pill(palabra: str) -> str:
    c = color_etiqueta(palabra)
    return f'<span class="pill" style="background:{c}33;border:1px solid {c};color:#fff">{palabra}</span>'
