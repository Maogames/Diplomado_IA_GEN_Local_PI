# Prompt maestro — Módulo 1: planteamiento del problema

> **Uso previsto:** Copie este prompt completo en ChatGPT (capa gratuita). Después, pegue o cargue el PDF del proyecto integrador cuando la plataforma lo permita. El texto está diseñado para producir un documento académico formal en español, no una conversación ni una lista de ideas.

---

## Prompt para copiar y pegar

```text
Eres un investigador académico, analista de requisitos y especialista en gestión de riesgos de IA con experiencia en proyectos de transformación digital universitaria. Redacta el documento correspondiente al **Módulo 1 — Planteamiento del problema** del proyecto integrador descrito en el PDF que adjuntaré o pegaré a continuación.

### Contexto mínimo obligatorio
El proyecto consiste en un **agente técnico para un laboratorio universitario**. El agente consulta guías y procedimientos autorizados, controla el inventario asociado a prácticas de laboratorio mediante una API y genera reportes. No posee acceso general al sistema institucional: debe operar solo con fuentes, endpoints y permisos explícitamente autorizados.

### Fuente de verdad y manejo de vacíos
1. Considera el PDF adjunto como fuente principal para nombres, entregables, restricciones, metodología, criterios institucionales y cualquier dato específico del proyecto.
2. No inventes información, cifras, políticas institucionales, tecnologías, integraciones, usuarios, resultados ni requisitos que el PDF no indique o que no se desprendan razonablemente del contexto mínimo.
3. Si el PDF contiene información suficiente, intégrala de manera explícita y coherente.
4. Si falta un dato indispensable, formula una **suposición de diseño** claramente rotulada como “Suposición por validar”, explica por qué es necesaria y mantén la solución en un nivel académico y viable. No interrumpas la redacción con preguntas salvo que el PDF sea ilegible, esté vacío o no se haya proporcionado.
5. Distingue con precisión entre capacidades propuestas, requisitos verificables y resultados esperados; no afirmes que el sistema ya está implementado.

### Objetivo de tu salida
Genera un documento formal de estilo tesis en español, listo para convertir a PDF. Debe presentar y delimitar el problema que resolverá el proyecto en el Módulo 1, con énfasis en el uso responsable y acotado de un agente de IA en un laboratorio universitario.

### Requisitos de forma
- Redacta en tono profesional, académico, objetivo y en tercera persona.
- Usa Markdown con títulos jerárquicos (`#`, `##`, `###`), párrafos completos, tablas y listas solo cuando aporten claridad.
- No incluyas saludos, explicaciones sobre tu proceso, notas al usuario, emojis ni texto conversacional.
- No uses citas, normas o autores inexistentes. Si el PDF aporta referencias, consérvalas sin inventar datos bibliográficos.
- Mantén coherencia terminológica: “agente técnico”, “laboratorio universitario”, “API autorizada”, “inventario de práctica” y “usuario autorizado”.
- Evita expresiones absolutas tales como “elimina todo riesgo”, “garantiza precisión total” o “acceso a todo el sistema”.
- La extensión objetivo es de 1,500 a 2,200 palabras, salvo que el PDF defina otra extensión. Privilegia la calidad y la trazabilidad sobre el relleno.

### Estructura obligatoria

# Módulo 1. Planteamiento del problema

## 1. Introducción
Expón brevemente el contexto de los laboratorios universitarios, la necesidad de consultar guías, disponer de inventario confiable para prácticas y elaborar reportes. Introduce la oportunidad y la restricción central: un agente técnico con acceso limitado y controlado, no un asistente con acceso general a los sistemas institucionales.

## 2. Contexto y situación problemática
Describe la situación actual o problemática utilizando únicamente lo indicado por el PDF y el contexto mínimo. Explica las posibles dificultades operativas que el proyecto busca atender, por ejemplo: dispersión de guías autorizadas, consulta manual de disponibilidad, inconsistencias en el seguimiento del inventario de prácticas, demora en la elaboración de reportes o falta de trazabilidad. Presenta estas situaciones como aspectos a validar si el PDF no las confirma.

Delimita el entorno: laboratorio universitario, prácticas académicas, información y API autorizadas, usuarios con roles definidos y ausencia de acceso general al sistema. Señala por qué esta delimitación es necesaria para proteger información, reducir acciones no autorizadas y mantener la supervisión humana.

## 3. Planteamiento del problema
Redacta un planteamiento del problema sólido, en varios párrafos conectados. Debe responder con claridad:
- Qué problema existe y en qué contexto ocurre.
- A quién afecta.
- Qué consecuencias operativas, académicas, de trazabilidad o de seguridad puede producir.
- Por qué las prácticas actuales resultan insuficientes.
- Cómo un agente técnico, limitado a guías autorizadas, API de inventario permitida y generación de reportes, podría contribuir a atenderlo sin sustituir decisiones críticas ni ampliar privilegios.

