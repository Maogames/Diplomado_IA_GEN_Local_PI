import { useEffect, useState } from "react";

/** Enrutador mínimo basado en el hash (#/prestamos/12). Sin dependencias extra. */
export function useRuta(): string[] {
  const leer = () => window.location.hash.replace(/^#\/?/, "").split("?")[0].split("/").filter(Boolean);
  const [partes, setPartes] = useState(leer);
  useEffect(() => {
    const cambio = () => setPartes(leer());
    window.addEventListener("hashchange", cambio);
    return () => window.removeEventListener("hashchange", cambio);
  }, []);
  return partes;
}

export function ir(ruta: string) {
  window.location.hash = ruta.startsWith("#") ? ruta : `#${ruta}`;
}
