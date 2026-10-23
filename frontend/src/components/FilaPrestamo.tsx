import type { Prestamo } from "../types";
import { fecha } from "../util";
import { Ciclo } from "./Ciclo";
import { Codigo, Estado } from "./ui";

export function FilaPrestamo({ p }: { p: Prestamo }) {
  return (
    <li>
      <a className="fila-prestamo" href={`#/prestamos/${p.id}`}>
        <span className="fp-id">#{p.id}</span>
        <span className="fp-principal">
          <span className="fp-practica">{p.practica}</span>
          <span className="fp-meta">
            {p.solicitante.nombre}, devolución {fecha(p.fecha_devolucion_prevista)}
          </span>
        </span>
        <span className="fp-elementos">
          {p.detalles.map((d) => (
            <Codigo key={d.elemento.id}>
              {d.elemento.codigo}
              {d.cantidad > 1 ? ` ×${d.cantidad}` : ""}
            </Codigo>
          ))}
        </span>
        <span className="fp-estado">
          <Ciclo p={p} compacto />
          <Estado estado={p.estado} vencido={p.vencido} />
        </span>
      </a>
    </li>
  );
}

export function ListaPrestamos({ prestamos }: { prestamos: Prestamo[] }) {
  return (
    <ul className="lista-prestamos">
      {prestamos.map((p) => (
        <FilaPrestamo key={p.id} p={p} />
      ))}
    </ul>
  );
}
