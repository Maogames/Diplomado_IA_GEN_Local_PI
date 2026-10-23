from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from .. import idempotency
from ..audit import registrar
from ..deps import DB, UsuarioActual, requiere
from ..models import Categoria, Elemento, Movimiento, TipoMovimiento, Usuario
from ..schemas import (
    CategoriaEntrada,
    CategoriaSalida,
    ElementoActualizar,
    ElementoCrear,
    ElementoSalida,
    MovimientoCrear,
    MovimientoSalida,
    Pagina,
)
from ..services.inventario import aplicar_movimiento, bloquear_elemento

router = APIRouter(tags=["Inventario"])


# ---------- Categorías ----------


@router.get("/categorias", response_model=list[CategoriaSalida])
def listar_categorias(db: DB, _: Usuario = requiere("inventario:leer")):
    return db.scalars(select(Categoria).order_by(Categoria.nombre)).all()


@router.post("/categorias", response_model=CategoriaSalida, status_code=201)
def crear_categoria(datos: CategoriaEntrada, request: Request, db: DB, u: Usuario = requiere("inventario:escribir")):
    if db.scalar(select(Categoria).where(func.lower(Categoria.nombre) == datos.nombre.lower())):
        raise HTTPException(409, "Ya existe una categoría con ese nombre.")
    cat = Categoria(**datos.model_dump())
    db.add(cat)
    db.flush()
    registrar(db, request, u, "crear_categoria", recurso="categoria", recurso_id=cat.id)
    db.commit()
    return cat


# ---------- Elementos ----------


def _consulta_elementos(q, categoria_id, solo_disponibles, solo_bajo_minimo, incluir_inactivos):
    consulta = select(Elemento).options(selectinload(Elemento.categoria))
    if not incluir_inactivos:
        consulta = consulta.where(Elemento.activo.is_(True))
    if q:
        patron = f"%{q.strip().lower()}%"
        consulta = consulta.where(
            or_(
                func.lower(Elemento.nombre).like(patron),
                func.lower(Elemento.codigo).like(patron),
                func.lower(Elemento.descripcion).like(patron),
            )
        )
    if categoria_id:
        consulta = consulta.where(Elemento.categoria_id == categoria_id)
    if solo_disponibles:
        consulta = consulta.where(Elemento.cantidad_disponible > 0)
    if solo_bajo_minimo:
        consulta = consulta.where(Elemento.stock_minimo > 0, Elemento.cantidad_disponible <= Elemento.stock_minimo)
    return consulta


@router.get("/elementos", response_model=Pagina[ElementoSalida], summary="Buscar y listar elementos del inventario")
def listar_elementos(
    db: DB,
    _: Usuario = requiere("inventario:leer"),
    q: str | None = Query(None, max_length=80, description="Texto a buscar en código, nombre o descripción"),
    categoria_id: int | None = None,
    solo_disponibles: bool = False,
    solo_bajo_minimo: bool = False,
    incluir_inactivos: bool = False,
    limite: int = Query(50, ge=1, le=200),
    desde: int = Query(0, ge=0),
):
    consulta = _consulta_elementos(q, categoria_id, solo_disponibles, solo_bajo_minimo, incluir_inactivos)
    total = db.scalar(select(func.count()).select_from(consulta.order_by(None).subquery()))
    items = db.scalars(consulta.order_by(Elemento.codigo).offset(desde).limit(limite)).all()
    return Pagina(total=total, items=items)


def _obtener(db, elemento_id: int) -> Elemento:
    e = db.get(Elemento, elemento_id)
    if e is None:
        raise HTTPException(404, "Elemento no encontrado.")
    return e


@router.get("/elementos/codigo/{codigo}", response_model=ElementoSalida)
def obtener_por_codigo(codigo: str, db: DB, _: Usuario = requiere("inventario:leer")):
    e = db.scalar(select(Elemento).where(Elemento.codigo == codigo.upper()))
    if e is None:
        raise HTTPException(404, "Elemento no encontrado.")
    return e


@router.get("/elementos/{elemento_id}", response_model=ElementoSalida)
def obtener_elemento(elemento_id: int, db: DB, _: Usuario = requiere("inventario:leer")):
    return _obtener(db, elemento_id)


