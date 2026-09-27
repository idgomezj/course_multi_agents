# Especificación del Cost Engine

## Objetivo

Todos los equipos deben cumplir objetivos operacionales **minimizando costo total**, pero cada empresa tiene una economía diferente.

La tool pública puede exponer:

`calculate_plan_cost(plan)`

y helpers especializados. Los estudiantes no modifican sus implementaciones.

## Componentes posibles

```text
C_total =
  purchase
+ production
+ holding
+ working_capital
+ stockout
+ lost_sales
+ overtime
+ changeover
+ downtime
+ expedite
+ quality
+ spoilage
+ outsourcing
+ contractual_penalties
```

No todos los componentes pesan igual en todos los casos.

## Perfil por caso

| Caso | Costos dominantes |
|---|---|
| Volatile Demand | lost sales, stockout, expedite |
| Stable MTS | holding, working capital, warehouse |
| JIT | holding + line stop + late material |
| Unreliable Supply | supplier failure, quality, shutdown, expedite |
| Capacity | downtime, late delivery, overtime, changeover, outsourcing |

## Diseño de parámetros

Mantener dos niveles:

### Información de negocio visible
El agente debe poder conocer los costos necesarios para decidir, mediante tools/RAG/datos autorizados.

### Parámetros privados del evaluador
La realización de eventos futuros y el costo benchmark del escenario permanecen privados.

No ocultar al alumno un costo que una empresa real necesitaría conocer para decidir. La dificultad debe venir de la incertidumbre y de los trade-offs, no de información imposible.

## Principio

Primero factibilidad, después costo.

```text
if critical_violation:
    operational_score = 0
else:
    simulate()
    service = measure_service()
    total_cost = cost_engine(plan, realized_events)
    cost_efficiency = compare_to_benchmark(total_cost)
```
