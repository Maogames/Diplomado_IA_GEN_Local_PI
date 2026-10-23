export type Rol = "estudiante" | "docente" | "tecnico" | "coordinador" | "admin";
export type EstadoPrestamo = "pendiente" | "aprobado" | "rechazado" | "entregado" | "devuelto" | "cancelado";
export type TipoMovimiento = "entrada" | "salida" | "baja" | "ajuste" | "prestamo" | "devolucion";

export interface Pagina<T> {
  total: number;
  items: T[];
}

export interface UsuarioResumen {
  id: number;
  nombre: string;
  rol: Rol;
}

export interface Usuario extends UsuarioResumen {
  email: string;
  codigo_institucional: string | null;
  telefono_whatsapp: string | null;
  activo: boolean;
  creado_en: string;
}

export interface Perfil extends Usuario {
  permisos: string[];
}

export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string | null;
}

export interface Elemento {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  categoria: Categoria | null;
  ubicacion: string | null;
  unidad: string;
  es_consumible: boolean;
  cantidad_total: number;
  cantidad_disponible: number;
  cantidad_prestada: number;
  stock_minimo: number;
  bajo_minimo: boolean;
  activo: boolean;
  actualizado_en: string;
}

export interface ElementoResumen {
  id: number;
  codigo: string;
  nombre: string;
}

export interface Movimiento {
  id: number;
  elemento: ElementoResumen;
  tipo: TipoMovimiento;
  cantidad: number;
  motivo: string | null;
  saldo_total: number;
  saldo_disponible: number;
  usuario: UsuarioResumen;
  prestamo_id: number | null;
  creado_en: string;
}

export interface Prestamo {
  id: number;
  estado: EstadoPrestamo;
  vencido: boolean;
  practica: string;
  solicitante: UsuarioResumen;
  docente_responsable: UsuarioResumen | null;
  fecha_devolucion_prevista: string;
  observaciones: string | null;
  motivo_rechazo: string | null;
  canal: string;
  detalles: { elemento: ElementoResumen; cantidad: number; cantidad_danada: number }[];
  creado_en: string;
  aprobado_por: UsuarioResumen | null;
  aprobado_en: string | null;
  entregado_por: UsuarioResumen | null;
  entregado_en: string | null;
  recibido_por: UsuarioResumen | null;
  devuelto_en: string | null;
}

export interface Resumen {
  elementos_activos: number;
  unidades_totales: number;
  unidades_disponibles: number;
  unidades_prestadas: number;
  elementos_bajo_minimo: number;
  prestamos_por_estado: Record<EstadoPrestamo, number>;
  prestamos_vencidos: number;
  movimientos_ultimos_7_dias: number;
}

export interface Reporte {
  reporte: string;
  generado_en: string;
  generado_por: UsuarioResumen;
  fuente: string;
  parametros: Record<string, unknown>;
  resumen: Record<string, unknown>;
  total_filas: number;
  filas: Record<string, string | number>[];
}

export interface RegistroAuditoria {
  id: number;
  creado_en: string;
  usuario_id: number | null;
  rol: string | null;
  canal: string;
  accion: string;
  recurso: string | null;
  recurso_id: string | null;
  resultado: "ok" | "denegado" | "error";
  detalle: Record<string, unknown> | null;
  ip: string | null;
  request_id: string | null;
}
