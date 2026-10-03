# Diplomado_IA_GEN_Local_PI

# Agente de IA Híbrido para Gestión de Laboratorio vía WhatsApp

Sistema inteligente de gestión e inventario de herramientas/piezas para laboratorios universitarios. Se comunica a través de **WhatsApp Cloud API**, implementando un modelo **híbrido (Nube/Local)** que garantiza privacidad de datos, ejecución de LLM sin costos recurrentes por token y un control estricto de accesos.

---

## Arquitectura del Sistema

El proyecto utiliza una arquitectura descentralizada para separar la mensajería en la nube de la lógica e inferencia local en el servidor de la universidad:

```text
┌─────────────────┐       ┌────────────────────────────────────────────────────────┐
│  Estudiantes /  │       │                      NUBE (Cloud)                      │
│ Administradores │ ────> │  • Meta WhatsApp Cloud API (Webhook)                   │
└─────────────────┘       │  • Middleware Orquestador (FastAPI / Node.js)          │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │ (Cloudflare Tunnel / TLS)
                                                     ▼
                          ┌────────────────────────────────────────────────────────┐
                          │                 LOCAL (Servidor Universidad)           │
                          │  • Gateway de Autenticación                            │
                          │  • LLM Local (vLLM / Ollama + Qwen2.5 / Llama 3.1)     │
                          │  • Base de Datos de Inventario (PostgreSQL + Redis)    │
                          └────────────────────────────────────────────────────────┘