Cierra esta sección con una pregunta de investigación o pregunta problema, concreta y viable. La pregunta debe incorporar el diseño o implementación del agente, el laboratorio universitario, la consulta de guías, el inventario mediante API, la generación de reportes y los límites de acceso.

## 4. Justificación
Argumenta la relevancia académica, operativa, tecnológica y de seguridad del proyecto. Explica el valor de centralizar consultas autorizadas, mejorar la disponibilidad de información para prácticas, apoyar el control del inventario y estandarizar reportes. Incluye por qué el principio de mínimo privilegio, la trazabilidad y la supervisión humana son condiciones de valor y no obstáculos del proyecto.

## 5. Usuarios y partes interesadas
Incluye una tabla con las columnas: **Actor**, **Rol o necesidad**, **Interacción permitida con el agente**, **Información o acción autorizada** y **Restricción o responsabilidad**.

Como mínimo, considera —si el PDF no indica otra clasificación— los siguientes actores:
- Estudiantes o practicantes autorizados.
- Docentes responsables de práctica.
- Técnicos o auxiliares de laboratorio.
- Coordinación o administración del laboratorio.
- Administrador de la API o sistema de inventario.
- Equipo responsable del proyecto.

No atribuyas permisos sensibles sin justificarlos. Explica después de la tabla la diferencia entre usuarios finales, responsables de aprobación y responsables técnicos.

## 6. Alcance y delimitación
Separa expresamente los siguientes apartados:

### 6.1 Alcance funcional incluido
Define capacidades dentro del alcance: consulta de guías y procedimientos autorizados; consulta o actualización del inventario de práctica solamente por API y según permisos; generación de reportes con datos autorizados; registro de solicitudes, respuestas, errores y acciones relevantes; escalamiento de solicitudes fuera de permiso a un responsable humano.

### 6.2 Exclusiones
Indica de manera explícita lo que no forma parte del proyecto: acceso general a sistemas institucionales; acceso a datos personales no necesarios; modificación de configuraciones críticas; toma autónoma de decisiones académicas, de seguridad o de compra; ejecución de acciones irreversibles sin validación humana; uso de fuentes no autorizadas como si fueran oficiales.

### 6.3 Límites operativos y supuestos por validar
Expón límites de permisos, dependencia de disponibilidad de la API, calidad y actualización de las guías, autenticación, registro de auditoría, revisión humana y gestión de errores. Rotula como “Suposición por validar” todo elemento que no proceda del PDF.

## 7. Requisitos del sistema
Incluye una tabla de requisitos con las columnas: **ID**, **Tipo**, **Requisito**, **Prioridad**, **Criterio de verificación** y **Relación con el riesgo**.

Define requisitos funcionales (RF), no funcionales (RNF) y de seguridad/gobierno (RSG). Incluye, como mínimo y adaptándolos al PDF:
- RF-01: consultar guías autorizadas y comunicar la fuente o versión disponible.
- RF-02: consultar el inventario de práctica mediante endpoints API autorizados.
- RF-03: ejecutar actualizaciones de inventario solo si el rol, la operación y la confirmación requerida lo permiten.
- RF-04: generar reportes trazables a partir de información autorizada.
- RF-05: derivar al responsable humano las solicitudes fuera de alcance o de confianza insuficiente.
- RNF-01: ofrecer respuestas comprensibles y conservar trazabilidad de las acciones relevantes.
- RNF-02: manejar fallos de API sin inventar disponibilidad, resultados ni confirmaciones.
- RSG-01: aplicar mínimo privilegio, autenticación y autorización por rol.
- RSG-02: no acceder, inferir ni revelar información fuera de las fuentes y permisos autorizados.
- RSG-03: registrar eventos, errores, denegaciones y aprobaciones para auditoría.
- RSG-04: exigir supervisión o aprobación humana en operaciones definidas como sensibles o irreversibles.

No declare que un requisito está cumplido: formule cada uno como condición de aceptación del futuro sistema.

## 8. Matriz de riesgos — NIST AI RMF
Presenta primero un párrafo que indique que la matriz se organiza conforme a las cuatro funciones del NIST AI Risk Management Framework: **GOVERN, MAP, MEASURE y MANAGE**. Explica brevemente que GOVERN atraviesa todo el ciclo de vida, mientras MAP contextualiza el sistema y sus impactos, MEASURE evalúa los riesgos identificados y MANAGE prioriza e implementa el tratamiento de riesgos.

Después, elabora una matriz en Markdown con estas columnas:

| ID | Función NIST AI RMF | Riesgo o escenario | Causa o fuente | Impacto potencial | Probabilidad | Nivel inherente | Controles o mitigación | Evidencia / métrica de seguimiento | Riesgo residual | Responsable |

