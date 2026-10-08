# Módulo 1. Planteamiento del problema

## 1. Introducción

Los laboratorios universitarios constituyen espacios fundamentales para el desarrollo de competencias prácticas en los procesos de formación profesional. En estos entornos, la ejecución de prácticas académicas requiere disponer de procedimientos claros, documentación técnica pertinente, recursos disponibles y mecanismos que permitan hacer seguimiento de las actividades desarrolladas. En el contexto del Diplomado en Inteligencia Artificial Generativa Local, estos elementos adquieren especial relevancia por la orientación del programa hacia soluciones de inteligencia artificial locales, reproducibles, evaluables y gobernables.

El proyecto integrador plantea el desarrollo de un **agente técnico para un laboratorio universitario**, orientado a consultar guías y procedimientos autorizados, interactuar con el inventario de práctica mediante una API autorizada y generar reportes. La solución se concibe bajo un principio de autonomía limitada: el agente técnico no dispone de acceso general a los sistemas institucionales, sino que opera únicamente sobre fuentes, herramientas, endpoints y permisos expresamente autorizados.

Esta delimitación responde a los principios de seguridad, trazabilidad, privacidad y supervisión humana promovidos por el diplomado, que establece que los agentes deben utilizar herramientas y permisos delimitados y que las operaciones sensibles requieren controles y, cuando corresponda, aprobación humana.

## 2. Contexto y situación problemática

El diplomado plantea una formación orientada a la construcción de soluciones de IA capaces de integrarse con fuentes de conocimiento, herramientas y sistemas existentes. En este marco, los agentes representan una evolución respecto de los sistemas que únicamente generan respuestas, pues pueden consultar conocimiento, invocar funciones, interactuar con recursos y coordinar tareas. Esa misma capacidad introduce riesgos relacionados con permisos excesivos, ejecución no autorizada, *prompt injection* y exposición de información.

En el caso del laboratorio universitario, el proyecto identifica la necesidad de un mecanismo técnico que facilite la consulta de guías y procedimientos, permita consultar o gestionar la información del inventario de práctica mediante una interfaz controlada y genere reportes sobre información autorizada. El documento fuente destaca como aspectos relevantes la necesidad de bases de conocimiento documentales, mecanismos de recuperación con referencias, herramientas delimitadas y trazabilidad de las invocaciones. El Módulo 3 del diplomado establece precisamente como práctica la construcción de asistentes que consulten documentos, recuperen evidencia, citen fuentes y utilicen herramientas delimitadas.

Las dificultades operativas que el proyecto busca atender incluyen la dispersión de guías y procedimientos en distintos documentos o sistemas, la consulta manual de la disponibilidad de recursos, las posibles inconsistencias en el seguimiento del inventario de práctica, la demora en la elaboración de reportes y la falta de trazabilidad sobre consultas y modificaciones.

**Suposición por validar:** el documento fuente no cuantifica la magnitud de estas dificultades ni describe el procedimiento vigente del laboratorio. Se presentan como situaciones plausibles que deberán confirmarse mediante levantamiento de información con los responsables del laboratorio.

El entorno del proyecto queda delimitado así: un laboratorio universitario, prácticas académicas, fuentes documentales y una API autorizada, usuarios autorizados con roles definidos y ausencia de acceso general al sistema institucional. Esta delimitación es necesaria para proteger la información, reducir la posibilidad de acciones no autorizadas y conservar la supervisión humana sobre las operaciones que lo requieran.

En consecuencia, el problema no consiste únicamente en crear una interfaz conversacional. El desafío principal es diseñar un agente técnico que apoye las actividades del laboratorio sin convertir su capacidad de automatización en un mecanismo de acceso indiscriminado a información o sistemas institucionales.

**Suposición por validar:** el documento fuente no especifica la estructura actual de las guías, los endpoints concretos de la API de inventario ni los roles institucionales definitivos. Estos elementos deberán definirse durante las fases de análisis y diseño.

