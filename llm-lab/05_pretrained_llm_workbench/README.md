# Pretrained LLM Workbench

> **Segunda fase del curso:** dejamos de crear todos los pesos desde cero y empezamos a estudiar un LLM real ya preentrenado.

Este laboratorio existe para responder, de manera práctica, una pregunta fundamental:

> **¿Qué recibimos realmente cuando descargamos un LLM de Internet, cómo lo inspeccionamos, cómo lo ejecutamos y cómo establecemos una línea base antes de volver a entrenarlo?**

Hasta ahora construimos nuestro propio camino:

```text
01_bigram
    ↓
02_context_window
    ↓
03_attention
    ↓
04_multihead_transformer
    ↓
Mini-GPT entrenado desde pesos aleatorios
```

Ahora iniciamos un camino diferente:

```text
PRETRAINED LLM
      ↓
download
      ↓
inspect files
      ↓
inspect tokenizer
      ↓
inspect architecture
      ↓
run inference
      ↓
save baseline
      ↓
      ├─────────────── future: Full Fine-Tuning
      ├─────────────── future: LoRA
      └─────────────── future: QLoRA
```

Este directorio **no se llama 05** deliberadamente. Marca el comienzo de una nueva línea de aprendizaje: trabajar con modelos reales preentrenados.

---

# 1. Modelo utilizado

Usaremos:

```text
Source model:
Qwen/Qwen3-0.6B-Base

Local Apple-Silicon version:
mlx-community/Qwen3-0.6B-Base-4bit
```

La versión MLX es una conversión cuantizada a 4 bits del modelo base original.

Características documentadas del modelo fuente:

```text
Type:                  Causal Language Model
Training stage:        Pretraining
Parameters:            ~0.6B
Non-embedding params:  ~0.44B
Transformer layers:    28
Query attention heads: 16
Key/value heads:       8
Context length:        32,768 tokens
License:               Apache 2.0
```

Fuentes oficiales:

- Qwen base model: https://huggingface.co/Qwen/Qwen3-0.6B-Base
- MLX conversion: https://huggingface.co/mlx-community/Qwen3-0.6B-Base-4bit
- MLX-LM: https://github.com/ml-explore/mlx-lm

---

# 2. ¿Por qué usamos el modelo **Base**?

Esta elección es intencional.

Existen dos conceptos que debes separar:

```text
PRETRAINED BASE MODEL
        ≠
INSTRUCTION-TUNED MODEL
```

Un modelo base aprende principalmente mediante **next-token prediction** sobre grandes cantidades de texto.

Conceptualmente:

```text
"The capital of France is"
              ↓
            model
              ↓
           "Paris"
```

No fue necesariamente entrenado para comportarse como:

```text
USER:
What is the capital of France?

ASSISTANT:
The capital of France is Paris.
```

Ese comportamiento conversacional suele aparecer después mediante:

```text
pretraining
    ↓
instruction tuning / SFT
    ↓
preference alignment
    ↓
assistant-style model
```

Por eso, en este laboratorio, es mejor probar prompts de continuación como:

```text
Artificial intelligence is
```

que asumir que el modelo base se comportará como ChatGPT.

Esto será extremadamente importante cuando hagamos fine-tuning.

---

# 3. ¿Por qué MLX?

Tu Mac usa Apple Silicon.

MLX es un framework de machine learning diseñado para Apple Silicon y MLX-LM proporciona herramientas para ejecutar y entrenar LLMs sobre MLX.

Nuestro flujo será:

```text
Hugging Face
      ↓
MLX-compatible model
      ↓
Apple unified memory
      ↓
CPU / GPU resources
      ↓
local inference
```

No necesitamos enviar el prompt a una API externa para este laboratorio.

El modelo se ejecuta localmente después de descargarlo.

---

# 4. ¿Por qué 4-bit?

El modelo fuente tiene aproximadamente 600 millones de parámetros.

Si imagináramos todos esos parámetros en FP32:

```text
600,000,000 parameters
×
4 bytes
≈
2.4 GB
```

En FP16/BF16, aproximadamente:

```text
600,000,000
×
2 bytes
≈
1.2 GB
```

La cuantización reduce la cantidad de bits utilizados para representar gran parte de los pesos.

En este laboratorio usamos una conversión:

