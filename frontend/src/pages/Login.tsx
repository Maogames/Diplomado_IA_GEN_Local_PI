import { useState, type FormEvent } from "react";
import { Aviso, Campo } from "../components/controles";
import { useSesion } from "../sesion";

// Cuentas sintéticas que crea `python -m app.seed`. Solo se muestran en desarrollo.
const DEMO = [
  ["tecnico@lab.test", "Técnico"],
  ["docente@lab.test", "Docente"],
  ["estudiante@lab.test", "Estudiante"],
  ["coordinacion@lab.test", "Coordinación"],
  ["admin@lab.test", "Administración"],
];

export function Login() {
  const { entrar } = useSesion();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await entrar(email, password);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login">
      <div className="login-panel">
        <div className="login-marca">
          <svg viewBox="0 0 120 24" width="120" height="24" aria-hidden="true" className="login-traza">
            <path d="M0 12h40l6-9 8 18 8-18 6 9h52" fill="none" stroke="currentColor" strokeWidth="2.5"
                  strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <h1>Laboratorio de prácticas</h1>
          <p>Inventario, préstamos y reportes del laboratorio.</p>
        </div>
        <form onSubmit={enviar} className="formulario">
          <Campo etiqueta="Correo institucional">
            <input type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </Campo>
          <Campo etiqueta="Contraseña">
            <input type="password" autoComplete="current-password" required value={password}
                   onChange={(e) => setPassword(e.target.value)} />
          </Campo>
          <Aviso>{error}</Aviso>
          <button className="btn btn-primario" disabled={enviando}>
            {enviando ? "Entrando…" : "Entrar"}
          </button>
        </form>
        {import.meta.env.DEV && (
          <div className="login-demo">
            <p>Cuentas de prueba (contraseña Demo1234!)</p>
            <div className="login-demo-lista">
              {DEMO.map(([correo, rol]) => (
                <button key={correo} type="button" className="btn btn-sutil"
                        onClick={() => { setEmail(correo); setPassword("Demo1234!"); }}>
                  {rol}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
