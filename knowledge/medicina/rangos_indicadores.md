# Rangos y cambios esperados de los indicadores en vuelo

> Fuente original: `indicadores_astronautas_completada_v2.xlsx` (equipo). Conversión literal de las filas; las celdas vacías se omiten.
> Los rangos son de referencia (estudios y documentos de NASA en la estación espacial); no son umbrales clínicos validados. IND013 (radiación) no viene en este documento.

## Resumen

- IND001 — Frecuencia cardíaca (reposo), unidad: bpm
- IND002 — Presión arterial sistólica (reposo), unidad: mmHg
- IND003 — Presión arterial diastólica (reposo), unidad: mmHg
- IND004 — Ritmo cardíaco (ECG) (reposo), unidad: sin unidad
- IND005 — Frecuencia respiratoria (reposo), unidad: respiraciones/min
- IND006 — Saturación de oxígeno (SpO2) (reposo), unidad: %
- IND007 — Temperatura corporal central (ejercicio), unidad: °C
- IND008 — Glucosa en sangre (reposo), unidad: mg/dL
- IND009 — Masa corporal (reposo), unidad: kg
- IND010 — Duración del sueño (reposo), unidad: h
- IND011 — Estado de ánimo (reposo), unidad: escala
- IND012 — Fatiga autorreportada (reposo), unidad: escala
- IND014 — Presión parcial de CO2 en cabina (reposo), unidad: mmHg

## IND001 — Frecuencia cardíaca (rangos y cambios en vuelo)

- ID: IND001
- Contexto: reposo
- Cambio esperado en vuelo: ≈0 % (sin cambio significativo en ISS)
- Unidad: bpm
- Tipo de dato: Cambio vs. pre-misión
- Notas: Sin rango absoluto estándar. Cohorte ISS (n=10): 69±9 lpm pre-vuelo v+s 70±12 en vuelo. Informe NASA HRP describe descenso de FC en vuelo.
- Fuentes: https://www.sciencedirect.com/science/article/pii/S0735109723059673 ; https://www.sciencedirect.com/science/article/abs/pii/S1569904809000652 ; https://humanresearchroadmap.nasa.gov/Evidence/reports/Cardio%20Risk%20EB%202022%20FINAL_4-3-2023.pdf
- Fecha de revisión: 2026-11-14

## IND002 — Presión arterial sistólica (rangos y cambios en vuelo)

- ID: IND002
- Contexto: reposo
- Cambio esperado en vuelo: disminuye entre 8 y 10; máximo observado: −14 mmHg (de 120 a 106) en monitoreo de 24 h
- Unidad: mmHg
- Tipo de dato: Cambio vs. pre-misión
- Notas: 24 h: 120±10 pre-vuelo a 106±9 en vuelo (p<0.01), vuelve a 122±13 al aterrizar.
- Fuentes: https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.119.041050 ; https://www.researchgate.net/publication/334575694_Impact_of_Prolonged_Spaceflight_on_Orthostatic_Tolerance_During_Ambulation_and_Blood_Pressure_Profiles_in_Astronauts ; https://www.sciencedirect.com/science/article/pii/S0735109723059673
- Fecha de revisión: 2026-11-14

## IND003 — Presión arterial diastólica (rangos y cambios en vuelo)

- ID: IND003
- Contexto: reposo
- Cambio esperado en vuelo: ≈0 (sin cambio significativo en monitoreo de 24 h)
- Unidad: mmHg
- Tipo de dato: Cambio vs. pre-misión
- Notas: Sin cambio en 24 h (p=0.96). El informe NASA HRP describe, con estudios más antiguos, descenso de PA diastólica en vuelo; las fuentes no coinciden del todo.
- Fuentes: https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.119.041050 ; https://www.sciencedirect.com/science/article/pii/S0735109723059673 ; https://humanresearchroadmap.nasa.gov/Evidence/reports/Cardio%20Risk%20EB%202022%20FINAL_4-3-2023.pdf
- Fecha de revisión: 2026-11-14

## IND004 — Ritmo cardíaco (ECG) (rangos y cambios en vuelo)

- ID: IND004
- Contexto: reposo
- Cambio esperado en vuelo: Sin rango numérico; umbral de alerta: QTc >0.44 s
- Unidad: sin unidad
- Tipo de dato: Cualitativo / umbral de alerta
- Notas: NASA no documenta aumento sistemático de arritmias; hay casos aislados. QTc >0.44 s se observó tras misiones largas.
- Fuentes: https://ntrs.nasa.gov/api/citations/20100030585/downloads/20100030585.pdf ; https://ntrs.nasa.gov/citations/20170005625 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC6932198
- Fecha de revisión: 2026-11-14

## IND005 — Frecuencia respiratoria (rangos y cambios en vuelo)

- ID: IND005
- Contexto: reposo
- Valor mínimo de referencia: 12
- Valor máximo de referencia: 20
- Unidad: respiraciones/min
- Notas: No cambia con respecto a los rangos de la tierra
- Fuentes: https://publications.ersnet.org/content/erj/43/5/1459.full.pdf
- Fecha de revisión: 2026-11-14

## IND006 — Saturación de oxígeno (SpO2) (rangos y cambios en vuelo)

- ID: IND006
- Contexto: reposo
- Unidad: %
- Tipo de dato: Cambio vs. pre-misión
- Notas: ≈97 % en vuelo (Shuttle, con hipoxia leve). Un caso en ISS: SpO2 mínima nocturna 95 %. No es un rango estándar de agencia.
- Fuentes: https://www.ingentaconnect.com/contentone/asma/amhp/2017/00000088/00000006/art00004 ; https://asma.kglmeridian.com/view/journals/amhp/96/12/article-p1084.xml
- Fecha de revisión: 2026-11-14