## 3. Planteamiento del problema

En un laboratorio universitario, la realización de prácticas académicas requiere que los usuarios dispongan de información sobre procedimientos, guías y recursos disponibles. Cuando esta información se encuentra distribuida en diferentes documentos o sistemas, aumenta la complejidad de su consulta y se dificulta la obtención de respuestas contextualizadas. De manera complementaria, la información del inventario de práctica requiere mecanismos de consulta y actualización que conserven su consistencia y trazabilidad.

La situación afecta a estudiantes o practicantes, que necesitan información confiable para ejecutar sus prácticas; a docentes, que orientan y supervisan dichas prácticas; al personal técnico, que gestiona los recursos y el inventario; y a los responsables administrativos o técnicos del laboratorio, que requieren reportes para el seguimiento de la operación. Las capacidades de cada actor deben diferenciarse mediante autenticación y autorización: la solución no debe asumir que un usuario que puede consultar una guía posee automáticamente autorización para modificar el inventario de práctica.

Las prácticas basadas en consulta manual y documentación dispersa resultan insuficientes porque dependen de la disponibilidad de personas concretas, dificultan verificar qué versión de una guía es vigente y no siempre dejan registro de quién consultó o modificó la información. A la vez, la incorporación de un agente sin restricciones podría producir consecuencias igualmente indeseables: respuestas basadas en información incorrecta o desactualizada, modificaciones no autorizadas del inventario, pérdida de trazabilidad, exposición de información y dependencia excesiva de las respuestas generadas. El propio diplomado identifica riesgos asociados con *prompt injection*, fuga de datos, uso indebido de herramientas y permisos excesivos.

El proyecto propone atender esta situación mediante un agente técnico capaz de consultar fuentes documentales autorizadas, acceder al inventario de práctica exclusivamente mediante una API autorizada y generar reportes a partir de información disponible y verificable. El enfoque RAG planteado por el diplomado resulta pertinente porque permite recuperar evidencia documental y presentar referencias, lo que reduce las respuestas no sustentadas. El agente técnico debe entenderse como un componente de apoyo y no como un sustituto de las responsabilidades humanas: su autonomía será limitada, observable y reversible, en particular cuando una operación pueda modificar información o requiera aprobación.

La pregunta problema que orienta el proyecto es:

> **¿Cómo diseñar e implementar un agente técnico para un laboratorio universitario que consulte guías y procedimientos autorizados, apoye las solicitudes de préstamo y demás procedimientos autorizados, interactúe con el inventario de práctica mediante una API autorizada y genere reportes trazables, manteniendo límites de acceso, controles de seguridad y supervisión humana sobre las operaciones sensibles?**

## 4. Justificación

### 4.1 Justificación académica

El proyecto permite aplicar de manera integrada las competencias desarrolladas en el diplomado sobre RAG, agentes, APIs, generación de código, evaluación y gobernanza. El proyecto integrador exige que la solución documente problema, usuarios, alcance, requisitos, arquitectura, evaluación, seguridad y documentación, lo que convierte este módulo en la base de las fases posteriores.

### 4.2 Justificación operativa

La integración de consultas documentales, información del inventario de práctica y generación de reportes puede proporcionar un punto único de apoyo a las actividades del laboratorio. Centralizar las consultas autorizadas puede mejorar la disponibilidad de información para las prácticas, apoyar el control del inventario y estandarizar el formato de los reportes, siempre que las operaciones estén condicionadas por los permisos establecidos.

### 4.3 Justificación tecnológica

El proyecto permite aplicar una arquitectura local o híbrida que combine modelos locales, una base de conocimiento RAG y herramientas controladas. El enfoque *local-first* del diplomado busca que los laboratorios puedan operar sin conexión una vez preparado el entorno y que la información que requiera confidencialidad permanezca dentro de la infraestructura de práctica.

