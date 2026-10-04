# Reglas del proyecto

## 1. Alcance permitido

El equipo puede:

- construir los datasets supervisados de `model_a` y `model_b` a partir del historial crudo JSON obtenido desde `/v1/teams/{team_id}/training-source.json` con el token de su equipo;
- definir transformaciones, ventanas temporales, features derivados y labels compatibles con el contrato;
- cambiar, mediante las opciones expuestas por el paquete, arquitectura, preprocessing, hiperparámetros, loss, optimizer y validación de los modelos PyTorch asignados;
- seleccionar features y features derivados permitidos sin cambiar el contrato I/O;
- modificar la configuración RAG autorizada;
- organizar metadata, prioridad y autoridad documental según las reglas del proyecto;
- modificar el contenido de Skills;
- modificar configuraciones autorizadas de forecast, riesgo, planificación y uso de tools;
- modificar settings autorizados del Manager LLM;
- documentar supuestos de negocio y ajustarlos con evidencia;
- ejecutar libremente los tests/escenarios públicos;
- analizar traces públicos.

La mayor parte de estas decisiones debe exponerse mediante YAML/JSON/Markdown. No se espera que el estudiante modifique el runtime Python para resolver el caso.

La descripción completa de las superficies editables y un ejemplo general sin resolver están en [STUDENT_SOLUTION_GUIDE.md](./STUDENT_SOLUTION_GUIDE.md).

El equipo no puede:

- modificar la plataforma o el evaluador;
- modificar la estrategia de evaluación, pesos, criterios, hidden tests, límites o scoring del curso;
- modificar el contrato de I/O del modelo para cambiar la interfaz esperada por las tools;
- modificar, falsificar o sustituir el historial crudo recibido desde la Data API; los estudiantes deben conservarlo como evidencia de entrada y crear archivos derivados nuevos;
- pedir a la Data API filas de entrenamiento o intentar descubrir datos/holdouts privados;
- hardcodear respuestas por scenario ID;
- detectar el test y devolver una respuesta precalculada;
- cambiar la implementación de una tool;
- cambiar la función de costos;
- acceder a hidden endpoints/datasets por mecanismos no autorizados;
- utilizar outcomes futuros como inputs del mismo ejemplo (target leakage).

## 2. Entrenamiento

El paquete local incluye:

- descripción del caso;
- `CASE_TRAINING.md`;
- `model_contract.json`.

El historial crudo se obtiene como JSON desde:

```text
GET https://course-agentic-api.idgomezj.com/v1/teams/{team_id}/training-source.json
X-Team-Token: <token asignado al equipo>
```

Cada token está limitado a su equipo. El endpoint devuelve observaciones históricas crudas, no un dataset supervisado terminado.

El equipo debe producir localmente `model_a_training.csv` y `model_b_training.csv`. La plataforma debe proporcionar mecanismos/configuraciones guiadas para preparación de datos y entrenamiento de modo que el reto no dependa de saber programar. La construcción conceptual del dataset, las decisiones de configuración y sus consecuencias deben poder explicarse en la defensa.

## 3. Colaboración entre equipos

Permitido:

- discutir conceptos;
- recomendar técnicas generales;
- discutir PyTorch, feature engineering, validación, RAG y diseño de Skills;
- compartir referencias bibliográficas.

No permitido:

- compartir datasets supervisados finales;
- compartir modelos `.pt2`;
- compartir archivos finales de RAG;
- compartir Skills finales;
- compartir submissions;
- compartir resultados/traces de hidden evaluation;
- entregar artefactos producidos por otro equipo como propios.

## 4. Generalización

La solución no debe memorizar los escenarios públicos. Los hidden tests combinan condiciones conocidas de formas no vistas y pueden incluir holdouts de modelado.

## 5. Evidencia experimental

El informe debe conservar evidencia de evolución:

- baseline;
- hipótesis;
- construcción/transformación de datos;
- cambio de modelo/RAG/Skill;
- métrica antes/después;
- decisión de conservar o revertir el cambio.

Se recomienda un mínimo de 8 experimentos documentados.

## 6. Resultado operativo

Una métrica ML alta o una respuesta textual convincente no compensan un plan inválido. La evaluación final considera el comportamiento del sistema completo sobre la salida estructurada y su desempeño en simulación.