```text
4-bit
```

y el archivo local de pesos es mucho más pequeño.

**Importante:** cuantizar no significa que el modelo tenga mágicamente menos conocimiento conceptual ni que el modelo fuente deje de ser un modelo de ~0.6B parámetros.

Significa que estamos usando una representación comprimida de esos pesos.

No confundas:

```text
parameter count
      ≠
file size
      ≠
memory representation
```

---

# 5. Estructura del laboratorio

```text
pretrained_llm_workbench/
├── README.md
├── config.py
├── requirements.txt
│
├── check_environment.py
├── download_model.py
│
├── inspect_tokenizer.py
├── inspect_architecture.py
├── compare_with_minigpt.py
│
├── generate.py
├── interactive.py
│
├── baseline_prompts.json
├── baseline_eval.py
│
├── models/
│   └── .gitkeep
│
└── outputs/
    └── .gitkeep
```

Los modelos descargados y los resultados generados localmente no deben subirse al repositorio.

---

# 6. Preparar el entorno

Entra al directorio:

```bash
cd llm-lab/pretrained_llm_workbench
```

Si sigues usando tu entorno Conda:

```bash
conda activate llm-lab
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

El archivo instala:

```text
mlx-lm
huggingface-hub
transformers
safetensors
```

---

# 7. Verifica tu Mac antes de descargar nada

Ejecuta:

```bash
python check_environment.py
```

En un Mac Apple Silicon esperamos algo similar a:

```text
Python: 3.12.x
Platform: macOS-...
Machine: arm64

MLX imported successfully.
MLX default device: Device(gpu, 0)
MLX test result: [2.0, 4.0, 6.0]
```

La prueba:

```python
a = mx.array(
    [1.0, 2.0, 3.0]
)

b = a * 2
```

parece trivial, pero verifica que:

```text
Python
  ↓
MLX
  ↓
Apple Silicon
```

funciona antes de introducir un LLM.

---

# 8. Descargar el modelo

Ejecuta:

```bash
python download_model.py
```

El script utiliza Hugging Face Hub y coloca el modelo dentro de:

```text
models/
└── qwen3-0.6b-base-4bit/
```

Después de la descarga tendrás archivos parecidos a:

```text
config.json
generation_config.json
tokenizer.json
tokenizer_config.json
vocab.json
merges.txt
model.safetensors
...
```

Este punto es fundamental.

Cuando dices:

> "Descargué un LLM"

realmente descargaste **varios componentes diferentes**.

---

# 9. Anatomía de un modelo descargado

## `config.json`

Describe la arquitectura.

Ejemplo de información:

```text
hidden_size
num_hidden_layers
num_attention_heads
num_key_value_heads
intermediate_size
vocab_size
head_dim
rope_theta
quantization
```

No contiene el conocimiento aprendido en sí.

Describe **cómo reconstruir la red neuronal**.

---

## `model.safetensors`

Contiene los pesos aprendidos.

Conceptualmente:

```text
architecture
+
weights
=
trained neural network
```

Los archivos Safetensors almacenan tensores de forma diseñada para ser segura y eficiente.

Aquí vive una gran parte de aquello que normalmente llamamos:

> "los parámetros del modelo."

---

## `tokenizer.json`

Contiene la lógica y datos del tokenizer.

El tokenizer convierte:

```text
TEXT
 ↓
TOKEN IDs
```

y también:

```text
TOKEN IDs
 ↓
TEXT
```

Sin el tokenizer correcto, los pesos del modelo no tienen sentido práctico.

---

## `vocab.json` + `merges.txt`

Estos archivos forman parte de la definición del vocabulario/tokenización BPE.

Nuestro Mini-GPT anterior utilizaba:

```text
1 character = 1 token
```

Un tokenizer moderno utiliza unidades subword.

---

# 10. Inspeccionar el tokenizer

Ejecuta:

```bash
python inspect_tokenizer.py \
  --text "Artificial intelligence is changing how software is built."
```

El script muestra:

```text
Text:
...

Vocabulary size:
...

Characters:
...

Tokens:
...

Tokenization:

