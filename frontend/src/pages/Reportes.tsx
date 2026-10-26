import { useState, type FormEvent } from "react";
import { api, descargarCsv } from "../api";
import { Cabecera } from "../components/Marco";
import { Aviso, Campo, Vacio } from "../components/controles";
import type { Categoria, Reporte } from "../types";
import { useCarga } from "../carga";
import { NOMBRE_ESTADO, NOMBRE_MOVIMIENTO, NOMBRE_ROL, fechaHora, hoyISO } from "../formato";

type Clave = "inventario" | "prestamos" | "vencidos" | "uso-elementos" | "movimientos";

const REPORTES: { clave: Clave; nombre: string; describe: string; rango?: boolean }[] = [
  { clave: "inventario", nombre: "Estado del inventario", describe: "Existencias actuales, prestadas y alertas de stock mínimo." },
  { clave: "prestamos", nombre: "Préstamos del periodo", describe: "Solicitudes hechas entre dos fechas, con su estado.", rango: true },
  { clave: "vencidos", nombre: "Préstamos vencidos", describe: "Entregados que pasaron su fecha de devolución, con días de retraso." },
  { clave: "uso-elementos", nombre: "Elementos más prestados", describe: "Ranking de uso en el periodo, con unidades dañadas.", rango: true },
  { clave: "movimientos", nombre: "Movimientos de inventario", describe: "Entradas, salidas, bajas, ajustes, préstamos y devoluciones.", rango: true },
];

const ENCABEZADOS: Record<string, string> = {
  codigo: "Código", nombre: "Nombre", categoria: "Categoría", ubicacion: "Ubicación", consumible: "Consumible",
  total: "Total", disponible: "Disponible", prestado: "Prestado", stock_minimo: "Mínimo", bajo_minimo: "Bajo mínimo",
  id: "N.º", solicitado_en: "Solicitado", solicitante: "Solicitante", practica: "Práctica",
  docente_responsable: "Docente", estado: "Estado", devolucion_prevista: "Devolución prevista", vencido: "Vencido",
  elementos: "Elementos", canal: "Canal", correo: "Correo", dias_retraso: "Días de retraso", prestamos: "Préstamos",
  unidades: "Unidades", danadas: "Dañadas", fecha: "Fecha", elemento: "Elemento", tipo: "Tipo", cantidad: "Cantidad",
  saldo_disponible: "Saldo disp.", saldo_total: "Saldo total", motivo: "Motivo", registrado_por: "Registró",
  prestamo_id: "Préstamo",
};

export function Reportes() {
  const [clave, setClave] = useState<Clave>("inventario");
  const [desde, setDesde] = useState(hoyISO(-30));
  const [hasta, setHasta] = useState(hoyISO());
  const [estado, setEstado] = useState("");
  const [tipo, setTipo] = useState("");
  const [categoria, setCategoria] = useState("");
  const [soloBajo, setSoloBajo] = useState(false);
  const [reporte, setReporte] = useState<Reporte | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);
  const categorias = useCarga(() => api<Categoria[]>("/categorias"), []);

  const elegido = REPORTES.find((r) => r.clave === clave)!;
  const filtros = () => {
    const p: Record<string, string | boolean> = {};
    if (elegido.rango) Object.assign(p, { desde, hasta });
    if (clave === "prestamos" && estado) p.estado = estado;
    if (clave === "movimientos" && tipo) p.tipo = tipo;
    if (clave === "inventario") Object.assign(p, { categoria_id: categoria, solo_bajo_minimo: soloBajo });
    return p;
  };

  async function generar(ev: FormEvent) {
    ev.preventDefault();
    setOcupado(true);
    setError(null);
    try {
      setReporte(await api<Reporte>(`/reportes/${clave}`, { params: filtros() }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  async function csv() {
    try {
      await descargarCsv(`/reportes/${clave}`, filtros());
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const columnas = reporte?.filas[0] ? Object.keys(reporte.filas[0]) : [];

  return (
    <>
      <Cabecera titulo="Reportes" />
      <div className="reportes">
        <nav className="reportes-lista" aria-label="Tipo de reporte">
          {REPORTES.map((r) => (
            <button key={r.clave} aria-pressed={clave === r.clave} onClick={() => { setClave(r.clave); setReporte(null); }}>
              <span className="rl-nombre">{r.nombre}</span>
              <span className="rl-desc">{r.describe}</span>
            </button>
          ))}
        </nav>

        <div className="reportes-cuerpo">
          <form className="filtros" onSubmit={generar}>
            {elegido.rango && (
              <>
                <Campo etiqueta="Desde"><input type="date" value={desde} max={hasta} onChange={(e) => setDesde(e.target.value)} /></Campo>
                <Campo etiqueta="Hasta"><input type="date" value={hasta} min={desde} onChange={(e) => setHasta(e.target.value)} /></Campo>
              </>
            )}
            {clave === "prestamos" && (
              <Campo etiqueta="Estado">
                <select value={estado} onChange={(e) => setEstado(e.target.value)}>
                  <option value="">Todos</option>
                  {Object.entries(NOMBRE_ESTADO).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </Campo>
            )}
            {clave === "movimientos" && (
              <Campo etiqueta="Tipo">
                <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
                  <option value="">Todos</option>
                  {Object.entries(NOMBRE_MOVIMIENTO).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </Campo>
            )}
            {clave === "inventario" && (
              <>
                <Campo etiqueta="Categoría">
                  <select value={categoria} onChange={(e) => setCategoria(e.target.value)}>
                    <option value="">Todas</option>
                    {categorias.datos?.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                  </select>
                </Campo>
                <label className="casilla">
                  <input type="checkbox" checked={soloBajo} onChange={(e) => setSoloBajo(e.target.checked)} /> Solo bajo el mínimo
                </label>
              </>
            )}
            <button className="btn btn-primario" disabled={ocupado}>Generar reporte</button>
            <button type="button" className="btn btn-sutil" onClick={csv}>Descargar CSV</button>
          </form>
          <Aviso>{error}</Aviso>

          {!reporte ? (
            <Vacio titulo={elegido.nombre}>{elegido.describe} Ajuste los filtros y genere el reporte.</Vacio>
          ) : (
            <section className="reporte">
              <dl className="reporte-traza">
                <div><dt>Generado</dt><dd>{fechaHora(reporte.generado_en)}</dd></div>
                <div><dt>Por</dt><dd>{reporte.generado_por.nombre}, {NOMBRE_ROL[reporte.generado_por.rol].toLowerCase()}</dd></div>
                <div><dt>Fuente</dt><dd>{reporte.fuente}</dd></div>
                <div><dt>Filas</dt><dd>{reporte.total_filas}</dd></div>
              </dl>
              {reporte.filas.length === 0 ? (
                <Vacio titulo="El reporte no tiene filas para estos filtros." />
              ) : (
                <div className="tabla-contenedor">
                  <table className="tabla tabla-densa">
                    <thead><tr>{columnas.map((c) => <th key={c} scope="col">{ENCABEZADOS[c] ?? c}</th>)}</tr></thead>
                    <tbody>
                      {reporte.filas.map((f, i) => (
                        <tr key={i}>
                          {columnas.map((c) => (
                            <td key={c} className={typeof f[c] === "number" ? "num" : undefined}>
                              {(c === "id" && reporte.reporte !== "movimientos") || c === "prestamo_id"
                                ? (f[c] ? <a href={`#/prestamos/${f[c]}`}>{f[c]}</a> : "")
                                : c === "solicitado_en" || c === "fecha" ? fechaHora(String(f[c])) : f[c]}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}
        </div>
      </div>
    </>
  );
}
