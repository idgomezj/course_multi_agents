# Reglas del proyecto

## 1. Alcance permitido

El equipo puede:
- cambiar arquitectura, features, hiperparámetros y entrenamiento de los modelos PyTorch asignados;
- modificar la configuración RAG autorizada;
- organizar metadata/documentos según las reglas del proyecto;
- modificar el contenido de Skills;
- ejecutar libremente los tests públicos;
- analizar traces públicos.

El equipo no puede:
- modificar la plataforma o el evaluador;
- hardcodear respuestas por scenario ID;
- detectar el test y devolver una respuesta precalculada;
- cambiar la implementación de una tool;
- cambiar la función de costos;
- acceder a hidden endpoints/datasets por mecanismos no autorizados.

## 2. Colaboración entre equipos

Permitido:
- discutir conceptos;
- recomendar técnicas generales;
- discutir PyTorch, RAG y diseño de Skills;
- compartir referencias bibliográficas.

No permitido:
- compartir modelos `.pt`;
- compartir archivos finales de RAG;
- compartir Skills finales;
- compartir submissions;
- compartir resultados/traces de hidden evaluation;
- entregar artefactos producidos por otro equipo como propios.

## 3. Generalización

La solución no debe memorizar los escenarios públicos. Los hidden tests combinan condiciones conocidas de formas no vistas.

## 4. Evidencia experimental

El informe debe conservar evidencia de evolución:
- baseline;
- hipótesis;
- cambio;
- métrica antes/después;
- decisión de conservar o revertir el cambio.

Se recomienda un mínimo de 8 experimentos documentados.

## 5. Resultado operativo

Una respuesta textual convincente no compensa un plan inválido. La evaluación se realiza sobre la salida estructurada del sistema y su desempeño en simulación.
