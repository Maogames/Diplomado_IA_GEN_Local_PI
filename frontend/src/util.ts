import { useCallback, useEffect, useRef, useState } from "react";
import type { EstadoPrestamo, Rol, TipoMovimiento } from "./types";

const ZONA = "America/Bogota";

export function fechaHora(iso: string | null | undefined) {
  if (!iso) return "";
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short", timeZone: ZONA }).format(new Date(iso));
}

export function fecha(isoFecha: string) {
  // "2026-10-23" es una fecha local, no un instante: se interpreta a mediodía para no correr el día.
  return new Intl.DateTimeFormat("es-CO", { day: "numeric", month: "short", year: "numeric", timeZone: ZONA }).format(
    new Date(`${isoFecha}T12:00:00-05:00`),
  );
}

export function hoyISO(desplazarDias = 0) {
  const d = new Date(Date.now() + desplazarDias * 86_400_000);
  return new Intl.DateTimeFormat("en-CA", { timeZone: ZONA }).format(d); // AAAA-MM-DD
}

export const NOMBRE_ROL: Record<Rol, string> = {
  estudiante: "Estudiante",
  docente: "Docente",
  tecnico: "Técnico de laboratorio",
  coordinador: "Coordinación",
  admin: "Administración del sistema",
};

export const NOMBRE_ESTADO: Record<EstadoPrestamo, string> = {
  pendiente: "Pendiente de aprobación",
  aprobado: "Aprobado, por entregar",
  rechazado: "Rechazado",
  entregado: "Entregado",
  devuelto: "Devuelto",
  cancelado: "Cancelado",
};

export const NOMBRE_MOVIMIENTO: Record<TipoMovimiento, string> = {
  entrada: "Entrada",
  salida: "Salida de consumible",
  baja: "Baja",
  ajuste: "Ajuste de conteo",
  prestamo: "Préstamo",
  devolucion: "Devolución",
};

/** Carga datos de la API y expone estado de carga, error y una forma de recargar. */
export function useCarga<T>(cargar: () => Promise<T>, deps: unknown[]) {
  const [datos, setDatos] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  const turno = useRef(0);

  const recargar = useCallback(() => {
    const mio = ++turno.current;
    setCargando(true);
    setError(null);
    cargar()
      .then((d) => mio === turno.current && setDatos(d))
      .catch((e: Error) => mio === turno.current && setError(e.message))
      .finally(() => mio === turno.current && setCargando(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(recargar, [recargar]);
  return { datos, error, cargando, recargar, setDatos };
}

export function useRetardo<T>(valor: T, ms = 300) {
  const [v, setV] = useState(valor);
  useEffect(() => {
    const t = setTimeout(() => setV(valor), ms);
    return () => clearTimeout(t);
  }, [valor, ms]);
  return v;
}
