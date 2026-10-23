import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, configurarSesion } from "./api";
import type { Perfil } from "./types";

interface Sesion {
  perfil: Perfil | null;
  cargando: boolean;
  entrar: (email: string, password: string) => Promise<void>;
  salir: () => void;
  puede: (permiso: string) => boolean;
}

const Contexto = createContext<Sesion | null>(null);
const CLAVE = "lab.token";

// El token se guarda en sessionStorage: se borra al cerrar la pestaña.
function leerToken(): string | null {
  try {
    return sessionStorage.getItem(CLAVE);
  } catch {
    return null;
  }
}

function guardarToken(t: string | null) {
  try {
    if (t) sessionStorage.setItem(CLAVE, t);
    else sessionStorage.removeItem(CLAVE);
  } catch {
    /* sin almacenamiento: la sesión dura lo que dure la página */
  }
}

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [cargando, setCargando] = useState(true);

  const salir = useCallback(() => {
    guardarToken(null);
    configurarSesion(null);
    setPerfil(null);
  }, []);

  useEffect(() => {
    const t = leerToken();
    configurarSesion(t, salir);
    if (!t) {
      setCargando(false);
      return;
    }
    api<Perfil>("/auth/me")
      .then(setPerfil)
      .catch(salir)
      .finally(() => setCargando(false));
  }, [salir]);

  const entrar = useCallback(
    async (email: string, password: string) => {
      const r = await api<{ access_token: string }>("/auth/login", { method: "POST", body: { email, password } });
      configurarSesion(r.access_token, salir);
      guardarToken(r.access_token);
      setPerfil(await api<Perfil>("/auth/me"));
    },
    [salir],
  );

  const puede = useCallback((permiso: string) => !!perfil?.permisos.includes(permiso), [perfil]);

  return <Contexto.Provider value={{ perfil, cargando, entrar, salir, puede }}>{children}</Contexto.Provider>;
}

export function useSesion() {
  const s = useContext(Contexto);
  if (!s) throw new Error("useSesion fuera de ProveedorSesion");
  return s;
}
