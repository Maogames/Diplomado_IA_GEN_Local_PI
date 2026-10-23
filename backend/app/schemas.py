from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import EstadoPrestamo, Rol, TipoMovimiento

T = TypeVar("T")

EMAIL_PATRON = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class Esquema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Pagina(BaseModel, Generic[T]):
    total: int
    items: list[T]


# ---------- Autenticación y usuarios ----------


class LoginEntrada(BaseModel):
    email: str = Field(pattern=EMAIL_PATRON, max_length=160)
    password: str = Field(min_length=1, max_length=128)


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_en: int


class UsuarioResumen(Esquema):
    id: int
    nombre: str
    rol: Rol


class UsuarioSalida(Esquema):
    id: int
    nombre: str
    email: str
    codigo_institucional: str | None
    telefono_whatsapp: str | None
    rol: Rol
    activo: bool
    creado_en: datetime


class PerfilSalida(UsuarioSalida):
    permisos: list[str]


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=EMAIL_PATRON, max_length=160)
    password: str = Field(min_length=8, max_length=128)
    rol: Rol
    codigo_institucional: str | None = Field(default=None, max_length=40)
    telefono_whatsapp: str | None = Field(default=None, pattern=r"^\+?\d{7,15}$")

    @field_validator("email")
    @classmethod
    def _minusculas(cls, v: str) -> str:
        return v.strip().lower()


class UsuarioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    rol: Rol | None = None
    activo: bool | None = None
    codigo_institucional: str | None = Field(default=None, max_length=40)
    telefono_whatsapp: str | None = Field(default=None, pattern=r"^\+?\d{7,15}$")
    password: str | None = Field(default=None, min_length=8, max_length=128)


class CambioClave(BaseModel):
    actual: str
    nueva: str = Field(min_length=8, max_length=128)


# ---------- Inventario ----------


class CategoriaEntrada(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)


class CategoriaSalida(Esquema):
    id: int
    nombre: str
    descripcion: str | None


class ElementoCrear(BaseModel):
    codigo: str = Field(min_length=2, max_length=30, pattern=r"^[A-Za-z0-9._-]+$")
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: str | None = None
    categoria_id: int | None = None
    ubicacion: str | None = Field(default=None, max_length=80)
    unidad: str = Field(default="unidad", max_length=20)
    es_consumible: bool = False
    cantidad_inicial: int = Field(default=0, ge=0, le=100_000)
    stock_minimo: int = Field(default=0, ge=0, le=100_000)

    @field_validator("codigo")
    @classmethod
    def _mayusculas(cls, v: str) -> str:
        return v.upper()


class ElementoActualizar(BaseModel):
    """Datos descriptivos. Las cantidades solo cambian mediante movimientos."""

    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    descripcion: str | None = None
    categoria_id: int | None = None
    ubicacion: str | None = Field(default=None, max_length=80)
    unidad: str | None = Field(default=None, max_length=20)
    es_consumible: bool | None = None
    stock_minimo: int | None = Field(default=None, ge=0, le=100_000)
    activo: bool | None = None


class ElementoSalida(Esquema):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    categoria: CategoriaSalida | None
    ubicacion: str | None
    unidad: str
    es_consumible: bool
    cantidad_total: int
    cantidad_disponible: int
    cantidad_prestada: int
    stock_minimo: int
    bajo_minimo: bool
    activo: bool
    actualizado_en: datetime


class ElementoResumen(Esquema):
    id: int
    codigo: str
    nombre: str


class MovimientoCrear(BaseModel):
    elemento_id: int
    tipo: TipoMovimiento
    cantidad: int = Field(description="Positiva. En 'ajuste' puede ser negativa.")
    motivo: str = Field(min_length=3, max_length=255)


class MovimientoSalida(Esquema):
    id: int
    elemento: ElementoResumen
    tipo: TipoMovimiento
    cantidad: int
    motivo: str | None
    saldo_total: int
    saldo_disponible: int
    usuario: UsuarioResumen
    prestamo_id: int | None
    creado_en: datetime


# ---------- Préstamos ----------


class DetalleEntrada(BaseModel):
    elemento_id: int
    cantidad: int = Field(gt=0, le=1000)


class PrestamoCrear(BaseModel):
    practica: str = Field(min_length=3, max_length=160, description="Asignatura o práctica para la que se pide.")
    docente_responsable_id: int | None = None
    fecha_devolucion_prevista: date
    observaciones: str | None = Field(default=None, max_length=1000)
    detalles: list[DetalleEntrada] = Field(min_length=1)


class Rechazo(BaseModel):
    motivo: str = Field(min_length=3, max_length=255)


class DanoEntrada(BaseModel):
    elemento_id: int
    cantidad: int = Field(gt=0)


class Devolucion(BaseModel):
    observaciones: str | None = Field(default=None, max_length=1000)
    danados: list[DanoEntrada] = Field(default_factory=list, description="Unidades devueltas dañadas o faltantes.")


class DetalleSalida(Esquema):
    elemento: ElementoResumen
    cantidad: int
    cantidad_danada: int


class PrestamoSalida(Esquema):
    id: int
    estado: EstadoPrestamo
    vencido: bool
    practica: str
    solicitante: UsuarioResumen
    docente_responsable: UsuarioResumen | None
    fecha_devolucion_prevista: date
    observaciones: str | None
    motivo_rechazo: str | None
    canal: str
    detalles: list[DetalleSalida]
    creado_en: datetime
    aprobado_por: UsuarioResumen | None
    aprobado_en: datetime | None
    entregado_por: UsuarioResumen | None
    entregado_en: datetime | None
    recibido_por: UsuarioResumen | None
    devuelto_en: datetime | None


# ---------- Auditoría ----------


class AuditoriaSalida(Esquema):
    id: int
    creado_en: datetime
    usuario_id: int | None
    rol: str | None
    canal: str
    accion: str
    recurso: str | None
    recurso_id: str | None
    resultado: str
    detalle: dict | None
    ip: str | None
    request_id: str | None
