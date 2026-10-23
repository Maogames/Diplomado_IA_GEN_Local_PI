# Frontend: panel del laboratorio

Panel web para técnicos, docentes, coordinación y estudiantes. React 19 + Vite + TypeScript, sin
librerías de interfaz ni fuentes remotas, para que funcione sin Internet una vez instalado.

## Ejecutar

Con el backend corriendo en el puerto 8000:

```bash
cd frontend
npm install
npm run dev
```

Abra http://localhost:5173. En desarrollo, la pantalla de inicio de sesión muestra botones para entrar
con las cuentas de prueba. Vite reenvía `/api` al backend (ver `vite.config.ts`).

Para compilar: `npm run build` (genera `dist/`). Si el backend está en otra dirección, defina
`VITE_API_URL`, por ejemplo `VITE_API_URL=http://192.168.1.20:8000/api/v1 npm run build`, y agregue
ese origen a `LAB_CORS_ORIGENES` en el backend.

## Pantallas según el rol

| Pantalla | Qué permite |
|---|---|
| Inicio | Bandejas de trabajo: solicitudes por aprobar, préstamos por entregar, vencidos y préstamos propios; indicadores y stock bajo |
| Inventario | Buscar elementos y ver disponibilidad; el técnico registra elementos, movimientos y consulta el historial |
| Préstamos | Lista por estado y ficha con el ciclo del préstamo y las acciones permitidas |
| Solicitar préstamo | Formulario con buscador de elementos disponibles |
| Reportes | Cinco reportes con trazabilidad (quién, cuándo, fuente) y descarga en CSV |
| Auditoría | Registros con filtros por resultado, canal y acción |
| Usuarios | Alta, edición, cambio de rol, desactivación y número de WhatsApp |

El menú y los botones se ocultan según los permisos, pero la autorización real la hace siempre el
backend.

## Estructura

```
src/
  api.ts            cliente HTTP (token, errores, Idempotency-Key, CSV)
  sesion.tsx        contexto de sesión (token en sessionStorage)
  rutas.ts          enrutador por hash (#/prestamos/12)
  components/       Marco, Ciclo del préstamo, filas, controles comunes
  pages/            una pantalla por archivo
  estilos.css       tokens de color y tipografía, modo claro y oscuro
```
