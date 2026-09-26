# 07 — LoRA Fine-Tuning Workbench

> **Objetivo:** adaptar el mismo Qwen3-0.6B-Base usado en el capítulo 06, con el mismo dataset y la misma evaluación, pero entrenando únicamente pequeñas matrices LoRA mientras los pesos originales permanecen congelados.

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
07_lora_finetuning_workbench   ← YOU ARE HERE
    ↓
08_qlora_finetuning_workbench
```

En 06 hicimos:

```text
pretrained W
     ↓
gradient
     ↓
modify W directly
```

En 07 haremos:

```text
pretrained W
     │
     └── FROZEN
          +
     small A/B matrices
          │
          └── TRAINABLE
```

---

# 2. La idea matemática

Una capa lineal normal:

\[
y = xW
\]

Full Fine-Tuning modifica directamente:

\[
W
\]

LoRA mantiene \(W\) congelada y aprende un update de bajo rango:

\[
\Delta W = BA
\]

Entonces:

\[
W' = W + BA
\]

y conceptualmente:

\[
y = xW + xBA
\]

MLX-LM aplica además un factor de escala sobre la rama LoRA.

La idea fundamental:

```text
BIG W
frozen

SMALL A
trainable

SMALL B
trainable
```

---

# 3. ¿Por qué ahorra tantos parámetros?

Supón:

```text
W = 1024 × 1024
```

Tiene:

```text
1,048,576 parameters
```

Con rank 8:

```text
A = 1024 × 8
B = 8 × 1024

A = 8,192 params
B = 8,192 params

LoRA = 16,384 params
```

Comparación:

```text
Full matrix: 1,048,576
LoRA:          16,384

≈ 64× fewer
```

El modelo real tiene matrices de tamaños distintos, por eso no asumimos el total. Lo medimos directamente con:

```bash
python inspect_lora_parameters.py
```

---

# 4. Experimento controlado: 06 vs 07

Este capítulo usa exactamente el mismo:

```text
Base model
Train dataset
Validation dataset
Test dataset
Evaluation prompts
Prompt masking
Generation comparison
```

que 06.

La variable principal que cambia es:

```text
TRAINING METHOD
```

Por eso podemos estudiar:

```text
                 SAME QWEN BASE
                       │
                 SAME DATASET
                       │
               SAME EVALUATION
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
        06 FULL FT          07 LoRA
```

---

# 5. Modelo

Usamos:

```text
mlx-community/Qwen3-0.6B-Base
```

Fuente:

```text
Qwen/Qwen3-0.6B-Base
```

Es la misma conversión BF16 usada en 06.

Página del modelo:

https://huggingface.co/mlx-community/Qwen3-0.6B-Base

La versión MLX ronda 1.19 GB.

---

# 6. Reutilizamos el modelo de 06

Ejecuta:

```bash
python prepare_model.py
```

El script primero busca:

```text
../06_full_finetuning_workbench/
    models/
    qwen3-0.6b-base-bf16/
```

Si existe, crea un symlink local:

```text
07_lora_finetuning_workbench/models/qwen3-0.6b-base-bf16
                         │
                         └────► chapter 06 model
```

Así no gastamos otros ~1.19 GB.

Si el modelo de 06 no existe, se descarga automáticamente.

También reconoce el nombre legacy:

```text
full_finetuning_workbench
```

por si tu working copy todavía conserva artifacts locales bajo el nombre anterior.

---

# 7. ¿Qué significa Low-Rank?

LoRA no aprende una matriz completa del mismo tamaño que \(W\).

Aprende dos matrices cuya dimensión interior es pequeña:

\[
A \in \mathbb{R}^{d_{in} \times r}
\]

\[
B \in \mathbb{R}^{r \times d_{out}}
\]

donde:

\[
r \ll d
\]

Nuestro:

```yaml
rank: 8
```

crea un cuello de botella de dimensión 8.

---

# 8. Rank

Rank controla capacidad y tamaño.

Rank pequeño:

```text
fewer trainable parameters
smaller adapter
less optimizer state
less adaptation capacity
```

Rank mayor:

```text
more trainable parameters
larger adapter
more optimizer state
more adaptation capacity
```

No confundas:

```text
rank: 8
```

con:

```text
num_layers: 8
```

Son variables distintas.

---

# 9. Qué layers adaptamos

Nuestro YAML:

```yaml
lora_parameters:
  keys:
    - "self_attn.q_proj"
    - "self_attn.v_proj"
  rank: 8
  scale: 20.0
  dropout: 0.0
