# 08 — QLoRA Fine-Tuning Workbench

> **Objetivo:** repetir el experimento de LoRA del capítulo 07 usando el mismo Qwen3-0.6B-Base, el mismo dataset, los mismos prompts y los mismos parámetros LoRA, pero manteniendo el modelo base en **4-bit**.

Este capítulo responde una pregunta concreta:

> Si LoRA ya reduce muchísimo los parámetros entrenables, ¿podemos reducir también la memoria y el almacenamiento del modelo base congelado?

La respuesta es **QLoRA**.

---

# 1. Dónde estamos

```text
01_bigram
    ↓
02_context_window
    ↓
03_attention
    ↓
04_multihead_transformer
    ↓
05_pretrained_llm_workbench
    ↓
06_full_finetuning_workbench
    ↓
07_lora_finetuning_workbench
    ↓
08_qlora_finetuning_workbench   ← YOU ARE HERE
    ↓
09_instruction_tuning_workbench ← NEXT
```

Ahora tenemos tres estrategias diferentes.

### 06 — Full Fine-Tuning

```text
BF16 base
original Transformer weights trainable
```

### 07 — LoRA

```text
BF16 base frozen
+
LoRA A/B trainable
```

### 08 — QLoRA

```text
4-bit base frozen
+
LoRA A/B trainable
```

---

# 2. La ecuación sigue siendo LoRA

QLoRA no reemplaza la idea matemática de LoRA.

Seguimos teniendo:

\[
W' = W + BA
\]

La diferencia está en cómo almacenamos la matriz base \(W\).

En capítulo 07:

```text
W = BF16
```

En capítulo 08:

```text
W = quantized 4-bit
```

Pero:

```text
W remains frozen
A/B remain trainable
```

---

# 3. Qué significa "Q" en QLoRA

La Q significa:

```text
Quantized
```

Conceptualmente:

```text
           LoRA

BF16 W frozen
+
A/B trainable


          QLoRA

4-bit W frozen
+
A/B trainable
```

La gran diferencia es el costo de mantener el modelo base.

---

# 4. MLX-LM detecta QLoRA automáticamente

La documentación actual de MLX-LM dice:

> If --model points to a quantized model, then training will use QLoRA; otherwise it will use regular LoRA.

Por eso nuestro YAML todavía dice:

```yaml
fine_tune_type: lora
```

pero:

```yaml
model: "models/qwen3-0.6b-base-4bit"
```

Como el modelo es cuantizado, el trainer aplica LoRA sobre QuantizedLinear layers.

Fuente:

https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md

---

# 5. Modelo usado

Usamos el mismo modelo que conocimos en capítulo 05:

```text
mlx-community/Qwen3-0.6B-Base-4bit
```

Fuente original:

```text
Qwen/Qwen3-0.6B-Base
```

El modelo local ocupa aproximadamente:

```text
~335 MB total repository files
~320 MiB model.safetensors
```

frente al BF16, que ocupa alrededor de:

```text
~1.19 GB
```

La cifra exacta depende de cómo se expresen MB/MiB y de los archivos auxiliares.

---

# 6. Reutilizamos capítulo 05

No descargamos otra copia si ya existe.

Ejecuta:

```bash
python prepare_model.py
```

Primero busca:

```text
../05_pretrained_llm_workbench/
    models/
    qwen3-0.6b-base-4bit/
```

Si está completo:

```text
08/models/qwen3-0.6b-base-4bit
        │
        └──── symlink ────► chapter 05 model
```

Si no existe, el script descarga:

```text
mlx-community/Qwen3-0.6B-Base-4bit
```

---

# 7. Qué significa cuantización

Un modelo normalmente almacena pesos como números de floating point.

Por ejemplo:

```text
BF16
≈ 16 bits per scalar
```

Una representación 4-bit usa muchos menos bits para representar los pesos.

Conceptualmente:

```text
BF16 weight
[ many bits ]

4-bit weight
[ few bits ]
```

Esto reduce fuertemente:

```text
disk storage
memory footprint of frozen weights
memory bandwidth
```

---

# 8. Parameter count NO cambia

Una idea muy importante:

```text
0.6B parameters in BF16
```

y:

```text
0.6B parameters represented in 4-bit
```

siguen describiendo aproximadamente el mismo número lógico de parámetros del modelo fuente.

No confundas:

