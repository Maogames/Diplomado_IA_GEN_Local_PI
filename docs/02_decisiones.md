# Registro de decisiones

Cada entrada explica qué se decidió, por qué y qué documentos afecta. Cuando una decisión cambie, no se borra:
se marca como *reemplazada* y se agrega una entrada nueva. Así queda la historia de por qué la arquitectura
actual difiere de la propuesta inicial, que es una pregunta habitual en la sustentación.

Estados: **Vigente** · **Propuesta** (falta confirmarla con el equipo) · **Reemplazada**.

| ID | Fecha | Decisión | Estado |
|---|---|---|---|
| D-01 | oct 2026 | Construir la API de inventario y préstamos desde cero | Vigente |
| D-02 | oct 2026 | Procesamiento 100 % local con un modelo pequeño | Vigente |
| D-03 | oct 2026 | Orden de desarrollo: backend y frontend primero, modelo al final | Vigente |
| D-04 | oct 2026 | Panel web en React + Vite en lugar de Streamlit | Vigente |
| D-05 | oct 2026 | SQLite para desarrollar, PostgreSQL para el servidor | Vigente |
| D-06 | oct 2026 | Aprobación de préstamos por técnico o docente responsable, fuera del agente | Vigente |
| D-07 | nov 2026 | WhatsApp fuera del producto mínimo | Propuesta |
| D-08 | nov 2026 | Estructura única de la documentación | Vigente |

## D-01. Construir la API de inventario y préstamos desde cero

- **Contexto:** el laboratorio es un escenario de referencia y no existe un sistema de inventario con API.
- **Decisión:** el equipo construye la API con FastAPI y datos sintéticos.
- **Consecuencias:** el planteamiento ya no presenta la API como supuesto (sección 2) y la describe como componente implementado (7.4). Los riesgos R-03, R-04 y R-07 se controlan en el propio código (ver `backend/README.md`).

## D-02. Procesamiento 100 % local con un modelo pequeño

- **Contexto:** el diplomado exige un LLM o SLM local, y el perfil mínimo del equipo es una MacBook Air M1 con 8 GB.
- **Decisión:** todo se ejecuta en el equipo. El modelo principal es Llama 3.2 3B Instruct (Q4_K_M), la alternativa es Qwen3-4B-Instruct-2507 y el respaldo es Qwen3 1.7B.
- **Detalle:** planteamiento, secciones 7.1 a 7.3. La elección final depende del benchmarking del Módulo 2.

## D-03. Orden de desarrollo

- **Decisión:** primero la API y el panel web, y al final el modelo, el RAG y el agente, que se montan sobre la API ya probada.
- **Consecuencia:** en la trazabilidad, los requisitos que dependen del agente (RF-01, RF-05, RSG-05) siguen pendientes.

## D-04. Panel web en React + Vite en lugar de Streamlit

- **Contexto:** la propuesta de la Sesión 3 planteaba Streamlit.
- **Decisión:** se construyó un panel en React 19 + Vite + TypeScript, sin librerías ni fuentes remotas, con pantallas por rol.
- **Motivo:** *por completar por el equipo.*
- **Consecuencias:** se actualizaron las secciones 7.4, 7.5 y 7.7 del planteamiento. La vista de conversación con el agente se agregará a este panel.

## D-05. SQLite para desarrollar, PostgreSQL para el servidor

- **Contexto:** Docker en macOS consume memoria y no accede a la GPU, y el equipo de 8 GB no tiene margen.
- **Decisión:** SQLite y ejecución sin Docker en el perfil mínimo. PostgreSQL con `docker compose` en los equipos con más RAM o en el servidor.
- **Consecuencia:** la base se elige con la variable `LAB_DATABASE_URL` y el código es el mismo en ambos casos.

## D-06. Aprobación de préstamos

- **Decisión:** aprueban el técnico o el docente responsable (este último solo en sus prácticas), y nadie aprueba su propia solicitud. Aprobar no es una herramienta del agente: se hace desde el panel, que llama directamente a la API.
- **Motivo:** la supervisión humana (RSG-04) queda garantizada por el diseño y no depende del modelo.
- **Reemplaza:** la propuesta inicial, en la que solo aprobaba el técnico.

## D-07. WhatsApp fuera del producto mínimo (propuesta)

- **Contexto:** el README anterior anunciaba un canal de WhatsApp, pero la sección 7.3 del planteamiento justifica una arquitectura totalmente local.
- **Decisión propuesta:** WhatsApp queda como mejora futura. La API ya registra el canal de cada petición (`X-Canal`) y guarda el número de WhatsApp de cada usuario, así que no hay que deshacer nada.
- **Si el equipo decide incluirlo:** la arquitectura pasa a ser híbrida, y hay que modificar la sección 7.3, RNF-03, CS-10 y R-06 y agregar un riesgo por el tratamiento de datos por un tercero (Ley 1581 de 2012), además de implementar OTP y la credencial de servicio del agente.

## D-08. Estructura única de la documentación

- **Decisión:** los requisitos (RF, RNF, RSG), los riesgos (R-xx) y los criterios de éxito (CS-xx) se definen solo en `docs/01_planteamiento_del_problema.md`. Los demás documentos los citan por su ID.
- **Se eliminaron:** `Propuesta_seccion_arquitectura.md` (integrada como sección 7 del planteamiento) y `pdp.docs` (borrador superado de la pregunta problema). Ambos se pueden recuperar con git.

## Decisiones pendientes

- Componente multimodal (OCR de guías, identificación de equipos por foto o voz local).
- Modelo de delegación de permisos del agente: credencial propia que actúe en nombre del usuario sin superar sus permisos.
- Umbrales de los criterios de éxito para el plan de evaluación.
