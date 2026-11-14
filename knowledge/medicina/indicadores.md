# Indicadores médicos

> **Fuente original:** `fuentes_originales/Indicadores.xlsx`  
> Conversión literal de todas las hojas y columnas. Las celdas vacías se marcan como `[REVISAR]`. Las fechas se muestran con el formato del Excel (aaaa-mm-dd).

## Hoja: 01_INDICADORES

| indicator_id | nombre | categoria | tipo_dato | unidad | metodo_medicion | frecuencia_medicion | descripcion | relevancia_espacial | fuente_id | fecha_revision | notas |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IND001 | Frecuencia cardíaca | cardiovascular | numerico | bpm | Sensores de pinza que miden oxígeno en la sangre simultáneamente con la frecuencia.<br>Bio-monitor<br>Cintas de pecho, electrodos | continua | Número de latidos del corazón por minuto | El corazón requiere menos esfuerzo para bombear sangre: pérdida de masa en ventrículo izq y pérdida de elasticidad en vasos sanguíneos. | SRC002 | 2026-11-12 | [REVISAR] |
| IND002 | Presión arterial sistólica | cardiovascular | numerico | mmHg | Tensiómetros<br>Monitores con manguitos de dedo<br>Ropa inteligente (bio-monitor) | diaria | Presión que ejerce la sangre sobre las arterias durante la contracción del corazón. | Sin gravedad suficiente, los fluidos se van hacia el pecho y la cabeza (las arterias superiores presentan una presión inusual). | SRC001 | 2026-11-12 | [REVISAR] |
| IND003 | Presión arterial diastólica | cardiovascular | numerico | mmHg | Tensiómetros<br>Monitores con manguitos de dedo<br>Ropa inteligente (bio-monitor) | diaria | Presión de la sangre sobre las arterias cuando el corazón se relaja. | Sin gravedad suficiente, los fluidos se van hacia el pecho y la cabeza (las arterias superiores presentan una presión inusual). | SRC001 | 2026-11-12 | [REVISAR] |
| IND004 | Ritmo cardíaco (ECG) | cardiovascular | categorico | sin unidad | Sensores de pinza que miden oxígeno en la sangre simultáneamente con la frecuencia.<br>Bio-monitor<br>Cintas de pecho, electrodos | ocasional | Registro de la actividad eléctrica del corazón, permite identificar el ritmo. | La falta de gravedad altera cómo circula la sangre | SRC002 | 2026-11-12 | Los astronautas pueden usar pantalones especiales que, gracias a las diferencias de presión, impulsan la sangre de vuelta al abdomen y las piernas. |
| IND005 | Frecuencia respiratoria | respiratorio | numerico | respiraciones/min | Bio-monitor | diaria | Número de respiraciones por minuto. | [REVISAR] | SRC003 | 2026-11-12 | [REVISAR] |
| IND006 | Saturación de oxígeno (SpO2) | respiratorio | numerico | % | Oxímetros de dedo | diaria | Porcentaje de hemoglobina que transporta oxígeno. | Al desplazarse los fluidos hacia el torso, puede ocurrir una leve congestión en los vasos pulmonares. | SRC004 | 2026-11-12 | En vuelos prolongados el sistema respiratorio vuelve a sus valores normales, por lo que no hay cambios significativos. |
| IND007 | Temperatura corporal central | termorregulacion | numerico | °C | Sensores térmicos de frente u oreja | diaria | Temperatura interna del cuerpo. | En el espacio el sudor se queda pegado a la piel en forma de película líquida, por lo que el cuerpo no irradia el exceso de calor de forma natural. Esto provoca un fenómeno crónico de estrés inflamatorio conocido como la "fiebre del espacio". | SRC005 | 2026-11-12 | [REVISAR] |
| IND008 | Glucosa en sangre | metabolico | numerico | mg/dL | Monitores continuos de glucosa (MCG), glucómetros tradicionales con tiras reactivas | ocasional | Concentración de glucosa en sangre. | [REVISAR] | SRC006 | 2026-11-12 | En 2025 se lanzaron estos instrumentos para medir la glucosa en sangre y evaluar posible monitoreo de este indicador en el espacio |
| IND009 | Masa corporal | metabolico | numerico | kg | Dispositivos SLAMMD y BMMD | semanal | Masa corporal de la persona | El cuerpo pierde masa muscular por la falta de gravedad. Los músculos se atrofian y los huesos pierden calcio. | SRC007 | 2026-11-12 | El dispositivo SLAMMD: brazo que ejerce una fuerza conocida sobre el astronauta y mide la aceleración. Por medio de F=ma calcula la masa.<br>El dispositivo BMMD / Massmeter: silla oscila hacia delante y hacia atrás. Mide el periodo de oscilación y calcula la masa con la frecuencia. |
| IND010 | Duración del sueño | sueno | numerico | h | Actígrafo, diarios de sueño | diaria | Horas dormidas por noche. | La falta de sueño lleva a un peor desempeño | SRC008 | 2026-11-13 | [REVISAR] |
| IND011 | Estado de ánimo | psicologico | escala | puntos | Entradas en diarios, encuestas digitales | diaria | Valoración del ánimo (escala). | Detectar cambios en la conducta de los astronautas permite la intervención temprana de problemas emocionales | SRC009 | 2026-11-13 | [REVISAR] |
| IND012 | Fatiga autorreportada | psicologico | escala | puntos | Cuestionarios, pruebas de reacción, bitácoras de sueño | diaria | Nivel de cansancio percibido (escala). | Medir la fatiga previene errores y protege la salud mental | SRC010 | 2026-11-13 | [REVISAR] |
| IND013 | Dosis equivalente de radiación | radiacion | numerico | mSv | Dosímetros personales en el cuerpo de los astronautas<br>Monitores ambientales dentro de la nave<br>Análisis biológicos avanzados | continua | Dosis de radiación ponderada por su efecto biológico. | No hay atmósfera que proteja. Aumenta el riesgo de cáncer, de problemas cardíacos y de cataratas. | SRC011 | 2026-11-13 | [REVISAR] |
| IND014 | Presión parcial de CO2 en cabina | ambiental | numerico | mmHg | El Major Constituent Analyzer (espectrómetro de masas) y el Spacecraft Atmosphere Monitor (SAM). Los astronautas también usan monitores personales de CO2 (Personal CO2 Monitor) | continua | Presión parcial del dióxido de carbono en el aire de la cabina. | El CO2 en la ISS es unas 10 veces mayor que en la superficie terrestre | SRC012 | 2026-11-13 | [REVISAR] |

