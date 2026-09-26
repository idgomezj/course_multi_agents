# Full Fine-Tuning Workbench

> **Objetivo:** tomar un LLM real ya preentrenado, calcular una nueva supervised loss sobre nuestro propio dataset y actualizar directamente los pesos completos de sus Transformer layers.

Este laboratorio es el puente entre dos mundos:

```text
PARTE 1 — MODELO DESDE CERO

random weights
      ↓
Bigram
      ↓
Context model
      ↓
Attention
      ↓
Mini-GPT


PARTE 2 — MODELO PREENTRENADO

Qwen pretrained weights
      ↓
inspect
      ↓
inference
      ↓
baseline


ESTE LABORATORIO

pretrained weights
      ↓
our training data
      ↓
forward
      ↓
loss
      ↓
backpropagation
      ↓
optimizer
      ↓
UPDATED PRETRAINED WEIGHTS
```

La meta **no** es crear el mejor modelo posible con 36 ejemplos.

La meta es entender exactamente qué significa:

> **fine-tune an existing LLM**

antes de aprender LoRA y QLoRA.

---

# 1. Modelo utilizado

Usamos la versión MLX BF16 de:

```text
Qwen/Qwen3-0.6B-Base
```

Modelo local:

```text
mlx-community/Qwen3-0.6B-Base
```

Este modelo:

- tiene aproximadamente 0.6B parámetros;
- usa 28 Transformer layers;
- hidden size 1024;
- 16 query heads;
- 8 key/value heads;
- vocabulario de 151,936 tokens;
- está almacenado en BF16;
- ocupa aproximadamente 1.19 GB como modelo MLX no cuantizado.

Fuente:

https://huggingface.co/mlx-community/Qwen3-0.6B-Base

---

# 2. ¿Por qué NO usamos el modelo 4-bit del laboratorio anterior?

En `05_pretrained_llm_workbench` usamos:

```text
Qwen3-0.6B-Base-4bit
```

Excelente para:

```text
inference
QLoRA
memory-efficient experimentation
```

Pero en este laboratorio queremos observar:

```text
real floating-point weights
       ↓
gradients
       ↓
optimizer
       ↓
modified floating-point weights
```

Por eso usamos:

```text
BF16
```

en vez de:

```text
4-bit
```

La comparación conceptual es:

| Model | Uso principal en este curso |
|---|---|
| 4-bit | inference y más adelante QLoRA |
| BF16 | full fine-tuning |
| BF16 + LoRA | próximo laboratorio |

---

# 3. Qué significa BF16

BF16 significa **Brain Floating Point 16-bit**.

Una representación de 16 bits ocupa aproximadamente:

```text
2 bytes per scalar
```

Para cientos de millones de parámetros:

```text
parameters
×
bytes per parameter
=
large memory requirement
```

Pero durante entrenamiento no tenemos solamente los pesos.

También aparecen:

```text
weights
+
gradients
+
optimizer state
+
activations
+
temporary buffers
```

Por eso:

> El tamaño del archivo del modelo NO es igual a la memoria necesaria para entrenarlo.

---

# 4. Estructura del laboratorio

```text
06_full_finetuning_workbench/
│
├── README.md
├── config.py
├── requirements.txt
│
├── check_environment.py
├── download_model.py
├── model_files.py
│
├── inspect_trainable_parameters.py
├── inspect_training_data.py
│
├── full_finetune.yaml
├── test_finetuned.yaml
│
├── run_training.py
├── test_finetuned.py
├── generate_finetuned.py
├── compare_before_after.py
├── export_finetuned.py
│
├── evaluation_prompts.json
│
├── data/
│   ├── train.jsonl
│   ├── valid.jsonl
│   └── test.jsonl
│
├── models/
│   └── .gitkeep
│
└── outputs/
    └── .gitkeep
```

Los modelos y checkpoints locales están ignorados por Git.

---

# 5. La idea central

Cuando construimos Mini-GPT hicimos:

```text
random parameters
      ↓
forward
      ↓
loss
      ↓
backward
      ↓
optimizer.step()
      ↓
better parameters
```

Ahora hacemos exactamente la misma matemática.

La diferencia es el punto inicial:

```text
PRETRAINING FROM SCRATCH

random W
  ↓
training
  ↓
W_pretrained
```

versus:

```text
FINE-TUNING

W_pretrained
     ↓
our dataset
     ↓
additional training
     ↓
W_finetuned
```

