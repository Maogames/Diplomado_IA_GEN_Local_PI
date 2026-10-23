import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { ProveedorAvisos } from "./components/ui";
import { ProveedorSesion } from "./sesion";
import "./estilos.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ProveedorSesion>
      <ProveedorAvisos>
        <App />
      </ProveedorAvisos>
    </ProveedorSesion>
  </StrictMode>,
);
