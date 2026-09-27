# Evaluación

## Nota final

| Componente | Peso |
|---|---:|
| Modelos PyTorch | 20% |
| RAG | 15% |
| Skills y comportamiento/tool selection | 15% |
| Desempeño operacional end-to-end | 40% |
| Informe y defensa | 10% |

## Modelos PyTorch — 20%

Las métricas dependen del caso. Ejemplos:
- MAE/RMSE para forecast;
- precision/recall/F1 para riesgos;
- calibration cuando la probabilidad es parte de la decisión;
- evaluación en holdout no visto.

## RAG — 15%

Se evalúa:
- retrieval del documento correcto;
- retrieval de la cláusula/sección relevante;
- cobertura en Top-K;
- rechazo de contexto irrelevante;
- capacidad de resolver conflictos documentales.

## Skills y tools — 15%

No se exige un path idéntico al del profesor. Se evalúa si el comportamiento:
- consulta capacidades necesarias;
- evita omisiones críticas;
- evita llamadas claramente irrelevantes/repetidas;
- aplica el procedimiento apropiado al contexto;
- llega a decisiones sustentadas.

## End-to-end — 40%

Primero existe un **feasibility gate**. Un escenario con violaciones críticas puede obtener 0 en desempeño operacional.

Después se miden:
- factibilidad;
- nivel de servicio;
- cumplimiento de políticas;
- robustez;
- costo total del plan.

El costo solo se premia entre soluciones válidas.

## Informe y defensa — 10%

Se evalúa:
- análisis del problema;
- diseño experimental;
- interpretación de resultados;
- explicación de trade-offs;
- defensa individual de decisiones técnicas.

La programación de frontend/backend no forma parte de la nota.