No existe una nueva clase mágica de aprendizaje.

Seguimos usando:

$$
\nabla_W L
$$

y:

$$
W_{new}
=
W_{old}
-
\eta \nabla_W L
$$

con un optimizer más sofisticado como AdamW.

---

# 6. Nuestro objetivo de especialización

Este dataset entrena un comportamiento visible.

Queremos transformar respuestas libres en respuestas de tutor técnico con estructura:

```text
Concept: ...

Definition: ...

Key idea: ...

Example: ...
```

Por ejemplo:

Prompt:

```text
What is gradient accumulation?
```

Target:

```text
Concept: Gradient accumulation
Definition: ...
Key idea: ...
Example: ...
```

Esto hace que el resultado de fine-tuning sea fácil de observar.

No estamos intentando agregar miles de millones de nuevos conocimientos.

Estamos enseñando principalmente:

```text
response behavior
+
response structure
+
domain emphasis
```

---

# 7. Dataset

MLX-LM reconoce automáticamente este formato:

```json
{
  "prompt": "What is gradient descent?",
  "completion": "Concept: Gradient descent\nDefinition: ..."
}
```

Cada ejemplo ocupa **una sola línea JSON**.

Tenemos:

```text
data/
├── train.jsonl
├── valid.jsonl
└── test.jsonl
```

Sus funciones son distintas.

---

## Train

```text
train.jsonl
```

participa en:

```text
loss
 ↓
backpropagation
 ↓
parameter update
```

El modelo puede aprender directamente de estos ejemplos.

---

## Validation

```text
valid.jsonl
```

se usa periódicamente para calcular:

```text
validation loss
```

pero **no actualiza parámetros**.

Sirve para detectar cosas como:

```text
train loss ↓
validation loss ↑
```

que puede ser una señal de overfitting.

---

## Test

```text
test.jsonl
```

se reserva para la evaluación final.

No debería utilizarse para tomar decisiones repetidas durante training.

Conceptualmente:

```text
TRAIN
learn

VALID
develop / monitor

TEST
final evaluation
```

---

# 8. Prompt masking

Nuestro archivo:

```text
full_finetune.yaml
```

incluye:

```yaml
mask_prompt: true
```

Esto es extremadamente importante.

Supón:

```text
PROMPT:
What is gradient descent?

COMPLETION:
Concept: Gradient descent...
```

Sin masking:

```text
loss on:
PROMPT + COMPLETION
```

Con prompt masking:

```text
PROMPT
used as context
but no supervised loss
        │
        ▼
COMPLETION
used for supervised loss
```

El prompt todavía entra al modelo.

Solo estamos diciendo:

> No penalices al modelo por no “predecir” los tokens del prompt. Entrénalo sobre la respuesta que queremos.

---

# 9. Mira el masking directamente

Después de descargar el BF16 model:

```bash
python inspect_training_data.py
```

El script usa el mismo `CompletionsDataset` de MLX-LM.

Verás:

```text
RAW TRAINING RECORD

Prompt:
...

Completion:
...

TOKEN COUNTS

All tokens: ...
Masked prompt tokens: ...
Loss-bearing completion tokens: ...
```

Luego imprime:

```text
MASKED REGION
```

y:

```text
REGION USED FOR SUPERVISED LOSS
```

Esto conecta el JSONL con la matemática del training loop.

---

# 10. De JSON a loss

Internamente el flujo es aproximadamente:

```text
JSON record
    ↓
prompt + completion
    ↓
chat template
    ↓
tokenizer
    ↓
token IDs
    ↓
input tokens
    ↓
Transformer
    ↓
logits
    ↓
shift targets by one position
    ↓
cross entropy
    ↓
mask prompt positions
    ↓
average completion loss
```

En lenguaje matemático:

$$
L
=
-\frac{1}{N}
\sum_{t \in completion}
\log p(y_t \mid y_{<t})
$$

Solo sumamos posiciones pertenecientes a la completion.

---

# 11. Preparar el entorno

Desde:

```bash
cd llm-lab/06_full_finetuning_workbench
```

Instala:

```bash
pip install -r requirements.txt
```

Luego:

```bash
python check_environment.py
```

Presta atención a:

```text
Python executable
mlx version
mlx-lm version
Machine: arm64
```

---

# 12. Importante: usa UN solo environment

Anteriormente vimos un shell así:

```text
(.venv) (base)
```

