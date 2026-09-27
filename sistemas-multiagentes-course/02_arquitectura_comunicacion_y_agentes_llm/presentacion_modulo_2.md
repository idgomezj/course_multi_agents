# Presentación — Módulo 2
## Arquitectura Interna, Comunicación y Agentes Modernos

**Estilo visual general:** corporativo y minimalista; diagramas simples; máximo 5 bullets; distinguir conceptos clásicos de implementaciones modernas mediante etiquetas “Clásico” y “Actual”.

---

## Diapositiva 1 — De un agente aislado a un agente conectado

### Puntos clave
- Un agente necesita percepción, estado, decisión y acción.
- En un SMA también necesita comunicación.
- La comunicación debe tener intención y estructura.
- Las interfaces definen qué puede observar y qué puede hacer.

### Sugerencia visual
Diagrama de un agente central con cuatro puertos: “Environment”, “Memory”, “Tools” y “Other Agents”.

---

## Diapositiva 2 — Arquitectura interna de un agente

### Puntos clave
- **Perception:** recibe eventos o datos.
- **Beliefs/State:** mantiene una representación interna.
- **Reasoning:** selecciona una acción o plan.
- **Capabilities/Tools:** acciones disponibles.
- **Communication:** intercambia mensajes con otros agentes.

### Sugerencia visual
Bloque vertical: Perception → Beliefs → Reasoning → Action; a la derecha, un bloque “Communication” conectado transversalmente a todos.

---

## Diapositiva 3 — El mensaje también tiene semántica

### Puntos clave
- No basta con enviar texto.
- El mensaje puede expresar solicitud, información, propuesta o aceptación.
- El receptor necesita interpretar intención y contenido.
- La semántica reduce ambigüedad entre agentes.

### Sugerencia visual
Tarjeta de mensaje con campos: Sender, Receiver, Performative, Conversation ID, Content.

---

## Diapositiva 4 — KQML: comunicación orientada a performativas

### Puntos clave
- KQML surgió para intercambio de conocimiento entre agentes.
- Separa intención comunicativa de contenido.
- Usa performativas como `ask`, `tell`, `achieve`.
- Fue una referencia importante en IAD.

### Sugerencia visual
Ejemplo visual de un mensaje KQML simplificado con la performativa resaltada y el contenido en un bloque separado.

---

## Diapositiva 5 — FIPA y la estandarización de agentes

### Puntos clave
- FIPA promovió interoperabilidad entre sistemas de agentes.
- Define referencias para comunicación y gestión de agentes.
- FIPA ACL formaliza actos comunicativos.
- Los estándares permiten agentes desarrollados por equipos distintos.

### Sugerencia visual
Diagrama de dos plataformas de agentes distintas conectadas mediante una capa central “FIPA ACL / Standard Interaction”.

---

## Diapositiva 6 — Performativas útiles en un SMA

### Puntos clave
- `REQUEST`: solicitar una acción.
- `INFORM`: comunicar un hecho.
- `PROPOSE`: ofrecer una alternativa.
- `ACCEPT_PROPOSAL`: aceptar una propuesta.
- `REJECT_PROPOSAL`: rechazarla.

### Sugerencia visual
Flujo tipo secuencia entre Agent A y Agent B: REQUEST → PROPOSE → ACCEPT_PROPOSAL → INFORM.

---

## Diapositiva 7 — AgentSpeak y JASON

### Puntos clave
- AgentSpeak representa agentes con orientación BDI.
- Creencias describen el estado conocido.
- Objetivos disparan planes.
- JASON implementa AgentSpeak sobre Java.
- Es una referencia clásica para agentes cognitivos.

### Sugerencia visual
Diagrama BDI: Beliefs + Goals → Plan Selection → Intention → Action, con etiqueta “AgentSpeak/JASON”.

---

## Diapositiva 8 — De lenguajes clásicos a implementaciones modernas

### Puntos clave
- KQML/FIPA: protocolos e intención comunicativa.
- AgentSpeak/JASON: razonamiento explícito orientado a agentes.
- Python/Pydantic: mensajes y estado tipados.
- Pydantic AI: LLM + tools + structured output.
- MCP: protocolo moderno para exponer herramientas, no sustituto de FIPA.

### Sugerencia visual
Línea temporal conceptual: KQML → FIPA ACL → JASON/AgentSpeak → Typed Python Agents → LLM Agents/MCP. Incluir texto “evolución tecnológica, no equivalencia exacta”.

---

## Diapositiva 9 — LLM como motor cognitivo

### Puntos clave
- El LLM puede interpretar contexto y seleccionar acciones.
- El agente sigue necesitando estado, herramientas y restricciones.
- El LLM no debe controlar recursos arbitrarios.
- Las salidas estructuradas reducen errores de integración.

### Sugerencia visual
Diagrama: Perception → Typed Context → LLM Reasoner → Structured Decision → Allowlisted Tool.

---

## Diapositiva 10 — Tools, memoria y conocimiento local

### Puntos clave
- Tool: capacidad explícita del agente.
- Memoria: estado persistido por la aplicación.
- RAG: recuperación de información relevante antes de responder.
- Todo puede residir localmente.
- El LLM externo no reemplaza las fuentes de verdad.

### Sugerencia visual
Agente central conectado a tres cajas locales: “Inventory JSON”, “Policy TXT”, “Calculator”; una nube aparte únicamente para “LLM API”.

---

## Diapositiva 11 — Caso aplicado: agente de abastecimiento

### Puntos clave
- Recibe una solicitud estructurada.
- Consulta inventario local.
- Recupera política de compras.
- Calcula cantidad sugerida.
- Devuelve una decisión tipada y justificable.

### Sugerencia visual
Flujo de negocio: Purchase Request → Procurement Agent → Inventory/Policy Tools → Structured Recommendation.

---

## Diapositiva 12 — Cierre del módulo

### Puntos clave
- La arquitectura define capacidades y límites del agente.
- La comunicación necesita intención y estructura.
- FIPA/KQML/JASON aportan fundamentos históricos.
- Pydantic AI permite una implementación moderna.
- El siguiente paso es coordinar varios agentes.

### Sugerencia visual
Roadmap: **Single Agent Architecture → Communication → Coordination → Multi-Agent System**.
