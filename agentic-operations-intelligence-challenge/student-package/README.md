# Proyecto Final — Agentic Operations Intelligence Challenge

## Su misión

La aplicación, el Manager, las tools, el simulador y el evaluador ya están construidos.

Su equipo debe enseñar al sistema cómo operar su caso mediante:

1. construcción y entrenamiento de sus modelos PyTorch;
2. configuración/estrategia RAG;
3. diseño/mejora de Skills.

## El entrenamiento también es parte del reto

**Case 0 is the instructor validation exception:** its two datasets are clean, deterministic and ready to train so the platform logic can be validated end-to-end. Teams 1–5 do not receive that shortcut.

No existe un endpoint que entregue un dataset supervisado listo.

Cada equipo recibe dentro de su paquete:

```text
student/team_X/training/
├── CASE_TRAINING.md
├── raw_case_history.csv
└── model_contract.json
```

`raw_case_history.csv` contiene evidencia histórica de negocio, no features/targets ya preparados. El equipo debe transformar esa historia en:

```text
model_a_training.csv
model_b_training.csv
```

según el contexto del caso y el contrato del modelo.

Esto exige construir ventanas, features y labels, decidir cómo validar, evitar leakage y justificar las decisiones. El equipo puede modificar la arquitectura y el procedimiento de entrenamiento, pero el modelo exportado debe respetar el contrato de entrada/salida entregado.

## Uso de la Data API

La Data API se utiliza **durante la ejecución de escenarios** para obtener el estado autorizado del negocio, documentos y escenarios públicos. No entrega training rows ni un generador de respuestas para los modelos.

La evaluación final utilizará escenarios y holdouts no vistos durante el desarrollo.

## Qué pueden modificar

Como parte del trabajo de modelos pueden:

- construir sus CSV supervisados locales a partir del historial entregado;
- modificar el trainer/arquitectura/hyperparámetros;
- entrenar y exportar `model_a.pt2` y `model_b.pt2`;
- modificar RAG dentro del alcance permitido;
- modificar Skills.

## Qué NO pueden modificar

No se puede modificar:

- Manager Agent de runtime;
- backend/framework;
- frontend;
- implementación de tools;
- simulador;
- motor de costos;
- evaluator/scoring;
- schemas;
- Data API;
- escenarios/holdouts ocultos;
- el contrato de I/O del modelo para evadir la plataforma.

## Resultado final

El sistema debe producir un plan mensual integrado que:

- cumpla servicio;
- respete materiales, capacidad, proveedores y políticas;
- maneje la incertidumbre particular del caso;
- minimice el costo operacional total;
- generalice a escenarios no vistos.