### 4.4 Justificación de seguridad y gobierno

El mínimo privilegio, la trazabilidad y la supervisión humana son condiciones de valor del proyecto y no obstáculos. Un agente técnico que solo accede a lo necesario reduce la superficie de error y de ataque; un agente cuyas acciones quedan registradas puede auditarse y corregirse; y un agente que escala las operaciones sensibles a un responsable humano preserva la rendición de cuentas institucional. El diplomado establece que los agentes no deben recibir acceso irrestricto y que las herramientas capaces de modificar datos requieren controles y aprobación humana en acciones sensibles.

## 5. Usuarios y partes interesadas

| Actor | Rol o necesidad | Interacción permitida con el agente | Información o acción autorizada | Restricción o responsabilidad |
|---|---|---|---|---|
| Estudiantes o practicantes autorizados | Consultar información para desarrollar prácticas | Consulta de guías, procedimientos y disponibilidad; registro de solicitudes de préstamo | Guías vigentes y disponibilidad del inventario de práctica | No pueden modificar el inventario; sus solicitudes requieren aprobación de un responsable |
| Docentes responsables de práctica | Orientar y supervisar prácticas | Consultas, generación de reportes de sus prácticas y aprobación de solicitudes | Guías, información de sus prácticas y reportes | Validar las solicitudes y acciones que requieran aprobación en su ámbito |
| Técnicos o auxiliares de laboratorio | Gestionar recursos e inventario | Consultas y operaciones de inventario según rol | Registro de entradas, salidas y préstamos por API autorizada | Responder por las operaciones ejecutadas; confirmar actualizaciones sensibles |
| Coordinación o administración del laboratorio | Supervisar la operación | Consulta de reportes e indicadores | Reportes consolidados e indicadores | Aprobar decisiones administrativas; no delegar en el agente decisiones de compra o sanción |
| Administrador de la API o sistema de inventario | Administrar la integración técnica | Configuración de endpoints y credenciales, fuera del canal conversacional | Permisos, credenciales y disponibilidad del servicio | Mantener autenticación, autorización y revocación de credenciales |
| Equipo responsable del proyecto | Diseñar, implementar y evaluar | Administración técnica en entorno de desarrollo y pruebas | Configuración, datos de prueba y documentación | No ampliar permisos fuera del alcance aprobado ni usar datos reales sin autorización |

**Suposición por validar:** la asignación de la aprobación de préstamos a docentes y técnicos se propone por coherencia con sus funciones; el reglamento del laboratorio deberá confirmarla.

La clasificación distingue tres tipos de actores. Los **usuarios finales** (estudiantes, docentes en su función de consulta y coordinación) utilizan las capacidades habilitadas para su rol. Los **responsables de aprobación** (docentes, técnicos y coordinación) intervienen en las operaciones sensibles y responden por ellas. Los **responsables técnicos** (administrador de la API y equipo del proyecto) administran la infraestructura, las integraciones, los permisos y los mecanismos de auditoría, sin intervenir en las decisiones académicas.

## 6. Alcance y delimitación

### 6.1 Alcance funcional incluido

El sistema propuesto incluirá:

- Consulta de guías y procedimientos autorizados, con referencia a la fuente y a la versión disponible.
- Consulta del inventario de práctica mediante la API autorizada.
- Actualización del inventario de práctica y registro de solicitudes de préstamo únicamente cuando el rol, la operación y la confirmación requerida lo permitan.
- Generación de reportes basados en información autorizada, con indicación del origen de los datos.
- Registro de solicitudes, respuestas, errores, denegaciones y acciones relevantes.
- Escalamiento a un responsable humano cuando una solicitud esté fuera del alcance, fuera de permiso o requiera aprobación.

### 6.2 Exclusiones

El proyecto no contempla:

