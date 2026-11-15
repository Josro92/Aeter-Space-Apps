from __future__ import annotations

import unicodedata

DESCARGO = (
    "Educational hackathon prototype: it is not a medical device and does not replace the medical officer, "
    "the flight surgeon or Mission Control. Sample data and protocols."
)


def normalizar(texto: str) -> str:
    """Lowercase and strip accents, to compare keywords."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


# --------------------------------------------------------------------------- how to measure
MEDICIONES = {
    "presion": {
        "titulo": "How to measure blood pressure",
        "palabras": ["blood pressure", "cuff", "presion", "tension", "brazalete", "tensiometro", "arterial"],
        "pasos": [
            "Let the person rest for 5 minutes, without talking or moving; secure them with the straps so they are stable in microgravity.",
            "Use a cuff of the right size on the bare arm, at heart level.",
            "Keep the arm relaxed and supported. Start the measurement and do not talk while it runs.",
            "Write down systolic/diastolic and repeat after 1-2 minutes; record the average.",
            "If the value is critical, confirm it with a second measurement before acting and alert the crew.",
        ],
    },
    "spo2": {
        "titulo": "How to measure oxygen saturation (SpO₂)",
        "palabras": ["saturation", "oximeter", "pulse ox", "spo2", "oxygen level", "saturacion", "oximetro", "pulsioximetro"],
        "pasos": [
            "Remove nail polish or artificial nails from the chosen finger and warm the hand if it is cold.",
            "Place the pulse oximeter on the index or middle finger, with the hand relaxed and still.",
            "Wait 20-30 seconds until the value settles and the pulse wave is clear.",
            "If the value is low, change fingers and repeat: a badly placed sensor gives false alarms.",
            "Write down the value and the time.",
        ],
    },
    "pulso": {
        "titulo": "How to measure the pulse (heart rate) by hand",
        "palabras": ["pulse", "heartbeat", "heart rate", "pulso", "latidos", "frecuencia cardiaca", "cardiaca"],
        "pasos": [
            "Place two fingers (index and middle, never the thumb) on the radial artery: wrist, thumb side.",
            "Count the beats for 30 seconds and multiply by 2 (if irregular, count for 60 seconds).",
            "Note whether the rhythm is regular or irregular and whether the pulse is strong or weak.",
            "Compare with the monitor value; if they differ a lot, check the electrodes/sensor.",
        ],
    },
    "temperatura": {
        "titulo": "How to measure body temperature",
        "palabras": ["temperature", "thermometer", "temperatura", "termometro"],
        "pasos": [
            "Use the thermometer from the mission medical kit (ear, forehead or oral) following its instructions.",
            "If oral, avoid eating or drinking in the minutes before; if ear, gently pull the ear.",
            "Wait for the device signal before removing it and write down the value.",
            "If the reading is abnormal, repeat in 5 minutes with the same technique.",
        ],
    },
    "respiracion": {
        "titulo": "How to measure the breathing rate",
        "palabras": ["breathing", "respiratory rate", "respiration", "respiracion", "respiratoria", "respiraciones", "respira"],
        "pasos": [
            "Without telling the person (so their rhythm does not change), watch the movement of the chest and abdomen.",
            "Count the breaths for 30 seconds and multiply by 2.",
            "Watch the effort (use of neck muscles), the color of the lips and whether they can speak in full sentences.",
            "Write down the value, the time and any sign of difficulty.",
        ],
    },
}

# --------------------------------------------------------------------------- emergencies
EMERGENCIAS = {
    "hipoxia": {
        "titulo": "Hypoxia: low oxygen saturation / breathing difficulty",
        "palabras": ["hypoxia", "oxygen", "shortness of breath", "can't breathe", "cannot breathe", "dyspnea", "cyanosis",
                     "hipoxia", "oxigeno", "saturacion", "falta de aire", "ahogo", "cianosis",
                     "no puedo respirar", "disnea", "dificultad para respirar"],
        "pasos": [
            "Alert the crew immediately and ask someone to stay with the affected person.",
            "Check the sensor: reposition the pulse oximeter, warm the hand and measure again.",
            "Check the environment: module ventilation, O₂ and CO₂ levels. A bad atmosphere affects everyone.",
            "If the reading is confirmed (< 90 %), give supplemental oxygen with a mask following the mission protocol.",
            "Keep the person at rest, loosening tight clothing and encouraging slow, deep breaths.",
            "Measure again every 1-2 minutes and record the trend.",
        ],
        "escalar": "Contact the flight surgeon / Mission Control. If SpO₂ stays < 90 %, or there is confusion, bluish lips or loss of consciousness: major emergency (consider moving to the safe module).",
    },
    "taquicardia": {
        "titulo": "Tachycardia: high heart rate",
        "palabras": ["tachycardia", "palpitations", "racing heart", "fast heart", "high pulse",
                     "taquicardia", "palpitaciones", "corazon", "latidos rapidos",
                     "frecuencia cardiaca alta", "pulso alto", "pulso rapido"],
        "pasos": [
            "Ask the person to stop and rest; secure them in a comfortable position.",
            "Confirm the value by taking the pulse by hand (radial artery).",
            "Ask about symptoms: chest pain or pressure, dizziness, shortness of breath, fainting.",
            "Look for common causes: recent exercise, dehydration, fever, pain, stress, caffeine.",
            "Hydrate if conscious and able to swallow; ask for slow breathing (inhale 4 s, exhale 6 s).",
            "Reassess every 2-3 minutes.",
        ],
        "escalar": "If it stays above 130-150 bpm at rest for several minutes, or there is chest pain, fainting or shortness of breath: alert the flight surgeon. If the person loses consciousness and does not breathe normally: start CPR and prepare the defibrillator.",
    },
    "bradicardia": {
        "titulo": "Bradycardia: low heart rate",
        "palabras": ["bradycardia", "low pulse", "slow heart", "slow pulse",
                     "bradicardia", "pulso bajo", "latidos lentos", "pulso lento"],
        "pasos": [
            "Confirm with a manual pulse and check that the electrodes/sensors are well placed.",
            "Ask about symptoms: dizziness, weakness, confusion, fainting, chest pain.",
            "If there are symptoms, keep the person secured and at rest; do not leave them alone.",
            "Check recent medications in their medical record that could lower the pulse.",
            "Monitor every 2 minutes.",
        ],
        "escalar": "If there are symptoms or the pulse drops below 40 bpm, alert the flight surgeon immediately. Unresponsive and not breathing normally: CPR.",
    },
    "hipertension": {
        "titulo": "Hypertension: high blood pressure",
        "palabras": ["hypertension", "high blood pressure", "severe headache",
                     "hipertension", "presion alta", "tension alta", "dolor de cabeza fuerte"],
        "pasos": [
            "Rest for 5 minutes and repeat the measurement with the cuff well placed (at heart level).",
            "Ask about symptoms: severe headache, blurred vision, chest pain, shortness of breath, confusion.",
            "Check the medical record: known hypertension or regular medication? Did they take it today?",
            "Avoid exertion, caffeine and salt; hydrate in moderation.",
            "Do not give antihypertensive drugs without the flight surgeon's instruction.",
            "Measure every 5-10 minutes and record the values.",
        ],
        "escalar": "If systolic exceeds 180 mmHg or there are neurological or chest symptoms, it is an emergency: alert the crew and the flight surgeon.",
    },
    "hipotension": {
        "titulo": "Hypotension / possible shock: low blood pressure",
        "palabras": ["hypotension", "low blood pressure", "fainting", "dizzy", "shock", "pale",
                     "hipotension", "presion baja", "desmayo", "mareo", "palidez"],
        "pasos": [
            "Secure the person with straps and keep them at rest; in microgravity 'lying down with legs raised' does not work, so make sure they are stable and watched.",
            "Repeat the measurement and take the pulse: fast and weak? cold, pale, sweaty skin?",
            "Look for the cause: dehydration, bleeding, reaction to a medication, infection, severe pain.",
            "If conscious and able to swallow, offer fluids in small sips.",
            "Control any visible bleeding with direct pressure.",
            "Monitor pressure, pulse and SpO₂ every 2 minutes.",
        ],
        "escalar": "Systolic pressure < 90 mmHg with symptoms, or < 85 mmHg in any case: emergency. Alert the crew and the flight surgeon; prepare the life-support equipment.",
    },
    "fiebre": {
        "titulo": "Fever: high body temperature",
        "palabras": ["fever", "high temperature", "chills", "feverish",
                     "fiebre", "temperatura alta", "calentura", "febril", "escalofrios"],
        "pasos": [
            "Confirm with a second temperature measurement.",
            "Hydrate often and reduce clothing and physical activity.",
            "Check the medical record (allergies and medications) before using any fever reducer from the kit, and follow the dose in the protocol/label.",
            "Ask about other symptoms: cough, sore throat, abdominal pain, stiff neck, rashes.",
            "If an infection is suspected, limit close contact and wear a mask.",
            "Measure the temperature every 30-60 minutes and record how it changes.",
        ],
        "escalar": "Temperature ≥ 39 °C, fever lasting more than 24 h, or confusion, stiff neck or rash: alert the flight surgeon.",
    },
    "hipotermia": {
        "titulo": "Hypothermia: low body temperature",
        "palabras": ["hypothermia", "low temperature", "very cold", "cold",
                     "hipotermia", "temperatura baja", "mucho frio", "frio"],
        "pasos": [
            "Confirm with a second temperature measurement.",
            "Check the thermal control of the suit/module and cover the person with insulating blankets.",
            "Offer warm (not hot) drinks if conscious.",
            "Avoid sudden rewarming; watch pulse and breathing.",
            "Measure the temperature every 15 minutes.",
        ],
        "escalar": "Temperature < 35 °C, confusion, severe shivering or drowsiness: alert the flight surgeon.",
    },
}

# (parameter, alert direction) -> protocol to suggest
MAPA_ALERTAS = {
    ("spo2", "baja"): "hipoxia", ("fr", "alta"): "hipoxia", ("fr", "baja"): "hipoxia",
    ("fc", "alta"): "taquicardia", ("fc", "baja"): "bradicardia",
    ("pas", "alta"): "hipertension", ("pad", "alta"): "hipertension",
    ("pas", "baja"): "hipotension", ("pad", "baja"): "hipotension",
    ("temp", "alta"): "fiebre", ("temp", "baja"): "hipotermia",
}

# --------------------------------------------------------------------------- medications
MEDICAMENTOS = {
    "titulo": "Safe use of medications from the medical kit",
    "palabras": ["medication", "medicine", "medical kit", "pill", "dose", "drug", "painkiller", "antibiotic",
                 "medicamento", "medicina", "botiquin", "pastilla", "dosis", "farmaco",
                 "analgesico", "antibiotico", "paracetamol", "ibuprofeno", "ibuprofen", "take something"],
    "pasos": [
        "Check the astronaut's record: ALLERGIES, current medications and conditions before giving anything.",
        "Use only drugs from the mission kit, following the label and the protocol. The exact dose is confirmed by the medical officer or the flight surgeon.",
        "If there is any doubt about an allergy or interaction, do NOT give it and ask for advice.",
        "Handle pills and liquids secured (bags/containers) so they do not float away or get lost.",
        "Record in the clinical log: drug, dose, time and who gave it.",
        "Watch for 15-30 minutes: rash, swelling of the face or lips, difficulty breathing or severe dizziness mean an adverse reaction.",
        "Reassess the vital signs after giving it.",
    ],
    "escalar": "Severe allergic reaction (swelling, difficulty breathing, drop in pressure): alert the whole crew, use the epinephrine auto-injector from the kit following the protocol and contact the flight surgeon.",
}


# --------------------------------------------------------------------------- utilities
def lista_numerada(pasos: list[str]) -> str:
    return "\n".join(f"{i}. {p}" for i, p in enumerate(pasos, 1))


def emergencia_md(clave: str) -> str:
    e = EMERGENCIAS[clave]
    return f"### {e['titulo']}\n{lista_numerada(e['pasos'])}\n\n**When to escalate:** {e['escalar']}"


def medicion_md(clave: str) -> str:
    m = MEDICIONES[clave]
    return f"### {m['titulo']}\n{lista_numerada(m['pasos'])}"


def medicamentos_md() -> str:
    m = MEDICAMENTOS
    return f"### {m['titulo']}\n{lista_numerada(m['pasos'])}\n\n**Severe reaction:** {m['escalar']}"


def detectar(texto: str, catalogo: dict) -> list[str]:
    """Catalog keys whose keywords appear in the text."""
    t = normalizar(texto)
    return [k for k, v in catalogo.items() if any(p in t for p in v["palabras"])]


def protocolos_para_alertas(alertas: list[dict]) -> list[str]:
    """Protocols recommended for a list of alerts, without repeats."""
    claves: list[str] = []
    for a in alertas:
        clave = MAPA_ALERTAS.get((a["parametro"], a["direccion"]))
        if clave and clave not in claves:
            claves.append(clave)
    return claves


def texto_referencia() -> str:
    """All protocols as plain text, for the AI prompt."""
    partes = ["## How to take measurements"]
    for m in MEDICIONES.values():
        partes.append(f"### {m['titulo']}\n{lista_numerada(m['pasos'])}")
    partes.append("## Emergencies")
    for e in EMERGENCIAS.values():
        partes.append(f"### {e['titulo']}\n{lista_numerada(e['pasos'])}\nEscalate: {e['escalar']}")
    partes.append("## Medications")
    partes.append(f"{lista_numerada(MEDICAMENTOS['pasos'])}\nEscalate: {MEDICAMENTOS['escalar']}")
    return "\n\n".join(partes)