0 | id=... | token=... | decoded=...
1 | id=... | token=... | decoded=...
...
```

Esto permite observar una diferencia enorme respecto a nuestro tokenizer anterior.

Nuestro modelo educativo podría interpretar:

```text
intelligence
```

como aproximadamente:

```text
i
n
t
e
l
l
i
g
e
n
c
e
```

El tokenizer real puede representarlo con una o pocas unidades subword.

---

# 11. ¿Por qué importa el tokenizer?

El modelo no recibe directamente:

```text
Artificial intelligence is useful
```

Recibe algo conceptualmente parecido a:

```text
[29453, 11245, 374, 3492]
```

Luego:

```text
token IDs
    ↓
embedding lookup
    ↓
vectors
    ↓
Transformer
```

Esto conecta directamente con todo lo que construimos en `04_multihead_transformer`.

La gran diferencia es que ahora el vocabulario puede tener alrededor de:

```text
151,936 tokens
```

en lugar de unas pocas decenas de caracteres.

---

# 12. Inspeccionar la arquitectura

Ejecuta:

```bash
python inspect_architecture.py
```

El script lee directamente:

```text
models/.../config.json
```

y muestra cosas como:

```text
Vocabulary size
Hidden size
Intermediate size
Layers
Query heads
Key/value heads
Head dimension
Max position embeddings
Activation
RMSNorm epsilon
RoPE theta
Quantization
```

También imprime los tamaños reales de los archivos descargados.

Para inspeccionar tensores:

```bash
python inspect_architecture.py \
  --show-tensors \
  --tensor-limit 30
```

Verás nombres parecidos a:

```text
model.layers.0.self_attn.q_proj...
model.layers.0.self_attn.k_proj...
model.layers.0.self_attn.v_proj...
...
```

Aquí estás mirando directamente la estructura almacenada del modelo.

---

# 13. Del Mini-GPT al modelo real

Ejecuta:

```bash
python compare_with_minigpt.py
```

El programa compara automáticamente nuestro proyecto:

```text
04_multihead_transformer
```

contra Qwen.

Conceptualmente verás algo parecido a:

| Feature | Nuestro Mini-GPT | Qwen3-0.6B-Base |
|---|---:|---:|
| Tokenizer | character | BPE/subword |
| Hidden size | 96 | 1024 |
| Layers | 4 | 28 |
| Query heads | 4 | 16 |
| KV heads | 4 | 8 |
| Head dimension | 24 | 128 |
| FFN size | 384 | 3072 |
| Normalization | LayerNorm | RMSNorm |
| Position | learned embeddings | RoPE |
| Attention | MHA | GQA |

Esta comparación es una de las partes más importantes del laboratorio.

No estamos frente a una tecnología completamente diferente.

Seguimos reconociendo:

```text
tokens
  ↓
embeddings
  ↓
Transformer layers
  ↓
attention
  ↓
feed-forward networks
  ↓
normalization
  ↓
vocabulary logits
```

Lo que cambia es la escala y varias decisiones arquitectónicas.

---

# 14. MHA vs GQA

Nuestro Mini-GPT hizo:

```text
4 query heads
4 key heads
4 value heads
```

Cada query head tenía sus propios K y V correspondientes.

Qwen utiliza **Grouped Query Attention — GQA**.

En este modelo:

```text
Query heads = 16
KV heads    = 8
```

Por tanto varias query heads pueden compartir grupos de key/value heads.

Conceptualmente:

```text
Q1 ─┐
    ├── KV group 1
Q2 ─┘

Q3 ─┐
    ├── KV group 2
Q4 ─┘

...
```

Esto puede reducir memoria y costo de la KV cache durante inferencia.

---

# 15. Learned positional embeddings vs RoPE

Nuestro Mini-GPT utilizó:

```python
token_embedding
+
position_embedding
```

Es decir, aprendíamos un vector explícito para:

```text
position 0
position 1
position 2
...
```

Qwen utiliza **Rotary Position Embeddings — RoPE**.

En vez de sumar una tabla aprendida de posiciones de la misma manera que nuestro proyecto, RoPE introduce información posicional mediante transformaciones rotacionales dentro del mecanismo de atención.

No necesitas dominar RoPE todavía.

Lo importante es reconocer:

```text
OUR MODEL
learned position embeddings