```text
PARAMETER COUNT
with
NUMBER OF BITS USED TO STORE PARAMETERS
```

La cuantización cambia representación, no convierte mágicamente un modelo de 0.6B parámetros en un modelo de 0.15B parámetros.

---

# 9. Inspeccionar la cuantización real

Ejecuta:

```bash
python inspect_quantization.py
```

El script lee:

```text
config.json
```

y muestra:

```text
bits
group_size
mode
disk size
```

Luego carga el modelo y muestra tipos reales:

```text
q_proj type
k_proj type
v_proj type
o_proj type
```

Esperamos observar:

```text
QuantizedLinear
```

en las projections cuantizadas.

---

# 10. Importante: este QLoRA no debe confundirse con cada detalle del paper original

El paper QLoRA popularizó técnicas como:

```text
4-bit quantization
LoRA adapters
NF4
double quantization
paged optimizers
```

Nuestro laboratorio usa la definición operacional de MLX-LM:

```text
LoRA training
+
quantized MLX model
=
QLoRA
```

El Qwen 4-bit que descargamos tiene su propia configuración de cuantización.

Por eso:

> No asumas NF4, double quantization o cualquier otra técnica solamente porque decimos "QLoRA".

Ejecuta:

```bash
python inspect_quantization.py
```

y mira la configuración real.

---

# 11. Cómo MLX-LM convierte una QuantizedLinear en LoRA

El código actual de MLX-LM permite convertir:

```text
nn.Linear
```

y:

```text
nn.QuantizedLinear
```

a LoRA.

Conceptualmente:

```text
BEFORE

QuantizedLinear
      W 4-bit


AFTER

LoRALinear
├── linear → QuantizedLinear W
├── lora_a
└── lora_b
```

Así la capa base cuantizada no desaparece.

Queda envuelta dentro del LoRA layer.

---

# 12. Forward real de QLoRA

El código de MLX-LM hace conceptualmente:

\[
y = linear(x)
\]

y:

\[
z = (xA)B
\]

y luego:

\[
output = y + scale \cdot z
\]

Donde:

```text
linear
=
frozen quantized base
```

y:

```text
A/B
=
trainable LoRA tensors
```

---

# 13. Verlo en tu modelo

Ejecuta:

```bash
python inspect_qlora_math.py
```

Verás algo equivalente a:

```text
BEFORE QLoRA

q_proj:
QuantizedLinear


AFTER QLoRA CONVERSION

wrapper:
LoRALinear

frozen base inside wrapper:
QuantizedLinear

A shape:
...

B shape:
...
```

Esto demuestra directamente la arquitectura.

---

# 14. A/B siguen sin ser 4-bit weights

Una distinción importante.

El base:

```text
W
quantized
frozen
```

Los adapters:

```text
A
B
trainable
```

no son simplemente otra copia de los 4-bit base weights.

Son nuevos parámetros trainables usados para representar el update de bajo rango.

Por eso QLoRA puede entrenar aunque el gran \(W\) base permanezca cuantizado y congelado.

---

# 15. ¿Dónde fluyen los gradients?

Forward:

```text
input
 │
 ├────────► Quantized W ──────┐
 │                            │
 └────────► A ─► B ──────────┤
                              ▼
                           output
```

Backward:

```text
loss
 │
 ▼
gradients
 │
 ├──► A
 └──► B

W:
frozen
no optimizer update
```

---

# 16. Configuración LoRA idéntica a 07

Para comparar justamente usamos:

```yaml
lora_parameters:
  keys:
    - "self_attn.q_proj"
    - "self_attn.v_proj"
  rank: 8
  scale: 20.0
  dropout: 0.0
```

Y:

```yaml
num_layers: -1
```

Es decir:

```text
same LoRA rank
same LoRA scale
same LoRA targets
same Transformer layers
```

La diferencia principal:

```text
07 base = BF16
08 base = 4-bit
```

---

# 17. Dataset idéntico

También copiamos exactamente:

```text
train.jsonl   36 examples
valid.jsonl    6 examples
test.jsonl     6 examples
```

y:

```text
evaluation_prompts.json
```

Esto nos permite aislar la quantization variable.

---

# 18. Prompt masking también es idéntico

```yaml
mask_prompt: true
```

Por tanto:

```text
PROMPT
context only

COMPLETION
supervised loss
```