@router.post("/elementos", response_model=ElementoSalida, status_code=201)
def crear_elemento(datos: ElementoCrear, request: Request, db: DB, u: Usuario = requiere("inventario:escribir")):
    if db.scalar(select(Elemento).where(Elemento.codigo == datos.codigo)):
        raise HTTPException(409, f"Ya existe un elemento con el código {datos.codigo}.")
    if datos.categoria_id and db.get(Categoria, datos.categoria_id) is None:
        raise HTTPException(422, "La categoría no existe.")
    e = Elemento(**datos.model_dump(exclude={"cantidad_inicial"}), cantidad_total=0, cantidad_disponible=0)
    db.add(e)
    db.flush()
    if datos.cantidad_inicial:
        aplicar_movimiento(db, e, TipoMovimiento.entrada, datos.cantidad_inicial, u, motivo="Registro inicial")
    registrar(db, request, u, "crear_elemento", recurso="elemento", recurso_id=e.id,
              detalle={"codigo": e.codigo, "cantidad_inicial": datos.cantidad_inicial})
    db.commit()
    db.refresh(e)
    return e


@router.patch("/elementos/{elemento_id}", response_model=ElementoSalida)
def actualizar_elemento(
    elemento_id: int, datos: ElementoActualizar, request: Request, db: DB, u: Usuario = requiere("inventario:escribir")
):
    e = _obtener(db, elemento_id)
    cambios = datos.model_dump(exclude_unset=True)
    for obligatorio in ("nombre", "unidad", "es_consumible", "stock_minimo", "activo"):
        if obligatorio in cambios and cambios[obligatorio] is None:
            del cambios[obligatorio]
    if cambios.get("categoria_id") and db.get(Categoria, cambios["categoria_id"]) is None:
        raise HTTPException(422, "La categoría no existe.")
    if cambios.get("activo") is False and e.cantidad_prestada > 0:
        raise HTTPException(409, "No se puede desactivar: hay unidades en préstamo.")
    antes = {k: getattr(e, k) for k in cambios}
    for k, v in cambios.items():
        setattr(e, k, v)
    registrar(db, request, u, "actualizar_elemento", recurso="elemento", recurso_id=e.id,
              detalle={"antes": antes, "despues": cambios})
    db.commit()
    db.refresh(e)
    return e


# ---------- Movimientos ----------

TIPOS_MANUALES = {TipoMovimiento.entrada, TipoMovimiento.salida, TipoMovimiento.baja, TipoMovimiento.ajuste}


@router.post("/movimientos", response_model=MovimientoSalida, status_code=201,
             summary="Registrar entrada, salida de consumible, baja o ajuste")
def crear_movimiento(datos: MovimientoCrear, request: Request, db: DB, u: Usuario = requiere("inventario:escribir")):
    if datos.tipo not in TIPOS_MANUALES:
        raise HTTPException(422, "Los movimientos de préstamo y devolución se generan desde el préstamo.")
    clave = idempotency.leer_clave(request)
    previa = idempotency.respuesta_previa(db, u, clave, "POST /movimientos")
    if previa:
        return previa
    elemento = bloquear_elemento(db, datos.elemento_id)
    mov = aplicar_movimiento(db, elemento, datos.tipo, datos.cantidad, u, motivo=datos.motivo)
    db.flush()
    db.refresh(mov)
    salida = MovimientoSalida.model_validate(mov)
    registrar(db, request, u, f"movimiento_{datos.tipo.value}", recurso="elemento", recurso_id=elemento.id,
              detalle={"cantidad": datos.cantidad, "motivo": datos.motivo, "movimiento_id": mov.id})
    idempotency.guardar(db, u, clave, "POST /movimientos", 201, salida)
    db.commit()
    return salida


@router.get("/movimientos", response_model=Pagina[MovimientoSalida])
def listar_movimientos(
    db: DB,
    _: Usuario = requiere("reportes:ver"),
    elemento_id: int | None = None,
    tipo: TipoMovimiento | None = None,
    prestamo_id: int | None = None,
    desde_fecha: datetime | None = None,
    hasta_fecha: datetime | None = None,
    limite: int = Query(50, ge=1, le=200),
    desde: int = Query(0, ge=0),
):
    consulta = select(Movimiento).options(selectinload(Movimiento.elemento), selectinload(Movimiento.usuario))
    if elemento_id:
        consulta = consulta.where(Movimiento.elemento_id == elemento_id)
    if tipo:
        consulta = consulta.where(Movimiento.tipo == tipo)
    if prestamo_id:
        consulta = consulta.where(Movimiento.prestamo_id == prestamo_id)
    if desde_fecha:
        consulta = consulta.where(Movimiento.creado_en >= desde_fecha)
    if hasta_fecha:
        consulta = consulta.where(Movimiento.creado_en <= hasta_fecha)
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    items = db.scalars(consulta.order_by(Movimiento.id.desc()).offset(desde).limit(limite)).all()
    return Pagina(total=total, items=items)