REAL MODEL
RoPE
```

El problema que ambos intentan resolver es el mismo:

> El modelo necesita saber el orden y las relaciones posicionales entre tokens.

---

# 16. LayerNorm vs RMSNorm

Nuestro Mini-GPT utilizó:

```text
LayerNorm
```

Qwen utiliza:

```text
RMSNorm
```

Ambas técnicas buscan estabilizar las activaciones durante el paso por redes profundas, pero calculan la normalización de forma diferente.

Esto es un ejemplo perfecto de la diferencia entre:

```text
fundamental Transformer concept
vs
modern architectural variation
```

---

# 17. GELU vs SiLU

Nuestro Feed Forward utilizó:

```text
GELU
```

Qwen utiliza:

```text
SiLU
```

De nuevo:

```text
Attention
   ↓
Feed Forward
```

sigue existiendo.

Lo que cambia es la función no lineal y la estructura específica del FFN.

---

# 18. Ejecutar inferencia

Después de descargar el modelo:

```bash
python generate.py \
  --prompt "Artificial intelligence is"
```

Puedes controlar generación:

```bash
python generate.py \
  --prompt "A neural network learns by" \
  --max-tokens 200 \
  --temperature 0.7 \
  --top-p 0.95 \
  --top-k 20
```

El flujo interno es:

```text
prompt
  ↓
tokenizer
  ↓
token IDs
  ↓
pretrained Transformer
  ↓
logits
  ↓
sampler
  ↓
next token
  ↓
append
  ↓
repeat
```

Exactamente el mismo patrón conceptual que implementamos manualmente antes.

---

# 19. Temperature, top-p y top-k

## Temperature

Temperature modifica qué tan concentrada queda la distribución de sampling.

```text
temperature = 0
```

usa decoding greedy.

```text
temperature < 1
```

tiende a concentrar más la distribución.

```text
temperature > 1
```

tiende a aumentar aleatoriedad.

---

## Top-k

```text
top_k = 20
```

significa:

> Solo considera los 20 tokens con mayor score para el sampling.

---

## Top-p

Top-p, también llamado nucleus sampling, selecciona un conjunto de tokens cuya probabilidad acumulada alcanza aproximadamente el umbral indicado.

Por ejemplo:

```text
top_p = 0.95
```

No significa literalmente elegir el 95% de todos los tokens.

Significa trabajar con el subconjunto superior necesario para cubrir aproximadamente esa masa probabilística.

---

# 20. Modo interactivo

Ejecuta:

```bash
python interactive.py
```

Verás:

```text
Interactive continuation mode.
This is a BASE model, not an instruction-tuned assistant.

Prompt>
```

Prueba:

```text
Prompt> Machine learning models
```

Para salir:

```text
/exit
```

Este modo mantiene el modelo cargado una sola vez.

Eso es importante porque cargar cientos de megabytes de pesos en cada prompt sería innecesario.

---

# 21. Cargar vs generar

Cuando ejecutamos:

```python
model, tokenizer = load(
    MODEL_DIR
)
```

ocurre:

```text
disk
 ↓
weights
 ↓
model structure
 ↓
unified memory
```

Eso es diferente de:

```python
generate(...)
```

que ejecuta inference usando los pesos ya cargados.

Conceptualmente:

```text
LOAD MODEL
happens once
     ↓
PROMPT 1
PROMPT 2
PROMPT 3
...
```

Por eso `interactive.py` es más eficiente para experimentar repetidamente.

---

# 22. ¿Dónde entra la KV cache?

Durante generación autoregresiva:

```text
Artificial
```

produce otro token.

Luego tendríamos:

```text
Artificial intelligence
```

Sin cache, el modelo tendría que recalcular repetidamente todas las Keys y Values anteriores.

Una KV cache conserva resultados de atención ya calculados.

Conceptualmente:

```text
token 1
  ↓
K1 V1 ────────────────┐

token 2               │
  ↓                   │
K2 V2 ────────────────┤
                      │
token 3               │
  ↓                   │
