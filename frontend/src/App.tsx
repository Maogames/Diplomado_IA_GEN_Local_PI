import { Marco } from "./components/Marco";
import { Cargando, Vacio } from "./components/ui";
import { useRuta } from "./rutas";
import { useSesion } from "./sesion";
import { Auditoria } from "./pages/Auditoria";
import { Inicio } from "./pages/Inicio";
import { Inventario } from "./pages/Inventario";
import { Login } from "./pages/Login";
import { DetallePrestamo, Prestamos } from "./pages/Prestamos";
import { Reportes } from "./pages/Reportes";
import { SolicitarPrestamo } from "./pages/SolicitarPrestamo";
import { Usuarios } from "./pages/Usuarios";

export function App() {
  const { perfil, cargando, puede } = useSesion();
  const [seccion = "inicio", sub] = useRuta();

  if (cargando) return <Cargando />;
  if (!perfil) return <Login />;

  let pagina;
  if (seccion === "inicio") pagina = <Inicio />;
  else if (seccion === "inventario" && puede("inventario:leer")) pagina = <Inventario />;
  else if (seccion === "prestamos" && sub === "nuevo" && puede("prestamos:solicitar")) pagina = <SolicitarPrestamo />;
  else if (seccion === "prestamos" && sub && /^\d+$/.test(sub)) pagina = <DetallePrestamo id={Number(sub)} />;
  else if (seccion === "prestamos") pagina = <Prestamos />;
  else if (seccion === "reportes" && puede("reportes:ver")) pagina = <Reportes />;
  else if (seccion === "auditoria" && puede("auditoria:ver")) pagina = <Auditoria />;
  else if (seccion === "usuarios" && puede("usuarios:gestionar")) pagina = <Usuarios />;
  else
    pagina = (
      <Vacio titulo="Esta página no existe o su rol no tiene acceso.">
        <a href="#/inicio">Volver al inicio</a>
      </Vacio>
    );

  return <Marco seccion={seccion}>{pagina}</Marco>;
}
