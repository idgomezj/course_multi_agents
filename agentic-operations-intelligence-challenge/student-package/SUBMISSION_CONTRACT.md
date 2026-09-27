# Contrato de entrega

La entrega técnica final contiene únicamente los artefactos permitidos.

```text
submission/
├── models/
│   ├── model_a.pt
│   └── model_b.pt
├── rag/
│   ├── config.yaml
│   └── metadata.*
└── skills/
    └── *.md
```

Los nombres concretos de modelos dependen del caso.

## No incluir
- frontend;
- backend;
- Manager;
- tools;
- evaluator;
- datasets ocultos;
- credenciales;
- caches;
- entornos virtuales.

## Salida operacional

El sistema completo debe producir una salida compatible con `schemas/monthly_plan.schema.json`.

El texto explicativo puede acompañar el plan, pero la evaluación automática usa la salida estructurada.
