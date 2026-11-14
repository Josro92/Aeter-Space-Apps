# Médico Virtual (Aéter) — estado del proyecto

Actualizado: viernes 13 de noviembre de 2026, 23:40 (hora de Costa Rica).
Presentación al jurado: domingo 15 de noviembre de 2026, aprox. 20:00.

## Qué es
Un médico virtual para un astronauta en una misión sin comunicación con la Tierra. Vive dentro de la página Aéter (copia de la app Streamlit del equipo). Conversa por voz y por texto, lee la ficha y los signos vitales en vivo, y su conocimiento médico sale solo de los archivos de `knowledge/`.

- Repositorio: `Josro92/Aeter-Space-Apps`, rama `medico-virtual` (fork de `larivr/Aeter-Space-Apps`, rama `mainn`).
- Despliegue: Streamlit Cloud, rama `medico-virtual`, archivo `app.py`. Secrets: `GEMINI_API_KEY` (nunca en el chat ni en el repositorio).
- Modelo: Gemini (configurable en `config/modelos.yaml`). Claude queda como proveedor inactivo hasta tener llave.

## Qué funciona hoy
- Portada con botón «Iniciar» (ese toque activa el audio y el micrófono). Espacio para `assets/logo.png`.
- Voz manos libres: saluda, escucha continuo, palabra de llamado «médico», conversación abierta 25 s, se interrumpe al decir «médico», botón 🎤 de respaldo, panel ⚙️ con diagnóstico, voz elegible y velocidad. La voz nunca pronuncia «médico» (dice «asistente» o «profesional de salud») para no oírse a sí misma. Solo Chrome o Edge.
- Acciones controladas (lista cerrada, validadas, con registro en `logs/acciones.jsonl`): ver signos, ver notas, ver procedimiento, ver medicamento, ver fuente, proponer nota (se guarda solo al confirmar), ir a una pantalla, cambiar de astronauta, pitido de emergencia, recordatorios, SOS y detener emergencia (piden «confirmo» o botón, vencen a los 2 min).
- Navegación inmediata por voz («muéstrame las alertas», «llévame al historial»).
- Recordatorios con hora (por voz y desde `config/recordatorios.json`, hora de Costa Rica). Anuncio de alertas críticas nuevas.
- Tripulación: Ana Rojas, Jason (hipertensión, losartán, alergia a penicilina) y María Quesada Antonelli (escoliosis, alergia a penicilina). Valores de reposo propios para Jason y María.
- Conocimiento: 95 medicamentos (MED), indicadores (IND), 23 enfermedades (CON001–CON023), ficha de María (PAC001–PAC006) y fuentes (SRC). Cualquier `.md` nuevo en `knowledge/` se incluye sin tocar código (secciones `## CÓDIGO — título`).
- Los `[REVISAR]` se quedan en los archivos pero el código los oculta: el médico no los ve ni los menciona. Informe en `docs/pendientes_revisar.md`.

## Reglas del médico (medico/prompt.md)
- Trato de «usted», cálido, breve (se lee en voz alta), puede conversar de temas no médicos.
- Lo médico solo sale de FICHA, ESTADO ACTUAL, INVENTARIO y CONOCIMIENTO. Sin información documentada: lo dice, remite a las bitácoras y registros médicos externos, pide avisar a la tripulación, ofrece SOS, y no da otro consejo médico.
- No da dosis de memoria, no inventa umbrales, cita códigos (MED012, CON005…).
- Los umbrales de `alertas.py` son «de ejemplo» y así se presentan.

## Cómo editar
- Comportamiento: `medico/prompt.md`. Cambiar una regla a la vez y repetir las pruebas.
- Conocimiento: archivos `.md` en `knowledge/`.
- Modelo: `config/modelos.yaml`. Datos del paciente: `db.py` (TRIPULACION, BASES_FIJAS). Umbrales: `alertas.py`.
- Recordatorios del constructor: `config/recordatorios.json`.
- Flujo: editar → `git add -A` → `git commit -m "..."` → `git push` → la app se actualiza sola en 1–2 min.

## Pendiente (por prioridad)
1. Contraseña de acceso en la portada (Secrets `ACCESO_DEMO`) para proteger la cuota de Gemini.
2. Pruebas de seguridad médica aún no medidas: atragantamiento, fractura expuesta, alergia grave, «¿qué dosis de ibuprofeno?», dolor de pecho. Debe decir que no tiene información documentada. Luego los 10 casos con Jason y María.
3. Protocolos del equipo a `knowledge/` (y retirar `protocolos.py` del flujo del médico).
4. Datos del equipo: fuentes SRC014–SRC037 sin título ni enlace; CON020 casi vacía; fechas de revisión de enfermedades con autoincremento (13/11 a 5/12); dosis, contraindicaciones y rangos de alerta.
5. Diseño: nombre «Aéter» en la barra lateral (aún dice AstroMonitor), colores, logo.
6. Modo presentación (ocultar panel de diagnóstico), plan B (video grabado y modo texto), guion de demo con 3 casos que tengan respaldo en `knowledge/`.
7. Revisión médica por una persona con formación en salud.
8. Ensayo completo con el micrófono real (audífonos con cable recomendados).
- Regla: sábado a mediodía se congelan las funciones nuevas.

## Riesgos y límites conocidos
- La voz depende del navegador (Chrome/Edge), del permiso de micrófono y de la red. El primer toque (botón Iniciar) es obligatorio.
- El pitido de «micrófono encendido» lo emite el navegador y no se puede quitar desde la página.
- Streamlit Cloud duerme la app si no se usa: abrirla minutos antes de presentar.
- La base de datos es efímera: se vuelve a crear con la tripulación al reiniciar; las notas y recordatorios por voz se pierden.
- Las computadoras con control de aplicaciones (Windows) bloquean pandas/pyarrow: no se puede ejecutar la app en local en el equipo del desarrollador; se prueba en Streamlit Cloud.
- Todo el contenido médico está `en_revision`: no validado clínicamente.
- Desde el entorno del asistente no hay conexión con Gemini: las pruebas con el modelo real se hacen en la página.
