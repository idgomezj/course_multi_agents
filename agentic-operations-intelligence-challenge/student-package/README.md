# Proyecto Final — Agentic Operations Intelligence Challenge

## Su misión

Su equipo recibe una operación manufacturera, una plataforma de IA completamente implementada y un conjunto amplio de tools.

**No deben construir la aplicación.**

Deben enseñar al sistema cómo operar correctamente su negocio mediante:

1. entrenamiento de los modelos PyTorch asignados;
2. mejora del RAG;
3. diseño/mejora de Skills.

El resultado final debe ser un **plan mensual integrado** que:
- satisfaga los objetivos de servicio;
- respete materiales, capacidad, proveedores y políticas;
- maneje la incertidumbre propia del caso;
- minimice el costo total.

## Qué NO pueden modificar

No se puede modificar:
- Manager Agent;
- backend;
- frontend;
- integración Pydantic AI;
- definición/implementación de tools;
- simulador;
- motor de costos;
- evaluador;
- schemas;
- optimizador proporcionado.

## Qué SÍ pueden modificar

Solo los directorios/artefactos indicados por el profesor como:

```text
student/
├── models/
├── rag/
└── skills/
```

## Concepto clave

```text
PyTorch models
"What is likely to happen?"
        ↓
RAG
"What are the facts, contracts and policies?"
        ↓
Skills
"How should this operation approach the problem?"
        ↓
Tools
"What capability should the Manager use?"
        ↓
Cost tool
"Which feasible alternative is economically preferable?"
        ↓
Manager
"What should we actually do?"
```

Su solución será evaluada también con escenarios no vistos durante el desarrollo.