```

MLX-LM permite elegir las Linear layers mediante `keys`.

El ejemplo oficial actual también muestra `q_proj` y `v_proj` como targets.

Fuente:

https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/examples/lora_config.yaml

---

# 10. ¿Por qué Query y Value?

Attention:

\[
Attention(Q,K,V)
=
softmax\left(
\frac{QK^T}{\sqrt{d}}
\right)V
\]

Tenemos:

```text
x
├── q_proj → Q
├── k_proj → K
└── v_proj → V
```

Adaptar Query puede modificar:

```text
what the token looks for
```

Adaptar Value puede modificar:

```text
what information is carried forward
```

No significa que sean universalmente las mejores targets.

Es una configuración compacta y educativa.

---

# 11. Scale

Configuramos:

```yaml
scale: 20.0
```

Conceptualmente:

\[
y = xW + s(xAB)
\]

donde \(s\) es el factor de escala.

No confundas:

```text
LoRA scale
```

con:

```text
learning rate
```

El learning rate controla el tamaño de los optimizer updates.

Scale controla cuánto contribuye la rama LoRA al forward.

---

# 12. Dropout

Inicialmente:

```yaml
dropout: 0.0
```

Queremos un experimento simple con pocas variables.

Luego puedes probar:

```text
0.05
0.10
```

y comparar validation loss.

---

# 13. Num layers

Usamos:

```yaml
num_layers: -1
```

En el trainer actual de MLX-LM:

```text
-1 = all Transformer layers
```

Esto NO significa full fine-tuning.

Significa:

> aplica LoRA a las targets seleccionadas en todos los Transformer blocks.

Los pesos originales siguen frozen.

---

# 14. Arquitectura conceptual

```text
                         QWEN BASE
                            │
                         FROZEN
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
       q_proj W          k_proj W          v_proj W
        frozen            frozen            frozen
          │                                   │
          │ + LoRA                            │ + LoRA
          ▼                                   ▼
        A_q B_q                             A_v B_v
       TRAINABLE                            TRAINABLE
          │                                   │
          └─────────────────┬─────────────────┘
                            ▼
                         Attention
```

---

# 15. Qué ocurre en forward

Aunque \(W\) esté frozen, sigue participando completamente.

```text
base branch:
xW

LoRA branch:
xAB

result:
xW + scaled(xAB)
```

LoRA NO reemplaza al modelo.

Añade una perturbación aprendida sobre el modelo pretrained.

---

# 16. Qué ocurre en backward

Autograd calcula gradients a través del computation graph.

Pero:

```text
W
frozen
→ no optimizer update

A/B
trainable
→ gradients
→ optimizer update
```

Esto reduce enormemente:

```text
trainable gradients
optimizer state
checkpoint size
```

---

# 17. Por qué pocos parámetros pueden cambiar el comportamiento

El pretrained model ya contiene:

```text
language
syntax
concepts
representations
attention patterns
general knowledge
```

Fine-tuning muchas veces no necesita reaprender todo.

Necesita aprender algo más cercano a:

```text
"Use what you already know
in this particular way."
```

Por eso una pequeña perturbación puede producir un cambio visible de comportamiento.

---

# 18. Nuestro target behavior

El dataset intenta producir respuestas:

```text
Concept: ...

Definition: ...

Key idea: ...