## IND007 — Temperatura corporal central (rangos y cambios en vuelo)

- ID: IND007
- Contexto: ejercicio
- Cambio esperado en vuelo: +1.39 °C en el máximo durante ejercicio; en reposo +1.01 °C; pendiente 0.10 → 0.15 °C/min
- Unidad: °C
- Tipo de dato: Cambio vs. pre-misión
- Notas: 11 astronautas, ~6 meses en ISS. En algunos individuos superó 40 °C. Sin límite oficial de agencia en las fuentes consultadas.
- Fuentes: https://pmc.ncbi.nlm.nih.gov/articles/PMC5701078
- Fecha de revisión: 2026-11-14

## IND008 — Glucosa en sangre (rangos y cambios en vuelo)

- ID: IND008
- Contexto: reposo
- Valor mínimo de referencia: 70
- Valor máximo de referencia: 140
- Unidad: mg/dL
- Tipo de dato: Referencia terrestre (no oficial de agencia)
- Notas: 70–140 mg/dL es el rango de referencia (no ayunas) de la tabla del estudio Axiom-1. Valores en vuelo de ese estudio: 86 y 104 mg/dL (dos participantes, Ax-1.1 y Ax-1.2).
- Fuentes: https://www.sciencedirect.com/science/article/pii/S0025619624002726 ; https://pubmed.ncbi.nlm.nih.gov/3160438 ; https://journals.physiology.org/doi/pdf/10.1152/japplphysiol.00550.2019
- Fecha de revisión: 2026-11-14

## IND009 — Masa corporal (rangos y cambios en vuelo)

- ID: IND009
- Contexto: reposo
- Cambio esperado en vuelo: disminuye entre 2.8 % y 4.4 % (casi todo en los primeros 30 días)
- Unidad: kg
- Tipo de dato: Cambio vs. pre-misión
- Notas: 25 tripulantes medidos con dos dispositivos en ISS. ENERGY (≥3 meses): −1.2 kg (79.4→78.2 kg).
- Fuentes: https://www.ncbi.nlm.nih.gov/pubmed/25197887 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC10973451
- Fecha de revisión: 2026-11-14

## IND010 — Duración del sueño (rangos y cambios en vuelo)

- ID: IND010
- Contexto: reposo
- Valor mínimo de referencia: 7
- Valor máximo de referencia: 9
- Cambio esperado en vuelo: −0.3 h/día (≈18 min) vs. 3 meses pre-lanzamiento; media histórica en órbita 6–6.5 h
- Unidad: h
- Tipo de dato: Rango recomendado + cambio vs. pre-misión
- Notas: 7–9 h: rango de adulto citado por NASA-STD-3001. NASA programa 8.5 h. Datos recientes de ISS: 7.33±1.16 h por noche.
- Fuentes: https://www.nasa.gov/sites/default/files/atoms/files/sleep_accomodations_technical_brief_ochmo.pdf ; https://ntrs.nasa.gov/citations/20230003916 ; https://ntrs.nasa.gov/api/citations/20230003916/downloads/AsMA%20Poster.pdf ; https://www.news-medical.net/news/20140810/Space-missions-affect-sleep-patterns-in-astronauts.aspx
- Fecha de revisión: 2026-11-14

## IND011 — Estado de ánimo (rangos y cambios en vuelo)

- ID: IND011
- Contexto: reposo
- Cambio esperado en vuelo: Sin rango estándar; comparar contra línea base individual (POMS / BDI-2)
- Unidad: escala
- Tipo de dato: Sin rango estándar
- Notas: NASA usa POMS (diario) y BDI-2/CES-D (semanal). La fuente no da valores normales numéricos.
- Fuentes: https://ntrs.nasa.gov/api/citations/20260002661/downloads/Bell_APEX_IWS_2026_final.pdf
- Fecha de revisión: 2026-11-14

## IND012 — Fatiga autorreportada (rangos y cambios en vuelo)

- ID: IND012
- Contexto: reposo
- Cambio esperado en vuelo: Sin rango estándar; comparar contra línea base individual
- Unidad: escala
- Tipo de dato: Sin rango estándar
- Notas: La fuente reconoce la fatiga como problema operativo pero no da escala ni umbral numérico.
- Fuentes: https://ntrs.nasa.gov/api/citations/20140016946/downloads/20140016946.pdf
- Fecha de revisión: 2026-11-14

## IND014 — Presión parcial de CO2 en cabina (rangos y cambios en vuelo)

- ID: IND014
- Contexto: reposo
- Valor máximo de referencia: 4
- Cambio esperado en vuelo: Ambiente ISS ≈3–4 mmHg; PETCO2 de astronautas +6.1 mmHg en vuelo
- Unidad: mmHg
- Tipo de dato: Límite operativo / normativa
- Notas: Regla de vuelo: <4 mmHg (documento de 2015; otra copia del mismo texto dice 3). SMAC histórico: 10 mmHg (24 h) y 5.3 mmHg (7–180 d). NASA eliminó los SMAC de CO2 en jun-2024; confirmar el límite operativo vigente.
- Fuentes: https://ntrs.nasa.gov/api/citations/20240007713/downloads/JSC%2020584_SMACs_Rev%20C_FINAL.pdf ; https://ntrs.nasa.gov/api/citations/20150021777/downloads/20150021777.pdf ; https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/87/10/article-p894.pdf ; https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20160014530.pdf
- Fecha de revisión: 2026-11-14