- Acceso general a sistemas institucionales.
- Consulta de datos personales que no sean necesarios para la operación.
- Modificación de configuraciones críticas.
- Toma autónoma de decisiones académicas, de seguridad o de compra.
- Ejecución de operaciones irreversibles sin validación humana.
- Uso de fuentes no autorizadas como si fueran oficiales.
- Ampliación automática de privilegios del agente técnico.

### 6.3 Límites operativos y supuestos por validar

- **Permisos:** el agente técnico actuará con credenciales propias de mínimo privilegio y con los permisos del usuario autorizado que realiza la solicitud, sin superar ninguno de los dos. *Suposición por validar:* el modelo de delegación de permisos deberá definirse en el diseño.
- **Disponibilidad de la API:** el agente dependerá de la disponibilidad y calidad de la API. Una falla del servicio no deberá llevarlo a inventar disponibilidad, resultados ni confirmaciones; deberá informar el error y, si corresponde, escalar.
- **Calidad de las guías:** la exactitud de las respuestas dependerá de que las guías estén vigentes y versionadas. *Suposición por validar:* se requiere un responsable de mantener el repositorio documental autorizado.
- **Autenticación:** *Suposición por validar:* el mecanismo concreto (por ejemplo, integración con el directorio institucional o cuentas locales del laboratorio) deberá definirse con el área técnica.
- **Auditoría:** los registros deberán conservar usuario, fecha, operación, resultado y aprobación asociada. *Suposición por validar:* el tiempo de retención y su ubicación deberán definirse.
- **Revisión humana:** *Suposición por validar:* el catálogo de operaciones sensibles que exigirán confirmación deberá acordarse con los responsables del laboratorio.
- **Gestión de errores:** ante entradas ambiguas, permisos insuficientes o confianza insuficiente en la respuesta, el agente deberá denegar o escalar en lugar de ejecutar.

## 7. Requisitos del sistema

| ID | Tipo | Requisito | Prioridad | Criterio de verificación | Relación con el riesgo |
|---|---|---|---|---|---|
| RF-01 | Funcional | Consultar guías autorizadas y comunicar la fuente o versión utilizada | Alta | Casos de prueba con preguntas sobre guías conocidas; cada respuesta indica fuente y versión | R-01, R-02 |
| RF-02 | Funcional | Consultar el inventario de práctica mediante endpoints de la API autorizada | Alta | Pruebas de consulta con permisos válidos; verificación de que solo se invocan endpoints de la lista permitida | R-03 |
| RF-03 | Funcional | Ejecutar actualizaciones de inventario y registrar solicitudes de préstamo solo si el rol, la operación y la confirmación requerida lo permiten | Alta | Pruebas positivas y negativas por rol; operaciones sin confirmación no se ejecutan | R-03, R-04 |
| RF-04 | Funcional | Generar reportes trazables a partir de información autorizada | Alta | Revisión de reportes: cada dato remite a su origen y momento de consulta | R-07 |
| RF-05 | Funcional | Derivar al responsable humano las solicitudes fuera de alcance o de confianza insuficiente | Alta | Casos de prueba con solicitudes no permitidas o ambiguas; se registran como escaladas | R-08 |
| RNF-01 | No funcional | Ofrecer respuestas comprensibles y conservar trazabilidad de las acciones relevantes | Alta | Revisión de respuestas por usuarios de prueba y verificación cruzada con registros | R-07 |
| RNF-02 | No funcional | Manejar fallos de la API sin inventar disponibilidad, resultados ni confirmaciones | Alta | Simulación de caída, latencia y respuestas inválidas de la API | R-05 |
| RSG-01 | Seguridad/gobierno | Aplicar mínimo privilegio, autenticación y autorización por rol | Alta | Pruebas de permisos por cada rol definido | R-03, R-10 |
| RSG-02 | Seguridad/gobierno | No acceder, inferir ni revelar información fuera de las fuentes y permisos autorizados | Alta | Pruebas de extracción y de fuga de información | R-06, R-09 |
| RSG-03 | Seguridad/gobierno | Registrar eventos, errores, denegaciones y aprobaciones para auditoría | Alta | Inspección de registros frente a un guion de operaciones de prueba | R-07 |
| RSG-04 | Seguridad/gobierno | Exigir supervisión o aprobación humana en operaciones definidas como sensibles o irreversibles | Alta | Pruebas de confirmación: ninguna operación sensible se completa sin aprobación registrada | R-04, R-08 |
| RSG-05 | Seguridad/gobierno | Tratar el contenido de documentos y entradas como datos, no como instrucciones | Alta | Pruebas adversariales de *prompt injection* | R-09 |