Eso significa que se habían activado:

```text
virtualenv
+
Conda base
```

simultáneamente.

Evítalo.

Usa:

```bash
which python
```

y:

```bash
python -c "import sys; print(sys.executable)"
```

para confirmar qué interpreter estás usando.

Para este curso lo importante es consistencia:

```text
same python
    ↓
same pip
    ↓
same mlx
    ↓
same mlx-lm
```

---

# 13. Descargar el modelo BF16

Ejecuta:

```bash
python download_model.py
```

Se descargará:

```text
mlx-community/Qwen3-0.6B-Base
```

a:

```text
models/
└── qwen3-0.6b-base-bf16/
```

Este download es aproximadamente 1.19 GB.

No lo confundas con:

```text
models/qwen3-0.6b-base-4bit
```

del laboratorio anterior.

Son representaciones distintas.

---

# 14. Por qué descargamos otra copia

Esto es intencional.

Queremos tener:

```text
05_pretrained_llm_workbench/
    4-bit model
    inference reference

06_full_finetuning_workbench/
    BF16 model
    trainable reference
```

Así podemos comparar sin sobreescribir nada.

---

# 15. ¿Qué significa FULL en MLX-LM?

Esta parte merece precisión.

MLX-LM hace primero:

```python
model.freeze()
```

En modo:

```yaml
fine_tune_type: full
```

después unfreezea las Transformer layers seleccionadas.

Nuestro config usa:

```yaml
num_layers: -1
```

que en MLX-LM significa:

```text
all Transformer layers
```

Esto NO significa necesariamente que absolutamente todos los tensores top-level del modelo queden trainables.

Por ejemplo, dependiendo de la arquitectura, elementos como:

```text
embedding
final norm
output head
```

pueden permanecer frozen.

Por eso incluimos una medición real.

---

# 16. Mide qué se entrenará

Ejecuta:

```bash
python inspect_trainable_parameters.py
```

El script replica la política de `full + num_layers=-1` y muestra:

```text
Total parameters:
...

Trainable parameters:
...

Trainable percentage:
...
```

También imprime algunos parameter groups que continúan frozen.

Este dato es mucho mejor que decir simplemente:

> “Full fine-tuning entrena 100% del modelo.”

En este curso queremos entender **la implementación exacta que estamos ejecutando**.

---

# 17. Configuración del entrenamiento

Archivo:

```text
full_finetune.yaml
```

Configuración inicial:

```yaml
fine_tune_type: full

num_layers: -1

batch_size: 1

iters: 80

learning_rate: 5e-6

grad_accumulation_steps: 4

max_seq_length: 256

grad_checkpoint: true

mask_prompt: true
```

Veamos cada una.

---

# 18. `fine_tune_type: full`

Esto indica que no queremos convertir las Linear layers en LoRA layers.

Estamos modificando directamente los pesos completos de las Transformer layers seleccionadas.

Comparación futura:

```text
FULL

W
↓
gradient
↓
W modified directly
```

versus:

```text
LoRA

W frozen

W' = W + BA

only A and B trained
```

---

# 19. `num_layers: -1`

MLX-LM interpreta:

```text
-1
```

como todas las Transformer layers.

Para Qwen3-0.6B-Base:

```text
28 layers
```

Por tanto nuestro experimento modifica las 28 Transformer blocks.

Después puedes experimentar con:

```yaml
num_layers: 4
```

o:

```yaml
num_layers: 8
```

para observar el efecto sobre:

```text
memory
speed
trainable parameters
specialization
```

---

# 20. Batch size

Usamos:

```yaml
batch_size: 1
```

porque full fine-tuning almacena muchas más gradients que LoRA.

Un batch mayor aumenta memoria.

---

# 21. Gradient accumulation

Tenemos:

```yaml
grad_accumulation_steps: 4
```

Conceptualmente:

```text
micro batch 1
gradient
   ↓
accumulate

micro batch 2
gradient
   ↓
accumulate

micro batch 3
gradient
   ↓
accumulate

micro batch 4
gradient
   ↓
accumulate
   ↓
optimizer step
```

Con:

```text
batch_size = 1
accumulation = 4
```

obtenemos aproximadamente:

```text
effective batch = 4 examples
```

sin mantener cuatro examples simultáneamente en memoria.

---

# 22. Gradient checkpointing

Configuramos:

```yaml
grad_checkpoint: true
```

Normal backprop necesita conservar activations del forward pass.

