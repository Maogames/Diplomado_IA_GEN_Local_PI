# Diplomado_IA_GEN_Local_PI

Proyecto integrador del Diplomado en IA Generativa Local: **agente técnico para un laboratorio universitario** que consulta guías autorizadas, gestiona el inventario de práctica y los préstamos mediante una API con permisos por rol, y genera reportes trazables. El modelo de lenguaje se ejecuta localmente.

## Estado

| Componente | Estado |
|---|---|
| API de inventario y préstamos (`backend/`) | Implementada, 49 pruebas automatizadas |
| Panel web (`frontend/`) | Implementado |
| Modelo local, RAG y agente | Pendiente |
| Componente multimodal | Por definir |
| Canal de WhatsApp | Mejora futura, fuera del producto mínimo ([D-07](docs/02_decisiones.md)) |

## Documentación

| Documento | Para qué sirve | Cuándo se actualiza |
|---|---|---|
| [`docs/01_planteamiento_del_problema.md`](docs/01_planteamiento_del_problema.md) | Entregable académico del Módulo 1: problema, usuarios, alcance, arquitectura, requisitos, riesgos y criterios de éxito | Cuando cambia el alcance, la arquitectura o un requisito |
| [`docs/02_decisiones.md`](docs/02_decisiones.md) | Registro de decisiones: qué se decidió, por qué y qué afecta | Cada vez que se cambia una tecnología o el alcance |
| [`docs/03_trazabilidad.md`](docs/03_trazabilidad.md) | Qué requisito está implementado, dónde y qué prueba lo verifica | Cuando se agrega código o pruebas |
| [`docs/referencias.md`](docs/referencias.md) | Bibliografía en APA 7 | Al citar una fuente nueva |
| [`backend/README.md`](backend/README.md) | Ejecutar la API, roles, endpoints y controles de riesgo | Cuando cambia la API |
| [`frontend/README.md`](frontend/README.md) | Ejecutar el panel y sus pantallas | Cuando cambia el panel |
| [`herramientas/prompts/`](herramientas/prompts/) | Prompts de trabajo usados con asistentes de IA (no son documentación del proyecto) | — |

Reglas para mantener la documentación:

1. Los requisitos (RF, RNF, RSG), los riesgos (R-xx) y los criterios de éxito (CS-xx) se definen **solo** en el planteamiento. Los demás documentos los citan por su ID.
2. Si se cambia una tecnología o el alcance, primero se agrega una entrada en `02_decisiones.md` y luego se ajusta el planteamiento.
3. Los README de `backend/` y `frontend/` explican cómo ejecutar y cómo funciona el código; no repiten el planteamiento.

Documentos pendientes para el Módulo 8: `docs/04_evaluacion.md` (plan de pruebas, preguntas de evaluación y métricas) y `docs/05_operacion_local.md` (instalación sin Internet y manifiesto de modelos con versión, licencia y hash).

## Desarrollo

| Carpeta | Qué es | Cómo se ejecuta |
|---|---|---|
| `backend/` | API autorizada de inventario y préstamos (FastAPI, PostgreSQL o SQLite) | `uvicorn app.main:app --reload` |
| `frontend/` | Panel web del laboratorio (React + Vite) | `npm run dev` |
| `Datasets/`, `Gradio/` | Conjuntos de datos y cuadernos de prueba (inventario de ferretería y de bodega); la API no los usa todavía | Google Colab |

El modelo LLM local y el agente se integrarán sobre esta API en la siguiente fase.

Inicio rápido (dos terminales):

```bash
# 1. Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.seed          # datos sintéticos; contraseña de prueba Demo1234!
uvicorn app.main:app --reload

# 2. Frontend
cd frontend && npm install && npm run dev   # http://localhost:5173
```

Con Docker (backend + PostgreSQL): `docker compose up --build`. En equipos de 8 GB se recomienda desarrollar con SQLite, sin Docker.