Estos requisitos constituyen condiciones de aceptación del futuro sistema y no evidencias de funcionalidades implementadas.

## 8. Matriz de riesgos — NIST AI RMF

La matriz se organiza según las cuatro funciones del **NIST AI Risk Management Framework: GOVERN, MAP, MEASURE y MANAGE**. GOVERN establece responsabilidades y políticas de manera transversal a todo el ciclo de vida; MAP contextualiza el sistema, su propósito y sus impactos; MEASURE evalúa los riesgos identificados mediante pruebas y métricas; y MANAGE prioriza e implementa su tratamiento. El diplomado adopta estas cuatro funciones como referencia para la documentación, la caracterización del contexto, las pruebas, las métricas, los controles y la mitigación. Cada riesgo se asigna a la función desde la cual se gestiona principalmente, aunque todos atraviesan las cuatro.

**Escala de valoración.** Probabilidad: *Baja* (poco esperable en la operación normal), *Media* (puede presentarse ocasionalmente), *Alta* (esperable sin controles). Nivel inherente y riesgo residual: *Bajo*, *Medio* o *Alto*, según la combinación de probabilidad e impacto antes y después de aplicar los controles previstos.

| ID | Función NIST AI RMF | Riesgo o escenario | Causa o fuente | Impacto potencial | Probabilidad | Nivel inherente | Controles o mitigación | Evidencia / métrica de seguimiento | Riesgo residual | Responsable |
|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | MEASURE | Respuesta inexacta, desactualizada o no sustentada | Guías desactualizadas o recuperación deficiente | Errores en la ejecución de prácticas | Media | Alto | Recuperación limitada a fuentes autorizadas; citación obligatoria de fuente y versión; respuesta "no encontrado" cuando no hay evidencia | % de respuestas con fuente autorizada identificable | Medio | Equipo del proyecto |
| R-02 | GOVERN | Uso de fuente no autorizada o confusión entre versiones | Repositorio sin control de versiones o configuración inadecuada | Información no oficial presentada como vigente | Media | Alto | Lista de fuentes permitidas; versionado y responsable del repositorio documental | Auditoría periódica de fuentes indexadas | Bajo | Responsable técnico |
| R-03 | MAP | Acceso indebido o privilegios excedentes en la API | Credenciales con permisos superiores a los necesarios | Consulta o modificación indebida del inventario | Media | Alto | Mínimo privilegio; lista de endpoints permitidos; autorización por rol | Resultados de pruebas de autorización por rol | Medio | Administrador de la API |
| R-04 | MANAGE | Actualización errónea, duplicada o no autorizada del inventario | Error del agente, del usuario o reintentos automáticos | Inventario inconsistente | Media | Alto | Validación de entradas; confirmación humana; operaciones idempotentes; registro reversible | Casos de prueba de actualización; incidencias registradas | Medio | Técnico de laboratorio |
| R-05 | MEASURE | Caída, latencia o respuesta inconsistente de la API | Falla del servicio o de la red | Información incompleta o retrasos | Media | Medio | Manejo seguro de errores; tiempos de espera; prohibición de completar datos faltantes | % de fallos reportados correctamente | Bajo | Responsable técnico |
| R-06 | GOVERN | Divulgación de información sensible o datos personales no necesarios | Permisos o fuentes mal configurados | Pérdida de confidencialidad | Baja | Alto | Control de acceso; minimización de datos; exclusión de datos personales de las fuentes | Resultados de pruebas de fuga de información | Medio | Responsable de seguridad |
| R-07 | MEASURE | Falta de trazabilidad o explicabilidad | Registros incompletos | Imposibilidad de auditar o corregir | Media | Alto | Registro de eventos, operaciones, denegaciones y aprobaciones | Cobertura de registros de auditoría | Bajo | Equipo del proyecto |
| R-08 | MANAGE | Dependencia excesiva del agente o ausencia de revisión humana | Confianza no calibrada de los usuarios | Decisiones incorrectas sin revisión | Media | Alto | Escalamiento obligatorio; aprobación humana en operaciones sensibles; formación de usuarios | Tasa de escalamiento; revisión de casos aprobados | Medio | Docente / responsable de laboratorio |
| R-09 | MAP | *Prompt injection* o intento de eludir restricciones | Documento o entrada maliciosa | Ejecución de acciones no autorizadas | Media | Alto | Contenido tratado como datos; aislamiento de herramientas; validación de entradas; pruebas adversariales | Resultados de *red teaming* | Medio | Responsable de seguridad |
| R-10 | GOVERN | Tratamiento desigual en el acceso, la respuesta o el escalamiento | Reglas o permisos inconsistentes entre roles o usuarios | Atención desigual a usuarios autorizados | Baja | Medio | Revisión de reglas por rol; casos de prueba equivalentes entre perfiles | Pruebas comparativas por perfil | Bajo | Equipo del proyecto |

