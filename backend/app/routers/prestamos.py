from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from .. import idempotency
from ..audit import canal_de, registrar
from ..deps import DB, UsuarioActual, denegar, requiere
from ..models import EstadoPrestamo, Prestamo, PrestamoDetalle, Rol, Usuario
from ..schemas import Devolucion, Pagina, PrestamoCrear, PrestamoSalida, Rechazo
from ..security import tiene_permiso
from ..services import prestamos as servicio
from ..tiempo import hoy_local

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])

_CARGA = (
    selectinload(Prestamo.detalles).selectinload(PrestamoDetalle.elemento),
    selectinload(Prestamo.solicitante),
    selectinload(Prestamo.docente_responsable),
    selectinload(Prestamo.aprobado_por),
    selectinload(Prestamo.entregado_por),
    selectinload(Prestamo.recibido_por),
)


def _salida(db, prestamo_id: int) -> PrestamoSalida:
    db.expire_all()
    p = db.scalar(select(Prestamo).where(Prestamo.id == prestamo_id).options(*_CARGA))
    return PrestamoSalida.model_validate(p)


@router.get("", response_model=Pagina[PrestamoSalida])
def listar(
    db: DB,
    usuario: UsuarioActual,
    estado: EstadoPrestamo | None = None,
    vencidos: bool = False,
    mios: bool = Query(False, description="Solo los que yo solicité"),
    solicitante_id: int | None = None,
    limite: int = Query(50, ge=1, le=200),
    desde: int = Query(0, ge=0),
):
    consulta = select(Prestamo).options(*_CARGA)
    if mios:
        consulta = consulta.where(Prestamo.solicitante_id == usuario.id)
    elif not tiene_permiso(usuario.rol, "prestamos:ver_todos"):
        # Estudiantes ven los suyos; docentes, los suyos y los de prácticas a su cargo.
        consulta = consulta.where(
            or_(Prestamo.solicitante_id == usuario.id, Prestamo.docente_responsable_id == usuario.id)
        )
    if solicitante_id:
        consulta = consulta.where(Prestamo.solicitante_id == solicitante_id)
    if vencidos:
        consulta = consulta.where(
            Prestamo.estado == EstadoPrestamo.entregado, Prestamo.fecha_devolucion_prevista < hoy_local()
        )
    elif estado:
        consulta = consulta.where(Prestamo.estado == estado)
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    items = db.scalars(consulta.order_by(Prestamo.id.desc()).offset(desde).limit(limite)).all()
    return Pagina(total=total, items=items)


@router.get("/{prestamo_id}", response_model=PrestamoSalida)
def obtener(prestamo_id: int, request: Request, db: DB, usuario: UsuarioActual):
    p = db.scalar(select(Prestamo).where(Prestamo.id == prestamo_id).options(*_CARGA))
    if p is None:
        raise HTTPException(404, "Préstamo no encontrado.")
    if not servicio.puede_ver(usuario, p):
        # Se responde 404 para no revelar que el préstamo existe.
        raise denegar(request, usuario, "ver_prestamo", "Préstamo no encontrado.", codigo=404,
                      recurso="prestamo", recurso_id=prestamo_id)
    return p


@router.post("", response_model=PrestamoSalida, status_code=201)
def solicitar(datos: PrestamoCrear, request: Request, db: DB, usuario: Usuario = requiere("prestamos:solicitar")):
    clave = idempotency.leer_clave(request)
    previa = idempotency.respuesta_previa(db, usuario, clave, "POST /prestamos")
    if previa:
        return previa
    p = servicio.crear(db, usuario, datos, canal_de(request))
    registrar(db, request, usuario, "solicitar_prestamo", recurso="prestamo", recurso_id=p.id,
              detalle={"elementos": [d.model_dump() for d in datos.detalles], "practica": datos.practica})
    db.flush()
    salida = _salida(db, p.id)
    idempotency.guardar(db, usuario, clave, "POST /prestamos", 201, salida)
    db.commit()
    return salida


