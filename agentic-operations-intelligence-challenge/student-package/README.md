# Proyecto Final — Agentic Operations Intelligence Challenge

## Su misión

La aplicación, el Manager, las tools, el simulador y el evaluador ya están construidos.

Su equipo debe enseñar al sistema cómo operar su caso mediante análisis y configuración, no modificando el runtime.

Las principales superficies de trabajo son:

1. configuración de preparación de datos y entrenamiento de Model A / Model B;
2. selección de features permitidos;
3. configuración/estrategia RAG y autoridad documental;
4. diseño/mejora de Skills;
5. política de combinación de forecasts;
6. thresholds y políticas de riesgo;
7. objetivos/restricciones de planificación;
8. política de uso de tools;
9. settings autorizados del Manager LLM;
10. supuestos de negocio documentados.

La **estrategia de evaluación no es editable por los estudiantes**.

La guía completa, incluyendo un ejemplo general deliberadamente sin resolver, está en [STUDENT_SOLUTION_GUIDE.md](./STUDENT_SOLUTION_GUIDE.md).

## El entrenamiento también es parte del reto

No existe un endpoint que entregue un dataset supervisado listo.

Cada equipo recibe localmente dentro de su paquete:

```text
student/team_X/training/
├── CASE_TRAINING.md
└── model_contract.json
```

El historial crudo **no se distribuye como CSV local**. Cada equipo debe obtener su propia evidencia histórica desde la Data API:

```text
GET https://course-agentic-api.idgomezj.com/v1/teams/{team_id}/training-source.json
X-Team-Token: <token asignado al equipo>
```

La respuesta es JSON crudo, imperfecto y específico del equipo. Puede guardarse localmente, por ejemplo como `student/team_X/training/raw_source.json`, únicamente como copia de trabajo. A partir de ese JSON el equipo debe construir:

```text
model_a_training.csv
model_b_training.csv
```

según el contexto del caso y el contrato del modelo.

Esto exige comprender cómo se construyen ventanas, features y labels, decidir entre las opciones de preparación/validación expuestas por el paquete, evitar leakage y justificar las decisiones. El trainer debe estar proporcionado por la plataforma para que el estudiante pueda experimentar principalmente mediante configuración de arquitectura, hiperparámetros, features y preprocessing, sin necesitar modificar el runtime Python. El modelo exportado siempre debe respetar el contrato de entrada/salida entregado.

## Dashboard de evaluación

El frontend del estudiante muestra, para los escenarios públicos de su equipo, el **Expected Optimized Cost** antes de ejecutar el Manager. Después de una ejecución puede comparar ese objetivo con el costo realizado, revisar factibilidad, servicio, RAG, Skills/Tools, desglose de costos, violaciones, trace y plan estructurado.

La información pública del dashboard puede cargarse antes de configurar el token. El token asignado al equipo sigue siendo obligatorio para ejecutar la evaluación.

## Uso de la Data API

La Data API del curso está publicada en:

```text
https://course-agentic-api.idgomezj.com
```

El paquete del estudiante ya usa esta URL como valor predeterminado. No es necesario ejecutar la Data API localmente ni leer su repositorio fuente para resolver el caso.

**Todos los endpoints de datos se encuentran bajo esta misma URL base.** Configure o reutilice:

```text
DATA_API_URL=https://course-agentic-api.idgomezj.com
```

Rutas principales:

```text
GET  /v1/teams/{team_id}/start-context
GET  /v1/teams/{team_id}/case
GET  /v1/teams/{team_id}/knowledge
GET  /v1/teams/{team_id}/training-source.json
GET  /v1/teams/{team_id}/scenarios
GET  /v1/teams/{team_id}/scenarios/{scenario_id}
POST /v1/teams/{team_id}/scenarios/{scenario_id}/evaluate
```

`/start-context` es público y requiere identificar honestamente al cliente mediante `X-Client-Type`. Los endpoints protegidos usan el token del equipo en `X-Team-Token`; cuando se ejecuta el challenge, `DATA_API_TOKEN` se envía automáticamente con ese header.

Ejemplo Team 1:

```bash
export DATA_API_URL=https://course-agentic-api.idgomezj.com
curl -H "X-Client-Type: ChatGPT" \\
  "$DATA_API_URL/v1/teams/team_1/start-context"

curl -H "X-Client-Type: ChatGPT" \\
  -H "X-Team-Token: $DATA_API_TOKEN" \\
  "$DATA_API_URL/v1/teams/team_1/training-source.json"
```

La Data API es la fuente autorizada de los datos del caso. `/start-context` entrega el contexto público inicial y es abierto. Los demás endpoints de datos requieren el token asignado al equipo y solo entregan información correspondiente a ese equipo.

Además del estado del negocio, documentos y escenarios autorizados, la Data API entrega el historial crudo de entrenamiento como JSON mediante `/v1/teams/{team_id}/training-source.json`. No entrega filas supervisadas listas, features/targets precalculados ni un generador de respuestas para los modelos.

La evaluación final utilizará escenarios y holdouts no vistos durante el desarrollo.

### Endpoints para probar el frontend

Después de ejecutar `python run.py`, el frontend usa el runtime local en `http://localhost:8000`. Puede verificar la carga de información con:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/teams
curl http://localhost:8000/api/scenarios/team_1
curl http://localhost:8000/api/status/team_1
```

Las rutas locales disponibles son `GET /api/health`, `GET /api/manager-models`, `GET /api/teams`, `GET /api/scenarios/{team_id}`, `GET /api/status/{team_id}`, `GET /api/config/{team_id}` y `POST /api/evaluate`. `/api/config/{team_id}` permite confirmar exactamente qué configuración editable validó y cargó el runtime. Estas rutas alimentan el frontend, pero los datos de equipos y escenarios siguen viniendo de la Data API hospedada en `https://course-agentic-api.idgomezj.com`.

## Qué pueden modificar

El reto está diseñado para que la mayor parte del trabajo se realice mediante YAML/JSON/Markdown y configuraciones guiadas.

Según las opciones expuestas por el paquete del equipo, pueden:

- analizar el historial crudo JSON de su equipo;
- seleccionar opciones de limpieza/preparación de datos;
- configurar arquitectura, hiperparámetros, loss, optimizer y validación usando settings permitidos;
- activar/desactivar features y features derivados permitidos por el contrato;
- entrenar y exportar `model_a.pt2` y `model_b.pt2` mediante el trainer proporcionado;
- modificar configuración RAG;
- configurar prioridad/autoridad documental;
- crear o mejorar Skills;
- configurar política de combinación de forecasts;
- configurar thresholds/políticas de riesgo;
- configurar objetivos y restricciones de planificación dentro de las reglas del caso;
- configurar cuándo deben usarse tools existentes;
- ajustar settings autorizados del Manager LLM;
- documentar y ajustar supuestos de negocio basados en evidencia.

Ver [STUDENT_SOLUTION_GUIDE.md](./STUDENT_SOLUTION_GUIDE.md) para el detalle de cada superficie editable.

## Qué NO pueden modificar

No se puede modificar:

- Manager Agent de runtime;
- backend/framework;
- frontend;
- implementación de tools;
- simulador;
- motor de costos;
- evaluator/scoring;
- estrategia de evaluación del curso;
- pesos/criterios de evaluación;
- hidden evaluation configuration;
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