La matriz no se considera exhaustiva y deberá actualizarse en las fases posteriores. Los controles propuestos se alinean con las recomendaciones del diplomado sobre aislamiento de agentes, limitación de directorios, comandos, redes y credenciales, así como con las pruebas de *prompt injection*, fuga de información y uso indebido de herramientas. Ningún riesgo residual se considera nulo.

### 8.1 GOVERN

La función GOVERN establecerá los responsables de cada riesgo, una política de uso aceptable del agente técnico, la propiedad de los datos documentales y del inventario de práctica, y la aplicación del principio de mínimo privilegio. Incluirá la formación de los usuarios autorizados sobre los alcances y límites del agente, la rendición de cuentas sobre las aprobaciones, un procedimiento de gestión de incidentes y la revisión periódica de esta matriz. El proyecto mantendrá documentación de las fuentes, modelos, herramientas y permisos utilizados.

### 8.2 MAP

MAP caracterizará el propósito del agente técnico, los usuarios autorizados, las fuentes autorizadas, los flujos de información entre usuario, agente, repositorio documental y API, y las decisiones que el agente solo asiste. Identificará los límites de automatización, las operaciones que requieren intervención humana, las personas que podrían verse afectadas por errores (por ejemplo, estudiantes a quienes se niega o asigna un recurso) y los riesgos propios del contexto del laboratorio.

### 8.3 MEASURE

La evaluación considerará, como mínimo, los siguientes indicadores:

| Indicador | Meta |
|---|---|
| Porcentaje de respuestas con fuente autorizada identificable | Por definir en la fase de validación |
| Tasa de operaciones API correctamente autorizadas | Por definir en la fase de validación |
| Porcentaje de fallos reportados correctamente sin información inventada | Por definir en la fase de validación |
| Cobertura de registros de auditoría | Por definir en la fase de validación |
| Tasa de solicitudes fuera de alcance correctamente escaladas | Por definir en la fase de validación |
| Resultados de pruebas de permisos, seguridad y calidad | A validar con el plan de pruebas |

### 8.4 MANAGE