Conceptualmente:

```text
forward
  ↓
store many activations
  ↓
backward
```

Checkpointing reduce memoria:

```text
forward
  ↓
store fewer activations
  ↓
backward
  ↓
recompute missing activations
```

Intercambiamos:

```text
less memory
for
more computation
```

---

# 23. Learning rate

Usamos:

```yaml
learning_rate: 5e-6
```

Fine-tuning suele necesitar updates mucho más pequeños que entrenar un pequeño modelo desde random initialization.

¿Por qué?

Porque queremos:

```text
preserve useful pretrained knowledge
+
introduce controlled specialization
```

Un learning rate demasiado alto puede destruir representaciones útiles rápidamente.

---

# 24. AdamW

Usamos:

```yaml
optimizer: adamw
```

y:

```yaml
weight_decay: 0.01
```

La secuencia sigue siendo:

```text
loss
 ↓
gradients
 ↓
AdamW state
 ↓
parameter update
```

AdamW no elimina la idea básica de gradient descent.

La hace más sofisticada mediante estadísticas adaptativas por parámetro y weight decay desacoplado.

---

# 25. Número de iteraciones

Primera corrida:

```yaml
iters: 80
```

Esto es un **experimento educativo pequeño**.

No significa:

> 80 iteraciones es una receta universal.

Queremos primero observar:

```text
does loss decrease?
does validation improve?
does output style change?
does it overfit?
how much memory?
how fast?
```

Luego modificamos una variable a la vez.

---

# 26. Ejecutar full fine-tuning

Primero:

```bash
python inspect_training_data.py
```

Luego:

```bash
python inspect_trainable_parameters.py
```

Cuando entiendas ambos:

```bash
python run_training.py
```

El wrapper ejecuta internamente MLX-LM usando:

```text
python -m mlx_lm lora
```

con:

```yaml
fine_tune_type: full
```

Aunque el comando histórico se llame `lora`, MLX-LM actualmente utiliza esa misma training entry point para:

```text
LoRA
DoRA
Full fine-tuning
```

---

# 27. Qué debes mirar durante training

Verás líneas con información semejante a:

```text
Iter ...
Train loss ...
Learning Rate ...
It/sec ...
Tokens/sec ...
Peak mem ...
Val loss ...
```

No mires únicamente Train loss.

Observa:

```text
TRAIN LOSS
    ↓

VALIDATION LOSS
    ↓
```

idealmente ambos mejoran inicialmente.

---

# 28. Un posible patrón saludable

```text
iteration     train       validation

0             3.20        3.15
10            2.10        2.25
20            1.30        1.55
30            0.90        1.10
```

No tienen que ser esos números.

Lo importante es la tendencia.

---

# 29. Un posible patrón de overfitting

```text
iteration     train       validation

20            1.20        1.50
40            0.60        1.20
60            0.20        1.80
80            0.05        2.40
```

Aquí:

```text
train gets better

validation gets worse
```

El dataset es pequeño, así que esto puede ocurrir rápidamente.

Eso sería un resultado educativo útil, no un fracaso del laboratorio.

---

# 30. ¿Dónde se guardan los pesos?

MLX-LM escribirá:

```text
outputs/
└── full_weights/
    ├── adapter_config.json
    └── adapters.safetensors
```

El nombre:

```text
adapters.safetensors
```

puede confundir.

En `fine_tune_type: full` no significa que estemos haciendo LoRA.

MLX-LM utiliza la misma infraestructura de output.

El config guardado identifica:

```text
fine_tune_type = full
```

y los pesos corresponden a los parámetros completos fine-tuned de las layers seleccionadas.

---

# 31. Evaluar el test set

Después del training:

```bash
python test_finetuned.py
```

El test usa:

```text
data/test.jsonl
```

y calcula loss/perplexity sobre ejemplos que no participaron en optimization.

El objetivo es responder:

> ¿El modelo aprendió algo que generaliza más allá de las respuestas exactas de train.jsonl?

---

# 32. Generar con el modelo fine-tuned

Ejecuta:

```bash
python generate_finetuned.py \
  --prompt "What is gradient accumulation?"
```

Queremos observar si aparece nuestro patrón:

```text
Concept:
Definition:
Key idea:
Example:
```

No importa si no lo reproduce perfectamente.

Queremos comparar contra la base.

---

# 33. El experimento más importante: BEFORE vs AFTER

