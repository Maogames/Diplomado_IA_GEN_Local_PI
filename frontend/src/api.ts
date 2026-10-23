const BASE: string = import.meta.env.VITE_API_URL ?? "/api/v1";

let token: string | null = null;
let alExpirar: (() => void) | null = null;

export function configurarSesion(nuevoToken: string | null, onExpira?: () => void) {
  token = nuevoToken;
  if (onExpira) alExpirar = onExpira;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

type Params = Record<string, string | number | boolean | null | undefined>;

interface Opciones {
  method?: "GET" | "POST" | "PATCH";
  body?: unknown;
  params?: Params;
  idempotencia?: string;
}

function armarUrl(ruta: string, params?: Params) {
  const url = new URL(BASE + ruta, window.location.origin);
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v !== undefined && v !== null && v !== "" && v !== false) url.searchParams.set(k, String(v));
  }
  return url.toString();
}

function encabezados(extra?: Record<string, string>) {
  const h: Record<string, string> = { "X-Canal": "web", ...extra };
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
}

function mensajeDeError(status: number, cuerpo: unknown): string {
  const detalle = (cuerpo as { detail?: unknown })?.detail;
  if (typeof detalle === "string") return detalle;
  if (Array.isArray(detalle) && detalle.length) {
    // Errores de validación de FastAPI: [{loc, msg}]
    return detalle
      .map((d: { loc?: (string | number)[]; msg?: string }) => {
        const campo = d.loc?.filter((p) => p !== "body").join(".");
        return campo ? `${campo}: ${d.msg}` : d.msg;
      })
      .join("; ");
  }
  if (status === 0) return "No se pudo conectar con el servidor. Revise que el backend esté encendido.";
  return `Error ${status}`;
}

export async function api<T>(ruta: string, op: Opciones = {}): Promise<T> {
  const extra: Record<string, string> = {};
  if (op.body !== undefined) extra["Content-Type"] = "application/json";
  if (op.idempotencia) extra["Idempotency-Key"] = op.idempotencia;
  let resp: Response;
  try {
    resp = await fetch(armarUrl(ruta, op.params), {
      method: op.method ?? "GET",
      headers: encabezados(extra),
      body: op.body !== undefined ? JSON.stringify(op.body) : undefined,
    });
  } catch {
    throw new ApiError(0, mensajeDeError(0, null));
  }
  if (resp.status === 204) return undefined as T;
  const cuerpo = await resp.json().catch(() => null);
  if (!resp.ok) {
    if (resp.status === 401 && token && alExpirar) alExpirar();
    throw new ApiError(resp.status, mensajeDeError(resp.status, cuerpo));
  }
  return cuerpo as T;
}

export async function descargarCsv(ruta: string, params: Params) {
  const resp = await fetch(armarUrl(ruta, { ...params, formato: "csv" }), { headers: encabezados() });
  if (!resp.ok) throw new ApiError(resp.status, mensajeDeError(resp.status, await resp.json().catch(() => null)));
  const nombre = /filename="([^"]+)"/.exec(resp.headers.get("Content-Disposition") ?? "")?.[1] ?? "reporte.csv";
  const url = URL.createObjectURL(await resp.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(url);
}

export function nuevaClave() {
  // randomUUID solo existe en contextos seguros (https o localhost).
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
  return Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
}