La gestión de riesgos contemplará cinco respuestas: **prevenir** (no habilitar capacidades fuera del alcance), **mitigar** (controles técnicos y de aprobación), **transferir** cuando aplique (por ejemplo, la disponibilidad de la API al área que la administra), **aceptar de forma documentada** los riesgos residuales y **detener o escalar** la operación. Ante anomalías en operaciones sensibles, el sistema deberá suspender dichas operaciones, revocar o rotar las credenciales comprometidas, informar a los responsables y corregir las guías, permisos o reglas que originaron el incidente antes de reanudar el servicio.

## 9. Criterios de éxito

| ID | Criterio de éxito | Indicador o evidencia | Meta o condición de aceptación | Método de validación | Responsable de validación |
|---|---|---|---|---|---|
| CS-01 | Consulta correcta de guías autorizadas | Respuestas con fuente y versión | Fuente identificable y pertinente; umbral por definir en la fase de validación | Casos de prueba con preguntas conocidas | Docente |
| CS-02 | Consulta de inventario autorizada | Registro de llamadas a la API | Solo se invocan endpoints permitidos | Pruebas de roles | Administrador de la API |
| CS-03 | Actualización controlada del inventario | Registro de la operación y su confirmación | Ninguna actualización sin permiso y confirmación definida | Pruebas positivas y negativas | Técnico de laboratorio |
| CS-04 | Reportes trazables | Reporte con origen de los datos | Cada dato remite a su fuente | Revisión documental | Docente |
| CS-05 | Denegación o escalamiento seguro | Registro de solicitudes rechazadas o escaladas | Ninguna solicitud no autorizada ejecutada | Pruebas de seguridad | Responsable técnico |
| CS-06 | Manejo de fallos de la API | Registro de errores y respuestas emitidas | No se inventan resultados ante fallos | Simulación de API caída o lenta | Equipo del proyecto |
| CS-07 | Trazabilidad y auditoría | Registros de eventos | Eventos relevantes registrados; cobertura por definir en la fase de validación | Inspección de registros | Responsable técnico |
| CS-08 | Supervisión humana | Evidencias de aprobación | Toda operación sensible cuenta con aprobación registrada | Pruebas funcionales | Responsable de laboratorio |
| CS-09 | Aceptación por usuarios | Resultados de revisión con usuarios autorizados de cada rol | Respuestas comprensibles según los usuarios; instrumento por definir | Sesiones de prueba con usuarios | Coordinación del laboratorio |

Los umbrales cuantitativos específicos quedan **por definir en la fase de validación**, ya que el documento fuente no establece valores concretos para este agente técnico.

## 10. Conclusión del Módulo 1

El proyecto plantea un agente técnico orientado a apoyar las actividades de un laboratorio universitario mediante tres capacidades principales: la consulta de guías autorizadas, la interacción controlada con el inventario de práctica mediante una API autorizada y la generación de reportes trazables, complementadas con el apoyo a solicitudes de préstamo y demás procedimientos autorizados.

El problema central no se limita a automatizar consultas, sino a lograr que la automatización ocurra dentro de límites técnicos y organizacionales verificables. El agente técnico deberá operar únicamente sobre fuentes y herramientas autorizadas, aplicar controles de acceso por rol, mantener registros que permitan revisar sus acciones y escalar a un responsable humano las operaciones sensibles. La propuesta es coherente con el enfoque del Diplomado en IA 5.0 Lab, que concibe la autonomía como una delegación limitada, observable y reversible, y que exige evaluación, seguridad, privacidad y documentación en los proyectos integradores.

El valor del proyecto dependerá de la coherencia entre problema, usuarios, datos, arquitectura, modelo, integración, evaluación y seguridad. El sistema no deberá interpretarse como un mecanismo de acceso general a los sistemas institucionales ni como sustituto de las decisiones humanas sensibles. Las fases posteriores de diseño, implementación y evaluación deberán validar los supuestos aquí señalados y demostrar, mediante pruebas y evidencias, que las capacidades definidas pueden ejecutarse de forma controlada y reproducible.