def _cargar_para_accion(db, request: Request, usuario: Usuario, prestamo_id: int, accion: str) -> Prestamo:
    p = servicio.cargar(db, prestamo_id, bloquear=True)
    if not servicio.puede_ver(usuario, p) and not tiene_permiso(usuario.rol, "prestamos:aprobar"):
        raise denegar(request, usuario, accion, "Préstamo no encontrado.", codigo=404,
                      recurso="prestamo", recurso_id=prestamo_id)
    return p


def _validar_aprobador(request: Request, usuario: Usuario, p: Prestamo, accion: str) -> None:
    if p.solicitante_id == usuario.id:
        raise denegar(request, usuario, accion, "No puede aprobar o rechazar su propia solicitud.",
                      recurso="prestamo", recurso_id=p.id)
    if usuario.rol == Rol.docente and p.docente_responsable_id != usuario.id:
        raise denegar(request, usuario, accion, "Solo el docente responsable de la práctica puede decidir esta solicitud.",
                      recurso="prestamo", recurso_id=p.id)


@router.post("/{prestamo_id}/aprobar", response_model=PrestamoSalida)
def aprobar(prestamo_id: int, request: Request, db: DB, usuario: Usuario = requiere("prestamos:aprobar")):
    p = _cargar_para_accion(db, request, usuario, prestamo_id, "aprobar_prestamo")
    _validar_aprobador(request, usuario, p, "aprobar_prestamo")
    servicio.aprobar(db, p, usuario)
    registrar(db, request, usuario, "aprobar_prestamo", recurso="prestamo", recurso_id=p.id)
    db.commit()
    return _salida(db, p.id)


@router.post("/{prestamo_id}/rechazar", response_model=PrestamoSalida)
def rechazar(prestamo_id: int, datos: Rechazo, request: Request, db: DB, usuario: Usuario = requiere("prestamos:aprobar")):
    p = _cargar_para_accion(db, request, usuario, prestamo_id, "rechazar_prestamo")
    _validar_aprobador(request, usuario, p, "rechazar_prestamo")
    servicio.rechazar(db, p, usuario, datos.motivo)
    registrar(db, request, usuario, "rechazar_prestamo", recurso="prestamo", recurso_id=p.id,
              detalle={"motivo": datos.motivo})
    db.commit()
    return _salida(db, p.id)


@router.post("/{prestamo_id}/cancelar", response_model=PrestamoSalida)
def cancelar(prestamo_id: int, request: Request, db: DB, usuario: UsuarioActual):
    p = _cargar_para_accion(db, request, usuario, prestamo_id, "cancelar_prestamo")
    if p.solicitante_id != usuario.id and usuario.rol != Rol.tecnico:
        raise denegar(request, usuario, "cancelar_prestamo", "Solo el solicitante o un técnico pueden cancelar.",
                      recurso="prestamo", recurso_id=p.id)
    servicio.cancelar(db, p)
    registrar(db, request, usuario, "cancelar_prestamo", recurso="prestamo", recurso_id=p.id)
    db.commit()
    return _salida(db, p.id)


@router.post("/{prestamo_id}/entregar", response_model=PrestamoSalida,
             summary="Registrar la entrega física (descuenta el stock disponible)")
def entregar(prestamo_id: int, request: Request, db: DB, usuario: Usuario = requiere("prestamos:entregar")):
    p = servicio.cargar(db, prestamo_id, bloquear=True)
    servicio.entregar(db, p, usuario)
    registrar(db, request, usuario, "entregar_prestamo", recurso="prestamo", recurso_id=p.id)
    db.commit()
    return _salida(db, p.id)


@router.post("/{prestamo_id}/devolver", response_model=PrestamoSalida,
             summary="Registrar la devolución (repone el stock; los dañados se dan de baja)")
def devolver(prestamo_id: int, datos: Devolucion, request: Request, db: DB,
             usuario: Usuario = requiere("prestamos:entregar")):
    p = servicio.cargar(db, prestamo_id, bloquear=True)
    servicio.devolver(db, p, usuario, datos)
    registrar(db, request, usuario, "devolver_prestamo", recurso="prestamo", recurso_id=p.id,
              detalle={"danados": [d.model_dump() for d in datos.danados]} if datos.danados else None)
    db.commit()
    return _salida(db, p.id)
