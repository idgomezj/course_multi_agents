# Agentic Operations Intelligence Challenge

Proyecto final del curso orientado a **LLM Agents, RAG, Skills, PyTorch y toma de decisiones operacionales**.

## Idea central

El profesor entrega una plataforma completamente funcional: frontend, backend, Manager Agent con Pydantic AI, catálogo de tools, motor de simulación, motor de costos, contratos de entrada/salida y evaluador público.

Los estudiantes **no construyen la aplicación**. Solo pueden mejorar tres componentes:

1. **Modelos PyTorch especializados** para el caso asignado.
2. **RAG** del Manager: chunking, metadata, retrieval y configuración permitida.
3. **Skills** que enseñan al Manager cómo abordar los problemas de su operación y cuándo usar las tools disponibles.

Todos los equipos deben producir un **plan mensual integrado de producción y abastecimiento**, cumplir restricciones operacionales y de negocio, y **minimizar el costo total**.

## Cinco casos distintos

| Equipo | Familia del caso | Incertidumbre/restricción dominante | Modelos PyTorch principales |
|---|---|---|---|
| 1 | Volatile Demand | demanda, promociones, estacionalidad | Demand Forecast + Demand Uncertainty |
| 2 | Stable Make-to-Stock | exceso de inventario y capital | Stable Demand Forecast + Excess Inventory Risk |
| 3 | Just-in-Time | sincronización y confiabilidad de entregas | Supplier Delay + Arrival-Time Prediction |
| 4 | Unreliable Supply Network | retrasos, calidad y alternativas | Supplier Delay + Supplier Quality Risk |
| 5 | Capacity-Constrained Plant | capacidad, downtime y changeovers | Downtime Risk + Production Feasibility |

Los cinco reciben la misma plataforma y toolbox, pero **no la misma solución**. Sus datos, documentos, costos, modelos, Skills relevantes y familias de escenarios son diferentes.

## Principio de evaluación

El sistema no se califica comparando una respuesta textual contra una respuesta escrita por el profesor.

El Manager debe producir un plan estructurado. Un evaluador independiente:

1. valida restricciones duras;
2. simula el mes;
3. mide servicio y cumplimiento;
4. calcula el costo real del plan;
5. compara el costo contra un benchmark instructor bajo la misma información disponible;
6. evalúa por separado PyTorch, RAG y comportamiento producido por las Skills.

## Estructura de este folder

- `student-package/`: material que **sí puede compartirse** con los estudiantes.
- `schemas/`: contratos de datos compartibles.
- `instructor-blueprint/`: diseño para el profesor. **No contiene secretos de evaluación**, pero no es material de la tarea.
- `SHARING_MATRIX.md`: fuente de verdad sobre qué se comparte y qué no.

> **Importante:** este repositorio es público. Nunca guardar aquí hidden tests reales, seeds secretos, holdout datasets, respuestas esperadas, planes benchmark ni credenciales del evaluador final. Esos activos deben vivir en infraestructura o repositorio privado.