Incluye entre 8 y 12 riesgos relevantes, sin presentar la lista como exhaustiva. Deben cubrir, según corresponda:
- Respuestas inexactas, desactualizadas o no sustentadas en guías autorizadas.
- Uso de una fuente no autorizada o confusión entre versiones de guías.
- Acceso indebido o excedente de privilegios en la API de inventario.
- Actualización errónea, duplicada o no autorizada del inventario.
- Caída, latencia o respuesta inconsistente de la API.
- Divulgación de información sensible o datos personales no necesarios.
- Falta de trazabilidad, auditoría o explicabilidad de respuestas y acciones.
- Dependencia excesiva del agente o ausencia de revisión humana en decisiones sensibles.
- Prompt injection, instrucciones maliciosas o intento de eludir restricciones.
- Sesgos o tratamiento desigual en el acceso, la respuesta o el escalamiento de solicitudes, si resulta aplicable al contexto.

Usa escalas cualitativas coherentes (Baja, Media, Alta; o Bajo, Medio, Alto) y define la escala inmediatamente antes de la tabla. Vincula cada mitigación con límites verificables: control de acceso por rol, lista de fuentes permitidas, validación de entradas, confirmación humana, registros de auditoría, manejo seguro de errores, pruebas, monitoreo y procedimiento de escalamiento. No presentes el riesgo residual como nulo si subsiste incertidumbre.

Tras la matriz, incorpora los siguientes subapartados:

### 8.1 GOVERN
Define responsables, políticas de uso aceptable, propiedad de datos, principio de mínimo privilegio, formación de usuarios, rendición de cuentas, gestión de incidentes y revisión periódica de la matriz.

### 8.2 MAP
Delimita propósito, usuarios, fuentes autorizadas, flujos de datos, decisiones asistidas, límites de automatización, posibles personas afectadas y riesgos contextuales.

### 8.3 MEASURE
Propón indicadores verificables: porcentaje de respuestas con fuente autorizada identificable; tasa de operaciones API autorizadas; porcentaje de fallos reportados correctamente sin información inventada; cobertura de registros de auditoría; tasa de escalamiento de casos fuera de alcance; y resultados de pruebas de permisos, seguridad y calidad. No inventes valores base; presenta metas como “por definir” o “a validar” cuando el PDF no las establezca.

### 8.4 MANAGE
Establece las respuestas al riesgo: prevenir, mitigar, transferir cuando aplique, aceptar de forma documentada o detener/escalar la operación. Incluye un mecanismo para suspender operaciones sensibles ante anomalías, revocar credenciales comprometidas, informar a responsables y corregir guías, permisos o reglas antes de reanudar el servicio.

## 9. Criterios de éxito
Incluye una tabla con: **ID**, **Criterio de éxito**, **Indicador o evidencia**, **Meta o condición de aceptación**, **Método de validación** y **Responsable de validación**.

Los criterios deben ser comprobables y alinearse con el alcance, los requisitos y la matriz de riesgos. Incluye criterios sobre consultas correctas a guías autorizadas, operaciones de inventario autorizadas, generación de reportes, denegación o escalamiento seguro de solicitudes fuera de permiso, trazabilidad, manejo de fallos de API, pruebas de roles y revisión de usuarios. Si no hay métricas específicas en el PDF, utiliza condiciones cualitativas verificables o marca el umbral cuantitativo como “por definir en la fase de validación”.

## 10. Conclusión del Módulo 1
Sintetiza el problema, la solución propuesta y sus límites. Reafirma que el valor del agente depende de que sus capacidades estén delimitadas, sean auditables, se basen en información autorizada y mantengan supervisión humana para las acciones sensibles. Conecta esta definición del problema con las fases posteriores de diseño, implementación y evaluación, sin afirmar que ya se han ejecutado.

### Control final antes de entregar
Verifica internamente y corrige antes de mostrar el documento:
- ¿Se usó el PDF como fuente principal y se separaron los supuestos por validar?
- ¿El planteamiento incluye problema, afectados, consecuencias, causas, delimitación y pregunta problema?
- ¿Existen usuarios, alcance, requisitos, matriz NIST AI RMF y criterios de éxito?
- ¿La matriz contiene GOVERN, MAP, MEASURE y MANAGE, y cada riesgo tiene mitigación, evidencia, responsable y riesgo residual?
- ¿Quedó explícito que el agente no tiene acceso general al sistema y opera mediante permisos y API autorizados?
- ¿El texto evita promesas absolutas, datos inventados y afirmaciones de implementación terminada?

Entrega únicamente el documento final en Markdown.
```

## Nota de diseño

Este prompt estructura la matriz según las cuatro funciones del núcleo del NIST AI RMF: **GOVERN, MAP, MEASURE y MANAGE**. El marco plantea GOVERN como función transversal, mientras que las otras tres permiten contextualizar, evaluar y tratar los riesgos del sistema de IA de forma iterativa. [web:1][web:3]

## Resultado esperado

Al usarlo, ChatGPT deberá generar un documento de Módulo 1 con una delimitación clara del agente: consulta de guías aprobadas, interacción restringida con una API de inventario y reportes trazables. También deberá excluir acceso institucional general, acciones irreversibles no aprobadas y uso de información fuera de los permisos definidos.
