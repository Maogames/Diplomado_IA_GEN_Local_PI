# Diplomado_IA_GEN_Local_PI

# Agente de IA Híbrido para Gestión de Laboratorio vía WhatsApp

Sistema inteligente de gestión e inventario de herramientas/piezas para laboratorios universitarios. Se comunica a través de **WhatsApp Cloud API**, implementando un modelo **híbrido (Nube/Local)** que garantiza privacidad de datos, ejecución de LLM sin costos recurrentes por token y un control estricto de accesos.

---

## Arquitectura del Sistema

El proyecto utiliza una arquitectura descentralizada para separar la mensajería en la nube de la lógica e inferencia local en el servidor de la universidad:
```text
┌─────────────────┐       ┌────────────────────────────────────────────────────────┐
│  Estudiantes /  │       │                      NUBE (Cloud)                      │
│ Administradores │ ────> │  • Meta WhatsApp Web                                   │
└─────────────────┘       │  • Middleware Orquestador (FastAPI / Node.js)          │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │ (Cloudflare Tunnel / TLS)
                                                     ▼
                          ┌────────────────────────────────────────────────────────┐
                          │                 LOCAL (Servidor Universidad)           │
                          │  • Gateway de Autenticación                            │
                          │  • LLM Local (Ollama + Qwen2.5/3 / Llama 3.1)     │
                          │  • Base de Datos de Inventario (PostgreSQL + Redis)    │
                          └────────────────────────────────────────────────────────┘
```
## Componentes del Modelo Híbrido

El sistema combina la escalabilidad de la nube para la gestión de mensajería con la potencia y privacidad de un servidor local para el almacenamiento e inferencia de Inteligencia Artificial.

---

### Nube (Messaging & Entry Point)

Capacitada para estar siempre en línea, procesar la comunicación externa y garantizar la seguridad de las conexiones recibidas.

* **WhatsApp Cloud API (Meta Graph API):** 
  Vía oficial para la comunicación bidireccional. Se encarga de recibir los mensajes de estudiantes y administradores en tiempo real para redirigirlos mediante un **Webhook** hacia la infraestructura del servidor.
* **Middleware Orquestador (Cloud Gateway):** 
  Servicio ligero desarrollado en **Python (FastAPI)** o **Node.js (Express/NestJS)**, alojado en un proveedor cloud (*AWS Lambda, GCP, DigitalOcean o Vercel*). 
  * Recibe el *payload* entrante del Webhook.
  * Valida la firma criptográfica (`HMAC-SHA256`) enviada por Meta para verificar el origen.
  * Controla y reenvía las peticiones de forma segura hacia la red local.

---

### B. Servidor Local (Laboratorio / Universidad)

Infraestructura alojada dentro de las instalaciones de la universidad para garantizar la privacidad de los datos y el costo $0 en procesamiento de inferencias.

* **Modelo LLM Local (Inferencia Local):**
  * **Motor de Inferencia:** Ejecutado sobre **Ollama** o **vLLM** aprovechando la aceleración por hardware mediante GPU local
  * **Modelo Recomendado:** **Qwen 2.5 (7B/4B)** o **Llama 3.1 (4B)**, afinados para seguimiento de instrucciones en español y soporte nativo de *Function Calling* (capacidad para invocar consultas a bases de datos y herramientas externas).
* **Gestión de Datos y Persistencia:**
  * **PostgreSQL:** Base de datos relacional encargada de gestionar el catálogo de piezas, inventario en tiempo real, registro de préstamos, estudiantes y administradores.
  * **Redis:** Caché en memoria para mantener la memoria del historial activo de cada conversación y almacenar tokens de sesión/OTP temporales.