## Hoja: LISTAS

Esta hoja contiene listas de valores independientes, una por columna; cada una se presenta como tabla separada.

### Lista: categoria

| categoria |
|---|
| cardiovascular |
| respiratorio |
| termorregulacion |
| metabolico |
| hematologico |
| renal_urinario |
| musculoesqueletico |
| ocular |
| neurologico_cognitivo |
| sueno |
| psicologico |
| radiacion |
| ambiental |
| infeccioso_inmune |
| digestivo |
| dental |
| dermatologico |
| toxicologico |
| descompresion |
| general |

### Lista: tipo_dato

| tipo_dato |
|---|
| numerico |
| escala |
| categorico |

### Lista: nivel_rango

| nivel_rango |
|---|
| critico_bajo |
| alerta_bajo |
| normal |
| alerta_alto |
| critico_alto |

### Lista: contexto

| contexto |
|---|
| reposo |
| ejercicio |
| sueno |
| cabina |
| eva |
| mision_general |

### Lista: estado

| estado |
|---|
| borrador |
| en_revision |
| aprobado |
| obsoleto |

### Lista: sino

| sino |
|---|
| 1 |
| 0 |

### Lista: gravedad

| gravedad |
|---|
| leve |
| moderada |
| grave |
| critica |

### Lista: nivel_atencion

| nivel_atencion |
|---|
| autocuidado |
| atencion_tripulacion |
| atencion_medica_remota |
| emergencia_critica |

### Lista: via_exposicion

| via_exposicion |
|---|
| inhalacion |
| contacto_piel |
| contacto_ojos |
| ingestion |
| radiacion |
| multiple |

### Lista: tipo_sustancia

| tipo_sustancia |
|---|
| gas |
| liquido |
| solido |
| aerosol_particulas |
| biologico |
| mixto |

### Lista: tipo_relacion

| tipo_relacion |
|---|
| causa |
| consecuencia |
| sintoma_de |
| factor_de_riesgo |
| se_altera |
| se_monitorea |
| se_trata_con |

### Lista: direccion

| direccion |
|---|
| aumenta |
| disminuye |
| varia |
| sin_cambio |

### Lista: rol_medicamento

| rol_medicamento |
|---|
| primera_linea |
| alternativa |
| complementario |
| evitar |

### Lista: grupo_terapeutico

| grupo_terapeutico |
|---|
| antibióticos |
| antifúngicos |
| antivirales |
| analgésicos_y_antiinflamatorios_no_opioides |
| analgésicos_opioides |
| anestésicos_locales_y_tópicos |
| anestésicos_generales_y_de_intubación |
| antihistamínicos_y_antialérgicos |
| descongestionantes_y_productos_nasales |
| broncodilatadores_y_antiasmáticos |
| corticoides_sistémicos |
| corticoides_tópicos |
| antidiarreicos_y_laxantes |
| antiácidos_y_protectores_gástricos |
| antieméticos_y_antivertiginosos |
| hipnóticos_e_inductores_del_sueño |
| estimulantes_del_sistema_nervioso_central |
| ansiolíticos_y_sedantes |
| antidepresivos |
| antipsicóticos |
| anticonvulsivantes |
| cardiovasculares |
| emergencia_y_soporte_vital |
| hormonales |
| urológicos |
| oftálmicos |
| óticos |
| dentales |
| cuidado_de_heridas |
| mal_de_altura |

### Lista: via_administracion

| via_administracion |
|---|
| oral |
| intravenosa |
| intramuscular |
| subcutanea |
| topica |
| oftalmica |
| inhalada |
| sublingual |
| rectal |
| intranasal |
| intraósea |
| ótica |

### Lista: tipo_alerta_med

| tipo_alerta_med |
|---|
| contraindicacion_alergia |
| contraindicacion_condicion |
| interaccion_medicamento |
| efecto_secundario |
| precaucion_espacial |

### Lista: confiabilidad

| confiabilidad |
|---|
| oficial_validada |
| revisada_por_pares |
| preprint |
| informe_tecnico |
| por_verificar |

### Lista: tipo_fuente

| tipo_fuente |
|---|
| manual_oficial |
| protocolo |
| articulo_cientifico |
| informe_tecnico |
| base_de_datos |
| ficha_seguridad |
| estandar |
| guia_clinica |

### Lista: fase_protocolo

| fase_protocolo |
|---|
| evaluacion |
| accion_inmediata |
| seguimiento |
| comunicacion |

### Lista: sexo_biologico

| sexo_biologico |
|---|
| femenino |
| masculino |

### Lista: grupo_sanguineo

| grupo_sanguineo |
|---|
| A+ |
| A- |
| B+ |
| B- |
| AB+ |
| AB- |
| O+ |
| O- |

### Lista: entidad_tipo

| entidad_tipo |
|---|
| condicion |
| sustancia |

### Lista: actividad

| actividad |
|---|
| reposo |
| ejercicio |
| sueno |
| trabajo |
| eva |
| comida |

### Lista: frecuencia_medicion

