import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import type { Elemento, EstadoPrestamo } from "../types";
import { NOMBRE_ESTADO } from "../formato";

export function Codigo({ children }: { children: ReactNode }) {
  return <span className="codigo">{children}</span>;
}

export function Estado({ estado, vencido }: { estado: EstadoPrestamo; vencido?: boolean }) {
  const clase = vencido ? "vencido" : estado;
  return <span className={`estado estado-${clase}`}>{vencido ? "Vencido" : NOMBRE_ESTADO[estado]}</span>;
}

/** Barra de disponibilidad: lleno = disponible, marca = stock mínimo. */
export function Nivel({ e }: { e: Pick<Elemento, "cantidad_total" | "cantidad_disponible" | "stock_minimo" | "bajo_minimo" | "unidad"> }) {
  // La escala incluye el doble del mínimo para que un consumible casi agotado no se vea "lleno".
  const total = Math.max(e.cantidad_total, e.stock_minimo * 2, 1);
  const pct = (e.cantidad_disponible / total) * 100;
  const minimo = (e.stock_minimo / total) * 100;
  return (
    <div className={`nivel ${e.bajo_minimo ? "nivel-bajo" : ""}`}>
      <div className="nivel-cifras">
        <strong>{e.cantidad_disponible}</strong>
        <span> de {e.cantidad_total} disponibles</span>
      </div>
      <div className="nivel-barra" role="img" aria-label={`${e.cantidad_disponible} de ${e.cantidad_total} disponibles, mínimo ${e.stock_minimo}`}>
        <div className="nivel-lleno" style={{ width: `${pct}%` }} />
        {e.stock_minimo > 0 && <div className="nivel-minimo" style={{ left: `${Math.min(minimo, 100)}%` }} />}
      </div>
    </div>
  );
}

export function Aviso({ children, tipo = "error" }: { children: ReactNode; tipo?: "error" | "info" }) {
  if (!children) return null;
  return (
    <div className={`aviso aviso-${tipo}`} role={tipo === "error" ? "alert" : "status"}>
      {children}
    </div>
  );
}

export function Vacio({ titulo, children }: { titulo: string; children?: ReactNode }) {
  return (
    <div className="vacio">
      <p className="vacio-titulo">{titulo}</p>
      {children && <div className="vacio-texto">{children}</div>}
    </div>
  );
}

export function Cargando() {
  return <p className="cargando" aria-live="polite">Cargando…</p>;
}

export function Paginador({ total, desde, limite, onCambio }: { total: number; desde: number; limite: number; onCambio: (d: number) => void }) {
  if (total <= limite) return null;
  const fin = Math.min(desde + limite, total);
  return (
    <div className="paginador">
      <span>
        {desde + 1}–{fin} de {total}
      </span>
      <button className="btn btn-sutil" disabled={desde === 0} onClick={() => onCambio(Math.max(0, desde - limite))}>
        Anterior
      </button>
      <button className="btn btn-sutil" disabled={fin >= total} onClick={() => onCambio(desde + limite)}>
        Siguiente
      </button>
    </div>
  );
}

export function Modal({ titulo, abierto, onCerrar, children, ancho }: {
  titulo: string;
  abierto: boolean;
  onCerrar: () => void;
  children: ReactNode;
  ancho?: "normal" | "amplio";
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (abierto && !d.open) d.showModal();
    if (!abierto && d.open) d.close();
  }, [abierto]);
  return (
    <dialog ref={ref} className={`modal modal-${ancho ?? "normal"}`} onClose={onCerrar} aria-labelledby="modal-titulo">
      {abierto && (
        <>
          <header className="modal-cabecera">
            <h2 id="modal-titulo">{titulo}</h2>
            <button className="btn-cerrar" onClick={onCerrar} aria-label="Cerrar">
              ×
            </button>
          </header>
          <div className="modal-cuerpo">{children}</div>
        </>
      )}
    </dialog>
  );
}

export function Campo({ etiqueta, ayuda, children }: { etiqueta: string; ayuda?: string; children: ReactNode }) {
  return (
    <label className="campo">
      <span className="campo-etiqueta">{etiqueta}</span>
      {children}
      {ayuda && <span className="campo-ayuda">{ayuda}</span>}
    </label>
  );
}

const ContextoAvisos = createContext<(texto: string) => void>(() => {});

export function ProveedorAvisos({ children }: { children: ReactNode }) {
  const [texto, setTexto] = useState<string | null>(null);
  const t = useRef<number>(undefined);
  const mostrar = useCallback((mensaje: string) => {
    setTexto(mensaje);
    window.clearTimeout(t.current);
    t.current = window.setTimeout(() => setTexto(null), 3500);
  }, []);
  return (
    <ContextoAvisos.Provider value={mostrar}>
      {children}
      <div className="toast" role="status" aria-live="polite" data-visible={texto ? "si" : "no"}>
        {texto}
      </div>
    </ContextoAvisos.Provider>
  );
}

export const useAviso = () => useContext(ContextoAvisos);
