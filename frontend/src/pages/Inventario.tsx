import { useState, type FormEvent } from "react";
import { api, nuevaClave } from "../api";
import { Cabecera } from "../components/Marco";
import { Aviso, Campo, Cargando, Codigo, Modal, Nivel, Paginador, Vacio, useAviso } from "../components/ui";
import { useSesion } from "../sesion";
import type { Categoria, Elemento, Movimiento, Pagina, TipoMovimiento } from "../types";
import { NOMBRE_MOVIMIENTO, fechaHora, useCarga, useRetardo } from "../util";

const LIMITE = 25;

export function Inventario() {
  const { puede } = useSesion();
  const escribe = puede("inventario:escribir");
  const [q, setQ] = useState("");
  const [categoria, setCategoria] = useState("");
  const [bajo, setBajo] = useState(false);
  const [desde, setDesde] = useState(0);
  const busqueda = useRetardo(q);
  const [modal, setModal] = useState<{ tipo: "nuevo" | "editar" | "movimiento" | "historial"; e?: Elemento } | null>(null);

  const categorias = useCarga(() => api<Categoria[]>("/categorias"), []);
  const lista = useCarga(
    () => api<Pagina<Elemento>>("/elementos", {
      params: { q: busqueda, categoria_id: categoria, solo_bajo_minimo: bajo, limite: LIMITE, desde },
    }),
    [busqueda, categoria, bajo, desde],
  );

  const cerrar = (recargar = false) => {
    setModal(null);
    if (recargar) lista.recargar();
  };

  return (
    <>
      <Cabecera titulo="Inventario">
        {escribe && (
          <button className="btn btn-primario" onClick={() => setModal({ tipo: "nuevo" })}>
            Registrar elemento
          </button>
        )}
      </Cabecera>

      <div className="filtros">
        <input type="search" placeholder="Buscar por código, nombre o descripción" aria-label="Buscar"
               value={q} onChange={(e) => { setQ(e.target.value); setDesde(0); }} />
        <select aria-label="Categoría" value={categoria} onChange={(e) => { setCategoria(e.target.value); setDesde(0); }}>
          <option value="">Todas las categorías</option>
          {categorias.datos?.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
        </select>
        <label className="casilla">
          <input type="checkbox" checked={bajo} onChange={(e) => { setBajo(e.target.checked); setDesde(0); }} />
          Solo bajo el mínimo
        </label>
      </div>

      {lista.error && <Aviso>{lista.error}</Aviso>}
      {lista.cargando && !lista.datos ? <Cargando /> : lista.datos && lista.datos.items.length === 0 ? (
        <Vacio titulo="Ningún elemento coincide con la búsqueda.">Pruebe con otro término o quite los filtros.</Vacio>
      ) : (
        <div className="tabla-contenedor">
          <table className="tabla">
            <thead>
              <tr>
                <th scope="col">Código</th>
                <th scope="col">Elemento</th>
                <th scope="col">Ubicación</th>
                <th scope="col" className="col-nivel">Disponibilidad</th>
                {escribe && <th scope="col"><span className="sr-only">Acciones</span></th>}
              </tr>
            </thead>
            <tbody>
              {lista.datos?.items.map((e) => (
                <tr key={e.id}>
                  <td><Codigo>{e.codigo}</Codigo></td>
                  <td>
                    <span className="celda-titulo">{e.nombre}</span>
                    <span className="celda-sub">
                      {e.categoria?.nombre}
                      {e.es_consumible && <span className="marca-consumible">Consumible</span>}
                    </span>
                  </td>
                  <td className="nowrap">{e.ubicacion}</td>
                  <td className="col-nivel"><Nivel e={e} /></td>
                  {escribe && (
                    <td className="celda-acciones">
                      <button className="btn btn-sutil" onClick={() => setModal({ tipo: "movimiento", e })}>Movimiento</button>
                      <button className="btn btn-sutil" onClick={() => setModal({ tipo: "editar", e })}>Editar</button>
                      <button className="btn btn-sutil" onClick={() => setModal({ tipo: "historial", e })}>Historial</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {lista.datos && <Paginador total={lista.datos.total} desde={desde} limite={LIMITE} onCambio={setDesde} />}

      <Modal titulo="Registrar elemento" abierto={modal?.tipo === "nuevo"} onCerrar={() => cerrar()}>
        <FormElemento categorias={categorias.datos ?? []} onListo={() => cerrar(true)} />
      </Modal>
      <Modal titulo={`Editar ${modal?.e?.codigo ?? ""}`} abierto={modal?.tipo === "editar"} onCerrar={() => cerrar()}>
        {modal?.e && <FormElemento e={modal.e} categorias={categorias.datos ?? []} onListo={() => cerrar(true)} />}
      </Modal>
      <Modal titulo={`Movimiento de ${modal?.e?.codigo ?? ""}`} abierto={modal?.tipo === "movimiento"} onCerrar={() => cerrar()}>
        {modal?.e && <FormMovimiento e={modal.e} onListo={() => cerrar(true)} />}
      </Modal>
      <Modal titulo={`Historial de ${modal?.e?.codigo ?? ""}`} abierto={modal?.tipo === "historial"} onCerrar={() => cerrar()} ancho="amplio">
        {modal?.e && <Historial e={modal.e} />}
      </Modal>
    </>
  );
}

function FormElemento({ e, categorias, onListo }: { e?: Elemento; categorias: Categoria[]; onListo: () => void }) {
  const aviso = useAviso();
  const [f, setF] = useState({
    codigo: e?.codigo ?? "",
    nombre: e?.nombre ?? "",
    descripcion: e?.descripcion ?? "",
    categoria_id: e?.categoria?.id ? String(e.categoria.id) : "",
    ubicacion: e?.ubicacion ?? "",
    unidad: e?.unidad ?? "unidad",
    es_consumible: e?.es_consumible ?? false,
    cantidad_inicial: "0",
    stock_minimo: String(e?.stock_minimo ?? 0),
  });
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const set = (k: keyof typeof f) => (ev: { target: { value: string } }) => setF({ ...f, [k]: ev.target.value });

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    setEnviando(true);
    setError(null);
    const comun = {
      nombre: f.nombre,
      descripcion: f.descripcion || null,
      categoria_id: f.categoria_id ? Number(f.categoria_id) : null,
      ubicacion: f.ubicacion || null,
      unidad: f.unidad || "unidad",
      es_consumible: f.es_consumible,
      stock_minimo: Number(f.stock_minimo),
    };
    try {
      if (e) {
        await api(`/elementos/${e.id}`, { method: "PATCH", body: comun });
        aviso(`${e.codigo} actualizado`);
      } else {
        await api("/elementos", { method: "POST", body: { ...comun, codigo: f.codigo, cantidad_inicial: Number(f.cantidad_inicial) } });
        aviso(`${f.codigo.toUpperCase()} registrado`);
      }
      onListo();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="formulario" onSubmit={enviar}>
      <div className="fila-campos">
        <Campo etiqueta="Código" ayuda={e ? "El código no se puede cambiar." : "Letras, números y guiones. Ej.: MED-007"}>
          <input required value={f.codigo} onChange={set("codigo")} disabled={!!e} pattern="[A-Za-z0-9._\-]+" maxLength={30} />
        </Campo>
        <Campo etiqueta="Categoría">
          <select value={f.categoria_id} onChange={set("categoria_id")}>
            <option value="">Sin categoría</option>
            {categorias.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
          </select>
        </Campo>
      </div>
      <Campo etiqueta="Nombre">
        <input required minLength={2} maxLength={120} value={f.nombre} onChange={set("nombre")} />
      </Campo>
      <Campo etiqueta="Descripción">
        <textarea rows={2} value={f.descripcion} onChange={set("descripcion")} />
      </Campo>
      <div className="fila-campos">
        <Campo etiqueta="Ubicación"><input value={f.ubicacion} onChange={set("ubicacion")} maxLength={80} /></Campo>
        <Campo etiqueta="Unidad"><input value={f.unidad} onChange={set("unidad")} maxLength={20} /></Campo>
      </div>
      <div className="fila-campos">
        {!e && (
          <Campo etiqueta="Cantidad inicial" ayuda="Queda como movimiento de entrada.">
            <input type="number" min={0} value={f.cantidad_inicial} onChange={set("cantidad_inicial")} />
          </Campo>
        )}
        <Campo etiqueta="Stock mínimo" ayuda="Por debajo de este número aparece la alerta.">
          <input type="number" min={0} value={f.stock_minimo} onChange={set("stock_minimo")} />
        </Campo>
      </div>
      <label className="casilla">
        <input type="checkbox" checked={f.es_consumible} onChange={(ev) => setF({ ...f, es_consumible: ev.target.checked })} />
        Es material consumible (se entrega como salida, no se presta)
      </label>
      {e && <p className="nota">Las cantidades solo cambian con movimientos, para que quede el registro.</p>}
      <Aviso>{error}</Aviso>
      <div className="acciones-form">
        <button className="btn btn-primario" disabled={enviando}>{e ? "Guardar cambios" : "Registrar elemento"}</button>
      </div>
    </form>
  );
}

const TIPOS: { tipo: TipoMovimiento; ayuda: string; soloConsumible?: boolean }[] = [
  { tipo: "entrada", ayuda: "Compra, donación o reposición: suma unidades." },
  { tipo: "salida", ayuda: "Material gastado en una práctica.", soloConsumible: true },
  { tipo: "baja", ayuda: "Unidades dañadas, perdidas o retiradas." },
  { tipo: "ajuste", ayuda: "Corrige el conteo físico. Use negativo para restar." },
];

function FormMovimiento({ e, onListo }: { e: Elemento; onListo: () => void }) {
  const aviso = useAviso();
  const tipos = TIPOS.filter((t) => !t.soloConsumible || e.es_consumible);
  const [tipo, setTipo] = useState<TipoMovimiento>("entrada");
  const [cantidad, setCantidad] = useState("1");
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [clave] = useState(nuevaClave); // misma clave si se reintenta el envío

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      const m = await api<Movimiento>("/movimientos", {
        method: "POST",
        body: { elemento_id: e.id, tipo, cantidad: Number(cantidad), motivo },
        idempotencia: clave,
      });
      aviso(`Movimiento registrado. Quedan ${m.saldo_disponible} disponibles de ${e.codigo}.`);
      onListo();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="formulario" onSubmit={enviar}>
      <p className="nota">
        {e.nombre}: {e.cantidad_disponible} disponibles de {e.cantidad_total}
        {e.cantidad_prestada > 0 && `, ${e.cantidad_prestada} en préstamo`}.
      </p>
      <fieldset className="opciones">
        <legend>Tipo de movimiento</legend>
        {tipos.map((t) => (
          <label key={t.tipo} className="opcion">
            <input type="radio" name="tipo" checked={tipo === t.tipo} onChange={() => setTipo(t.tipo)} />
            <span>
              <span className="opcion-nombre">{NOMBRE_MOVIMIENTO[t.tipo]}</span>
              <span className="opcion-ayuda">{t.ayuda}</span>
            </span>
          </label>
        ))}
      </fieldset>
      <div className="fila-campos">
        <Campo etiqueta="Cantidad">
          <input type="number" required value={cantidad} min={tipo === "ajuste" ? undefined : 1}
                 onChange={(ev) => setCantidad(ev.target.value)} />
        </Campo>
        <Campo etiqueta="Motivo" ayuda="Queda en el historial y en auditoría.">
          <input required minLength={3} maxLength={255} value={motivo} onChange={(ev) => setMotivo(ev.target.value)} />
        </Campo>
      </div>
      <Aviso>{error}</Aviso>
      <div className="acciones-form">
        <button className="btn btn-primario" disabled={enviando}>Registrar movimiento</button>
      </div>
    </form>
  );
}

function Historial({ e }: { e: Elemento }) {
  const { puede } = useSesion();
  const { datos, error } = useCarga(
    () => api<Pagina<Movimiento>>("/movimientos", { params: { elemento_id: e.id, limite: 50 } }),
    [e.id],
  );
  if (!puede("reportes:ver")) return <p className="nota">Su rol no puede ver el historial de movimientos.</p>;
  if (error) return <Aviso>{error}</Aviso>;
  if (!datos) return <Cargando />;
  return (
    <div className="tabla-contenedor">
      <table className="tabla tabla-densa">
        <thead>
          <tr>
            <th scope="col">Fecha</th><th scope="col">Tipo</th><th scope="col" className="num">Cantidad</th>
            <th scope="col" className="num">Disponible</th><th scope="col">Motivo</th><th scope="col">Registró</th>
          </tr>
        </thead>
        <tbody>
          {datos.items.map((m) => (
            <tr key={m.id}>
              <td>{fechaHora(m.creado_en)}</td>
              <td>{NOMBRE_MOVIMIENTO[m.tipo]}</td>
              <td className={`num ${m.cantidad < 0 ? "negativo" : "positivo"}`}>{m.cantidad > 0 ? `+${m.cantidad}` : m.cantidad}</td>
              <td className="num">{m.saldo_disponible}/{m.saldo_total}</td>
              <td>
                {m.motivo}
                {m.prestamo_id && <> (<a href={`#/prestamos/${m.prestamo_id}`}>préstamo #{m.prestamo_id}</a>)</>}
              </td>
              <td>{m.usuario.nombre}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
