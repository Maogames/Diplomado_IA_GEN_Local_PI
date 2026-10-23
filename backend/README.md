# Backend: API de inventario y préstamos

API autorizada que usará el agente técnico (y el panel web) para consultar el inventario de práctica,
gestionar préstamos con aprobación humana, generar reportes trazables y dejar registro de auditoría.

Stack: **FastAPI + SQLAlchemy 2 + PostgreSQL** (SQLite para desarrollo local). Python 3.10 o superior.

## Ejecutar en local (sin Docker)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env               # opcional: por defecto usa SQLite

python -m app.seed                 # carga datos SINTÉTICOS (usa --reiniciar para recargar)
uvicorn app.main:app --reload
```

- Documentación interactiva: http://localhost:8000/docs (botón **Authorize** con un correo de prueba).
- Todas las cuentas de prueba usan la contraseña `Demo1234!`:
  `admin@lab.test`, `coordinacion@lab.test`, `tecnico@lab.test`, `docente@lab.test`, `estudiante@lab.test`
  (y variantes `tecnico2`, `docente2`, `estudiante2…4`).

## Ejecutar con PostgreSQL (Docker)

Desde la raíz del repositorio:

```bash
docker compose up --build -d
docker compose exec api python -m app.seed
```

> En una MacBook Air de 8 GB, Docker Desktop consume bastante memoria. Para desarrollar basta con SQLite;
> PostgreSQL se usa en el servidor del laboratorio o en los equipos con más RAM.

## Pruebas

```bash
pytest
```

Cubren la matriz de permisos, el flujo completo de préstamo, control de stock, idempotencia,
reportes y registros de auditoría (49 pruebas).

## Modelo de permisos (mínimo privilegio, RSG-01)

| Permiso | Estudiante | Docente | Técnico | Coordinación | Admin |
|---|:-:|:-:|:-:|:-:|:-:|
| Consultar inventario | ✓ | ✓ | ✓ | ✓ | ✓ |
| Registrar elementos y movimientos | | | ✓ | | |
| Solicitar préstamos | ✓ | ✓ | ✓ | | |
| Ver todos los préstamos | | | ✓ | ✓ | ✓ |
| Aprobar / rechazar préstamos | | ✓ (solo de sus prácticas) | ✓ | | |
| Registrar entrega y devolución | | | ✓ | | |
| Reportes | | ✓ (solo de sus prácticas) | ✓ | ✓ | ✓ |
| Auditoría | | | | ✓ | ✓ |
| Gestionar usuarios | | | | | ✓ |

Reglas adicionales: nadie aprueba su propia solicitud; los estudiantes solo ven sus préstamos; el
administrador gestiona cuentas pero no opera el inventario. La matriz está en `app/security.py`.

## Ciclo de un préstamo

```
pendiente ──aprobar──> aprobado ──entregar──> entregado ──devolver──> devuelto
    ├──rechazar──> rechazado
    └──cancelar──> cancelado (también desde aprobado)
```

El stock disponible se descuenta al **entregar** (cuando el elemento sale físicamente) y se repone al
**devolver**. Las unidades reportadas como dañadas en la devolución se dan de baja automáticamente.

## Decisiones relacionadas con la matriz de riesgos

| Control | Dónde | Riesgo |
|---|---|---|
| Toda variación de stock pasa por un único servicio que bloquea la fila y guarda el saldo resultante | `services/inventario.py` | R-04 |
| Encabezado `Idempotency-Key` en solicitudes de préstamo y movimientos: un reintento no duplica la operación | `idempotency.py` | R-04 |
| Auditoría de operaciones, denegaciones de permiso y errores de negocio, con canal (`X-Canal`: web, whatsapp, agente) e id de petición | `audit.py`, `main.py` | R-07 |
| Errores internos no exponen detalles; devuelven un `request_id` para rastrearlos | `main.py` | R-06 |
| Bloqueo temporal tras 5 intentos fallidos de inicio de sesión; mismo mensaje si el correo no existe | `routers/auth.py` | R-03 |
| Contraseñas con PBKDF2-SHA256 (600 000 iteraciones, biblioteca estándar) | `security.py` | R-03 |
| Reportes con autor, fecha, parámetros y fuente; su generación queda auditada | `routers/reportes.py` | R-01, R-07 |
| Datos de prueba sintéticos; el seed no corre si `LAB_ENTORNO=produccion` | `seed.py` | R-06 |

## Endpoints principales (`/api/v1`)

| Método | Ruta | Uso |
|---|---|---|
| POST | `/auth/login` | Inicia sesión (JSON) y devuelve un token JWT |
| GET | `/auth/me` | Perfil y permisos del usuario actual |
| GET | `/elementos?q=` | Buscar en el inventario |
| GET | `/elementos/codigo/{codigo}` | Consultar un elemento por código |
| POST | `/movimientos` | Entrada, salida de consumible, baja o ajuste |
| POST | `/prestamos` | Solicitar un préstamo |
| POST | `/prestamos/{id}/aprobar`, `/rechazar`, `/entregar`, `/devolver`, `/cancelar` | Ciclo del préstamo |
| GET | `/reportes/{inventario,prestamos,vencidos,uso-elementos,movimientos}` | Reportes (`?formato=csv`) |
| GET | `/reportes/resumen` | Indicadores del tablero |
| GET | `/auditoria` | Registros de auditoría |

## Pendiente para las siguientes fases

- Migraciones con Alembic (hoy las tablas se crean al iniciar con `LAB_CREAR_TABLAS_AL_INICIAR=true`).
- Autenticación del agente: credencial de servicio propia que actúe *en nombre de* un usuario
  identificado por su número de WhatsApp, sin superar los permisos de ese usuario.
- Redis para historial de conversación y códigos OTP del canal de WhatsApp.
- Registro de guías autorizadas (título, versión, vigencia) para el RAG.