Example: ...
```

Por tanto podemos observar fácilmente si LoRA cambia el estilo.

---

# 19. Dataset

Igual que 06:

```text
data/
├── train.jsonl   36 examples
├── valid.jsonl    6 examples
└── test.jsonl     6 examples
```

Formato:

```json
{
  "prompt": "What is gradient descent?",
  "completion": "Concept: Gradient descent\nDefinition: ..."
}
```

---

# 20. Prompt masking

También mantenemos:

```yaml
mask_prompt: true
```

Así:

```text
PROMPT
conditions model
but does not contribute to supervised loss

COMPLETION
contributes to supervised loss
```

Esto mantiene la objective comparable con 06.

---

# 21. Inspeccionar el dataset

Ejecuta:

```bash
python inspect_training_data.py
```

Verás:

```text
All tokens
Masked prompt tokens
Loss-bearing completion tokens
```

Esto demuestra que:

```text
data objective = same as chapter 06
```

mientras:

```text
parameter update strategy = different
```

---

# 22. Inspeccionar parámetros LoRA

Ejecuta:

```bash
python inspect_lora_parameters.py
```

El script usa la misma función interna de MLX-LM que convierte Linear layers en LoRA layers.

Imprime:

```text
Original base parameters
LoRA parameters added
Trainable parameters
Trainable / base %
```

y los primeros trainable tensors.

Para nuestra configuración esperamos alrededor de:

```text
~1.15M trainable LoRA parameters
```

pero usa siempre el número medido por tu instalación.

---

# 23. Ver A y B reales

Ejecuta:

```bash
python inspect_lora_math.py
```

El script imprime módulos reales:

```text
...q_proj.lora_a
...q_proj.lora_b
...v_proj.lora_a
...v_proj.lora_b
```

con shapes y parameter counts.

El objetivo es conectar:

\[
\Delta W = BA
\]

con tensors concretos.

---

# 24. Configuración de entrenamiento

```yaml
fine_tune_type: lora

num_layers: -1

batch_size: 1

iters: 80

learning_rate: 1e-5

grad_accumulation_steps: 4

max_seq_length: 256

grad_checkpoint: true

mask_prompt: true
```

---

# 25. ¿Por qué LR 1e-5 y no exactamente 5e-6 como 06?

Los métodos tienen dinámicas distintas.

Full FT modifica matrices grandes directamente.

LoRA optimiza una pequeña rama inicialmente cercana a un update nulo.

Mantendremos iguales:

```text
base model
dataset
splits
target behavior
evaluation prompts
generation strategy
```

pero permitimos que cada training method tenga hyperparameters apropiados.

La comparación debe reportarlos explícitamente.

---

# 26. Gradient accumulation

Seguimos usando:

```yaml
batch_size: 1
grad_accumulation_steps: 4
```

Conceptualmente:

```text
micro batch 1 ─┐
micro batch 2 ─┤
micro batch 3 ─┤──► optimizer step
micro batch 4 ─┘
```

Effective batch aproximado:

```text
4 examples
```

---

# 27. Gradient checkpointing

También:

```yaml
grad_checkpoint: true
```

Esto reduce activation memory intercambiando:

```text
less memory
for
more recomputation
```

Ahora podremos comparar peak memory con Full FT.

---

# 28. Training

Ejecuta:

```bash
python run_training.py
```

Internamente:

```text
python -m mlx_lm.lora
```

con:

```yaml
fine_tune_type: lora
```

El trainer actual de MLX-LM soporta:

```text
lora
dora
full
```

Fuente:

https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md

---

# 29. Qué debes observar

Durante training:

```text
Train loss
Validation loss
Tokens/sec
Peak memory
```

Y ahora además:

```text
Trainable parameter count
Adapter size
```

---

# 30. Adapter output

Después:

```text
outputs/
└── lora_adapter/
    ├── adapter_config.json
    └── adapters.safetensors
```

Este checkpoint NO necesita contener otra copia de todo Qwen.

Guarda los parámetros de adaptación.

---

# 31. Test

Ejecuta:

```bash
python test_lora.py
```

Usa:

```text
data/test.jsonl
```

que no participó en optimizer updates.

---

# 32. Generate

```bash
python generate_lora.py \
  --prompt "What is gradient accumulation?"