Ejecuta:

```bash
python compare_before_after.py
```

El script corre primero:

```text
BASE BF16 MODEL
```

y después:

```text
FULLY FINE-TUNED MODEL
```

sobre exactamente los mismos prompts.

Ejemplo conceptual:

```text
PROMPT

What is gradient accumulation?


BEFORE

Gradient accumulation is...


AFTER

Concept: Gradient accumulation
Definition: ...
Key idea: ...
Example: ...
```

Finalmente guarda:

```text
outputs/before_after.json
```

---

# 34. ¿Por qué usamos decoding greedy en la comparación?

Usamos:

```text
temperature = 0
```

para minimizar variabilidad de sampling.

Si antes usamos:

```text
temperature 0.9
```

y después:

```text
temperature 0.7
```

no sabríamos si el cambio proviene de:

```text
weights
or
sampling randomness
```

Por eso las comparaciones experimentales deben controlar las variables.

---

# 35. Exportar un modelo standalone

Después de entrenar:

```bash
python export_finetuned.py
```

Generará:

```text
outputs/
└── fused_model/
```

Ese directorio puede cargarse como un modelo normal sin tener que pasar separadamente:

```text
base model
+
fine-tuned weight path
```

Conceptualmente:

```text
BASE MODEL
+
FULL FINE-TUNED WEIGHTS
        ↓
      export
        ↓
STANDALONE MODEL
```

---

# 36. Fine-tuning no crea conocimiento de la nada

Nuestro tiny dataset tiene decenas de ejemplos.

No esperes que convierta 0.6B Qwen en un experto universal.

El objetivo es observar:

```text
behavioral specialization
```

y entender:

```text
training mechanics
```

La calidad final depende de:

- dataset quality;
- dataset size;
- learning rate;
- iteration count;
- sequence length;
- distribution;
- model capacity;
- objective;
- evaluation.

---

# 37. Catastrophic forgetting

Full fine-tuning tiene mucha capacidad para modificar el modelo.

Eso es poderoso.

También es peligroso.

Supón:

```text
PRETRAINED MODEL

English
math
coding
facts
reasoning patterns
...
```

y lo entrenamos demasiado sobre:

```text
tiny narrow dataset
tiny narrow dataset
tiny narrow dataset
...
```

Los weights pueden especializarse demasiado.

Resultado:

```text
new domain ↑

other capabilities ↓
```

A esto lo llamamos:

```text
catastrophic forgetting
```

Por eso luego aprenderemos técnicas parameter-efficient como LoRA.

---

# 38. Full fine-tuning vs LoRA

## Full

```text
pretrained W
     ↓
gradient
     ↓
modify W directly
```

Ventajas:

- máxima libertad para adaptar pesos;
- puede producir cambios fuertes;
- conceptualmente directo.

Desventajas:

- más memoria;
- más optimizer state;
- checkpoints mayores;
- mayor riesgo de olvidar capacidades;
- más costoso.

---

## LoRA

```text
W frozen

A trainable
B trainable

W' = W + BA
```

Ventajas:

- muchísimo menos trainable memory;
- pequeños adapters;
- fácil mantener varias especializaciones;
- base model permanece intacto.

Lo aprenderemos después.

---

# 39. Full fine-tuning vs QLoRA

QLoRA combina:

```text
quantized base model
+
LoRA
```

Conceptualmente:

```text
4-bit W
frozen

+
trainable low-rank adapters
```

Es muy diferente de lo que estamos haciendo aquí:

```text
BF16 W
+
direct full-weight updates
```

---

# 40. Memory troubleshooting

Tu máquina tiene unified memory.

Si recibes memory pressure, cambia **una variable a la vez**.

Primero:

```yaml
max_seq_length: 128
```

Luego, si fuera necesario:

```yaml
num_layers: 16
```

después:

```yaml
num_layers: 8
```

Ya tenemos:

```yaml
batch_size: 1
grad_checkpoint: true
```

que son decisiones orientadas a reducir memoria.

No cambies diez parámetros simultáneamente o perderás el valor experimental.

---

# 41. Sobre `num_layers`

Un excelente experimento futuro:

```text
Run A:
num_layers = 4

Run B:
num_layers = 16

Run C:
num_layers = -1
```

Mide:

```text
trainable parameters
peak memory
tokens/sec
validation loss
response change
```

Esto demuestra que “full fine-tuning” también puede controlar cuántas layers completas se actualizan.

