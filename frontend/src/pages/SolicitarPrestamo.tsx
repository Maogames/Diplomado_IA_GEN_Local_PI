import { useState, type FormEvent } from "react";
import { api, nuevaClave } from "../api";
import { Cabecera } from "../components/Marco";
import { Aviso, Campo, Codigo, useAviso } from "../components/controles";
import { ir } from "../rutas";
import { useSesion } from "../sesion";
import type { Elemento, Pagina, Prestamo, UsuarioResumen } from "../types";
import { useCarga, useRetardo } from "../carga";
import { hoyISO } from "../formato";

const DIAS_MAX = 15; // debe coincidir con LAB_DIAS_MAX_PRESTAMO del backend

export function SolicitarPrestamo() {
  const { perfil } = useSesion();
  const aviso = useAviso();
  const [practica, setPractica] = useState("");
  const [docente, setDocente] = useState("");
  const [devolucion, setDevolucion] = useState(hoyISO(3));
  const [obs, setObs] = useState("");
  const [elegidos, setElegidos] = useState<{ e: Elemento; cantidad: number }[]>([]);
  const [q, setQ] = useState("");
  const busqueda = useRetardo(q);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [clave] = useState(nuevaClave);

  const docentes = useCarga(() => api<UsuarioResumen[]>("/usuarios/docentes"), []);
  const resultados = useCarga(
    () => busqueda.trim().length < 2
      ? Promise.resolve({ total: 0, items: [] } as Pagina<Elemento>)
      : api<Pagina<Elemento>>("/elementos", { params: { q: busqueda, solo_disponibles: true, limite: 8 } }),
    [busqueda],
  );
  const opciones = (resultados.datos?.items ?? []).filter(
    (e) => !e.es_consumible && !elegidos.some((linea) => linea.e.id === e.id),
  );

  function agregar(e: Elemento) {
    setElegidos([...elegidos, { e, cantidad: 1 }]);
    setQ("");
  }

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    if (!elegidos.length) {
      setError("Agregue al menos un elemento.");
      return;
    }
    setEnviando(true);
    setError(null);
    try {
      const p = await api<Prestamo>("/prestamos", {
        method: "POST",
        idempotencia: clave,
        body: {
          practica,
          docente_responsable_id: docente ? Number(docente) : null,
          fecha_devolucion_prevista: devolucion,
          observaciones: obs || null,
          detalles: elegidos.map((linea) => ({ elemento_id: linea.e.id, cantidad: linea.cantidad })),
        },
      });
      aviso(`Solicitud #${p.id} enviada. Queda pendiente de aprobación.`);
      ir(`/prestamos/${p.id}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <Cabecera titulo="Solicitar préstamo" />
      <form className="formulario formulario-ancho" onSubmit={enviar}>
        <div className="fila-campos">
          <Campo etiqueta="Práctica o asignatura">
            <input required minLength={3} maxLength={160} placeholder="Ej.: Sistemas Embebidos, laboratorio 2"
                   value={practica} onChange={(e) => setPractica(e.target.value)} />
          </Campo>
          <Campo etiqueta="Docente responsable"
                 ayuda={perfil?.rol === "estudiante" ? "El docente o un técnico aprobará la solicitud." : undefined}>
            <select value={docente} onChange={(e) => setDocente(e.target.value)} required={perfil?.rol === "estudiante"}>
              <option value="">{perfil?.rol === "estudiante" ? "Seleccione un docente" : "Ninguno"}</option>
              {docentes.datos?.map((d) => <option key={d.id} value={d.id}>{d.nombre}</option>)}
            </select>
          </Campo>
          <Campo etiqueta="Fecha de devolución" ayuda={`Máximo ${DIAS_MAX} días.`}>
            <input type="date" required min={hoyISO()} max={hoyISO(DIAS_MAX)} value={devolucion}
                   onChange={(e) => setDevolucion(e.target.value)} />
          </Campo>
        </div>

        <fieldset className="elegir">
          <legend>Elementos</legend>
          <div className="buscador">
            <input type="search" placeholder="Busque por nombre o código, por ejemplo multímetro o MCU-002"
                   aria-label="Buscar elementos" value={q} onChange={(e) => setQ(e.target.value)} />
            {opciones.length > 0 && (
              <ul className="sugerencias" role="listbox">
                {opciones.map((e) => (
                  <li key={e.id}>
                    <button type="button" onClick={() => agregar(e)}>
                      <Codigo>{e.codigo}</Codigo>
                      <span>{e.nombre}</span>
                      <span className="sug-disp">{e.cantidad_disponible} disponibles</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {busqueda.length >= 2 && resultados.datos && opciones.length === 0 && (
              <p className="nota">No hay elementos prestables disponibles con ese nombre.</p>
            )}
          </div>
          {elegidos.length > 0 && (
            <table className="tabla tabla-densa">
              <thead><tr><th scope="col">Elemento</th><th scope="col" className="num">Disponibles</th>
                <th scope="col" className="num">Cantidad</th><th scope="col"><span className="sr-only">Quitar</span></th></tr></thead>
              <tbody>
                {elegidos.map((linea, i) => (
                  <tr key={linea.e.id}>
                    <td><Codigo>{linea.e.codigo}</Codigo> {linea.e.nombre}</td>
                    <td className="num">{linea.e.cantidad_disponible}</td>
                    <td className="num">
                      <input type="number" className="input-corto" min={1} max={linea.e.cantidad_disponible} required
                             aria-label={`Cantidad de ${linea.e.codigo}`} value={linea.cantidad}
                             onChange={(ev) => setElegidos(elegidos.map((otra, j) => j === i ? { ...otra, cantidad: Number(ev.target.value) } : otra))} />
                    </td>
                    <td><button type="button" className="btn btn-sutil" onClick={() => setElegidos(elegidos.filter((_, j) => j !== i))}>Quitar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </fieldset>

        <Campo etiqueta="Observaciones">
          <textarea rows={2} maxLength={1000} value={obs} onChange={(e) => setObs(e.target.value)} />
        </Campo>
        <Aviso>{error}</Aviso>
        <div className="acciones-form">
          <a className="btn btn-sutil" href="#/prestamos">Cancelar</a>
          <button className="btn btn-primario" disabled={enviando}>{enviando ? "Enviando…" : "Enviar solicitud"}</button>
        </div>
      </form>
    </>
  );
}
