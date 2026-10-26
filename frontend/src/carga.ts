import { useCallback, useEffect, useRef, useState } from "react";

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