Igual que 06 y 07.

---

# 19. Hyperparameters también se mantienen

```yaml
batch_size: 1

iters: 80

learning_rate: 1e-5

grad_accumulation_steps: 4

max_seq_length: 256

grad_checkpoint: true
```

Esto hace que 07 vs 08 sea una comparación especialmente limpia.

---

# 20. Inspeccionar los parámetros trainables

Ejecuta:

```bash
python inspect_qlora_parameters.py
```

El script:

1. carga el 4-bit base;
2. confirma que `q_proj` es quantized;
3. congela el modelo;
4. aplica la conversión LoRA;
5. confirma que el wrapper contiene un base quantized;
6. cuenta A/B.

Esperamos que:

```text
LoRA trainable parameter count
≈
QLoRA trainable parameter count
```

si usamos:

```text
same rank
same layers
same target modules
```

---

# 21. Esta igualdad es importante

LoRA:

```text
BF16 W frozen
+
A/B rank 8
```

QLoRA:

```text
4-bit W frozen
+
A/B rank 8
```

La cantidad de parámetros A/B depende principalmente de:

```text
input dimensions
output dimensions
rank
number of adapted modules
```

No de si W está almacenada en BF16 o 4-bit.

---

# 22. Entonces ¿dónde está el ahorro adicional?

Principalmente aquí:

```text
07 LoRA

BF16 frozen base
+
small adapters


08 QLoRA

4-bit frozen base
+
small adapters
```

Los adapters pueden ser similares en tamaño.

Lo que cambia mucho es:

```text
BASE MODEL STORAGE / MEMORY
```

---

# 23. Estructura del capítulo

```text
08_qlora_finetuning_workbench/
│
├── README.md
├── config.py
├── requirements.txt
├── check_environment.py
│
├── prepare_model.py
├── model_files.py
│
├── inspect_quantization.py
├── inspect_training_data.py
├── inspect_qlora_parameters.py
├── inspect_qlora_math.py
│
├── qlora_finetune.yaml
├── test_qlora.yaml
│
├── run_training.py
├── test_qlora.py
├── generate_qlora.py
├── compare_before_after.py
├── compare_06_07_08.py
├── export_qlora.py
│
├── evaluation_prompts.json
│
├── data/
│   ├── train.jsonl
│   ├── valid.jsonl
│   └── test.jsonl
│
├── models/
└── outputs/
```

---

# 24. Preparar environment

Desde:

```bash
cd llm-lab/08_qlora_finetuning_workbench
```

Instala:

```bash
pip install -r requirements.txt
```

Luego:

```bash
python check_environment.py
```

Mantén un solo Python environment activo.

---

# 25. Preparar el 4-bit model

```bash
python prepare_model.py
```

Si capítulo 05 ya tiene el modelo:

```text
reuse via symlink
```

Si no:

```text
download
```

---

# 26. Inspección antes de training

Primero:

```bash
python inspect_quantization.py
```

Después:

```bash
python inspect_training_data.py
```

Después:

```bash
python inspect_qlora_parameters.py
```

Y finalmente:

```bash
python inspect_qlora_math.py
```

No recomiendo saltar directamente a training.

La meta del curso es entender el mecanismo.

---

# 27. Training

Ejecuta:

```bash
python run_training.py
```

Internamente:

```text
python -m mlx_lm lora
```

apunta a:

```text
models/qwen3-0.6b-base-4bit
```

Por ser quantized, MLX-LM utiliza QLoRA.

---

# 28. Qué debes mirar durante training

Igual que antes:

```text
train loss
validation loss
tokens/sec
training behavior
```

Y registra también el runtime peak memory que observes.

No lo infieras únicamente del tamaño del checkpoint.

---

# 29. Por qué no inferimos peak memory

Training memory incluye:

```text
base weights
LoRA weights
gradients
optimizer states
activations
temporary kernels
allocator cache
```

Por tanto:

```text
model file size
≠
training peak memory
```

Nuestro reporte final no inventa esa métrica.

---

# 30. Test

Después:

```bash
python test_qlora.py
```

Esto utiliza:

```text
test.jsonl
```

exactamente como 06 y 07.

---

# 31. Generation

```bash
python generate_qlora.py \
  --prompt "What is gradient accumulation?"
```

Queremos observar si QLoRA aprendió:

```text
Concept:
Definition:
Key idea:
Example:
```

