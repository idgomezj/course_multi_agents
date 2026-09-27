# Matriz de familias de escenarios

Cada grupo tiene su **propia suite**, no los mismos tests con números distintos.

## Estructura de dificultad recomendada por suite

Para el final:
- 5 basic;
- 5 intermediate;
- 6 combined;
- 4 stress;
- total: 20 hidden scenarios por grupo.

Para desarrollo:
- 12–15 public scenarios por grupo.

## Grupo 1 — Demand Volatility

Basic:
- estacionalidad;
- promoción;
- forecast normal.

Intermediate:
- promoción cancelada;
- spike;
- demand collapse;
- confirmed orders vs forecast.

Combined/stress:
- spike + material limit;
- alta incertidumbre + supplier delay;
- forecast conflict + capacity issue.

## Grupo 2 — Stable Make-to-Stock

Basic:
- demanda estable;
- reorder normal;
- open PO.

Intermediate:
- exceso de inventario;
- MOQ;
- descuento por volumen;
- working-capital pressure.

Combined/stress:
- descuento atractivo + warehouse limit;
- demand decline + large incoming PO;
- low stockout risk + very high holding cost.

## Grupo 3 — JIT

Basic:
- entrega a tiempo;
- micro-buffer;
- PO en tránsito.

Intermediate:
- atraso;
- early delivery;
- cheap but variable supplier;
- production-date change.

Combined/stress:
- demand change + late PO;
- supplier risk + line-stop exposure;
- cheaper slow supplier + moved production;
- simultaneous small deliveries.

## Grupo 4 — Unreliable Supply

Basic:
- supplier delay;
- quality alert;
- alternate supplier.

Intermediate:
- cancellation;
- high-risk cheap supplier;
- contract restriction;
- dual sourcing.

Combined/stress:
- delay + quality;
- two supplier failures;
- critical material + port disruption;
- expedite vs strategic buffer.

## Grupo 5 — Capacity Constrained

Basic:
- normal capacity;
- single downtime event;
- overtime option.

Intermediate:
- changeover;
- line incompatibility;
- labor shortage;
- maintenance event.

Combined/stress:
- downtime + urgent customer;
- two lines constrained;
- overtime + outsourcing trade-off;
- capacity loss + high late-delivery penalty.

## Anti-overfitting

Public tests enseñan conceptos por separado.

Hidden tests deben **combinar conceptos conocidos**, no introducir reglas nunca enseñadas.

```text
public: A, B, C
hidden: A+C, B+C, A+B+C
```

La dificultad viene de generalización.
