from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import func, or_, select

from ..audit import registrar
from ..deps import DB, UsuarioActual, requiere
from ..models import Rol, Usuario
from ..schemas import Pagina, UsuarioActualizar, UsuarioCrear, UsuarioResumen, UsuarioSalida
from ..security import hash_password

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/docentes", response_model=list[UsuarioResumen], summary="Docentes activos (para elegir responsable)")
def listar_docentes(db: DB, _: UsuarioActual):
    q = select(Usuario).where(Usuario.rol == Rol.docente, Usuario.activo.is_(True)).order_by(Usuario.nombre)
    return db.scalars(q).all()


@router.get("", response_model=Pagina[UsuarioSalida])
def listar(
    db: DB,
    _: Usuario = requiere("usuarios:gestionar"),
    q: str | None = Query(None, max_length=80),
    rol: Rol | None = None,
    activo: bool | None = None,
    limite: int = Query(50, ge=1, le=200),
    desde: int = Query(0, ge=0),
):
    consulta = select(Usuario)
    if q:
        patron = f"%{q.lower()}%"
        consulta = consulta.where(or_(func.lower(Usuario.nombre).like(patron), func.lower(Usuario.email).like(patron)))
    if rol:
        consulta = consulta.where(Usuario.rol == rol)
    if activo is not None:
        consulta = consulta.where(Usuario.activo.is_(activo))
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    items = db.scalars(consulta.order_by(Usuario.nombre).offset(desde).limit(limite)).all()
    return Pagina(total=total, items=items)


@router.post("", response_model=UsuarioSalida, status_code=201)
def crear(datos: UsuarioCrear, request: Request, db: DB, admin: Usuario = requiere("usuarios:gestionar")):
    if db.scalar(select(Usuario).where(func.lower(Usuario.email) == datos.email)):
        raise HTTPException(409, "Ya existe un usuario con ese correo.")
    if datos.telefono_whatsapp and db.scalar(select(Usuario).where(Usuario.telefono_whatsapp == datos.telefono_whatsapp)):
        raise HTTPException(409, "Ese número de WhatsApp ya está asociado a otro usuario.")
    usuario = Usuario(**datos.model_dump(exclude={"password"}), password_hash=hash_password(datos.password))
    db.add(usuario)
    db.flush()
    registrar(db, request, admin, "crear_usuario", recurso="usuario", recurso_id=usuario.id,
              detalle={"rol": usuario.rol.value})
    db.commit()
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioSalida)
def actualizar(
    usuario_id: int, datos: UsuarioActualizar, request: Request, db: DB, admin: Usuario = requiere("usuarios:gestionar")
):
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario no encontrado.")
    cambios = datos.model_dump(exclude_unset=True)
    for obligatorio in ("nombre", "rol", "activo", "password"):
        if obligatorio in cambios and cambios[obligatorio] is None:
            del cambios[obligatorio]
    if usuario.id == admin.id and (cambios.get("activo") is False or cambios.get("rol", Rol.admin) != Rol.admin):
        raise HTTPException(409, "No puede desactivarse ni quitarse el rol de administrador a sí mismo.")
    if "telefono_whatsapp" in cambios and cambios["telefono_whatsapp"]:
        otro = db.scalar(select(Usuario).where(Usuario.telefono_whatsapp == cambios["telefono_whatsapp"]))
        if otro and otro.id != usuario.id:
            raise HTTPException(409, "Ese número de WhatsApp ya está asociado a otro usuario.")
    # En auditoría solo quedan los nombres de los campos, no datos personales ni claves.
    detalle: dict = {"campos": sorted(cambios)}
    if "rol" in cambios:
        detalle["rol_nuevo"] = cambios["rol"].value
    if "activo" in cambios:
        detalle["activo"] = cambios["activo"]
    if "password" in cambios:
        usuario.password_hash = hash_password(cambios.pop("password"))
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    registrar(db, request, admin, "actualizar_usuario", recurso="usuario", recurso_id=usuario.id, detalle=detalle)
    db.commit()
    return usuario
