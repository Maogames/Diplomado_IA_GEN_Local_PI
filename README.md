# Diplomado_IA_GEN_Local_PI

Proyecto integrador del Diplomado en IA Generativa Local: **agente técnico para un laboratorio universitario** que consulta guías autorizadas, gestiona el inventario de práctica y los préstamos mediante una API con permisos por rol, y genera reportes trazables. El modelo de lenguaje se ejecuta localmente.

## Documentación

| Documento | Contenido |
|---|---|
| [`Modulo1/`](Modulo1/) | Planteamiento del problema, propuesta de arquitectura (Sesión 3) y referencias |
| [`backend/README.md`](backend/README.md) | API de inventario y préstamos: roles, endpoints y controles de riesgo |
| [`frontend/README.md`](frontend/README.md) | Panel web del laboratorio |

## Desarrollo

| Carpeta | Qué es | Cómo se ejecuta |
|---|---|---|
| `backend/` | API autorizada de inventario y préstamos (FastAPI, PostgreSQL o SQLite) | `uvicorn app.main:app --reload` |
| `frontend/` | Panel web del laboratorio (React + Vite) | `npm run dev` |

El modelo LLM local y el canal de WhatsApp se integrarán sobre esta API en una fase posterior.

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