---

# 32. 4-bit Base vs QLoRA

Ejecuta:

```bash
python compare_before_after.py
```

Para cada prompt:

```text
4-BIT BASE:
...

QLoRA:
...
```

Se guarda:

```text
outputs/before_after_qlora.json
```

---

# 33. Comparación final 06 vs 07 vs 08

Ejecuta:

```bash
python compare_06_07_08.py
```

El script recopila:

```text
BF16 base storage
4-bit base storage

06 full checkpoint size
07 LoRA adapter size
08 QLoRA adapter size

saved tensor elements

06 behavior output
07 behavior output
08 behavior output
```

y guarda:

```text
outputs/06_full_vs_07_lora_vs_08_qlora.json
```

---

# 34. Qué esperamos observar

Conceptualmente:

| Metric | 06 Full FT | 07 LoRA | 08 QLoRA |
|---|---|---|---|
| Base | BF16 | BF16 | 4-bit |
| Base frozen | No | Yes | Yes |
| LoRA A/B | No | Yes | Yes |
| Trainable params | Very high | Low | Low |
| Base storage | High | High | Much lower |
| Adapter/checkpoint | Large | Small | Small |
| Optimizer state | High | Low | Low |
| General behavior | Measure | Measure | Measure |

No rellenamos números hasta medirlos.

---

# 35. ¿Qué ocurre durante quantized matrix multiplication?

No debes imaginar que el optimizer convierte permanentemente todo W a BF16 y lo actualiza.

La base cuantizada permanece representada con sus quantization tensors.

MLX ejecuta la operación cuantizada según la implementación de `QuantizedLinear`.

La rama LoRA se calcula aparte:

```text
quantized base output
        +
LoRA delta
```

---

# 36. Fusionar QLoRA

Ejecuta:

```bash
python export_qlora.py
```

MLX-LM puede fusionar:

\[
W + BA
\]

Para una base cuantizada, su implementación:

1. dequantiza el weight para construir el delta;
2. suma el LoRA delta;
3. por defecto puede volver a cuantizar el resultado.

El output:

```text
outputs/fused_qlora_model/
```

queda como un modelo standalone.

---

# 37. Dequantized export

MLX-LM `fuse` también ofrece:

```text
--dequantize
```

si deliberadamente quieres guardar un modelo fused no cuantizado.

Eso cambia significativamente el tamaño.

No lo hacemos por defecto porque queremos preservar la ventaja del experimento QLoRA.

---

# 38. Quantization error

Cuantizar introduce aproximación.

Conceptualmente:

```text
original weight
    ↓
quantization
    ↓
approximate low-bit representation
```

Por tanto:

```text
BF16 model output
≠ necessarily exactly
4-bit model output
```

Aunque representen el mismo pretrained model family.

---

# 39. ¿Puede LoRA compensar parte del quantization error?

Es una pregunta experimental interesante.

QLoRA aprende adapters sobre el comportamiento de la base cuantizada.

Por tanto el adapter puede aprender una specialization compatible con esa representación.

Pero no debemos concluir sin medir que:

```text
QLoRA always equals BF16 LoRA quality
```

Ese es precisamente el objetivo de la comparación 07 vs 08.

---

# 40. El principal trade-off

```text
LoRA BF16

more base precision
more base memory


QLoRA 4-bit

less base precision
much less base memory
```

Ambos:

```text
few trainable adapter parameters
```

---

# 41. Experimento de rank

Después de la corrida inicial:

```text
rank 4
rank 8
rank 16
```

Mide:

```text
adapter size
loss
test loss
response behavior
```

El base 4-bit permanece constante.

---

# 42. Experimento de target modules

Inicial:

```yaml
keys:
  - self_attn.q_proj
  - self_attn.v_proj
```

Luego:

```yaml
keys:
  - self_attn.q_proj
  - self_attn.k_proj
  - self_attn.v_proj
  - self_attn.o_proj
```

Más modules:

```text
more capacity
more trainable params
more optimizer state
```

---

# 43. Experimento de precision

La comparación más importante ya viene incorporada:

```text
07:
BF16 base + LoRA

08:
4-bit base + LoRA
```

Con exactamente:

```text
rank = 8
same targets
same data
same iters
same LR
same evaluation
```

Eso permite estudiar el efecto de quantization de manera mucho más limpia.

---

