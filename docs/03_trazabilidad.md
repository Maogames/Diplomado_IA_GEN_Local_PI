# Trazabilidad: requisitos → código → pruebas

Los requisitos, riesgos y criterios de éxito se definen en `docs/01_planteamiento_del_problema.md`
(secciones 8, 9 y 10). Esta tabla solo indica **qué está implementado, dónde y qué prueba lo verifica**.
Actualícela cuando agregue código o pruebas que cubran un requisito.

Estado: **Hecho** · **Parcial** · **Pendiente**. Rutas relativas a `backend/app/`; pruebas en `backend/tests/`.

| Req. | Riesgos | Criterio | Estado | Dónde | Pruebas |
|---|---|---|---|---|---|
| RF-01 Guías con fuente y versión | R-01, R-02 | CS-01 | Pendiente | RAG y agente | — |
| RF-02 Consultar inventario por la API | R-03 | CS-02 | Parcial: API hecha, falta el agente | `routers/inventario.py` | `test_inventario.py::test_buscar_elementos`, `test_auth_permisos.py::test_matriz_de_permisos` |
| RF-03 Actualizar inventario y préstamos según rol y confirmación | R-03, R-04 | CS-03 | Hecho en la API | `services/inventario.py`, `services/prestamos.py`, `idempotencia.py` | `test_prestamos.py::test_flujo_completo`, `test_no_se_salta_estados`, `test_stock_insuficiente`; `test_inventario.py::test_no_permite_stock_negativo`, `test_idempotencia_evita_duplicados` |
| RF-04 Reportes trazables | R-07 | CS-04 | Hecho en la API | `routers/reportes.py` | `test_reportes_auditoria.py::test_reporte_inventario_trazable`, `test_reporte_csv`, `test_reporte_prestamos_y_uso` |
| RF-05 Escalar lo que está fuera de alcance | R-08 | CS-05 | Pendiente | Agente | — |
| RNF-01 Respuestas comprensibles y trazables | R-07 | CS-07, CS-11 | Parcial: trazabilidad en la API | `auditoria.py` | `test_reportes_auditoria.py::test_auditoria_registra_flujo` |
| RNF-02 Fallos de la API sin inventar datos | R-05 | CS-06 | Parcial: errores con `request_id`; falta el comportamiento del agente | `main.py` | Pendiente: simulación de caída y latencia |
| RNF-03 Operación local | R-06 | CS-10 | Parcial: API y panel sin dependencias remotas; falta el modelo | `frontend/` sin fuentes ni librerías remotas | Pendiente: prueba sin Internet |
| RSG-01 Mínimo privilegio y autorización por rol | R-03, R-10 | CS-02 | Hecho en la API; falta aislar el agente | `seguridad.py`, `dependencias.py`, `routers/auth.py` | `test_auth_permisos.py::test_matriz_de_permisos`, `test_sin_token_401`, `test_login_incorrecto_no_revela_si_existe`, `test_bloqueo_por_intentos_fallidos` |
| RSG-02 No revelar información fuera de permisos | R-06, R-09 | CS-05 | Parcial: visibilidad por rol | `routers/prestamos.py` | `test_prestamos.py::test_visibilidad` |
| RSG-03 Registro para auditoría | R-07 | CS-07 | Hecho en la API; faltan las invocaciones del agente | `auditoria.py`, `main.py` | `test_auth_permisos.py::test_denegacion_queda_en_auditoria`, `test_canal_se_registra`; `test_reportes_auditoria.py::test_errores_de_negocio_quedan_en_auditoria` |
| RSG-04 Aprobación humana en operaciones sensibles | R-04, R-08 | CS-08 | Hecho (D-06) | `services/prestamos.py` | `test_prestamos.py::test_nadie_aprueba_su_propia_solicitud`, `test_solo_docente_responsable`, `test_estudiante_no_puede_aprobar_ni_entregar` |
| RSG-05 Contenido tratado como datos | R-09 | CS-09 | Pendiente | Agente y RAG | Pendiente: casos de *prompt injection* |
| RSG-06 Manifiesto de modelos y secretos fuera del repo | R-11 | — | Parcial: `.env` ignorado; la API no arranca en producción con el secreto por defecto; falta el manifiesto | `config.py`, `.gitignore` | — |

## Resumen

- **Hecho o parcial en la API:** RF-02, RF-03, RF-04, RSG-01, RSG-03, RSG-04 (49 pruebas, `cd backend && pytest`).
- **Depende del agente, el RAG o el modelo:** RF-01, RF-05, RSG-05 y la parte pendiente de RNF-01, RNF-02, RNF-03 y RSG-02.
- **Sin cubrir todavía:** CS-09 (*red teaming*), CS-10 (demostración sin Internet), CS-11 (prueba con usuarios) y RSG-06 (manifiesto de modelos).