Q3 compares with ◄────┘
cached K/V
```

Esto es una optimización fundamental para inferencia autoregresiva.

---

# 23. El experimento más importante: BASELINE

Antes de modificar los pesos necesitamos saber:

> ¿Cómo se comportaba el modelo original?

Tenemos:

```text
baseline_prompts.json
```

con prompts fijos.

Ejecuta:

```bash
python baseline_eval.py
```

El script usa:

```text
temperature = 0
greedy decoding
```

para obtener resultados reproducibles.

Genera:

```text
outputs/
└── baseline_results.json
```

Con estructura similar a:

```json
{
  "model_repo": "...",
  "decoding": "greedy",
  "results": [
    {
      "id": "gradient_descent",
      "prompt": "The purpose of gradient descent is",
      "response": "..."
    }
  ]
}
```

---

# 24. ¿Por qué guardamos el baseline?

Porque después vamos a entrenar el modelo.

Supongamos:

```text
BASE MODEL
accuracy / behavior A
```

Hacemos fine-tuning:

```text
BASE MODEL
   ↓
training dataset
   ↓
fine-tuning
   ↓
NEW MODEL
```

Luego ejecutamos exactamente los mismos prompts:

```text
baseline prompts
      ↓
fine-tuned model
```

Y comparamos:

```text
BEFORE
vs
AFTER
```

Sin baseline, es muy fácil caer en:

> "Me parece que ahora responde mejor."

Eso no es una evaluación rigurosa.

---

# 25. Pretraining vs Fine-Tuning

Este concepto conecta las dos grandes fases del curso.

## Nuestro Mini-GPT

Empezó con:

```text
random weights
```

y luego:

```text
random weights
      ↓
training corpus
      ↓
next-token loss
      ↓
backpropagation
      ↓
learned weights
```

Eso fue entrenamiento desde cero.

---

## Qwen descargado

Empieza así:

```text
already trained weights
```

Por tanto el futuro fine-tuning será:

```text
pretrained weights
       ↓
our smaller dataset
       ↓
new loss
       ↓
backpropagation
       ↓
modified weights
```

La diferencia fundamental es el punto inicial.

---

# 26. ¿Qué NO hacemos todavía?

En este workbench **no modificamos pesos**.

Todavía no hacemos:

```text
loss.backward()
optimizer.step()
```

Estamos haciendo:

```text
download
inspect
understand
inference
measure baseline
```

Eso es deliberado.

Antes de entrenar un modelo real debes saber exactamente:

- cuál modelo estás usando;
- qué tokenizer usa;
- cuál es su arquitectura;
- cómo se ejecuta;
- cuál es su comportamiento inicial;
- cómo medirás el cambio.

---

# 27. Orden recomendado de ejecución

Ejecuta exactamente en este orden:

```bash
python check_environment.py
```

Luego:

```bash
python download_model.py
```

Después:

```bash
python inspect_architecture.py
```

Luego:

```bash
python inspect_tokenizer.py \
  --text "Artificial intelligence is changing software."
```

Compara con nuestro Mini-GPT:

```bash
python compare_with_minigpt.py
```

Genera:

```bash
python generate.py \
  --prompt "Artificial intelligence is"
```

Prueba modo interactivo:

```bash
python interactive.py
```

Finalmente captura el baseline:

```bash
python baseline_eval.py
```

---

# 28. Qué debes observar durante la práctica

No te concentres todavía en si la respuesta es "buena".

Concéntrate en entender el sistema.

Pregúntate:

1. ¿Cuántos archivos necesita un modelo real?
2. ¿Cuál archivo define la arquitectura?
3. ¿Dónde están los pesos?
4. ¿Qué hace el tokenizer?
5. ¿Cuántos tokens produce mi prompt?
6. ¿Cuántas capas tiene el modelo?
7. ¿Por qué hay más query heads que KV heads?
8. ¿Qué significa cuantización 4-bit?
9. ¿Por qué el modelo base no siempre actúa como asistente?
10. ¿Qué diferencia hay entre cargar el modelo y generar?
11. ¿Qué hace la KV cache?
12. ¿Por qué guardamos un baseline?

---

# 29. Preguntas que debes poder responder al terminar

### Fundamentos

**1. ¿Qué diferencia hay entre `config.json` y `model.safetensors`?**

**2. ¿Por qué un tokenizer es parte esencial de un LLM?**

**3. ¿Por qué nuestro tokenizer de caracteres no escala tan bien como un tokenizer subword?**

**4. ¿Qué significa que el modelo sea causal?**

**5. ¿Qué significa que el modelo ya esté pretrained?**

---

### Arquitectura

**6. ¿Qué representa `hidden_size`?**

**7. ¿Qué representa `intermediate_size`?**

**8. ¿Por qué existen 28 Transformer layers?**

**9. ¿Cuál es la diferencia entre MHA y GQA?**

**10. ¿Cuál es la diferencia entre learned position embeddings y RoPE?**

**11. ¿Cuál es la diferencia entre LayerNorm y RMSNorm a nivel conceptual?**

---

### Inferencia

**12. ¿Qué ocurre desde que escribes un prompt hasta que aparece el primer token generado?**

**13. ¿Qué controla temperature?**

**14. ¿Qué controla top-k?**

**15. ¿Qué controla top-p?**

**16. ¿Qué hace una KV cache?**

---

### Entrenamiento

**17. ¿Por qué todavía no estamos haciendo fine-tuning?**

**18. ¿Qué pesos modificaríamos durante full fine-tuning?**

**19. ¿Por qué necesitamos guardar resultados antes del entrenamiento?**

**20. ¿Qué significa evaluar "before vs after"?**

Si puedes responder estas preguntas sin mirar el README, ya estás listo para entrenar un LLM preexistente.

---

# 30. Relación completa con nuestro curso

Ahora puedes conectar todo:

```text
OUR BIGRAM
   ↓