```

El proceso es:

```text
base BF16
+
LoRA adapter
+
prompt
↓
generation
```

---

# 33. BASE vs LoRA

Ejecuta:

```bash
python compare_before_after.py
```

Usa los mismos prompts con:

```text
temperature = 0
```

y guarda:

```text
outputs/before_after_lora.json
```

---

# 34. 06 Full vs 07 LoRA

Este es el experimento más importante:

```bash
python compare_06_full_vs_07_lora.py
```

Mide:

```text
Base parameter count

06 Full trainable parameters
07 LoRA trainable parameters

Trainable reduction factor

06 checkpoint size
07 adapter size

06 before/after outputs
07 before/after outputs
```

y guarda:

```text
outputs/06_full_vs_07_lora.json
```

---

# 35. Una ventaja operacional enorme

Con Full FT:

```text
base → finance model copy
base → coding model copy
base → legal model copy
```

Con LoRA:

```text
                 ONE BASE
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     finance      coding       legal
      LoRA         LoRA         LoRA
```

Puedes mantener muchas especializaciones pequeñas sobre una sola base.

---

# 36. LoRA NO elimina la necesidad del base model

Un adapter de pocos MB no es un LLM completo.

Para inference necesitas:

```text
base model
+
adapter
```

Así que:

```text
small adapter
≠
small complete LLM
```

Eso prepara el siguiente concepto: QLoRA.

---

# 37. Fusing

Puedes fusionar:

```bash
python export_lora.py
```

Resultado:

```text
outputs/fused_lora_model/
```

Conceptualmente:

\[
W_{fused} = W + BA
\]

Entonces el update queda incorporado al model weight efectivo.

---

# 38. ¿Por qué no fusionar siempre?

Porque adapters separados permiten:

```text
one base
+
many small personalities/tasks/domains
```

sin duplicar todo el modelo.

Fusionar es útil para deployment cuando quieres una sola variante standalone.

---

# 39. Experimento: rank

Después de la primera corrida prueba:

```yaml
rank: 4
```

luego:

```yaml
rank: 8
```

luego:

```yaml
rank: 16
```

Mide:

```text
trainable parameters
adapter size
peak memory
validation loss
test loss
response quality
```

Cambia solo rank.

---

# 40. Experimento: number of layers

Prueba:

```yaml
num_layers: 4
```

```yaml
num_layers: 14
```

```yaml
num_layers: -1
```

Pregunta:

> ¿Cuántos Transformer blocks necesitan adaptación para esta tarea?

---

# 41. Experimento: target modules

Inicial:

```yaml
keys:
  - self_attn.q_proj
  - self_attn.v_proj
```

Luego podrías probar:

```yaml
keys:
  - self_attn.q_proj
  - self_attn.k_proj
  - self_attn.v_proj
  - self_attn.o_proj
```

Más targets:

```text
more trainable parameters
more capacity
more optimizer state
```

No significa automáticamente mejor generalization.

---

# 42. Experiment: scale

Prueba:

```text
10
20
40
```

manteniendo rank constante.

Scale interactúa con:

```text
learning rate
rank
training duration
data
```

No existe una regla "bigger is better".

---

# 43. Adapter initialization

Queremos que al inicio:

\[
\Delta W \approx 0
\]

Así:

```text
effective model at start
≈
pretrained base model
```

Durante training:

```text
A/B learn
↓
ΔW becomes useful
```

---

# 44. Optimizer memory

Full FT necesita optimizer state para muchísimos parámetros.

LoRA necesita optimizer state principalmente para:

```text
A
B
```

Esto explica gran parte de la reducción de training memory.

---

# 45. Gradients

Full FT:

```text
∂L/∂W
for many large W
```

LoRA:

```text
∂L/∂A
∂L/∂B
```

mientras W permanece frozen.

---

# 46. Full vs LoRA vs QLoRA

```text
06 FULL

