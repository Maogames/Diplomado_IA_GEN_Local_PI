import { useState, type FormEvent } from "react";
import { api } from "../api";
import { Ciclo } from "../components/Ciclo";
import { ListaPrestamos } from "../components/FilaPrestamo";
import { Cabecera } from "../components/Marco";
import { Aviso, Campo, Cargando, Codigo, Estado, Modal, Paginador, Vacio, useAviso } from "../components/ui";
import { useSesion } from "../sesion";
import type { Pagina, Prestamo } from "../types";
import { NOMBRE_ROL, fecha, useCarga } from "../util";

const LIMITE = 25;
const PESTANAS = [
  { clave: "", nombre: "Todos" },
  { clave: "pendiente", nombre: "Por aprobar" },
  { clave: "aprobado", nombre: "Por entregar" },
  { clave: "entregado", nombre: "En préstamo" },
  { clave: "vencidos", nombre: "Vencidos" },
  { clave: "devuelto", nombre: "Devueltos" },
  { clave: "cerrados", nombre: "Rechazados y cancelados" },
];

export function Prestamos() {
  const { puede } = useSesion();
  const [pestana, setPestana] = useState("");
  const [desde, setDesde] = useState(0);
  const [cerradoComo, setCerradoComo] = useState<"rechazado" | "cancelado">("rechazado");

  const params: Record<string, string | number | boolean> = { limite: LIMITE, desde };
  if (pestana === "vencidos") params.vencidos = true;
  else if (pestana === "cerrados") params.estado = cerradoComo;
  else if (pestana) params.estado = pestana;

  const { datos, error, cargando } = useCarga(
    () => api<Pagina<Prestamo>>("/prestamos", { params }),
    [pestana, desde, cerradoComo],
  );

  return (
    <>
      <Cabecera titulo="Préstamos">
        {puede("prestamos:solicitar") && <a className="btn btn-primario" href="#/prestamos/nuevo">Solicitar préstamo</a>}
      </Cabecera>
      <div className="pestanas" role="tablist" aria-label="Filtrar por estado">
        {PESTANAS.map((p) => (
          <button key={p.clave} role="tab" aria-selected={pestana === p.clave}
                  onClick={() => { setPestana(p.clave); setDesde(0); }}>
            {p.nombre}
          </button>
        ))}
      </div>
      {pestana === "cerrados" && (
        <div className="filtros">
          <select aria-label="Tipo de cierre" value={cerradoComo} onChange={(e) => setCerradoComo(e.target.value as "rechazado" | "cancelado")}>
            <option value="rechazado">Rechazados</option>
            <option value="cancelado">Cancelados</option>
          </select>
        </div>
      )}
      {!puede("prestamos:ver_todos") && (
        <p className="nota">Se muestran sus solicitudes{puede("prestamos:aprobar") ? " y las de las prácticas a su cargo" : ""}.</p>
      )}
      <Aviso>{error}</Aviso>
      {cargando && !datos ? <Cargando /> : datos?.items.length ? (
        <ListaPrestamos prestamos={datos.items} />
      ) : (
        <Vacio titulo="No hay préstamos en esta vista." />
      )}
      {datos && <Paginador total={datos.total} desde={desde} limite={LIMITE} onCambio={setDesde} />}
    </>
  );
}