| frecuencia_medicion |
|---|
| continua |
| diaria |
| semanal |
| mensual |
| previa_y_posterior_a_mision |
| ocasional |

### Lista: poblacion_estudio

| poblacion_estudio |
|---|
| astronautas_en_orbita |
| astronautas_en_tierra |
| simulacion_analogo |
| poblacion_general_adulta |
| otra |

### Lista: tipo_antecedente

| tipo_antecedente |
|---|
| condicion |
| cirugia |
| antecedente_familiar |
| lesion |

### Lista: estado_actual

| estado_actual |
|---|
| activa |
| controlada |
| resuelta |

## Hoja: 08_FUENTES

| source_id | titulo | institucion | autor | año | enlace | tipo | fecha_consulta | confiabilidad | notas |
|---|---|---|---|---|---|---|---|---|---|
| SRC001 | Cardiovascular Health in Microgravity | NASA | NASA | 2020 | https://www.nasa.gov/missions/station/cardiovascular-health-in-microgravity/ | estandar | 2026-11-12 | oficial_validada | [REVISAR] |
| SRC002 | Evidence Based Review: Risk of Cardiac Rhythm Problems during Spaceflight | NASA | Platts, S. H., Stenger, M .B., Phillips, T. R., Brown, A. K., Arzeno N. M., Levine, B., Summers, R. | 2009 | https://ntrs.nasa.gov/api/citations/20100017571/downloads/20100017571.pdf | estandar | 2026-11-12 | oficial_validada | [REVISAR] |
| SRC003 | CARDIOBREATH: Taking a deep dive into astronaut health | Canadian Space Agency | Blaber, A.., Tavakolian, K. | 2025 | https://www.asc-csa.gc.ca/eng/sciences/cardiobreath.asp | articulo_cientifico | 2026-11-12 | por_verificar | [REVISAR] |
| SRC004 | MEDICINA HUMANA ESPACIAL: PERFORMANCE FISIOLÓGICO Y CONTRAMEDIDAS PARA MEJORAR LA SALUD DEL ASTRONAUTA | Facultad de Medicina Humana URP | Rivera, M. V., Cornejo, J., Huallpayunca, K., Diaz, A. B., Ortiz-Benique, Z. N., Reina, A. D., Jamanza Lino, G., Ticllacuri, V. | 2020 | https://www.scielo.org.pe/pdf/rfmh/v20n2/2308-0531-rfmh-20-02-303.pdf | articulo_cientifico | 2026-11-12 | por_verificar | [REVISAR] |
| SRC005 | Researchers: Help NASA Find Practical Ways to Monitor Astronaut Body Temperature in Low Earth Orbit | NASA | NASA | 2026 | https://www.nasa.gov/help-nasa-find-practical-ways-to-monitor-astronaut-body-temperature-in-low-earth-orbit/ | base_de_datos | 2026-11-12 | por_verificar | [REVISAR] |
| SRC006 | New Space-Based Research May Pave the Way for First Astronaut with Diabetes | ISS National Laboratory | O'Neill P. | 2025 | https://issnationallab.org/press-releases/ax4-suite-ride-diabetes-research/ | estandar | 2026-11-13 | por_verificar | [REVISAR] |
| SRC007 | Body mass changes during long-duration spaceflight | Aviat Space Environ Med. | Zwart SR, Launius RD, Coen GK, Morgan JL, Charles JB, Smith SM. | 2014 | https://pubmed.ncbi.nlm.nih.gov/25197887/ | informe_tecnico | 2026-11-13 | por_verificar | [REVISAR] |
| SRC008 | Wearable Tech for Space Station Research | NASA | Gaskill, M. L. | 2024 | https://www.nasa.gov/missions/station/iss-research/wearable-tech-for-space-station-research/ | articulo_cientifico | 2026-11-13 | por_verificar | [REVISAR] |
| SRC009 | Mental Well-Being in Space | NASA | Gaskill, M. L. | 2024 | https://www.nasa.gov/missions/station/iss-research/mental-well-being-in-space/ | articulo_cientifico | 2026-11-13 | por_verificar | [REVISAR] |
| SRC010 | Standard Measures for Use in Analog Studies, ISS,<br>and Research for Long-Duration Exploration Missions | NASA | Wenzel, E. M. | 2021 | https://ntrs.nasa.gov/api/citations/20210021987/downloads/NASA_TM20210021987.pdf | informe_tecnico | 2026-11-13 | por_verificar | [REVISAR] |
| SRC011 | Radi-N2: Tracking space radiation and its risks | Canadian Space Agency | CSA | 2025 | https://www.asc-csa.gc.ca/eng/sciences/radi-n2.asp | estandar | 2026-11-13 | por_verificar | [REVISAR] |
| SRC012 | Calibration and Performance of the Spacecraft<br>Atmosphere Monitor, an Air Constituent<br>Monitor for Human Spaceflight | California Institute of Technology | M. Darrach, B. Bae, D. Fu, V. Garkanian, M. L. Homer, R. D. Kidd, C. Jung-Kubiak, H. Krause, F. Maiwald, S. Madzunkov, C. Malone, D. Nikolic, M. Rais-Zadeh, J. Simcic, T. Tillmans, y F. Zhong | 2023 | https://ttu-ir.tdl.org/server/api/core/bitstreams/42e856c5-2e26-4da8-a44f-669a3ef8015f/content | articulo_cientifico | 2026-11-13 | por_verificar | [REVISAR] |
| SRC013 | 3.001 MEDICAL KIT- CONTENTS AND REFERENCE | NASA | NASA | 2009 | https://www.nasa.gov/wp-content/uploads/2015/03/medical_kit_checklist_-_full_release.pdf | ficha_seguridad | 2026-11-13 | por_verificar | [REVISAR] |
| SRC014 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | por_verificar | [REVISAR] |
| SRC015 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | articulo_cientifico | [REVISAR] | por_verificar | [REVISAR] |
| SRC016 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | ficha_seguridad | [REVISAR] | por_verificar | [REVISAR] |
| SRC017 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC018 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | estandar | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC019 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | estandar | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC020 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC021 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | articulo_cientifico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC022 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC023 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | articulo_cientifico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC024 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC025 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | estandar | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC026 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | estandar | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC027 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC028 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | articulo_cientifico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC029 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC030 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC031 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | articulo_cientifico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC032 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | informe_tecnico | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC033 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC034 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC035 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] |
| SRC036 | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] | [REVISAR] |

