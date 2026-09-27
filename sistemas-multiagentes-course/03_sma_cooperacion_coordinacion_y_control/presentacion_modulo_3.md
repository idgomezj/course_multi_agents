# Presentación — Módulo 3
## Sistemas Multiagentes: Cooperación, Coordinación y Control

**Estilo visual general:** profesional, limpio, con diagramas de arquitectura y secuencias. Evitar párrafos largos; priorizar relaciones entre agentes.

---

## Diapositiva 1 — ¿Qué cambia cuando tenemos varios agentes?

### Puntos clave
- Cada agente conserva autonomía local.
- Los agentes comparten un entorno.
- Las decisiones de uno afectan a otros.
- Aparecen dependencias, conflictos y oportunidades de cooperación.
- El objetivo global no emerge automáticamente.

### Sugerencia visual
Tres agentes alrededor de un recurso compartido; mostrar flechas de interacción y un objetivo global en la parte superior.

---

## Diapositiva 2 — Organización social en un SMA

### Puntos clave
- Define roles y responsabilidades.
- Establece relaciones de autoridad o colaboración.
- Determina quién inicia, ejecuta y valida tareas.
- Puede ser estática o dinámica.

### Sugerencia visual
Organigrama simple con roles “Coordinator”, “Producer A”, “Producer B”, “Validator”.

---

## Diapositiva 3 — Cooperación

### Puntos clave
- Los agentes combinan capacidades para alcanzar un objetivo común.
- La cooperación puede implicar compartir información o trabajo.
- Requiere confianza operacional y reglas de interacción.
- No elimina los objetivos locales.

### Sugerencia visual
Dos agentes aportando piezas diferentes de un rompecabezas que forman un objetivo común “Complete Order”.

---

## Diapositiva 4 — Coordinación

### Puntos clave
- Ordena acciones interdependientes.
- Reduce duplicidad y conflictos.
- Gestiona recursos compartidos.
- Puede ser centralizada o distribuida.
- Incluye asignación, secuenciación y sincronización.

### Sugerencia visual
Línea de tiempo con tres agentes ejecutando tareas coordinadas; resaltar una dependencia “B inicia después de A”.

---

## Diapositiva 5 — Control

### Puntos clave
- Verifica que el comportamiento permanezca dentro de reglas.
- Detecta incumplimientos o desviaciones.
- Puede residir en un supervisor o estar distribuido.
- Control no significa eliminar autonomía.

### Sugerencia visual
Loop: Plan → Execute → Monitor → Correct → Plan, con un “Control Agent” observando el ciclo.

---

## Diapositiva 6 — Arquitecturas de SMA

### Puntos clave
- Supervisor/worker.
- Jerárquica.
- Peer-to-peer.
- Secuencial.
- Paralela con agregador.
- Híbrida.

### Sugerencia visual
Seis mini-diagramas en una cuadrícula 2×3 mostrando la topología de cada arquitectura.

---

## Diapositiva 7 — Asignación de tareas

### Puntos clave
- ¿Quién debe ejecutar cada trabajo?
- La decisión puede considerar capacidad, costo y tiempo.
- Los agentes pueden competir mediante propuestas.
- Un coordinador puede seleccionar la mejor alternativa.

### Sugerencia visual
Una orden de producción entra a un coordinador; salen tres “Call for Proposal”; regresan tres bids con costo y tiempo.

---

## Diapositiva 8 — Contract Net: idea básica

### Puntos clave
- Manager anuncia una tarea.
- Contractors evalúan capacidad local.
- Cada contractor propone o rechaza.
- Manager selecciona una propuesta.
- El ganador asume un compromiso.

### Sugerencia visual
Diagrama de secuencia: Coordinator → Machine A/B/C: CFP; A/B/C → Coordinator: PROPOSE/REFUSE; Coordinator → Winner: ACCEPT.

---

## Diapositiva 9 — Negociación y utilidad local

### Puntos clave
- Cada agente calcula su propia propuesta.
- La propuesta refleja su estado local.
- El coordinador aplica una función de selección.
- Cambiar la función cambia el comportamiento global.

### Sugerencia visual
Tabla de bids: Machine A/B/C con columnas Capability, Completion Time, Cost, Score; destacar el ganador.

---

## Diapositiva 10 — Caso industrial: asignar una orden de producción

### Puntos clave
- Orden requiere una capacidad específica.
- Máquinas tienen cargas y costos diferentes.
- Agentes de máquina calculan bids.
- Coordinador selecciona la mejor combinación costo-tiempo.
- Se registra el compromiso del ganador.

### Sugerencia visual
Layout de planta con tres máquinas y una orden “JOB-1042”; flechas hacia un bloque “Coordinator”.

---

## Diapositiva 11 — ¿Dónde están cooperación, coordinación y control?

### Puntos clave
- Cooperación: máquinas participan en la solución.
- Coordinación: el protocolo organiza el intercambio.
- Control: el coordinador valida capacidad y selecciona.
- Compromiso: el ganador reserva capacidad.
- Organización: roles manager/contractor.

### Sugerencia visual
Mapa conceptual que conecte cada concepto con una etapa del Contract Net.

---

## Diapositiva 12 — Cierre del módulo

### Puntos clave
- Un SMA necesita reglas de interacción.
- Arquitectura y protocolo condicionan el comportamiento global.
- La coordinación puede implementarse sin LLM.
- Los agentes pueden combinar decisión determinística y cognitiva.
- El siguiente paso es diseñar un SMA sistemáticamente.

### Sugerencia visual
Roadmap: **Agents → Protocol → Organization → Coordination → Methodology → Capstone**.
