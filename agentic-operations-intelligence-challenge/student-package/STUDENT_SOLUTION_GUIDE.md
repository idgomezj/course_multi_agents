# Guía de solución del estudiante — configuración, análisis y decisiones

## Propósito

Este reto no está diseñado como una competencia de programación. La aplicación, el Manager, las tools, el simulador, el motor de costos y el evaluador son parte fija de la plataforma.

El trabajo del equipo consiste en **entender una empresa, analizar información imperfecta, formular hipótesis, configurar el sistema y justificar decisiones**.

El equipo debe aprender a mejorar un sistema multiagente utilizando principalmente:

- archivos YAML/JSON de configuración;
- documentos Markdown para Skills;
- documentos y metadata para RAG;
- configuraciones de entrenamiento y selección de features;
- configuraciones del LLM;
- políticas de forecast, riesgo, planificación y uso de tools;
- supuestos de negocio documentados.

No se espera que el estudiante modifique código Python del runtime para resolver el caso.

---

## 1. El caso debe representar una empresa realista

El `start-context` de cada equipo debe proporcionar suficiente información para comprender la empresa y tomar decisiones defendibles, pero **no debe revelar la solución correcta**.

Como mínimo, el contexto debe explicar:

- tipo de empresa e industria;
- productos y/o familias de productos;
- tipos de clientes y prioridades comerciales;
- comportamiento histórico relevante de la demanda;
- promociones, estacionalidad u otros eventos comerciales;
- significado y confiabilidad de órdenes confirmadas;
- inventario disponible y restricciones de almacenamiento;
- capacidad normal y extraordinaria;
- proveedores, costos, lead times y confiabilidad;
- materiales/BOM cuando aplique;
- open purchase orders;
- políticas de servicio;
- restricciones financieras y presupuesto;
- costos de stockout, holding, overtime, expedite u otros costos relevantes;
- reglas especiales o excepciones del negocio;
- qué información puede contener ruido, retrasos, duplicados o inconsistencias;
- documentos organizacionales disponibles y su fecha/autoridad cuando corresponda;
- objetivo general y principales trade-offs.

El estudiante debe tener información suficiente para razonar. La dificultad debe venir de **decisiones ambiguas y trade-offs**, no de ocultar datos indispensables.

---

## 2. Información incompleta e imperfecta

La evidencia histórica puede contener problemas realistas, por ejemplo:

- valores faltantes;
- semanas incompletas;
- duplicados;
- nombres inconsistentes;
- observaciones extremas;
- datos cargados tarde;
- órdenes confirmadas que luego cambian;
- promociones canceladas;
- información proveniente de sistemas diferentes;
- notas operativas que no siempre son confiables.

El objetivo no es adivinar qué fila es "mala". El equipo debe analizar la evidencia, documentar supuestos y seleccionar configuraciones de limpieza/preprocesamiento disponibles en el paquete.

La plataforma debe proporcionar opciones configurables sin requerir que los estudiantes escriban algoritmos de limpieza desde cero.

Ejemplo conceptual:

```yaml
data_preparation:
  missing_values: <student decision>
  duplicate_handling: <student decision>
  outlier_policy: <student decision>
  categorical_normalization: <student decision>
```

Los valores disponibles y su significado deben estar documentados por el paquete del equipo.

---

## 3. Modelos y señales que pueden estar en desacuerdo

El sistema puede presentar simultáneamente señales distintas:

- Model A;
- Model B / uncertainty;
- moving average;
- exponential smoothing;
- confirmed orders;
- promociones;
- estacionalidad;
- inventario;
- open purchase orders;
- información del mercado;
- políticas internas.

No se espera que una señal sea siempre correcta.

Un caso puede mostrar, por ejemplo:

```text
Model A forecast:          1,620
Moving average:            1,270
Exponential smoothing:     1,310
Confirmed orders:          1,480
Promotion scheduled:       yes
Model B uncertainty:       0.37
```

Estos números **no indican qué decisión tomar**. El estudiante debe configurar cómo el sistema interpreta desacuerdos usando el contexto de negocio, RAG, Skills y políticas configurables.

---

## 4. Restricciones que no pueden optimizarse todas al mismo tiempo

El caso puede exigir objetivos en tensión, por ejemplo:

- alto nivel de servicio;
- presupuesto limitado;
- inventario máximo;
- overtime limitado;
- restricciones de capacidad;
- proveedores con diferentes costos y lead times;
- límites de emergency procurement;
- políticas especiales para clientes o productos prioritarios.

Ejemplo conceptual:

```text
Minimum service level:       96%
Monthly operating budget:    $82,000
Maximum warehouse inventory: 9,500 units
Maximum overtime:            100 hours
Emergency procurement cap:   250 units
```

