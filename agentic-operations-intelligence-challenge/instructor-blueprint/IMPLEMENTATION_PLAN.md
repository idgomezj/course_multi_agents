# Plan de implementación del profesor

## Fase 1 — Contratos

1. congelar schema de `MonthlyOperationsPlan`;
2. congelar interfaces de tools;
3. definir wrapper estándar para modelos `.pt`;
4. definir formato RAG editable;
5. definir formato de Skills.

## Fase 2 — Plataforma

6. implementar Manager Pydantic AI;
7. implementar tool registry;
8. implementar loader de Skills;
9. implementar RAG engine;
10. implementar frontend de resultados/traces.

## Fase 3 — Business engine

11. inventory/material ledger;
12. BOM/MRP calculations;
13. capacity validation;
14. supplier constraints;
15. monthly simulator;
16. cost engine;
17. plan validator.

## Fase 4 — Cinco casos

18. generar datasets PyTorch por familia;
19. crear documentos RAG por familia;
20. definir baseline Skills;
21. parametrizar costos;
22. definir public scenarios;
23. definir hidden scenario generators.

## Fase 5 — Evaluación

24. model evaluator;
25. RAG evaluator;
26. tool/Skill trace evaluator;
27. end-to-end evaluator;
28. benchmark/oracle;
29. score aggregation;
30. anti-hardcoding checks.

## Fase 6 — Entrega

31. crear cinco team packages;
32. levantar public evaluator;
33. levantar final private evaluator;
34. ejecutar baseline completo;
35. verificar dificultad equivalente;
36. pilotear con una solución “buena” y una “mala” por caso.

## Criterio de listo

No publicar el proyecto hasta demostrar:
- baseline deliberadamente imperfecto pero funcional;
- existe mejora medible mediante los tres componentes permitidos;
- copiar artefactos entre casos degrada o no ayuda de forma sustancial;
- hidden tests premian generalización;
- costo introduce trade-offs reales;
- ningún equipo depende de información que no puede observar.
