import enum
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, FechaHoraUTC
from .tiempo import ahora, hoy_local


def _enum(cls):
    # Guarda el valor ("tecnico") y no el nombre del miembro, y sin tipo ENUM nativo
    # para no depender de migraciones de tipos en PostgreSQL.
    return Enum(cls, values_callable=lambda e: [m.value for m in e], native_enum=False, length=20)


class Rol(str, enum.Enum):
    estudiante = "estudiante"
    docente = "docente"
    tecnico = "tecnico"
    coordinador = "coordinador"
    admin = "admin"


class EstadoPrestamo(str, enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"
    entregado = "entregado"
    devuelto = "devuelto"
    cancelado = "cancelado"


class TipoMovimiento(str, enum.Enum):
    entrada = "entrada"  # compra o donación: suma al total y al disponible
    salida = "salida"  # consumo de material consumible: resta de ambos
    baja = "baja"  # daño o pérdida: resta de ambos
    ajuste = "ajuste"  # corrección de conteo físico (positivo o negativo)
    prestamo = "prestamo"  # sale en préstamo: resta solo del disponible
    devolucion = "devolucion"  # vuelve del préstamo: suma al disponible


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    codigo_institucional: Mapped[str | None] = mapped_column(String(40))
    # Número que usará el canal de WhatsApp para identificar al usuario.
    telefono_whatsapp: Mapped[str | None] = mapped_column(String(20), unique=True)
    rol: Mapped[Rol] = mapped_column(_enum(Rol))
    password_hash: Mapped[str] = mapped_column(String(255))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(FechaHoraUTC())
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC(), default=ahora)


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class Elemento(Base):
    """Herramienta, pieza, equipo o material del inventario de práctica."""

    __tablename__ = "elementos"
    __table_args__ = (
        CheckConstraint("cantidad_total >= 0", name="ck_total_no_negativo"),
        CheckConstraint("cantidad_disponible >= 0", name="ck_disponible_no_negativo"),
        CheckConstraint("cantidad_disponible <= cantidad_total", name="ck_disponible_menor_total"),
        CheckConstraint("stock_minimo >= 0", name="ck_minimo_no_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), index=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"))
    ubicacion: Mapped[str | None] = mapped_column(String(80))
    unidad: Mapped[str] = mapped_column(String(20), default="unidad")
    es_consumible: Mapped[bool] = mapped_column(Boolean, default=False)
    cantidad_total: Mapped[int] = mapped_column(Integer, default=0)
    cantidad_disponible: Mapped[int] = mapped_column(Integer, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC(), default=ahora)
    actualizado_en: Mapped[datetime] = mapped_column(FechaHoraUTC(), default=ahora, onupdate=ahora)

    categoria: Mapped[Categoria | None] = relationship()

    @property
    def cantidad_prestada(self) -> int:
        return self.cantidad_total - self.cantidad_disponible

    @property
    def bajo_minimo(self) -> bool:
        return self.stock_minimo > 0 and self.cantidad_disponible <= self.stock_minimo


class Movimiento(Base):
    """Libro de movimientos: cada cambio de stock deja una fila con el saldo resultante."""

    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    elemento_id: Mapped[int] = mapped_column(ForeignKey("elementos.id"), index=True)
    tipo: Mapped[TipoMovimiento] = mapped_column(_enum(TipoMovimiento))
    cantidad: Mapped[int] = mapped_column(Integer)  # con signo según el efecto sobre el disponible
    motivo: Mapped[str | None] = mapped_column(String(255))
    saldo_total: Mapped[int] = mapped_column(Integer)
    saldo_disponible: Mapped[int] = mapped_column(Integer)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    prestamo_id: Mapped[int | None] = mapped_column(ForeignKey("prestamos.id"))
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC(), default=ahora, index=True)

    elemento: Mapped[Elemento] = relationship()
    usuario: Mapped[Usuario] = relationship()


class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    docente_responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    practica: Mapped[str] = mapped_column(String(160))
    estado: Mapped[EstadoPrestamo] = mapped_column(_enum(EstadoPrestamo), default=EstadoPrestamo.pendiente, index=True)
    fecha_devolucion_prevista: Mapped[date] = mapped_column(Date)
    observaciones: Mapped[str | None] = mapped_column(Text)
    motivo_rechazo: Mapped[str | None] = mapped_column(String(255))
    canal: Mapped[str] = mapped_column(String(20), default="web")

    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC(), default=ahora, index=True)
    aprobado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    aprobado_en: Mapped[datetime | None] = mapped_column(FechaHoraUTC())
    entregado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    entregado_en: Mapped[datetime | None] = mapped_column(FechaHoraUTC())
    recibido_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    devuelto_en: Mapped[datetime | None] = mapped_column(FechaHoraUTC())

    solicitante: Mapped[Usuario] = relationship(foreign_keys=[solicitante_id])
    docente_responsable: Mapped[Usuario | None] = relationship(foreign_keys=[docente_responsable_id])
    aprobado_por: Mapped[Usuario | None] = relationship(foreign_keys=[aprobado_por_id])
    entregado_por: Mapped[Usuario | None] = relationship(foreign_keys=[entregado_por_id])
    recibido_por: Mapped[Usuario | None] = relationship(foreign_keys=[recibido_por_id])
    detalles: Mapped[list["PrestamoDetalle"]] = relationship(
        back_populates="prestamo", cascade="all, delete-orphan", order_by="PrestamoDetalle.id"
    )

    @property
    def vencido(self) -> bool:
        return self.estado == EstadoPrestamo.entregado and self.fecha_devolucion_prevista < hoy_local()


class PrestamoDetalle(Base):
    __tablename__ = "prestamo_detalles"
    __table_args__ = (
        UniqueConstraint("prestamo_id", "elemento_id", name="uq_prestamo_elemento"),
        CheckConstraint("cantidad > 0", name="ck_cantidad_positiva"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    prestamo_id: Mapped[int] = mapped_column(ForeignKey("prestamos.id"))
    elemento_id: Mapped[int] = mapped_column(ForeignKey("elementos.id"))
    cantidad: Mapped[int] = mapped_column(Integer)
    cantidad_danada: Mapped[int] = mapped_column(Integer, default=0)

    prestamo: Mapped[Prestamo] = relationship(back_populates="detalles")
    elemento: Mapped[Elemento] = relationship()


class RegistroAuditoria(Base):
    """Registro de solicitudes, operaciones, denegaciones y errores (RSG-03)."""

    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC(), default=ahora, index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), index=True)
    rol: Mapped[str | None] = mapped_column(String(20))
    canal: Mapped[str] = mapped_column(String(20), default="api")
    accion: Mapped[str] = mapped_column(String(60), index=True)
    recurso: Mapped[str | None] = mapped_column(String(40))
    recurso_id: Mapped[str | None] = mapped_column(String(40))
    resultado: Mapped[str] = mapped_column(String(20))  # ok | denegado | error
    detalle: Mapped[dict | None] = mapped_column(JSON)
    ip: Mapped[str | None] = mapped_column(String(64))
    request_id: Mapped[str | None] = mapped_column(String(64))


class ClaveIdempotencia(Base):
    """Evita operaciones duplicadas por reintentos (riesgo R-04)."""

    __tablename__ = "claves_idempotencia"
    __table_args__ = (UniqueConstraint("usuario_id", "clave", name="uq_usuario_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    clave: Mapped[str] = mapped_column(String(80))
    ruta: Mapped[str] = mapped_column(String(120))
    codigo_http: Mapped[int] = mapped_column(Integer)
    respuesta: Mapped[dict] = mapped_column(JSON)
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC(), default=ahora)