---

# 42. Sobre el nombre del comando `mlx_lm.lora`

Puede parecer extraño que Full Fine-Tuning utilice el comando:

```text
mlx_lm lora
```

Históricamente esa herramienta empezó alrededor de LoRA.

Actualmente el mismo trainer acepta:

```text
lora
dora
full
```

a través de:

```yaml
fine_tune_type:
```

No confundas:

```text
command name
with
training method
```

Nuestro YAML controla el método real.

---

# 43. Orden exacto para ejecutar el laboratorio

Desde:

```bash
cd llm-lab/06_full_finetuning_workbench
```

### 1. Environment

```bash
python check_environment.py
```

### 2. Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download BF16 model

```bash
python download_model.py
```

### 4. Inspect exact trainable parameter count

```bash
python inspect_trainable_parameters.py
```

### 5. Inspect dataset → tokens → masked loss

```bash
python inspect_training_data.py
```

### 6. Train

```bash
python run_training.py
```

### 7. Evaluate held-out test set

```bash
python test_finetuned.py
```

### 8. Generate manually

```bash
python generate_finetuned.py \
  --prompt "What is gradient accumulation?"
```

### 9. Compare before vs after

```bash
python compare_before_after.py
```

### 10. Optional standalone export

```bash
python export_finetuned.py
```

---

# 44. Qué debes escribir en tus notas

Antes de entrenar:

```text
Trainable parameters:
Peak memory before training:
Baseline output:
```

Durante:

```text
Train loss:
Validation loss:
Tokens/sec:
Peak memory:
```

Después:

```text
Test loss:
Test perplexity:
Behavior before:
Behavior after:
```

Así conviertes el laboratorio en un experimento reproducible.

---

# 45. Preguntas que debes poder responder

## Dataset

1. ¿Cuál es la diferencia entre train, validation y test?
2. ¿Qué significa prompt masking?
3. ¿Por qué el prompt todavía entra al forward pass aunque esté masked?
4. ¿Por qué JSONL exige un ejemplo por línea?

## Fine-tuning

5. ¿Cuál es la diferencia entre pretraining y fine-tuning?
6. ¿Qué pesos existen antes de comenzar este training?
7. ¿Qué hace `loss.backward()` conceptualmente?
8. ¿Qué hace AdamW después de obtener gradients?
9. ¿Por qué usamos learning rate pequeño?
10. ¿Qué significa `num_layers=-1` en MLX-LM?

## Memory

11. ¿Por qué training usa más memoria que inference?
12. ¿Qué almacena un optimizer además de los weights?
13. ¿Cómo reduce memoria gradient checkpointing?
14. ¿Cómo funciona gradient accumulation?
15. ¿Por qué batch size 1 puede ser útil?

## Evaluation

16. ¿Por qué no debemos mirar únicamente train loss?
17. ¿Cómo detectas overfitting?
18. ¿Por qué reservamos test.jsonl?
19. ¿Por qué usamos greedy decoding para BEFORE vs AFTER?
20. ¿Qué es catastrophic forgetting?

## Full vs LoRA

21. ¿Qué significa modificar W directamente?
22. ¿Qué significa congelar W en LoRA?
23. ¿Por qué LoRA requiere menos memoria?
24. ¿Qué diferencia hay entre LoRA y QLoRA?
25. ¿Por qué primero estamos aprendiendo Full Fine-Tuning?

Si puedes explicar estas preguntas sin leer las respuestas, ya entiendes mucho más que simplemente “correr un fine-tuning command”.

---

# 46. Qué sigue después

Cuando completes este laboratorio tendremos:

```text
PRETRAINED BASE MODEL
      ↓
FULL FINE-TUNING
      ↓
BEFORE / AFTER evidence
```

El próximo workbench debe repetir **el mismo dataset y la misma evaluación**, pero usando:

```text
LoRA
```

Entonces podremos comparar científicamente:

```text
                    FULL              LoRA

Trainable params     many               few

Base weights         modified           frozen

Memory               higher             lower

Checkpoint           larger             small

Training time        higher             lower

Specialization       strong             efficient
```

Y después:

```text
QLoRA
```

usando nuevamente el modelo 4-bit.

Ese será el punto donde podrás explicar claramente:

> **Full Fine-Tuning vs LoRA vs QLoRA**

no como tres comandos diferentes, sino como tres estrategias diferentes para modificar el comportamiento de un LLM.
