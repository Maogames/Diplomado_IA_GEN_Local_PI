import type { Prestamo } from "../types";
import { fecha, fechaHora } from "../util";

const PASOS = ["Solicitado", "Aprobado", "Entregado", "Devuelto"];
const EN_ESPERA = ["", "Por aprobar", "Por entregar", "Por devolver"];
const NIVEL: Record<string, number> = { pendiente: 0, aprobado: 1, entregado: 2, devuelto: 3 };

/**
 * El ciclo del préstamo dibujado como una pista de circuito: cada estado es un pad.
 * Los pads hechos se rellenan, el siguiente queda encendido en espera y, si el
 * préstamo se rechazó o canceló, la pista se corta ahí.
 */
export function Ciclo({ p, compacto = false }: { p: Prestamo; compacto?: boolean }) {
  const cortado = p.estado === "rechazado" || p.estado === "cancelado";
  const nivel = cortado ? (p.estado === "cancelado" && p.aprobado_en ? 1 : 0) : NIVEL[p.estado];
  const fechas = [p.creado_en, p.aprobado_en, p.entregado_en, p.devuelto_en];
  const quien = [p.solicitante, p.aprobado_por, p.entregado_por, p.recibido_por];

  return (
    <ol className={`ciclo ${compacto ? "ciclo-compacto" : ""}`} aria-label="Ciclo del préstamo">
      {PASOS.map((nombreBase, i) => {
        const hecho = i <= nivel;
        const siguiente = i === nivel + 1;
        let estado = hecho ? "hecho" : siguiente ? "espera" : "futuro";
        let nombre = hecho ? nombreBase : siguiente ? EN_ESPERA[i] : nombreBase;
        let nota: string | null = hecho && fechas[i] ? fechaHora(fechas[i]) + (quien[i] ? ` por ${quien[i]!.nombre}` : "") : null;
        if (siguiente && cortado) {
          estado = "corte";
          nombre = p.estado === "rechazado" ? "Rechazado" : "Cancelado";
          nota = p.motivo_rechazo;
        } else if (siguiente && p.vencido) {
          estado = "vencido";
          nombre = "Vencido";
          nota = `Debía devolverse el ${fecha(p.fecha_devolucion_prevista)}`;
        } else if (siguiente && i === 3) {
          nota = `Hasta el ${fecha(p.fecha_devolucion_prevista)}`;
        }
        if (cortado && i > nivel + 1) estado = "anulado";
        return (
          <li key={nombreBase} className={`ciclo-paso ciclo-${estado}`} aria-current={siguiente ? "step" : undefined}>
            <span className="ciclo-pad" aria-hidden="true" />
            <span className={compacto ? "sr-only" : "ciclo-texto"}>
              <span className="ciclo-nombre">{nombre}</span>
              {nota && !compacto && <span className="ciclo-nota">{nota}</span>}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
