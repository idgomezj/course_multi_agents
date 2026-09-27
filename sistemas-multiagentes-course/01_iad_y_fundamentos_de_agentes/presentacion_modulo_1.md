# Presentación — Módulo 1
## Inteligencia Artificial Distribuida y Fundamentos de Agentes

**Estilo visual general:** fondo claro, tipografía sans-serif, máximo 4–5 bullets por diapositiva, una idea visual dominante por slide, iconografía lineal, diagramas con pocos colores.

---

## Diapositiva 1 — ¿Qué estudia un Sistema Multiagente?

### Puntos clave
- IA distribuida: inteligencia repartida entre entidades autónomas.
- Un agente percibe, decide y actúa.
- Un SMA coordina múltiples agentes.
- El foco del curso es la interacción, no solo el modelo de IA.

### Sugerencia visual
Insertar un diagrama minimalista con un **entorno central** y tres agentes alrededor: “Producción”, “Inventario” y “Mantenimiento”, conectados entre sí con flechas bidireccionales.

---

## Diapositiva 2 — De IA centralizada a IA distribuida

### Puntos clave
- IA clásica: una entidad concentra estado y decisión.
- IAD: conocimiento, control y acción se distribuyen.
- Los problemas reales suelen estar físicamente distribuidos.
- La distribución introduce coordinación y comunicación.

### Sugerencia visual
Diagrama comparativo en dos columnas: izquierda, “Centralizada” con un único cerebro conectado a todos los recursos; derecha, “Distribuida” con varios nodos autónomos que cooperan.

---

## Diapositiva 3 — ¿Cuándo tiene sentido distribuir la inteligencia?

### Puntos clave
- Información localizada en diferentes puntos.
- Decisiones concurrentes.
- Recursos heterogéneos.
- Necesidad de autonomía y tolerancia a fallos.
- Objetivos locales que deben alinearse con un objetivo global.

### Sugerencia visual
Mapa de una planta industrial con estaciones, almacén, mantenimiento y despacho; cada zona debe mostrar un pequeño agente local.

---

## Diapositiva 4 — Definición operativa de agente

### Puntos clave
- Percibe un entorno.
- Mantiene estado interno.
- Toma decisiones.
- Ejecuta acciones.
- Opera con cierto grado de autonomía.

### Sugerencia visual
Pipeline horizontal: **Percepción → Estado/Creencias → Decisión → Acción → Entorno**, con una flecha de retroalimentación del entorno hacia percepción.

---

## Diapositiva 5 — Agente vs objeto de software

### Puntos clave
- Un objeto responde cuando otro componente lo invoca.
- Un agente puede iniciar acciones.
- Un agente persigue objetivos.
- Un agente decide cuándo y cómo actuar.
- Ambos encapsulan estado y comportamiento.

### Sugerencia visual
Tabla visual de dos columnas “Objeto” vs “Agente”; usar icono de engranaje para objeto e icono de brújula/cerebro para agente.

---

## Diapositiva 6 — Arquitectura interna: BDI simplificado

### Puntos clave
- **Beliefs:** lo que el agente cree sobre el entorno.
- **Desires/Goals:** estados que desea alcanzar.
- **Intentions:** planes que decide ejecutar.
- **Capabilities:** acciones que puede realizar.
- **Commitments:** decisiones asumidas frente a otros agentes.

### Sugerencia visual
Diagrama circular BDI con cuatro bloques: Beliefs, Goals, Intentions y Capabilities; agregar una salida llamada Commitments hacia otros agentes.

---

## Diapositiva 7 — Creencias, capacidades, decisiones y compromisos

### Puntos clave
- Las creencias pueden ser incompletas o desactualizadas.
- Las capacidades restringen las decisiones posibles.
- Una decisión selecciona una acción o plan.
- Un compromiso crea una expectativa de comportamiento.
- En un SMA, los compromisos facilitan coordinación.

### Sugerencia visual
Ejemplo de una orden de producción: “Creencia: máquina A disponible”, “Capacidad: producir pieza X”, “Decisión: aceptar orden”, “Compromiso: terminar antes de 14:00”.

---

## Diapositiva 8 — Tipologías de agentes I

### Puntos clave
- **Reactivos:** responden directamente a estímulos.
- **Cognitivos:** razonan con estado y objetivos.
- **Híbridos:** combinan reacción rápida y planificación.
- **Autónomos:** toman decisiones con mínima intervención externa.

### Sugerencia visual
Matriz 2×2 con cada tipo de agente y un ejemplo industrial: alarma térmica, planificador, controlador híbrido y robot autónomo.

---

## Diapositiva 9 — Tipologías de agentes II

### Puntos clave
- **De interfaz:** median entre usuario y sistema.
- **De información:** localizan, filtran y transforman información.
- **Móviles:** cambian de nodo o entorno de ejecución.
- **Adaptativos:** modifican su comportamiento según experiencia.

### Sugerencia visual
Cuatro iconos lineales: usuario-interfaz, lupa/documentos, agente moviéndose entre servidores, y gráfica de aprendizaje/adaptación.

---

## Diapositiva 10 — Ejemplo industrial: celda de manufactura inteligente

### Puntos clave
- Agente reactivo protege la máquina ante temperatura crítica.
- Agente cognitivo decide cómo procesar la cola de trabajo.
- Agente híbrido combina seguridad y planificación.
- El entorno cambia y los agentes vuelven a decidir.

### Sugerencia visual
Diagrama de una celda CNC con sensores de temperatura, cola de órdenes y tres capas etiquetadas Reactive / Cognitive / Hybrid.

---

## Diapositiva 11 — Del concepto al código

### Puntos clave
- El ejemplo implementa percepciones como estructuras de datos.
- Las creencias se actualizan con cada observación.
- Las capacidades se declaran explícitamente.
- Cada tipo de agente tiene una política de decisión diferente.
- No se requiere LLM para que exista un agente.

### Sugerencia visual
Captura conceptual de clases Python: `ReactiveAgent`, `CognitiveAgent`, `HybridAgent`; destacar métodos `perceive()` y `decide()`.

---

## Diapositiva 12 — Cierre del módulo

### Puntos clave
- Un agente no es sinónimo de chatbot.
- La autonomía distingue al agente de una función pasiva.
- El estado interno permite razonamiento.
- Las tipologías dependen de cómo se decide y actúa.
- El siguiente paso es comunicar agentes y dotarlos de herramientas.

### Sugerencia visual
Roadmap horizontal: **Agente individual → Comunicación → Cooperación → Sistema Multiagente → Diseño SMA**.