El estudiante debe entender los trade-offs y configurar prioridades coherentes con el caso.

---

## 5. Documentos relevantes, irrelevantes y potencialmente obsoletos

RAG no debe consistir en buscar una única respuesta obvia.

La colección del equipo puede incluir:

```text
inventory_policy_2024.md
inventory_policy_2026.md
supplier_contract_current.md
supplier_contract_draft.md
promotion_playbook.md
finance_budget_2026.md
meeting_notes.md
travel_reimbursement_policy.md
office_parking_rules.md
```

Algunos documentos pueden ser:

- directamente relevantes;
- parcialmente relevantes;
- obsoletos;
- borradores;
- informativos pero no autoritativos;
- completamente irrelevantes para planificación.

El equipo debe aprender a mejorar recuperación, metadata y autoridad documental sin borrar evidencia simplemente porque dificulta el retrieval.

---

# Áreas que el estudiante puede modificar

## 6. Skills

Los Skills describen **cómo debe actuar el sistema** bajo determinadas condiciones.

Ejemplos de temas:

- planificación mensual;
- manejo de incertidumbre;
- revisión de promociones;
- respuesta a demanda inesperada;
- producción y replanning;
- procurement;
- validación antes de finalizar;
- tratamiento de información contradictoria.

Los Skills no deben contener respuestas hardcodeadas para scenarios específicos.

---

## 7. Configuración RAG

El equipo puede experimentar con parámetros como:

```yaml
chunk_size: <student decision>
overlap: <student decision>
top_k: <student decision>
min_score: <student decision>
ngram_max: <student decision>
```

Debe justificar el balance entre:

- demasiado poco contexto;
- suficiente evidencia;
- exceso de documentos irrelevantes.

---

## 8. Prioridad y autoridad documental

El paquete puede permitir configurar metadata de fuentes:

```yaml
documents:
  inventory_policy_2026.md:
    authority: <student decision>
    effective_date: <student decision>

  meeting_notes.md:
    authority: <student decision>

  inventory_policy_2024.md:
    authority: <student decision>
```

El estudiante debe leer la información de la empresa y decidir qué fuente debe tener mayor confianza.

No debe cambiar el contenido factual original para fabricar una política más conveniente.

---

## 9. Configuración de entrenamiento

El paquete debe proporcionar un trainer ya construido. El estudiante modifica settings, no la implementación del runtime.

Ejemplo:

```yaml
model_a:
  architecture: <small|medium|large>
  epochs: <student decision>
  learning_rate: <student decision>
  hidden_size: <student decision>
  dropout: <student decision>
  loss: <mae|mse|huber>
  optimizer: <adam|adamw>

model_b:
  architecture: <small|medium|large>
  epochs: <student decision>
  learning_rate: <student decision>
  hidden_size: <student decision>

validation:
  method: <available documented option>
  validation_fraction: <student decision>
```

El objetivo es que el equipo pruebe configuraciones, compare resultados y pueda explicar por qué conserva una configuración.

---

## 10. Selección de features

Los equipos pueden seleccionar features permitidos por el contrato o features derivados previamente implementados por la plataforma.

Ejemplo:

```yaml
model_a_features:
  last4_mean: <true|false>
  last4_std: <true|false>
  trend: <true|false>
  promotion: <true|false>
  price_index: <true|false>
  confirmed_orders: <true|false>
  seasonal_index: <true|false>

derived_features:
  promotion_x_seasonality: <true|false>
  confirmed_order_ratio: <true|false>
  rolling_growth: <true|false>
```

El estudiante no debe cambiar el contrato requerido por runtime. Solo puede utilizar opciones oficialmente expuestas.

---

## 11. Política de combinación de forecasts

El equipo puede configurar cómo balancear señales disponibles:

```yaml
forecast_policy:
  model_a_weight: <student decision>
  confirmed_orders_weight: <student decision>
  moving_average_weight: <student decision>
  exponential_smoothing_weight: <student decision>

  high_uncertainty_threshold: <student decision>

  when_high_uncertainty:
    model_weight_adjustment: <student decision>
    confirmed_orders_weight_adjustment: <student decision>
    require_additional_checks: <true|false>
```

No existe una combinación universalmente correcta. Debe derivarse del caso.

---

## 12. Configuración de riesgo

Ejemplo:

```yaml
risk_policy:
  uncertainty:
    medium: <student decision>
    high: <student decision>

  forecast_disagreement:
    investigate_above: <student decision>

  stockout_risk:
    safety_stock_review_above: <student decision>

  emergency_procurement:
    allowed_below_service_level: <student decision>
```

