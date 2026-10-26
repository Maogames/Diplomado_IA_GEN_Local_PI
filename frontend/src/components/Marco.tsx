import type { ReactNode } from "react";
import { useSesion } from "../sesion";
import { NOMBRE_ROL } from "../formato";

const SECCIONES = [
  { ruta: "inicio", nombre: "Inicio", permiso: null },
  { ruta: "inventario", nombre: "Inventario", permiso: "inventario:leer" },
  { ruta: "prestamos", nombre: "Préstamos", permiso: null },
  { ruta: "reportes", nombre: "Reportes", permiso: "reportes:ver" },
  { ruta: "auditoria", nombre: "Auditoría", permiso: "auditoria:ver" },
  { ruta: "usuarios", nombre: "Usuarios", permiso: "usuarios:gestionar" },
];

export function Marco({ seccion, children }: { seccion: string; children: ReactNode }) {
  const { perfil, puede, salir } = useSesion();
  return (
    <div className="marco">
      <aside className="lateral">
        <a href="#/inicio" className="marca">
          <svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true">
            <rect width="32" height="32" rx="6" fill="currentColor" />
            <path d="M6 16h7l3-6 3 12 3-6h4" fill="none" stroke="var(--papel)" strokeWidth="2.4"
                  strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span>
            <span className="marca-nombre">Laboratorio</span>
            <span className="marca-sub">Inventario y préstamos</span>
          </span>
        </a>
        <nav aria-label="Secciones">
          <ul>
            {SECCIONES.filter((s) => !s.permiso || puede(s.permiso)).map((s) => (
              <li key={s.ruta}>
                <a href={`#/${s.ruta}`} aria-current={seccion === s.ruta ? "page" : undefined}>
                  {s.nombre}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        {perfil && (
          <div className="usuario">
            <span className="usuario-nombre">{perfil.nombre}</span>
            <span className="usuario-rol">{NOMBRE_ROL[perfil.rol]}</span>
            <button className="btn btn-sutil" onClick={salir}>
              Cerrar sesión
            </button>
          </div>
        )}
      </aside>
      <main className="principal" id="contenido">
        {children}
      </main>
    </div>
  );
}

export function Cabecera({ titulo, children }: { titulo: string; children?: ReactNode }) {
  return (
    <header className="cabecera">
      <h1>{titulo}</h1>
      {children && <div className="cabecera-acciones">{children}</div>}
    </header>
  );
}
