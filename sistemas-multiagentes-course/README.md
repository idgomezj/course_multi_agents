# Sistemas Multiagentes e Inteligencia Artificial

Curso compacto de cuatro módulos, alineado con el programa oficial de la asignatura y diseñado para impartirse en pocos días.

## Principio de diseño

El curso está centrado en **Sistemas Multiagentes (SMA)**. Los LLMs y Pydantic AI se utilizan como herramientas modernas de implementación, no como sustitutos de los conceptos clásicos de Inteligencia Artificial Distribuida.

El material previo del repositorio se conserva intacto:

- `llm-lab/`
- `pydantic-ai-lab/`

Este directorio es independiente y no modifica los laboratorios existentes.

## Estructura

```text
sistemas-multiagentes-course/
├── README.md
├── CURRICULUM_MAP.md
│
├── 01_iad_y_fundamentos_de_agentes/
│   ├── presentacion_modulo_1.md
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
├── 02_arquitectura_comunicacion_y_agentes_llm/
│   ├── presentacion_modulo_2.md
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── data/
│   │   ├── inventory.json
│   │   └── procurement_policy.txt
│   └── README.md
│
├── 03_sma_cooperacion_coordinacion_y_control/
│   ├── presentacion_modulo_3.md
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
└── 04_metodologias_diseno_y_proyecto_final/
    ├── presentacion_modulo_4.md
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── plantilla_proyecto_final.md
    └── README.md
```

## Secuencia sugerida

### Módulo 1 — IAD y fundamentos de agentes

- Inteligencia Artificial Distribuida
- problemas distribuidos
- definición de agente
- agente vs objeto
- creencias, capacidades, decisiones y compromisos
- agentes reactivos, cognitivos, de interfaz, de información, híbridos, móviles, autónomos y adaptativos

### Módulo 2 — Arquitectura, comunicación y agentes modernos

- arquitectura interna
- percepción, estado, razonamiento y acción
- comunicación agente-agente
- performativas
- FIPA y KQML
- AgentSpeak/JASON
- tools, memoria, recuperación local y LLMs como motor cognitivo
- Pydantic AI como implementación moderna

### Módulo 3 — Sistemas Multiagentes

- organización social
- cooperación
- coordinación
- control
- arquitecturas SMA
- supervisor, jerarquía, peer-to-peer, secuencial y paralelo
- asignación de tareas
- negociación
- Contract Net simplificado

### Módulo 4 — Metodologías y proyecto final

- MAS-CommonKADS
- GAIA
- MaSE
- FIPA como referencia de interoperabilidad
- aplicaciones históricas y modernas
- diseño de un SMA
- implementación
- validación
- proyecto final

## Infraestructura

Los módulos 1 y 3 son totalmente locales.

Los módulos 2 y 4 pueden usar un proveedor LLM externo mediante Pydantic AI. No requieren:

- Redis
- PostgreSQL
- pgvector
- vector database
- MCP remoto
- observabilidad hospedada
- Kubernetes
- workflow engine

Cuando no se habilita el LLM, el proyecto final también puede ejecutarse en modo local.

## Filosofía docente

El curso evita enseñar un framework como si fuera el contenido académico.

La secuencia es:

```text
concepto de agente
      ↓
arquitectura
      ↓
comunicación
      ↓
organización multiagente
      ↓
cooperación / coordinación / control
      ↓
metodología de diseño
      ↓
implementación moderna
      ↓
validación
```

Pydantic AI aparece como una herramienta para construir agentes modernos, del mismo modo que JASON/AgentSpeak representa una aproximación clásica orientada a agentes.