## Hoja: DICCIONARIO

| hoja | columna | tipo | obligatorio | valores_permitidos | ejemplo | descripcion |
|---|---|---|---|---|---|---|
| 01_INDICADORES | indicator_id | id | sí | [REVISAR] | IND001 | Identificador único del indicador. |
| 01_INDICADORES | nombre | texto | sí | [REVISAR] | Frecuencia cardíaca | Nombre del indicador. |
| 01_INDICADORES | categoria | lista | sí | lista: cardiovascular, respiratorio, termorregulacion, metabolico, hematologico, renal_urinario, musculoesqueletico, ocular, neurologico_cognitivo, sueno, psicologico, radiacion, ambiental, infeccioso_inmune, digestivo, dental, dermatologico, toxicologico, descompresion, general | cardiovascular | Sistema u origen del indicador. |
| 01_INDICADORES | tipo_dato | lista | sí | lista: numerico, escala, categorico | numerico | numerico, escala o categorico. |
| 01_INDICADORES | unidad | texto | sí | [REVISAR] | bpm | Unidad estándar de medición (sugerida; verificar con la fuente). |
| 01_INDICADORES | metodo_medicion | texto | sí | [REVISAR] | Sensor cardíaco | Cómo se mide en la nave. |
| 01_INDICADORES | frecuencia_medicion | lista | no | lista: continua, diaria, semanal, mensual, previa_y_posterior_a_mision, ocasional | continua | Cada cuánto se mide. |
| 01_INDICADORES | descripcion | texto_largo | sí | [REVISAR] | Latidos por minuto | Qué mide. |
| 01_INDICADORES | relevancia_espacial | texto_largo | sí | [REVISAR] | [REVISAR] | Por qué importa en microgravedad/misión. |
| 01_INDICADORES | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente científica de este dato (hoja 08_FUENTES). Sin fuente no se aprueba. |
| 01_INDICADORES | version | texto | sí | [REVISAR] | v1.0 | Versión del dato o del protocolo. |
| 01_INDICADORES | fecha_revision | fecha | sí | [REVISAR] | 2026-11-12 | Cuándo se verificó el dato contra la fuente (AAAA-MM-DD). |
| 01_INDICADORES | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Solo los registros con estado = aprobado deben ser usados por el asistente. |
| 01_INDICADORES | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios libres (población estudiada, condiciones, dudas). |
| 02_ENFERMEDADES | condition_id | id | sí | [REVISAR] | CON001 | Identificador único de la condición. |
| 02_ENFERMEDADES | nombre | texto | sí | [REVISAR] | Síndrome neuro-ocular asociado a vuelos espaciales | Nombre en español. |
| 02_ENFERMEDADES | nombre_en | texto | no | [REVISAR] | Spaceflight Associated Neuro-ocular Syndrome | Nombre en inglés (útil para buscar en fuentes de NASA/ESA). |
| 02_ENFERMEDADES | categoria | lista | sí | lista: cardiovascular, respiratorio, termorregulacion, metabolico, hematologico, renal_urinario, musculoesqueletico, ocular, neurologico_cognitivo, sueno, psicologico, radiacion, ambiental, infeccioso_inmune, digestivo, dental, dermatologico, toxicologico, descompresion, general | ocular | Sistema afectado. |
| 02_ENFERMEDADES | descripcion | texto_largo | sí | [REVISAR] | [REVISAR] | Qué es. |
| 02_ENFERMEDADES | factores_riesgo | texto_largo | sí | [REVISAR] | [REVISAR] | Factores asociados (un factor por frase, separados por ;). |
| 02_ENFERMEDADES | relacion_espacial | texto_largo | sí | [REVISAR] | [REVISAR] | Relación con los peligros del vuelo espacial. |
| 02_ENFERMEDADES | gravedad_tipica | lista | sí | lista: leve, moderada, grave, critica | moderada | Gravedad habitual según la fuente. |
| 02_ENFERMEDADES | requiere_contacto_tierra | booleano | sí | lista: True, False | TRUE | ¿Debe contactarse al equipo médico terrestre? |
| 02_ENFERMEDADES | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente científica de este dato (hoja 08_FUENTES). Sin fuente no se aprueba. |
| 02_ENFERMEDADES | version | texto | sí | [REVISAR] | v1.0 | Versión del dato o del protocolo. |
| 02_ENFERMEDADES | fecha_revision | fecha | sí | [REVISAR] | 2026-11-12 | Cuándo se verificó el dato contra la fuente (AAAA-MM-DD). |
| 02_ENFERMEDADES | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Solo los registros con estado = aprobado deben ser usados por el asistente. |
| 02_ENFERMEDADES | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios libres (población estudiada, condiciones, dudas). |
| 03_MEDICAMENTOS | medication_id | id | sí | [REVISAR] | MED001 | Identificador único del medicamento. |
| 03_MEDICAMENTOS | nombre_generico | texto | sí | [REVISAR] | Paracetamol | Principio activo. |
| 03_MEDICAMENTOS | nombre_comercial | texto | no | [REVISAR] | [REVISAR] | Nombre comercial, si aplica. |
| 03_MEDICAMENTOS | grupo_terapeutico | lista | sí | lista: analgesico_antiinflamatorio, antialergico_emergencia, antiemetico, sueno_estimulante, descongestionante, antibiotico, antiviral_antifungico, gastrointestinal, cardiovascular, respiratorio, oftalmico, dermatologico, fluidos, otro | analgesico_antiinflamatorio | Grupo terapéutico. |
| 03_MEDICAMENTOS | uso_medico | texto_largo | sí | [REVISAR] | [REVISAR] | Para qué se utiliza (según la fuente oficial). |
| 03_MEDICAMENTOS | via_administracion | lista | sí | lista: oral, intravenosa, intramuscular, subcutanea, topica, oftalmica, inhalada, sublingual, rectal | oral | Vía de administración. |
| 03_MEDICAMENTOS | presentacion | texto | no | [REVISAR] | [REVISAR] | Forma farmacéutica y concentración. |
| 03_MEDICAMENTOS | condiciones_almacenamiento | texto | sí | [REVISAR] | [REVISAR] | Temperatura, luz, humedad. |
| 03_MEDICAMENTOS | estabilidad_espacial | texto_largo | no | [REVISAR] | [REVISAR] | Cambios de estabilidad en misión prolongada / radiación. |
| 03_MEDICAMENTOS | disponibilidad_mision | booleano | sí | lista: True, False | TRUE | ¿Está en el inventario médico de la misión? |
| 03_MEDICAMENTOS | requiere_supervision_medica | booleano | sí | lista: True, False | TRUE | ¿Su uso requiere indicación de personal médico autorizado? |
| 03_MEDICAMENTOS | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente científica de este dato (hoja 08_FUENTES). Sin fuente no se aprueba. |
| 03_MEDICAMENTOS | version | texto | sí | [REVISAR] | v1.0 | Versión del dato o del protocolo. |
| 03_MEDICAMENTOS | fecha_revision | fecha | sí | [REVISAR] | 2026-11-12 | Cuándo se verificó el dato contra la fuente (AAAA-MM-DD). |
| 03_MEDICAMENTOS | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Solo los registros con estado = aprobado deben ser usados por el asistente. |
| 03_MEDICAMENTOS | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios libres (población estudiada, condiciones, dudas). |
| 04_PROTOCOLOS | protocol_id | id | sí | [REVISAR] | PRO001 | Identificador único del protocolo. |
| 04_PROTOCOLOS | emergencia | texto | sí | [REVISAR] | Reacción alérgica / anafilaxia | Nombre de la situación. |
| 04_PROTOCOLOS | categoria | lista | sí | lista: cardiovascular, respiratorio, termorregulacion, metabolico, hematologico, renal_urinario, musculoesqueletico, ocular, neurologico_cognitivo, sueno, psicologico, radiacion, ambiental, infeccioso_inmune, digestivo, dental, dermatologico, toxicologico, descompresion, general | infeccioso_inmune | Sistema u origen. |
| 04_PROTOCOLOS | nivel_atencion | lista | sí | lista: autocuidado, atencion_tripulacion, atencion_medica_remota, emergencia_critica | emergencia_critica | Nivel de atención según el protocolo oficial. |
| 04_PROTOCOLOS | sintomas_reconocibles | texto_largo | sí | [REVISAR] | [REVISAR] | Cómo reconocerla (resumen; el detalle va en 15_SINTOMAS). |
| 04_PROTOCOLOS | evaluacion_inicial | texto_largo | sí | [REVISAR] | [REVISAR] | Qué información recopilar primero. |
| 04_PROTOCOLOS | contacto_tierra_inmediato | booleano | sí | lista: True, False | TRUE | ¿Contactar de inmediato a la Tierra? |
| 04_PROTOCOLOS | cuando_contactar_tierra | texto_largo | sí | [REVISAR] | [REVISAR] | Criterios de comunicación. |
| 04_PROTOCOLOS | documento_oficial | texto | no | [REVISAR] | [REVISAR] | Nombre del manual/checklist oficial del que sale. |
| 04_PROTOCOLOS | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente científica de este dato (hoja 08_FUENTES). Sin fuente no se aprueba. |
| 04_PROTOCOLOS | version | texto | sí | [REVISAR] | v1.0 | Versión del dato o del protocolo. |
| 04_PROTOCOLOS | fecha_revision | fecha | sí | [REVISAR] | 2026-11-12 | Cuándo se verificó el dato contra la fuente (AAAA-MM-DD). |
| 04_PROTOCOLOS | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Solo los registros con estado = aprobado deben ser usados por el asistente. |
| 04_PROTOCOLOS | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios libres (población estudiada, condiciones, dudas). |
| 05_SUSTANCIAS | substance_id | id | sí | [REVISAR] | SUB001 | Identificador único de la sustancia. |
| 05_SUSTANCIAS | nombre | texto | sí | [REVISAR] | Dióxido de carbono | Nombre de la sustancia. |
| 05_SUSTANCIAS | nombre_en | texto | no | [REVISAR] | Carbon dioxide | Nombre en inglés. |
| 05_SUSTANCIAS | formula | texto | no | [REVISAR] | CO₂ | Fórmula química. |
| 05_SUSTANCIAS | tipo | lista | sí | lista: gas, liquido, solido, aerosol_particulas, biologico, mixto | gas | Estado/tipo. |
| 05_SUSTANCIAS | origen_en_nave | texto_largo | sí | [REVISAR] | [REVISAR] | De dónde viene (metabolismo, equipos, materiales...). |
| 05_SUSTANCIAS | riesgo | texto_largo | sí | [REVISAR] | [REVISAR] | Tipo de peligro. |
| 05_SUSTANCIAS | via_exposicion | lista | sí | lista: inhalacion, contacto_piel, contacto_ojos, ingestion, radiacion, multiple | inhalacion | Vía principal. |
| 05_SUSTANCIAS | deteccion | texto | sí | [REVISAR] | [REVISAR] | Cómo se detecta (sensor, olor, análisis). |
| 05_SUSTANCIAS | limite_exposicion_valor | numero | no | [REVISAR] | [REVISAR] | Límite de exposición (p. ej. SMAC) – valor numérico. |
| 05_SUSTANCIAS | limite_exposicion_unidad | texto | no | [REVISAR] | [REVISAR] | Unidad del límite (ppm, mg/m³, mmHg...). |
| 05_SUSTANCIAS | limite_exposicion_duracion | texto | no | [REVISAR] | [REVISAR] | Duración a la que aplica el límite (1 h, 24 h, 1000 días...). |
| 05_SUSTANCIAS | acciones_seguridad | texto_largo | sí | [REVISAR] | [REVISAR] | Procedimientos oficiales (el detalle por pasos va en 11_PASOS_PROTOCOLO). |
| 05_SUSTANCIAS | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente científica de este dato (hoja 08_FUENTES). Sin fuente no se aprueba. |
| 05_SUSTANCIAS | version | texto | sí | [REVISAR] | v1.0 | Versión del dato o del protocolo. |
| 05_SUSTANCIAS | fecha_revision | fecha | sí | [REVISAR] | 2026-11-12 | Cuándo se verificó el dato contra la fuente (AAAA-MM-DD). |
| 05_SUSTANCIAS | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Solo los registros con estado = aprobado deben ser usados por el asistente. |
| 05_SUSTANCIAS | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios libres (población estudiada, condiciones, dudas). |
| 06_HISTORIAL | astronaut_id | id | sí | [REVISAR] | AST001 | Identificador anónimo. Nunca usar nombres. |
| 06_HISTORIAL | es_ficticio | booleano | sí | lista: True, False | TRUE | TRUE mientras sea prototipo con datos sintéticos. |
| 06_HISTORIAL | fecha_nacimiento | fecha | sí | [REVISAR] | 1990-01-01 | AAAA-MM-DD. |
| 06_HISTORIAL | sexo_biologico | lista | no | lista: femenino, masculino | femenino | Relevante para valores de referencia y medicación. |
| 06_HISTORIAL | peso_kg | numero | no | [REVISAR] | 65 | Peso en kg. |
| 06_HISTORIAL | altura_cm | numero | no | [REVISAR] | 168 | Altura en cm. |
| 06_HISTORIAL | grupo_sanguineo | lista | no | lista: A+, A-, B+, B-, AB+, AB-, O+, O- | O+ | Si está disponible. |
| 06_HISTORIAL | restricciones | texto | no | [REVISAR] | Ninguna | Restricciones médicas relevantes. |
| 06_HISTORIAL | fecha_actualizacion | fecha | sí | [REVISAR] | 2026-11-12 | Última actualización del registro. |
| 07_MEDICIONES | measurement_id | id | sí | [REVISAR] | M001 | Identificador único de la medición. |
| 07_MEDICIONES | astronaut_id | id | sí | ID existente en 06_HISTORIAL | AST001 | A quién pertenece (hoja 06_HISTORIAL). |
| 07_MEDICIONES | indicator_id | id | sí | ID existente en 01_INDICADORES | IND001 | Qué se midió (hoja 01_INDICADORES). |
| 07_MEDICIONES | fecha_hora | fecha_hora | sí | [REVISAR] | 2026-11-12 08:00 | Momento de la medición. |
| 07_MEDICIONES | valor | numero | sí | [REVISAR] | 75 | Resultado numérico (sin unidades en la celda). |
| 07_MEDICIONES | unidad | texto | sí | [REVISAR] | bpm | Debe coincidir con la unidad del indicador. |
| 07_MEDICIONES | actividad | lista | sí | lista: reposo, ejercicio, sueno, trabajo, eva, comida | reposo | Contexto: reposo, ejercicio, sueño... |
| 07_MEDICIONES | mission_day | numero | sí | [REVISAR] | 1 | Día de misión. |
| 07_MEDICIONES | observaciones | texto | no | [REVISAR] | [REVISAR] | Información adicional. |
| 08_FUENTES | source_id | id | sí | [REVISAR] | SRC001 | Identificador único de la fuente. |
| 08_FUENTES | titulo | texto_largo | sí | [REVISAR] | [REVISAR] | Nombre del documento. |
| 08_FUENTES | institucion | texto | sí | [REVISAR] | NASA | NASA, ESA, OMS, revista... |
| 08_FUENTES | autor | texto | no | [REVISAR] | [REVISAR] | Autor o institución responsable. |
| 08_FUENTES | anio | numero | sí | [REVISAR] | 2020 | Año de publicación. |
| 08_FUENTES | enlace | texto | sí | [REVISAR] | [REVISAR] | URL directa. |
| 08_FUENTES | tipo | lista | sí | lista: manual_oficial, protocolo, articulo_cientifico, informe_tecnico, base_de_datos, ficha_seguridad, estandar, guia_clinica | manual_oficial | Tipo de documento. |
| 08_FUENTES | licencia | texto | no | [REVISAR] | [REVISAR] | Condiciones de uso. |
| 08_FUENTES | fecha_consulta | fecha | sí | [REVISAR] | 2026-11-12 | Cuándo se revisó. |
| 08_FUENTES | confiabilidad | lista | sí | lista: oficial_validada, revisada_por_pares, preprint, informe_tecnico, por_verificar | por_verificar | Estado de validación científica. |
| 08_FUENTES | notas | texto | no | [REVISAR] | [REVISAR] | Qué datos se sacaron de aquí. |
| 09_REL_CONDICION_INDICADOR | condition_id | id | sí | ID existente en 02_ENFERMEDADES | CON001 | Condición (02_ENFERMEDADES). |
| 09_REL_CONDICION_INDICADOR | indicator_id | id | sí | ID existente en 01_INDICADORES | IND001 | Indicador relacionado (01_INDICADORES). |
| 09_REL_CONDICION_INDICADOR | nombre_condicion | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 09_REL_CONDICION_INDICADOR | nombre_indicador | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 09_REL_CONDICION_INDICADOR | tipo_relacion | lista | sí | lista: causa, consecuencia, sintoma_de, factor_de_riesgo, se_altera, se_monitorea, se_trata_con | se_altera | Tipo de relación. |
| 09_REL_CONDICION_INDICADOR | direccion | lista | sí | lista: aumenta, disminuye, varia, sin_cambio | aumenta | Cómo cambia el indicador. |
| 09_REL_CONDICION_INDICADOR | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 09_REL_CONDICION_INDICADOR | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 09_REL_CONDICION_INDICADOR | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 10_RANGOS_REFERENCIA | indicator_id | id | sí | ID existente en 01_INDICADORES | IND001 | Indicador (01_INDICADORES). |
| 10_RANGOS_REFERENCIA | nombre_indicador | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 10_RANGOS_REFERENCIA | nivel | lista | sí | lista: critico_bajo, alerta_bajo, normal, alerta_alto, critico_alto | normal | Nivel del rango. Un indicador tiene un rango por nivel. |
| 10_RANGOS_REFERENCIA | contexto | lista | sí | lista: reposo, ejercicio, sueno, cabina, eva, mision_general | reposo | Condición de medición. |
| 10_RANGOS_REFERENCIA | valor_min | numero | sí | [REVISAR] | 60 | Límite inferior (vacío si no aplica). |
| 10_RANGOS_REFERENCIA | valor_max | numero | sí | [REVISAR] | 100 | Límite superior (vacío si no aplica). |
| 10_RANGOS_REFERENCIA | unidad | texto | sí | [REVISAR] | bpm | Unidad del rango. |
| 10_RANGOS_REFERENCIA | poblacion_estudio | lista | sí | lista: astronautas_en_orbita, astronautas_en_tierra, simulacion_analogo, poblacion_general_adulta, otra | astronautas_en_orbita | Población en la que se obtuvo el rango. |
| 10_RANGOS_REFERENCIA | aplica_microgravedad | booleano | sí | lista: True, False | TRUE | ¿El rango fue medido/validado en microgravedad? |
| 10_RANGOS_REFERENCIA | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 10_RANGOS_REFERENCIA | version | texto | sí | [REVISAR] | v1.0 | Versión. |
| 10_RANGOS_REFERENCIA | fecha_revision | fecha | sí | [REVISAR] | 2026-11-12 | Fecha de verificación. |
| 10_RANGOS_REFERENCIA | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 10_RANGOS_REFERENCIA | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 11_PASOS_PROTOCOLO | protocol_id | id | sí | ID existente en 04_PROTOCOLOS | PRO001 | Protocolo (04_PROTOCOLOS). |
| 11_PASOS_PROTOCOLO | emergencia | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 11_PASOS_PROTOCOLO | orden | numero | sí | [REVISAR] | 1 | Número del paso (1, 2, 3...). |
| 11_PASOS_PROTOCOLO | fase | lista | sí | lista: evaluacion, accion_inmediata, seguimiento, comunicacion | evaluacion | Fase del protocolo. |
| 11_PASOS_PROTOCOLO | paso | texto_largo | sí | [REVISAR] | [REVISAR] | Instrucción tal como la indica el protocolo oficial. |
| 11_PASOS_PROTOCOLO | requiere_confirmacion | booleano | sí | lista: True, False | TRUE | ¿El asistente debe pedir confirmación antes de pasar al siguiente? |
| 11_PASOS_PROTOCOLO | advertencia | texto | no | [REVISAR] | [REVISAR] | Precaución asociada al paso. |
| 11_PASOS_PROTOCOLO | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 11_PASOS_PROTOCOLO | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 11_PASOS_PROTOCOLO | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 12_REL_PROTOCOLO_MEDICAMENTO | protocol_id | id | sí | ID existente en 04_PROTOCOLOS | PRO001 | Protocolo (04_PROTOCOLOS). |
| 12_REL_PROTOCOLO_MEDICAMENTO | medication_id | id | sí | ID existente en 03_MEDICAMENTOS | MED001 | Medicamento (03_MEDICAMENTOS). |
| 12_REL_PROTOCOLO_MEDICAMENTO | nombre_emergencia | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 12_REL_PROTOCOLO_MEDICAMENTO | nombre_medicamento | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 12_REL_PROTOCOLO_MEDICAMENTO | rol | lista | sí | lista: primera_linea, alternativa, complementario, evitar | primera_linea | Rol del medicamento en el protocolo. |
| 12_REL_PROTOCOLO_MEDICAMENTO | condicion_de_uso | texto_largo | sí | [REVISAR] | [REVISAR] | Cuándo se contempla, según el protocolo aprobado. |
| 12_REL_PROTOCOLO_MEDICAMENTO | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 12_REL_PROTOCOLO_MEDICAMENTO | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 12_REL_PROTOCOLO_MEDICAMENTO | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 13_REL_PROTOCOLO_CONDICION | protocol_id | id | sí | ID existente en 04_PROTOCOLOS | PRO001 | Protocolo (04_PROTOCOLOS). |
| 13_REL_PROTOCOLO_CONDICION | condition_id | id | sí | ID existente en 02_ENFERMEDADES | CON001 | Condición (02_ENFERMEDADES). |
| 13_REL_PROTOCOLO_CONDICION | nombre_emergencia | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 13_REL_PROTOCOLO_CONDICION | nombre_condicion | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 13_REL_PROTOCOLO_CONDICION | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 13_REL_PROTOCOLO_CONDICION | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 13_REL_PROTOCOLO_CONDICION | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 14_REL_PROTOCOLO_SUSTANCIA | protocol_id | id | sí | ID existente en 04_PROTOCOLOS | PRO007 | Protocolo (04_PROTOCOLOS). |
| 14_REL_PROTOCOLO_SUSTANCIA | substance_id | id | sí | ID existente en 05_SUSTANCIAS | SUB001 | Sustancia (05_SUSTANCIAS). |
| 14_REL_PROTOCOLO_SUSTANCIA | nombre_emergencia | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 14_REL_PROTOCOLO_SUSTANCIA | nombre_sustancia | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 14_REL_PROTOCOLO_SUSTANCIA | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 14_REL_PROTOCOLO_SUSTANCIA | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 14_REL_PROTOCOLO_SUSTANCIA | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 15_SINTOMAS | entidad_tipo | lista | sí | lista: condicion, sustancia | condicion | condicion o sustancia. |
| 15_SINTOMAS | entidad_id | texto | sí | [REVISAR] | CON001 | condition_id o substance_id correspondiente. |
| 15_SINTOMAS | sintoma | texto | sí | [REVISAR] | Visión borrosa | Un síntoma por fila, escrito siempre igual (sin sinónimos). |
| 15_SINTOMAS | es_signo_alarma | booleano | sí | lista: True, False | TRUE | ¿Es un signo de alarma que escala la emergencia? |
| 15_SINTOMAS | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 15_SINTOMAS | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 15_SINTOMAS | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 16_MED_ALERTAS | medication_id | id | sí | ID existente en 03_MEDICAMENTOS | MED001 | Medicamento (03_MEDICAMENTOS). |
| 16_MED_ALERTAS | nombre_medicamento | formula | auto | automático (fórmula) | [REVISAR] | Se llena sola. |
| 16_MED_ALERTAS | tipo_alerta | lista | sí | lista: contraindicacion_alergia, contraindicacion_condicion, interaccion_medicamento, efecto_secundario, precaucion_espacial | contraindicacion_alergia | Tipo de alerta. |
| 16_MED_ALERTAS | sustancia_o_condicion | texto | sí | [REVISAR] | Penicilinas | Alergeno, condición o medicamento implicado (escrito siempre igual). |
| 16_MED_ALERTAS | gravedad | lista | sí | lista: leve, moderada, grave, critica | grave | Gravedad. |
| 16_MED_ALERTAS | descripcion | texto_largo | sí | [REVISAR] | [REVISAR] | Detalle de la alerta. |
| 16_MED_ALERTAS | fuente_id | id | sí | ID existente en 08_FUENTES | SRC001 | Fuente (08_FUENTES). |
| 16_MED_ALERTAS | estado | lista | sí | lista: borrador, en_revision, aprobado, obsoleto | borrador | Estado de validación. |
| 16_MED_ALERTAS | notas | texto | no | [REVISAR] | [REVISAR] | Comentarios. |
| 17_HIST_ALERGIAS | astronaut_id | id | sí | ID existente en 06_HISTORIAL | AST001 | Astronauta (06_HISTORIAL). |
| 17_HIST_ALERGIAS | alergeno | texto | sí | [REVISAR] | Penicilinas | Escribir igual que en 16_MED_ALERTAS para poder cruzar. |
| 17_HIST_ALERGIAS | reaccion | texto | no | [REVISAR] | Urticaria | Reacción observada. |
| 17_HIST_ALERGIAS | gravedad | lista | sí | lista: leve, moderada, grave, critica | moderada | Gravedad. |
| 17_HIST_ALERGIAS | fecha_actualizacion | fecha | sí | [REVISAR] | 2026-11-12 | Última actualización. |
| 18_HIST_ANTECEDENTES | astronaut_id | id | sí | ID existente en 06_HISTORIAL | AST001 | Astronauta (06_HISTORIAL). |
| 18_HIST_ANTECEDENTES | tipo | lista | sí | lista: condicion, cirugia, antecedente_familiar, lesion | cirugia | Tipo de antecedente. |
| 18_HIST_ANTECEDENTES | descripcion | texto | sí | [REVISAR] | Apendicectomía | Descripción. |
| 18_HIST_ANTECEDENTES | fecha_o_anio | texto | no | [REVISAR] | 2012 | Fecha o año aproximado. |
| 18_HIST_ANTECEDENTES | estado_actual | lista | sí | lista: activa, controlada, resuelta | resuelta | Estado actual. |
| 18_HIST_ANTECEDENTES | condition_id | id | no | ID existente en 02_ENFERMEDADES | [REVISAR] | Si corresponde a una condición del catálogo (02_ENFERMEDADES). |
| 19_HIST_MEDICAMENTOS | astronaut_id | id | sí | ID existente en 06_HISTORIAL | AST002 | Astronauta (06_HISTORIAL). |
| 19_HIST_MEDICAMENTOS | medication_id | id | no | ID existente en 03_MEDICAMENTOS | MED001 | Medicamento del catálogo (03_MEDICAMENTOS), si está. |
| 19_HIST_MEDICAMENTOS | nombre_medicamento | texto | sí | [REVISAR] | [REVISAR] | Nombre del medicamento tal como lo toma el astronauta. |
| 19_HIST_MEDICAMENTOS | dosis_prescrita | texto | no | [REVISAR] | [REVISAR] | Según la prescripción del médico (no la define el asistente). |
| 19_HIST_MEDICAMENTOS | frecuencia | texto | no | [REVISAR] | [REVISAR] | Frecuencia prescrita. |
| 19_HIST_MEDICAMENTOS | fecha_inicio | fecha | no | [REVISAR] | 2026-01-01 | AAAA-MM-DD. |
| 19_HIST_MEDICAMENTOS | fecha_fin | fecha | no | [REVISAR] | [REVISAR] | Vacío si continúa. |
