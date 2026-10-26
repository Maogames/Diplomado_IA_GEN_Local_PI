import { useState } from "react";
import { api } from "../api";
import { Cabecera } from "../components/Marco";
import { Aviso, Cargando, Paginador, Vacio } from "../components/controles";
import type { Pagina, RegistroAuditoria } from "../types";
import { useCarga, useRetardo } from "../carga";
import { fechaHora } from "../formato";

const LIMITE = 50;
const RESULTADOS = { ok: "Correcto", denegado: "Denegado", error: "Error" } as const;

function resumirDetalle(d: Record<string, unknown> | null) {
  if (!d) return "";
  return Object.entries(d)
    .map(([k, v]) => `${k}: ${typeof v === "object" ? JSON.stringify(v) : String(v)}`)
    .join("; ");
}

export function Auditoria() {
  const [resultado, setResultado] = useState("");
  const [canal, setCanal] = useState("");
  const [accion, setAccion] = useState("");
  const [desde, setDesde] = useState(0);
  const accionBuscada = useRetardo(accion.trim());

  const { datos: pagina, error, cargando } = useCarga(
    () => api<Pagina<RegistroAuditoria>>("/auditoria", {
      params: { resultado, canal, accion: accionBuscada, limite: LIMITE, desde },
    }),
    [resultado, canal, accionBuscada, desde],
  );

  return (
    <>
      <Cabecera titulo="Auditoría" />
      <p className="nota">
        Cada solicitud, aprobación, movimiento, reporte, denegación de permiso y error de negocio queda registrado aquí.
        Los registros no se pueden editar desde el panel.
      </p>
      <div className="filtros">
        <select aria-label="Resultado" value={resultado} onChange={(e) => { setResultado(e.target.value); setDesde(0); }}>
          <option value="">Todos los resultados</option>
          {Object.entries(RESULTADOS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select aria-label="Canal" value={canal} onChange={(e) => { setCanal(e.target.value); setDesde(0); }}>
          <option value="">Todos los canales</option>
          <option value="web">Panel web</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="agente">Agente</option>
          <option value="api">API directa</option>
        </select>
        <input type="search" aria-label="Acción exacta" placeholder="Acción, por ejemplo aprobar_prestamo"
               value={accion} onChange={(e) => { setAccion(e.target.value); setDesde(0); }} />
      </div>
      <Aviso>{error}</Aviso>
      {cargando && !pagina ? <Cargando /> : !pagina?.items.length ? <Vacio titulo="No hay registros con esos filtros." /> : (
        <div className="tabla-contenedor">
          <table className="tabla tabla-densa">
            <thead>
              <tr>
                <th scope="col">Fecha</th><th scope="col">Usuario</th><th scope="col">Canal</th><th scope="col">Acción</th>
                <th scope="col">Recurso</th><th scope="col">Resultado</th><th scope="col">Detalle</th>
              </tr>
            </thead>
            <tbody>
              {pagina.items.map((r) => (
                <tr key={r.id}>
                  <td className="nowrap">{fechaHora(r.creado_en)}</td>
                  <td>{r.usuario_id ? `#${r.usuario_id} ${r.rol ?? ""}` : "Anónimo"}</td>
                  <td>{r.canal}</td>
                  <td>{r.accion}</td>
                  <td>{r.recurso ? `${r.recurso} ${r.recurso_id ?? ""}` : ""}</td>
                  <td><span className={`resultado resultado-${r.resultado}`}>{RESULTADOS[r.resultado]}</span></td>
                  <td className="celda-detalle">{resumirDetalle(r.detalle)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {pagina && <Paginador total={pagina.total} desde={desde} limite={LIMITE} onCambio={setDesde} />}
    </>
  );
}
