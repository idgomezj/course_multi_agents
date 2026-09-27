# Arquitectura de Testing

## Regla principal

No evaluar texto libre contra una “respuesta correcta”.

El Manager produce un plan estructurado. Un motor independiente lo valida, simula y costea.

```text
Student intelligence
    ↓
Manager + tools
    ↓
MonthlyOperationsPlan
    ↓
Constraint Validator
    ↓
Month Simulator
    ↓
Cost Engine
    ↓
Scenario Score
```

## Capa A — PyTorch hidden holdout

Cada familia tiene sus propias métricas.

Ejemplos:
- Grupo 1: forecast error + uncertainty calibration;
- Grupo 2: forecast error + excess-inventory classification;
- Grupo 3: delay classification + arrival-time error;
- Grupo 4: delay + quality-risk classification;
- Grupo 5: downtime + feasibility classification.

El holdout final nunca se entrega.

## Capa B — RAG tests

Cada hidden query tiene:
- documentos/cláusulas relevantes;
- distractores;
- criterios de recuperación.

Medir:
- Recall@K;
- hit de cláusula;
- precision/relevancia;
- ausencia de policy conflict no resuelto.

No puntuar “adivinó la política” si no recuperó la evidencia requerida.

## Capa C — Skill/tool behavior

No forzar una secuencia única.

Para cada escenario definir:
- capabilities requeridas;
- capabilities opcionales;
- llamadas prohibidas solo cuando realmente invalidan el contexto;
- penalización pequeña por llamadas irrelevantes/repetidas.

La Skill se evalúa por el comportamiento que genera, no por similitud de texto.

## Capa D — End-to-end

### Gate 1: restricciones críticas
Ejemplos:
- producir sin materiales;
- exceder capacidad;
- proveedor prohibido;
- material vencido cuando aplica;
- violar aprobación obligatoria;
- incumplir una política no negociable.

Una violación crítica puede dejar el operational score del escenario en 0.

### Gate 2: simulación
El simulador realiza el mes usando:
- demanda realizada;
- arrivals realizados;
- downtime realizado;
- calidad realizada;
- eventos del scenario.

### Gate 3: servicio
Medir según el caso:
- fill rate;
- on-time service;
- line continuity;
- stockout;
- producción completada.

### Gate 4: costo
Solo planes válidos compiten por eficiencia económica.

## Benchmark

El benchmark debe usar **la misma información disponible al agente al momento de decidir**, no conocimiento perfecto del futuro.

Guardar:
- plan benchmark;
- costo benchmark;
- configuración/version;
- scenario seed.

## Cost gap

```text
gap = (student_cost - benchmark_cost) / benchmark_cost
```

Sugerencia de score:
- gap <= 5%: 100
- 5–10%: 90
- 10–20%: 75
- 20–30%: 60
- >30%: 40 o menos

Puede usarse una función continua en implementación.

## Robustez LLM

Para final evaluation:
- misma versión de modelo;
- misma configuración;
- temperatura mínima/estable posible;
- mismos seeds del simulador;
- 2–3 repeticiones solo en escenarios sensibles si el presupuesto lo permite.

La nota no debe depender de una ejecución afortunada.
