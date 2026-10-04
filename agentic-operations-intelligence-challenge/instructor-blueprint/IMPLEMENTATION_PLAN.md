# Plan de implementación del profesor

## Fase 1 — Contratos

1. congelar schema de `MonthlyOperationsPlan`;
2. congelar interfaces de tools;
3. definir wrapper estándar para modelos `.pt`;
4. definir formato RAG editable y metadata de autoridad documental;
5. definir formato de Skills;
6. definir schema validado para training/features/forecast/risk/planning/tool/LLM/assumptions configs.

## Fase 2 — Plataforma

7. implementar Manager Pydantic AI;
8. implementar tool registry;
9. implementar loader de Skills;
10. implementar RAG engine con autoridad documental;
11. implementar student-config loader con límites/validación;
12. implementar frontend de resultados/traces/config readiness.

## Fase 3 — Business engine

11. inventory/material ledger;
12. BOM/MRP calculations;
13. capacity validation;
14. supplier constraints;
15. monthly simulator;
16. cost engine;
17. plan validator.

## Fase 4 — Cinco casos

20. crear empresas/casos realistas con contexto suficiente;
21. generar evidencia histórica imperfecta por familia;
22. crear documentos RAG actuales + obsoletos + draft + irrelevantes;
23. definir baseline Skills;
24. definir baseline configs deliberadamente no óptimos;
25. parametrizar costos, presupuesto y restricciones simultáneas;
26. diseñar señales conflictivas;
27. definir public scenarios;
28. definir hidden scenario generators.

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

## Case 0 obligatorio

Antes de publicar Team 1–5, Case 0 debe demostrar end-to-end todas las superficies editables: raw-data analysis, training settings, feature selection, RAG/document authority, Skills, forecast/risk/planning/tool/LLM configs, assumptions, hard constraints y reference plans.

## Criterio de listo

No publicar el proyecto hasta demostrar:
- baseline deliberadamente imperfecto pero funcional;
- existe mejora medible mediante los tres componentes permitidos;
- copiar artefactos entre casos degrada o no ayuda de forma sustancial;
- hidden tests premian generalización;
- costo introduce trade-offs reales;
- ningún equipo depende de información que no puede observar;
- cada `start-context` contiene suficiente información para entender la empresa;
- los baseline configs funcionan pero dejan espacio medible para mejora;
- los hard constraints no pueden ser debilitados por configuración del estudiante;
- RAG requiere distinguir fuentes actuales de ruido documental;
- Case 0 muestra y explica el proceso completo sin ser una plantilla numérica para Team 1–5.