# 44. Orden exacto

```bash
cd llm-lab/08_qlora_finetuning_workbench
```

### 1

```bash
python check_environment.py
```

### 2

```bash
pip install -r requirements.txt
```

### 3

```bash
python prepare_model.py
```

### 4

```bash
python inspect_quantization.py
```

### 5

```bash
python inspect_training_data.py
```

### 6

```bash
python inspect_qlora_parameters.py
```

### 7

```bash
python inspect_qlora_math.py
```

### 8

```bash
python run_training.py
```

### 9

```bash
python test_qlora.py
```

### 10

```bash
python generate_qlora.py \
  --prompt "What is gradient accumulation?"
```

### 11

```bash
python compare_before_after.py
```

### 12

```bash
python compare_06_07_08.py
```

### 13 — optional

```bash
python export_qlora.py
```

---

# 45. Qué debes registrar

Para cada método:

```text
base precision
base disk size
trainable parameters
adapter/checkpoint size
training loss
validation loss
test loss
tokens/sec
observed peak memory
before/after responses
```

---

# 46. Tabla de aprendizaje

| Concept | 06 Full | 07 LoRA | 08 QLoRA |
|---|---|---|---|
| Base precision | BF16 | BF16 | 4-bit |
| Base frozen | No | Yes | Yes |
| Original W updated | Yes | No | No |
| A/B adapters | No | Yes | Yes |
| Parameter-efficient | No | Yes | Yes |
| Quantized base | No | No | Yes |
| Small specialization checkpoint | No | Yes | Yes |

---

# 47. Preguntas que debes poder responder

1. ¿Qué significa Q en QLoRA?
2. ¿Qué diferencia hay entre LoRA y QLoRA?
3. ¿Cambia el número lógico de parámetros del modelo al cuantizar?
4. ¿Qué cambia entonces?
5. ¿Qué es `QuantizedLinear`?
6. ¿Qué ocurre con `q_proj` al aplicar LoRA?
7. ¿La matriz base cuantizada recibe optimizer updates?
8. ¿Qué recibe gradients?
9. ¿Por qué A/B pueden conservar el mismo parameter count que en LoRA?
10. ¿Dónde ocurre el ahorro extra de QLoRA?
11. ¿Por qué model file size no equivale a peak training memory?
12. ¿Qué significa fusionar un QLoRA adapter?
13. ¿Qué hace `--dequantize` al fusionar?
14. ¿Por qué 4-bit puede introducir error?
15. ¿Por qué usamos exactamente el mismo dataset de 07?
16. ¿Por qué usamos los mismos hyperparameters?
17. ¿Qué métrica debemos medir en lugar de asumir?
18. ¿Qué detalles del paper QLoRA no debemos asumir automáticamente?
19. ¿Cómo inspeccionamos la quantization real del modelo?
20. ¿Cuándo preferirías LoRA BF16 sobre QLoRA?

---

# 48. La gran comparación

Al terminar deberías poder explicar:

```text
FULL FINE-TUNING
"Modify the big original weights."


LoRA
"Freeze the big BF16 weights and learn
small low-rank updates."


QLoRA
"Freeze a quantized version of the big
weights and learn the same kind of
small low-rank updates."
```

---

# 49. ¿Qué sigue?

Después de 08 ya entendemos **cómo adaptar weights**.

Ahora la pregunta cambia.

Hasta ahora nuestro dataset fue artificialmente simple:

```text
prompt
→
structured completion
```

El siguiente capítulo será:

```text
09_instruction_tuning_workbench
```

Ahí estudiaremos:

```text
system
user
assistant
```

chat templates, SFT datasets, multi-turn conversations, dataset quality, instruction diversity y cómo transformar un base model en un modelo que siga instrucciones de manera consistente.

---

# 50. Ruta después de 08

```text
09_instruction_tuning_workbench
    ↓
10_model_evaluation_workbench
    ↓
11_preference_tuning_dpo
    ↓
12_quantization_deployment
    ↓
13_tool_calling_foundations
    ↓
14_single_agent
    ↓
15_multi_agent_systems
```

No entraremos en agentes hasta que la parte de modelos, entrenamiento, alignment y evaluación esté clara.

Ese orden mantiene el objetivo original del curso:

> entender primero qué hay dentro del modelo y cómo se entrena, antes de construir sistemas de agentes encima.