BF16 base
original Transformer weights trainable


07 LoRA

BF16 base frozen
A/B adapters trainable


08 QLoRA

4-bit base frozen
A/B adapters trainable
```

---

# 47. Por qué QLoRA viene después

LoRA reduce:

```text
trainable parameter memory
gradient memory
optimizer memory
checkpoint specialization size
```

pero el base sigue BF16.

QLoRA preguntará:

> ¿Y si también almacenamos el base frozen en 4 bits?

Ahí reutilizaremos el 4-bit model de capítulo 05.

---

# 48. Orden exacto de ejecución

Desde:

```bash
cd llm-lab/07_lora_finetuning_workbench
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
python inspect_training_data.py
```

### 5

```bash
python inspect_lora_parameters.py
```

### 6

```bash
python inspect_lora_math.py
```

### 7

```bash
python run_training.py
```

### 8

```bash
python test_lora.py
```

### 9

```bash
python generate_lora.py \
  --prompt "What is gradient accumulation?"
```

### 10

```bash
python compare_before_after.py
```

### 11

```bash
python compare_06_full_vs_07_lora.py
```

### 12 — optional

```bash
python export_lora.py
```

---

# 49. Qué debes registrar

## Chapter 06

```text
Trainable parameters
Trainable %
Peak memory
Tokens/sec
Validation loss
Test loss
Checkpoint size
Behavior after training
```

## Chapter 07

```text
Rank
Target modules
Trainable parameters
Trainable %
Peak memory
Tokens/sec
Validation loss
Test loss
Adapter size
Behavior after training
```

---

# 50. Tabla final

| Metric | 06 Full FT | 07 LoRA |
|---|---:|---:|
| Base model | Qwen3-0.6B BF16 | Qwen3-0.6B BF16 |
| Train examples | 36 | 36 |
| Validation examples | 6 | 6 |
| Test examples | 6 | 6 |
| Trainable parameters | measure | measure |
| Trainable % | measure | measure |
| Peak memory | measure | measure |
| Checkpoint size | measure | measure |
| Test loss | measure | measure |
| Structured response learned? | inspect | inspect |

---

# 51. Preguntas que debes poder responder

1. ¿Qué significa Low-Rank Adaptation?
2. ¿Qué representa W?
3. ¿Qué representan A y B?
4. ¿Qué controla rank?
5. ¿Por qué LoRA tiene menos parámetros?
6. ¿Qué weights están frozen?
7. ¿El base model sigue participando en forward?
8. ¿Qué recibe optimizer updates?
9. ¿Qué controla `num_layers`?
10. ¿Qué controla `keys`?
11. ¿Qué controla `scale`?
12. ¿Qué controla `dropout`?
13. ¿Por qué LoRA usa menos optimizer memory?
14. ¿Por qué el adapter puede ser muy pequeño?
15. ¿Por qué sigue siendo necesario el base model?
16. ¿Por qué usamos el mismo dataset que 06?
17. ¿Por qué usamos temperature 0 en comparaciones?
18. ¿Qué significa fusionar un adapter?
19. ¿Por qué podrías mantener adapters separados?
20. ¿Cuál es la diferencia fundamental entre LoRA y QLoRA?

Si puedes explicar los outputs de:

```text
inspect_lora_parameters.py
inspect_lora_math.py
compare_06_full_vs_07_lora.py
```

ya no estás usando LoRA como una caja negra.

---

# 52. Siguiente capítulo

```text
08_qlora_finetuning_workbench
```

Usaremos:

```text
Qwen3-0.6B-Base-4bit
```

con LoRA adapters.

Entonces tendremos una comparación experimental completa:

```text
06 Full Fine-Tuning
        vs
07 LoRA
        vs
08 QLoRA
```

y podremos estudiar con datos reales:

```text
trainable parameters
memory
checkpoint size
speed
loss
behavior
```

Ese es el objetivo final de esta secuencia.
