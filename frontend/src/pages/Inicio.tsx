import { api } from "../api";
import { ListaPrestamos } from "../components/FilaPrestamo";
import { Cabecera } from "../components/Marco";
import { Aviso, Cargando, Codigo, Nivel, Vacio } from "../components/controles";
import { useSesion } from "../sesion";
import type { Elemento, Pagina, Prestamo, Resumen } from "../types";
import { useCarga } from "../carga";

function Bandeja({ titulo, vacio, cargar, filtro }: {
  titulo: string;
  vacio: string;
  cargar: () => Promise<Pagina<Prestamo>>;
  filtro?: (p: Prestamo) => boolean;
}) {
  const { datos: pagina, error, cargando } = useCarga(cargar, []);
  const lista = (pagina?.items ?? []).filter(filtro ?? (() => true));
  return (
    <section className="bandeja">
      <h2>
        {titulo}
        {!cargando && lista.length > 0 && <span className="contador">{lista.length}</span>}
      </h2>
      {cargando ? <Cargando /> : error ? <Aviso>{error}</Aviso> : lista.length ? <ListaPrestamos prestamos={lista} /> : <p className="nota">{vacio}</p>}
    </section>
  );
}

function Indicadores() {
  const { datos: resumen } = useCarga(() => api<Resumen>("/reportes/resumen"), []);
  if (!resumen) return null;
  const filas: [string, number, string?][] = [
    ["Unidades prestadas ahora", resumen.unidades_prestadas],
    ["Préstamos vencidos", resumen.prestamos_vencidos, resumen.prestamos_vencidos ? "alarma" : undefined],
    ["Solicitudes por aprobar", resumen.prestamos_por_estado.pendiente],
    ["Aprobados por entregar", resumen.prestamos_por_estado.aprobado],
    ["Elementos bajo el mínimo", resumen.elementos_bajo_minimo, resumen.elementos_bajo_minimo ? "led" : undefined],
  ];
  return (
    <section className="panel">
      <h2>El laboratorio hoy</h2>
      <dl className="indicadores">
        {filas.map(([nombre, valor, tono]) => (
          <div key={nombre} className={tono ? `ind-${tono}` : undefined}>
            <dt>{nombre}</dt>
            <dd>{valor}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function StockBajo() {
  const { datos: bajos } = useCarga(
    () => api<Pagina<Elemento>>("/elementos", { params: { solo_bajo_minimo: true, limite: 8 } }),
    [],
  );
  if (!bajos) return null;
  return (
    <section className="panel">
      <h2>Stock bajo el mínimo</h2>
      {bajos.items.length === 0 ? (
        <p className="nota">Todos los elementos están por encima de su mínimo.</p>
      ) : (
        <ul className="lista-stock">
          {bajos.items.map((e) => (
            <li key={e.id}>
              <span className="ls-nombre">
                <Codigo>{e.codigo}</Codigo> {e.nombre}
              </span>
              <Nivel e={e} />
            </li>
          ))}
        </ul>
      )}
      {bajos.total > bajos.items.length && <a href="#/inventario">Ver los {bajos.total} elementos</a>}
    </section>
  );
}

export function Inicio() {
  const { perfil, puede } = useSesion();
  if (!perfil) return null;
  const listar = (params: Record<string, string | number | boolean>) => () =>
    api<Pagina<Prestamo>>("/prestamos", { params: { limite: 20, ...params } });

  const bandejas = [];
  if (puede("prestamos:aprobar")) {
    bandejas.push(
      <Bandeja key="aprobar" titulo="Solicitudes por aprobar" vacio="No hay solicitudes esperando su aprobación."
               cargar={listar({ estado: "pendiente" })}
               filtro={(p) => p.solicitante.id !== perfil.id && (perfil.rol !== "docente" || p.docente_responsable?.id === perfil.id)} />,
    );
  }
  if (puede("prestamos:entregar")) {
    bandejas.push(
      <Bandeja key="entregar" titulo="Aprobados, listos para entregar" vacio="No hay préstamos esperando entrega."
               cargar={listar({ estado: "aprobado" })} />,
    );
  }
  if (puede("prestamos:entregar") || puede("prestamos:ver_todos")) {
    bandejas.push(
      <Bandeja key="vencidos" titulo="Vencidos sin devolver" vacio="Ningún préstamo está vencido."
               cargar={listar({ vencidos: true })} />,
    );
  }
  if (puede("prestamos:solicitar")) {
    bandejas.push(
      <Bandeja key="mios" titulo="Mis préstamos en curso" vacio="No tiene préstamos en curso."
               cargar={listar({ mios: true })}
               filtro={(p) => ["pendiente", "aprobado", "entregado"].includes(p.estado)} />,
    );
  }

  return (
    <>
      <Cabecera titulo="Inicio">
        {puede("prestamos:solicitar") && (
          <a className="btn btn-primario" href="#/prestamos/nuevo">
            Solicitar préstamo
          </a>
        )}
      </Cabecera>
      <div className="inicio">
        <div className="inicio-bandejas">
          {bandejas.length ? bandejas : (
            <Vacio titulo="Su rol consulta información; no tiene préstamos que gestionar.">
              Use Reportes para revisar la operación del laboratorio.
            </Vacio>
          )}
        </div>
        {puede("reportes:ver") && (
          <div className="inicio-lateral">
            <Indicadores />
            <StockBajo />
          </div>
        )}
      </div>
    </>
  );
}
