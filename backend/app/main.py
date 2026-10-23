import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from . import models  # noqa: F401  (registra las tablas en Base.metadata)
from .audit import registrar_aparte
from .config import get_settings
from .database import Base, SessionLocal, engine
from .routers import auditoria, auth, inventario, prestamos, reportes, usuarios

log = logging.getLogger("laboratorio")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    if get_settings().crear_tablas_al_iniciar:
        Base.metadata.create_all(engine)
    yield


settings = get_settings()
app = FastAPI(
    title=settings.nombre_app,
    version="0.1.0",
    description=(
        "API autorizada del agente técnico de laboratorio: inventario de práctica, préstamos con "
        "aprobación humana, reportes trazables y auditoría. Los permisos se asignan por rol."
    ),
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origenes,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Canal", "X-Request-ID"],
    expose_headers=["X-Request-ID", "Content-Disposition"],
)


@app.middleware("http")
async def id_de_peticion(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = rid[:64]
    respuesta = await call_next(request)
    respuesta.headers["X-Request-ID"] = request.state.request_id
    return respuesta


@app.exception_handler(HTTPException)
async def registrar_errores_de_negocio(request: Request, exc: HTTPException):
    # Las reglas de negocio rechazadas (conflictos de estado, stock insuficiente, datos
    # inválidos) quedan en auditoría. Las denegaciones de permiso ya se registran en deps.denegar.
    usuario = getattr(request.state, "usuario", None)
    if request.method != "GET" and exc.status_code in (409, 422) and usuario is not None:
        registrar_aparte(
            request, usuario, f"{request.method} {request.url.path}", resultado="error",
            detalle={"codigo": exc.status_code, "mensaje": exc.detail},
        )
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def error_inesperado(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", None)
    log.exception("Error no controlado (request_id=%s)", rid)
    try:
        registrar_aparte(
            request, getattr(request.state, "usuario", None), f"{request.method} {request.url.path}",
            resultado="error", detalle={"tipo": type(exc).__name__},
        )
    except Exception:  # la auditoría nunca debe tumbar la respuesta de error
        log.exception("No se pudo registrar el error en auditoría")
    # No se exponen detalles internos al cliente: solo el identificador para rastrearlo.
    return JSONResponse({"detail": "Error interno del servidor.", "request_id": rid}, status_code=500)


PREFIJO = "/api/v1"
for r in (auth.router, usuarios.router, inventario.router, prestamos.router, reportes.router, auditoria.router):
    app.include_router(r, prefix=PREFIJO)


@app.get("/health", tags=["Sistema"])
def salud():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"estado": "ok", "version": app.version}