learn next character from one character

OUR CONTEXT MODEL
   ↓
use multiple previous characters

OUR SINGLE ATTENTION
   ↓
tokens learn where to look

OUR MULTIHEAD TRANSFORMER
   ↓
multiple heads
residuals
feed forward
stacked Transformer blocks

REAL PRETRAINED MODEL
   ↓
same broad Transformer family
but:
much larger
better tokenizer
modern normalization
RoPE
GQA
hundreds of millions of parameters
massive pretraining corpus
```

Eso es exactamente lo que queríamos lograr construyendo primero los modelos pequeños.

Cuando miras el modelo real, ya no debe parecer una caja negra.

---

# 31. Próxima fase

Una vez completes este workbench tendremos guardado:

```text
BASE MODEL
+
BASELINE RESULTS
```

El siguiente laboratorio debe empezar con:

```text
pretrained weights
       ↓
our dataset
       ↓
loss
       ↓
backpropagation
       ↓
optimizer
       ↓
modified model
```

Primero podremos estudiar **full fine-tuning** conceptualmente.

Después:

```text
LoRA
```

y luego:

```text
QLoRA
```

Así podremos comparar no solamente resultados, sino también:

```text
trainable parameters
memory
training time
checkpoint size
behavior before
behavior after
```

Ese es el punto donde pasamos de:

> "sé ejecutar un modelo"

a:

> **"entiendo cómo especializar un modelo existente."**


---

## Troubleshooting: No safetensors found

If MLX-LM reports:

```text
FileNotFoundError: No safetensors found in .../models/qwen3-0.6b-base-4bit
```

the model directory exists but the actual weight file was not downloaded completely.

The official MLX repository contains a large `model.safetensors` file, so first resume the download:

```bash
python download_model.py
```

Then verify:

```bash
ls -lh models/qwen3-0.6b-base-4bit/*.safetensors
```

If the file is still missing, force the download:

```bash
python download_model.py --force
```

The downloader now validates that at least one non-empty `.safetensors` weight file exists before reporting success.

The model weights are hosted through Hugging Face's large-file storage backend. Keep `huggingface_hub` current:

```bash
pip install -U huggingface_hub
```

Modern `huggingface_hub` versions install the Xet integration used for large model-file downloads.


---

## Troubleshooting: square brackets in the project path

If the model file exists but MLX-LM still reports:

```text
FileNotFoundError: No safetensors found in ...
```

check whether any parent directory contains square brackets, for example:

```text
curso [Sistemas Multiagentes e Inteligencia Artificial]
```

MLX-LM discovers local weight files using a glob pattern similar to:

```python
glob.glob(str(model_path / "model*.safetensors"))
```

In glob syntax, `[` and `]` have special meaning. Therefore an otherwise valid absolute path containing brackets can prevent the weight file from matching.

The course workbench handles this automatically by temporarily entering the model directory and loading it through the relative path:

```text
.
```

instead of passing the bracket-containing absolute path to MLX-LM.

The model does not need to be downloaded again when `model.safetensors` is already present.
