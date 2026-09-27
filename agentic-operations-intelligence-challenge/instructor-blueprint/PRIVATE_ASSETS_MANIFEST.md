# Activos privados — NO guardar en este repo público

Crear estos activos en un repositorio privado o directamente en el backend final.

```text
private-evaluator/
├── hidden/
│   ├── team_1/
│   ├── team_2/
│   ├── team_3/
│   ├── team_4/
│   └── team_5/
├── holdout/
│   ├── team_1/
│   ├── team_2/
│   ├── team_3/
│   ├── team_4/
│   └── team_5/
├── oracle/
│   ├── benchmark_plans/
│   └── benchmark_costs/
├── seeds/
├── evaluator/
└── credentials/
```

## Hidden por escenario

Guardar como mínimo:
- scenario definition;
- seed;
- realized demand;
- realized arrivals/delays;
- realized downtime/quality events;
- critical constraints;
- required evidence tags;
- capability expectations;
- benchmark plan/version;
- benchmark cost;
- scoring result.

## Holdout PyTorch

No reutilizar exactamente el public validation set como final test.

## Hidden RAG

No publicar:
- queries;
- expected document IDs;
- expected clauses;
- distractor labels.

## Seguridad

El endpoint final:
- autentica por team;
- limita intentos;
- guarda hash/version de submission;
- no devuelve expected outputs;
- no devuelve hidden trace completo antes del cierre;
- registra modelo/versión/configuración de evaluación.

## Regla

Si un archivo permite a un alumno ajustar directamente su solución contra el final test, es privado.