Los thresholds elegidos deben producir un comportamiento razonable tanto en escenarios normales como adversos.

---

## 13. Objetivos y restricciones de planificación

El equipo puede traducir la información empresarial a configuración:

```yaml
planning:
  service_level_target: <student decision>
  max_budget: <student decision>
  max_overtime: <student decision>
  max_inventory: <student decision>
  max_emergency_procurement: <student decision>

priorities:
  service: <student decision>
  total_cost: <student decision>
  ending_inventory: <student decision>
  plan_stability: <student decision>
```

La configuración debe respetar las restricciones duras entregadas por el caso. Una prioridad no puede usarse para ignorar una política obligatoria.

---

## 14. Política de uso de tools

El estudiante puede configurar **cuándo** deben utilizarse tools ya implementadas.

Ejemplo:

```yaml
tool_policy:
  calculate_safety_stock:
    when: <student decision>

  get_supplier_options:
    when: <student decision>

  validate_plan:
    required: <true|false>

  replan:
    max_attempts: <student decision>
```

No se modifica la implementación de las tools.

El objetivo es evitar tanto:

- omitir tools necesarias;
- llamar todas las tools sin criterio.

---

## 15. Configuración del Manager LLM

Cuando el paquete lo permita, el estudiante puede experimentar con settings controlados:

```yaml
manager_llm:
  provider: <allowed provider>
  model: <allowed model>
  temperature: <student decision>
  max_tokens: <student decision>
  reasoning_mode: <allowed setting>

context:
  max_rag_documents: <student decision>
  include_model_diagnostics: <true|false>
  include_cost_breakdown: <true|false>
  include_previous_plan: <true|false>
```

La lista exacta de providers/modelos disponibles depende de los recursos del curso.

Los estudiantes no administran API keys ni agregan proveedores no autorizados.

---

## 16. Supuestos de negocio

El equipo puede mantener un archivo explícito de supuestos:

```yaml
business_assumptions:
  promotion_lift: <student decision>
  supplier_reliability_interpretation: <student decision>
  forecast_bias_tolerance: <student decision>
  inventory_buffer: <student decision>
```

Cada supuesto debe tener una razón basada en:

- `start-context`;
- historial;
- documentos RAG;
- observaciones públicas;
- resultados experimentales.

Un supuesto no debe presentarse como hecho si no está soportado por evidencia.

---

# Lo que NO es editable por estudiantes

## 17. Componentes bloqueados

Los estudiantes no pueden modificar:

- Manager/runtime implementation;
- backend/framework;
- frontend;
- implementación de tools;
- schemas;
- simulador;
- función de costos;
- evaluator/scoring;
- hidden scenarios;
- hidden holdouts;
- benchmark solutions;
- reglas de seguridad;
- Data API;
- contrato I/O para evadir la plataforma;
- **estrategia de evaluación del curso**.

La estrategia de evaluación, sus pesos, hidden tests, límites y criterios pertenecen al instructor/plataforma. **No es una superficie editable del caso.**

---

# Ejemplo general — solo para entender el tipo de problema

> Este ejemplo es ficticio. No pertenece a ningún equipo y no contiene una solución. Los valores son ilustrativos y las configuraciones quedan intencionalmente sin resolver.

## 18. Empresa ficticia

```text
Company: Orion Home Goods
Industry: household consumer products

Products:
- NOVA: high-volume core product
- LUMA: lower-volume premium product

Customers:
- national retailers
- regional distributors
- direct-to-consumer

Management priorities:
- protect strategic-retailer service
- avoid repeating recent promotion stockouts
- reduce excess inventory after cancelled promotions
```

## 19. Información operativa

```text
Normal production capacity:      3,600 units/week
Maximum overtime capacity:         550 units/week
Warehouse capacity:              9,800 units
Monthly operating budget:       $84,000
Strategic customer service goal:    98%
Other customer service goal:        95%
```

Suppliers:

| Supplier | Cost | Lead time | Historical reliability |
|---|---:|---:|---:|
| Alpha | lower | 3 weeks | 91% |
| Beta | +16% | 1 week | 98% |
| Emergency | +60% | same week | high |

Esto todavía no dice cuál proveedor debe utilizarse. Esa decisión depende de la situación completa.

## 20. Historial imperfecto

Una pequeña parte del historial podría verse así:

| Week | Product | Actual demand | Promotion | Confirmed orders | Seasonal index | Observation |
|---|---|---:|---|---:|---:|---|
| 18 | NOVA | 1,180 | no | 1,090 | 1.02 | normal |
| 19 | NOVA | missing | no | 1,130 | 1.01 | late system upload |
| 20 | nova | 1,240 | yes | 1,400 | 1.08 | product ID casing differs |
| 20 | NOVA | 1,255 | yes | 1,395 | 1.08 | possible duplicate |
| 21 | NOVA | 4,700 | no | 1,020 | 1.00 | unusual observation |