export function DetallePrestamo({ id }: { id: number }) {
  const { perfil, puede } = useSesion();
  const aviso = useAviso();
  const { datos: p, error, setDatos } = useCarga(() => api<Prestamo>(`/prestamos/${id}`), [id]);
  const [modal, setModal] = useState<"rechazar" | "devolver" | null>(null);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);

  if (error) return <Vacio titulo={error}><a href="#/prestamos">Volver a préstamos</a></Vacio>;
  if (!p || !perfil) return <Cargando />;

  const esSolicitante = p.solicitante.id === perfil.id;
  const puedeDecidir = p.estado === "pendiente" && puede("prestamos:aprobar") && !esSolicitante &&
    (perfil.rol !== "docente" || p.docente_responsable?.id === perfil.id);
  const puedeEntregar = p.estado === "aprobado" && puede("prestamos:entregar");
  const puedeDevolver = p.estado === "entregado" && puede("prestamos:entregar");
  const puedeCancelar = ["pendiente", "aprobado"].includes(p.estado) && (esSolicitante || perfil.rol === "tecnico");

  async function accion(ruta: string, mensaje: string, body?: unknown) {
    setOcupado(true);
    setErrorAccion(null);
    try {
      const actualizado = await api<Prestamo>(`/prestamos/${id}/${ruta}`, { method: "POST", body });
      setDatos(actualizado);
      setModal(null);
      aviso(mensaje);
    } catch (e) {
      setErrorAccion((e as Error).message);
    } finally {
      setOcupado(false);
    }
  }

  const hayAcciones = puedeDecidir || puedeEntregar || puedeDevolver || puedeCancelar;

  return (
    <>
      <Cabecera titulo={`Préstamo #${p.id}`}>
        <a className="btn btn-sutil" href="#/prestamos">Todos los préstamos</a>
      </Cabecera>

      <section className="ficha">
        <div className="ficha-cabeza">
          <div>
            <p className="ficha-practica">{p.practica}</p>
            <p className="ficha-meta">
              Solicitado por {p.solicitante.nombre} ({NOMBRE_ROL[p.solicitante.rol].toLowerCase()})
              {p.canal !== "web" && <> desde {p.canal === "whatsapp" ? "WhatsApp" : p.canal}</>}
            </p>
          </div>
          <Estado estado={p.estado} vencido={p.vencido} />
        </div>
        <Ciclo p={p} />
      </section>

      {hayAcciones && (
        <section className="barra-acciones" aria-label="Acciones">
          {puedeDecidir && (
            <>
              <button className="btn btn-primario" disabled={ocupado} onClick={() => accion("aprobar", `Préstamo #${p.id} aprobado`)}>
                Aprobar
              </button>
              <button className="btn btn-peligro" disabled={ocupado} onClick={() => setModal("rechazar")}>Rechazar</button>
            </>
          )}
          {puedeEntregar && (
            <button className="btn btn-primario" disabled={ocupado} onClick={() => accion("entregar", `Entrega del préstamo #${p.id} registrada`)}>
              Registrar entrega
            </button>
          )}
          {puedeDevolver && (
            <button className="btn btn-primario" disabled={ocupado} onClick={() => setModal("devolver")}>Registrar devolución</button>
          )}
          {puedeCancelar && (
            <button className="btn btn-sutil" disabled={ocupado} onClick={() => accion("cancelar", `Préstamo #${p.id} cancelado`)}>
              Cancelar solicitud
            </button>
          )}
          {puedeEntregar && <span className="nota">Al registrar la entrega se descuentan las unidades del inventario.</span>}
          {p.estado === "pendiente" && esSolicitante && puede("prestamos:aprobar") && (
            <span className="nota">Otra persona debe aprobar esta solicitud porque usted la hizo.</span>
          )}
        </section>
      )}
      {!modal && <Aviso>{errorAccion}</Aviso>}

      <div className="detalle-rejilla">
        <section className="panel">
          <h2>Elementos</h2>
          <table className="tabla tabla-densa">
            <thead>
              <tr><th scope="col">Código</th><th scope="col">Elemento</th><th scope="col" className="num">Cantidad</th>
                {p.estado === "devuelto" && <th scope="col" className="num">Dañadas</th>}</tr>
            </thead>
            <tbody>
              {p.detalles.map((d) => (
                <tr key={d.elemento.id}>
                  <td><Codigo>{d.elemento.codigo}</Codigo></td>
                  <td>{d.elemento.nombre}</td>
                  <td className="num">{d.cantidad}</td>
                  {p.estado === "devuelto" && <td className={`num ${d.cantidad_danada ? "negativo" : ""}`}>{d.cantidad_danada}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        <section className="panel">
          <h2>Datos de la solicitud</h2>
          <dl className="datos">
            <dt>Devolución prevista</dt><dd>{fecha(p.fecha_devolucion_prevista)}</dd>
            <dt>Docente responsable</dt><dd>{p.docente_responsable?.nombre ?? "Sin docente asignado"}</dd>
            {p.motivo_rechazo && <><dt>Motivo del rechazo</dt><dd>{p.motivo_rechazo}</dd></>}
            {p.observaciones && <><dt>Observaciones</dt><dd className="pre">{p.observaciones}</dd></>}
          </dl>
        </section>
      </div>

      <Modal titulo={`Rechazar préstamo #${p.id}`} abierto={modal === "rechazar"} onCerrar={() => setModal(null)}>
        <FormRechazo ocupado={ocupado} error={errorAccion}
                     onEnviar={(motivo) => accion("rechazar", `Préstamo #${p.id} rechazado`, { motivo })} />
      </Modal>
      <Modal titulo={`Registrar devolución del préstamo #${p.id}`} abierto={modal === "devolver"} onCerrar={() => setModal(null)}>
        <FormDevolucion p={p} ocupado={ocupado} error={errorAccion}
                        onEnviar={(body) => accion("devolver", `Devolución del préstamo #${p.id} registrada`, body)} />
      </Modal>
    </>
  );
}

function FormRechazo({ onEnviar, ocupado, error }: { onEnviar: (m: string) => void; ocupado: boolean; error: string | null }) {
  const [motivo, setMotivo] = useState("");
  return (
    <form className="formulario" onSubmit={(e: FormEvent) => { e.preventDefault(); onEnviar(motivo); }}>
      <Campo etiqueta="Motivo" ayuda="El solicitante verá este motivo.">
        <textarea required minLength={3} maxLength={255} rows={3} value={motivo} onChange={(e) => setMotivo(e.target.value)} />
      </Campo>
      <Aviso>{error}</Aviso>
      <div className="acciones-form"><button className="btn btn-peligro" disabled={ocupado}>Rechazar</button></div>
    </form>
  );
}

function FormDevolucion({ p, onEnviar, ocupado, error }: {
  p: Prestamo;
  onEnviar: (b: unknown) => void;
  ocupado: boolean;
  error: string | null;
}) {
  const [danados, setDanados] = useState<Record<number, string>>({});
  const [obs, setObs] = useState("");
  function enviar(e: FormEvent) {
    e.preventDefault();
    onEnviar({
      observaciones: obs || null,
      danados: Object.entries(danados)
        .map(([id, n]) => ({ elemento_id: Number(id), cantidad: Number(n) }))
        .filter((d) => d.cantidad > 0),
    });
  }
  return (
    <form className="formulario" onSubmit={enviar}>
      <p className="nota">Todas las unidades vuelven al inventario. Si alguna llegó dañada o falta, indíquelo: se dará de baja.</p>
      <table className="tabla tabla-densa">
        <thead><tr><th scope="col">Elemento</th><th scope="col" className="num">Prestadas</th><th scope="col" className="num">Dañadas o faltantes</th></tr></thead>
        <tbody>
          {p.detalles.map((d) => (
            <tr key={d.elemento.id}>
              <td><Codigo>{d.elemento.codigo}</Codigo> {d.elemento.nombre}</td>
              <td className="num">{d.cantidad}</td>
              <td className="num">
                <input type="number" min={0} max={d.cantidad} className="input-corto" aria-label={`Dañadas de ${d.elemento.codigo}`}
                       value={danados[d.elemento.id] ?? "0"} onChange={(e) => setDanados({ ...danados, [d.elemento.id]: e.target.value })} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Campo etiqueta="Observaciones">
        <textarea rows={2} maxLength={1000} value={obs} onChange={(e) => setObs(e.target.value)} />
      </Campo>
      <Aviso>{error}</Aviso>
      <div className="acciones-form"><button className="btn btn-primario" disabled={ocupado}>Registrar devolución</button></div>
    </form>
  );
}
