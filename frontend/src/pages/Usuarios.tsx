import { useState, type FormEvent } from "react";
import { api } from "../api";
import { Cabecera } from "../components/Marco";
import { Aviso, Campo, Cargando, Modal, Paginador, useAviso } from "../components/controles";
import { useSesion } from "../sesion";
import type { Pagina, Rol, Usuario } from "../types";
import { useCarga, useRetardo } from "../carga";
import { NOMBRE_ROL } from "../formato";

const LIMITE = 50;
const ROLES = Object.keys(NOMBRE_ROL) as Rol[];

export function Usuarios() {
  const [q, setQ] = useState("");
  const [rol, setRol] = useState("");
  const [desde, setDesde] = useState(0);
  const busqueda = useRetardo(q);
  const [editando, setEditando] = useState<Usuario | "nuevo" | null>(null);
  const lista = useCarga(
    () => api<Pagina<Usuario>>("/usuarios", { params: { q: busqueda, rol, limite: LIMITE, desde } }),
    [busqueda, rol, desde],
  );

  return (
    <>
      <Cabecera titulo="Usuarios">
        <button className="btn btn-primario" onClick={() => setEditando("nuevo")}>Crear usuario</button>
      </Cabecera>
      <div className="filtros">
        <input type="search" aria-label="Buscar" placeholder="Buscar por nombre o correo" value={q}
               onChange={(e) => { setQ(e.target.value); setDesde(0); }} />
        <select aria-label="Rol" value={rol} onChange={(e) => { setRol(e.target.value); setDesde(0); }}>
          <option value="">Todos los roles</option>
          {ROLES.map((r) => <option key={r} value={r}>{NOMBRE_ROL[r]}</option>)}
        </select>
      </div>
      <Aviso>{lista.error}</Aviso>
      {!lista.datos ? <Cargando /> : (
        <div className="tabla-contenedor">
          <table className="tabla">
            <thead>
              <tr><th scope="col">Nombre</th><th scope="col">Correo</th><th scope="col">Rol</th>
                <th scope="col">WhatsApp</th><th scope="col">Estado</th><th scope="col"><span className="sr-only">Acciones</span></th></tr>
            </thead>
            <tbody>
              {lista.datos.items.map((u) => (
                <tr key={u.id} className={u.activo ? undefined : "fila-inactiva"}>
                  <td>
                    <span className="celda-titulo">{u.nombre}</span>
                    {u.codigo_institucional && <span className="celda-sub">Código {u.codigo_institucional}</span>}
                  </td>
                  <td>{u.email}</td>
                  <td>{NOMBRE_ROL[u.rol]}</td>
                  <td>{u.telefono_whatsapp}</td>
                  <td>{u.activo ? "Activo" : "Inactivo"}</td>
                  <td className="celda-acciones"><button className="btn btn-sutil" onClick={() => setEditando(u)}>Editar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {lista.datos && <Paginador total={lista.datos.total} desde={desde} limite={LIMITE} onCambio={setDesde} />}
      <Modal titulo={editando === "nuevo" ? "Crear usuario" : `Editar ${editando?.nombre ?? ""}`} abierto={!!editando}
             onCerrar={() => setEditando(null)}>
        {editando && (
          <FormUsuario u={editando === "nuevo" ? undefined : editando}
                       onListo={() => { setEditando(null); lista.recargar(); }} />
        )}
      </Modal>
    </>
  );
}

function FormUsuario({ u, onListo }: { u?: Usuario; onListo: () => void }) {
  const { perfil } = useSesion();
  const aviso = useAviso();
  const [f, setF] = useState({
    nombre: u?.nombre ?? "",
    email: u?.email ?? "",
    rol: u?.rol ?? ("estudiante" as Rol),
    codigo_institucional: u?.codigo_institucional ?? "",
    telefono_whatsapp: u?.telefono_whatsapp ?? "",
    activo: u?.activo ?? true,
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const esYo = u?.id === perfil?.id;
  const set = (k: keyof typeof f) => (e: { target: { value: string } }) => setF({ ...f, [k]: e.target.value });

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    if (enviando) return;
    setEnviando(true);
    setError(null);
    const body: Record<string, unknown> = {
      nombre: f.nombre,
      rol: f.rol,
      codigo_institucional: f.codigo_institucional || null,
      telefono_whatsapp: f.telefono_whatsapp || null,
    };
    try {
      if (u) {
        body.activo = f.activo;
        if (f.password) body.password = f.password;
        await api(`/usuarios/${u.id}`, { method: "PATCH", body });
        aviso("Usuario actualizado");
      } else {
        await api("/usuarios", { method: "POST", body: { ...body, email: f.email, password: f.password } });
        aviso("Usuario creado");
      }
      onListo();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="formulario" onSubmit={enviar}>
      <Campo etiqueta="Nombre completo"><input required minLength={2} value={f.nombre} onChange={set("nombre")} /></Campo>
      <Campo etiqueta="Correo">
        <input type="email" required value={f.email} onChange={set("email")} disabled={!!u} />
      </Campo>
      <div className="fila-campos">
        <Campo etiqueta="Rol" ayuda={esYo ? "No puede cambiar su propio rol." : undefined}>
          <select value={f.rol} onChange={set("rol")} disabled={esYo}>
            {ROLES.map((r) => <option key={r} value={r}>{NOMBRE_ROL[r]}</option>)}
          </select>
        </Campo>
        <Campo etiqueta="Código institucional"><input value={f.codigo_institucional} onChange={set("codigo_institucional")} maxLength={40} /></Campo>
      </div>
      <Campo etiqueta="Número de WhatsApp" ayuda="Con indicativo, por ejemplo +573001234567. Lo usará el canal de WhatsApp.">
        <input value={f.telefono_whatsapp} onChange={set("telefono_whatsapp")} pattern="\+?\d{7,15}" />
      </Campo>
      <Campo etiqueta={u ? "Nueva contraseña" : "Contraseña inicial"} ayuda={u ? "Déjela vacía para no cambiarla." : "Mínimo 8 caracteres."}>
        <input type="password" autoComplete="new-password" minLength={8} required={!u} value={f.password} onChange={set("password")} />
      </Campo>
      {u && !esYo && (
        <label className="casilla">
          <input type="checkbox" checked={f.activo} onChange={(e) => setF({ ...f, activo: e.target.checked })} />
          Cuenta activa (si la desactiva, no podrá iniciar sesión)
        </label>
      )}
      <Aviso>{error}</Aviso>
      <div className="acciones-form">
        <button type="submit" className="btn btn-primario" aria-busy={enviando}>{enviando ? "Guardando…" : u ? "Guardar cambios" : "Crear usuario"}</button>
      </div>
    </form>
  );
}