El estudiante debe investigar. El ejemplo **no indica** si la última fila es correcta, incorrecta o parcialmente explicable.

## 21. Señales en desacuerdo

Para una semana futura:

```text
Model A:                    1,620
Moving average:             1,270
Exponential smoothing:      1,310
Confirmed orders:           1,480
Promotion scheduled:        YES
Model B uncertainty:        0.37
Available finished goods:     420
Open PO arriving next week:   300
```

No existe una instrucción en este ejemplo que diga:

- qué forecast usar;
- qué pesos asignar;
- cuánto producir;
- cuánto comprar;
- cuál proveedor seleccionar;
- cuánto safety stock mantener.

Eso es precisamente lo que el equipo debe analizar.

## 22. Documentos RAG disponibles

```text
inventory_policy_2024.md
inventory_policy_2026.md
strategic_customer_service_policy.md
supplier_contract_alpha.md
supplier_contract_beta.md
promotion_playbook.md
marketing_meeting_notes.md
travel_reimbursement_policy.md
office_parking_rules.md
```

El estudiante debe determinar qué documentos son relevantes y cuáles tienen autoridad.

## 23. Restricciones simultáneas

```text
Minimum required service:          96%
Strategic-retailer target:         98%
Monthly budget:                 $84,000
Maximum warehouse inventory:     9,800 units
Maximum overtime:                  100 hours
Emergency procurement cap:         220 units
```

Una solución que maximice servicio sin considerar presupuesto puede fallar.

Una solución que minimice costo sacrificando servicio también puede fallar.

El ejemplo no entrega los pesos correctos.

## 24. Lo que el estudiante recibiría para modificar

Una versión simplificada podría incluir:

```text
student/team_example/
├── training/
│   ├── CASE_TRAINING.md
│   ├── model_contract.json
│   ├── training_config.yaml
│   └── feature_config.yaml
├── models/
│   ├── model_a.pt2
│   └── model_b.pt2
├── rag/
│   ├── config.yaml
│   └── document_priorities.yaml
├── skills/
│   └── *.md
├── config/
│   ├── forecast_policy.yaml
│   ├── risk_policy.yaml
│   ├── planning_objectives.yaml
│   ├── tool_policy.yaml
│   └── manager_llm.yaml
└── assumptions/
    └── business_assumptions.yaml
```

## 25. Ejemplo de configuración SIN resolver

```yaml
forecast_policy:
  model_a_weight: <student decision>
  confirmed_orders_weight: <student decision>
  moving_average_weight: <student decision>
  exponential_smoothing_weight: <student decision>

risk_policy:
  high_uncertainty_threshold: <student decision>

planning:
  service_level_target: <student decision>
  max_budget: <student decision>
  max_overtime: <student decision>

rag:
  top_k: <student decision>
  min_score: <student decision>

manager_llm:
  temperature: <student decision>
  max_rag_documents: <student decision>
```

The student is expected to determine defensible values through analysis and experimentation.

## 26. Qué debe resolver el equipo

Para este ejemplo ficticio, el equipo tendría que:

1. comprender la empresa antes de tocar configuraciones;
2. revisar la calidad del historial;
3. seleccionar opciones de preparación de datos;
4. seleccionar features;
5. ajustar settings de entrenamiento de Model A y Model B;
6. verificar si los modelos generalizan;
7. configurar cómo manejar forecasts contradictorios;
8. configurar thresholds de riesgo;
9. mejorar RAG para encontrar políticas correctas;
10. identificar fuentes obsoletas o irrelevantes;
11. escribir/mejorar Skills;
12. configurar cuándo usar tools;
13. traducir presupuesto, servicio, capacidad e inventario a políticas;
14. experimentar con settings autorizados del Manager LLM;
15. documentar supuestos;
16. probar escenarios públicos;
17. comparar resultados y justificar qué cambios conserva.

El equipo **no recibe una combinación correcta predeterminada** y no debe resolver el reto modificando el evaluator.

---

## 27. Principio de diseño del reto

El reto debe poder resumirse así:

> La plataforma proporciona las capacidades. El caso proporciona una empresa suficientemente detallada. Los datos contienen ambigüedad realista. El estudiante debe configurar el sistema para que tome buenas decisiones y explicar por qué.

La dificultad debe provenir de comprender la empresa, distinguir señales útiles de ruido, manejar incertidumbre y balancear restricciones; no de exigir experiencia avanzada programando.
