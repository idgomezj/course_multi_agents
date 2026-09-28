# Contrato de entrega

La entrega técnica final contiene los artefactos permitidos.

```text
submission/
├── models/
│   ├── model_a.pt2
│   └── model_b.pt2
├── rag/
│   ├── config.yaml
│   └── metadata.*
└── skills/
    └── *.md
```

El instructor puede solicitar por separado el código/notebook de construcción del dataset y la evidencia experimental para la defensa, pero los CSV históricos suministrados no deben duplicarse dentro del submission final.

## Contrato de modelos

Los dos modelos deben respetar el `model_contract.json` entregado con el caso:

- nombres/orden de features;
- shape de salida;
- tipo de tarea;
- nombre del artifact.

El equipo puede cambiar la arquitectura y el entrenamiento, pero no la interfaz que consume la plataforma.

## No incluir

- frontend;
- backend;
- Manager;
- tools;
- evaluator;
- escenarios/holdouts ocultos;
- credenciales;
- caches;
- entornos virtuales.

## Salida operacional

El sistema completo debe producir una salida compatible con `schemas/monthly_plan.schema.json`.

El texto explicativo puede acompañar el plan, pero la evaluación automática usa la salida estructurada.
