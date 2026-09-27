# Presentación — Módulo 4
## Metodologías de Diseño y Proyecto Final de Sistemas Multiagentes

**Estilo visual general:** profesional, corporativo y minimalista. Usar diagramas de proceso, matrices comparativas y una arquitectura final. Máximo 5 bullets por diapositiva.

---

## Diapositiva 1 — De agentes individuales a ingeniería de un SMA

### Puntos clave
- Un SMA necesita diseño antes de implementación.
- Roles, objetivos e interacciones deben ser explícitos.
- La metodología reduce decisiones ad hoc.
- El proyecto final integra análisis, diseño, implementación y validación.

### Sugerencia visual
Pipeline horizontal: **Problem → Goals → Roles → Interactions → Architecture → Implementation → Validation**.

---

## Diapositiva 2 — ¿Por qué una metodología específica para SMA?

### Puntos clave
- Existen múltiples entidades autónomas.
- Los objetivos pueden ser locales y globales.
- Las interacciones son parte del diseño.
- La organización social afecta el comportamiento.
- No basta con diseñar clases de software aisladas.

### Sugerencia visual
Comparación: diagrama UML tradicional con objetos a la izquierda; organización de agentes con roles y protocolos a la derecha.

---

## Diapositiva 3 — MAS-CommonKADS

### Puntos clave
- Extiende ideas de ingeniería del conocimiento a SMA.
- Modela agentes, tareas, experiencia y coordinación.
- Favorece análisis estructurado del conocimiento.
- Útil cuando el razonamiento experto es central.

### Sugerencia visual
Diagrama de cuatro bloques: Agent Model, Task Model, Expertise/Knowledge Model, Coordination Model.

---

## Diapositiva 4 — GAIA

### Puntos clave
- Trata el SMA como una organización.
- Identifica roles y responsabilidades.
- Define permisos, actividades y protocolos.
- Evoluciona de análisis organizacional a diseño.
- Muy útil para explicar estructura social.

### Sugerencia visual
Tabla de un rol GAIA con campos: Role, Responsibilities, Permissions, Activities, Protocols.

---

## Diapositiva 5 — MaSE

### Puntos clave
- Parte de objetivos del sistema.
- Refina objetivos en roles.
- Define conversaciones entre roles.
- Ensambla clases de agentes.
- Conecta análisis con implementación.

### Sugerencia visual
Flujo: Goals → Use Cases → Roles → Concurrent Tasks → Conversations → Agent Classes → Deployment.

---

## Diapositiva 6 — Comparación de metodologías

### Puntos clave
- MAS-CommonKADS: conocimiento y tareas.
- GAIA: organización, roles y protocolos.
- MaSE: objetivos, conversaciones e implementación.
- No existe una metodología universalmente superior.
- El proyecto puede combinar artefactos útiles de varias.

### Sugerencia visual
Matriz 3×4 con metodologías en filas y columnas: Focus, Core Artifact, Strength, Best Fit.

---

## Diapositiva 7 — FIPA como referencia de interoperabilidad

### Puntos clave
- FIPA buscó estandarizar sistemas de agentes.
- Comunicación e interacción requieren convenciones.
- Los estándares reducen acoplamiento entre implementaciones.
- El curso usa mensajes simplificados, no una plataforma FIPA completa.

### Sugerencia visual
Dos plataformas heterogéneas comunicándose mediante una capa intermedia “Standard Agent Communication”.

---

## Diapositiva 8 — Aplicaciones históricas del programa

### Puntos clave
- Investigación avanzada distribuida.
- Sistemas de visión de propósito general.
- Robótica móvil.
- Coordinación de entidades autónomas.
- Los ejemplos históricos muestran que SMA precede a los LLM.

### Sugerencia visual
Composición de tres imágenes conceptuales: red de investigación tipo DARPA, sistema de visión distribuida y robot móvil tipo Khepera. Etiquetarlas como “referentes históricos”.

---

## Diapositiva 9 — Aplicaciones modernas

### Puntos clave
- Manufactura y mantenimiento.
- Logística y supply chain.
- Mercados y negociación.
- Ciberseguridad.
- Sistemas con LLMs, tools y conocimiento distribuido.

### Sugerencia visual
Cinco tarjetas con iconos: factory, truck, market chart, shield y AI network.

---

## Diapositiva 10 — Caso capstone: respuesta a una disrupción operacional

### Puntos clave
- Demanda aumenta inesperadamente.
- Inventario puede resultar insuficiente.
- Capacidad de producción es limitada.
- Logística presenta retrasos.
- Varios agentes analizan partes diferentes del problema.

### Sugerencia visual
Cadena de suministro con cuatro agentes: Demand, Inventory, Production, Logistics, conectados a un Coordinator.

---

## Diapositiva 11 — Diseño organizacional del capstone

### Puntos clave
- Demand Agent: estima demanda.
- Inventory Agent: calcula exposición.
- Production Agent: evalúa capacidad.
- Logistics Agent: evalúa retraso de suministro.
- Coordinator: integra decisiones.
- Optional LLM Supervisor: sintetiza recomendación ejecutiva.

### Sugerencia visual
Arquitectura tipo hub-and-spoke: cuatro especialistas alrededor de Coordinator; encima, un bloque opcional “LLM Supervisor”.

---

## Diapositiva 12 — Interacción y estado compartido

### Puntos clave
- Cada agente produce un reporte local.
- El coordinador integra hechos, no texto libre arbitrario.
- El plan final contiene acciones y restricciones.
- El estado se serializa localmente.
- El supervisor LLM solo ve datos proporcionados.

### Sugerencia visual
Flujo: Specialist Reports → Shared State JSON → Coordinator → Validator → Optional LLM Summary.

---

## Diapositiva 13 — Validación del SMA

### Puntos clave
- Correctitud: restricciones respetadas.
- Consistencia: decisiones no se contradicen.
- Desempeño: tiempo, costo o servicio.
- Robustez: comportamiento ante cambios.
- Trazabilidad: saber qué agente aportó cada dato.

### Sugerencia visual
Dashboard de cinco indicadores con checks: Constraints, Consistency, Performance, Robustness, Traceability.

---

## Diapositiva 14 — Entregables del proyecto final

### Puntos clave
- Problema y entorno.
- Agentes, roles y objetivos.
- Protocolo de interacción.
- Implementación ejecutable.
- Escenarios de prueba.
- Evidencia de validación.

### Sugerencia visual
Checklist corporativo con seis entregables y un indicador de progreso.

---

## Diapositiva 15 — Cierre del curso

### Puntos clave
- IAD explica por qué distribuir inteligencia.
- Los agentes aportan autonomía y decisión.
- Los protocolos permiten cooperación y coordinación.
- Las metodologías convierten conceptos en arquitectura.
- El valor final está en el comportamiento del sistema completo.

### Sugerencia visual
Roadmap completo: **IAD → Agent → Communication → Cooperation → Coordination → Methodology → Validated SMA**.
