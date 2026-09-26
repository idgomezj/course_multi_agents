# 04 — Multi-Head Transformer: nuestro primer Mini-GPT

Esta parte del curso transforma el modelo de una sola cabeza de `03_attention` en una arquitectura mucho más cercana a un GPT real.

El objetivo **no** es crear un modelo competitivo. El objetivo es entender, con código suficientemente pequeño para leerlo completo, cómo se conectan las piezas fundamentales de un Transformer causal:

```text
texto
  ↓
character tokenizer
  ↓
token ids
  ↓
token embeddings + position embeddings
  ↓
┌──────────────────────────────────┐
│ Transformer Block 1              │
│                                  │
│ LayerNorm                        │
│    ↓                             │
│ Multi-Head Causal Self-Attention │
│    ↓                             │
│ Residual connection              │
│    ↓                             │
│ LayerNorm                        │
│    ↓                             │
│ Feed-Forward Network             │
│    ↓                             │
│ Residual connection              │
└──────────────────────────────────┘
  ↓
Transformer Block 2
  ↓
Transformer Block 3
  ↓
Transformer Block 4
  ↓
final LayerNorm
  ↓
linear vocabulary head
  ↓
logits
  ↓
cross-entropy loss durante training
  ↓
probabilidades + sampling durante generation
```

Al terminar esta lección debes poder explicar **por qué existen Multi-Head Attention, residual connections, LayerNorm, Feed-Forward Networks y múltiples Transformer blocks**.

---

## 1. De dónde venimos

El curso hasta aquí avanza deliberadamente por capas:

| Parte | Modelo | Qué aprende |
|---|---|---|
| `01_bigram` | Bigram LM | `P(next token \| current token)` |
| `02_context_window` | Context MLP | usa varios tokens, pero aplana todo el contexto |
| `03_attention` | Single-head attention | cada token puede seleccionar información de tokens anteriores |
| **`04_multihead_transformer`** | **Mini-GPT** | varias cabezas + FFN + residuals + varios bloques |

La Parte 3 ya implementó la idea central:

$$
Attention(Q,K,V)
=
softmax\left(
\frac{QK^T}{\sqrt{d_k}}
\right)V
$$

Pero solo teníamos **una cabeza de atención** y una transformación relativamente simple después de ella.

Ahora construiremos un Transformer completo.

---

## 2. Estructura del directorio

```text
04_multihead_transformer/
├── README.md
├── config.py
├── tokenizer.py
├── data.py
├── model.py
├── train.py
├── generate.py
├── inspect_heads.py
├── training.txt
├── requirements.txt
└── checkpoints/
    └── .gitkeep
```

### `config.py`

Centraliza todos los hiperparámetros.

Los más importantes son:

```python
BLOCK_SIZE = 64
BATCH_SIZE = 32

N_EMBD = 96
N_HEADS = 4
N_LAYERS = 4

DROPOUT = 0.10
FF_MULTIPLIER = 4
```

Esto significa:

- cada secuencia contiene hasta **64 caracteres**;
- entrenamos **32 secuencias simultáneamente**;
- cada token se representa con **96 números**;
- cada Transformer block tiene **4 attention heads**;
- el modelo apila **4 Transformer blocks**;
- el feed-forward expande temporalmente de 96 a `4 × 96 = 384` dimensiones.

Como:

```text
96 / 4 = 24
```

cada attention head trabaja con un subespacio de **24 dimensiones**.

---

## 3. Shapes que debes dominar

En Transformers vas a ver estas letras constantemente:

- `B` = batch size
- `T` = sequence length / time
- `C` = embedding channels
- `H` = number of attention heads
- `V` = vocabulary size

Con la configuración actual:

```text
B = 32
T = 64
C = 96
H = 4
head_size = 24
```

El batch empieza con:

```text
token ids
(B, T)
=
(32, 64)
```

Después del embedding:

```text
(B, T, C)
=
(32, 64, 96)
```

Dentro de cada head:

```text
Q = (32, 64, 24)
K = (32, 64, 24)
V = (32, 64, 24)
```

El producto:

$$
QK^T
$$

produce:

```text
(B, T, T)
=
(32, 64, 64)
```

Es decir: para cada ejemplo del batch, cada posición compara su Query con las Keys de las demás posiciones visibles.

---

## 4. Token embeddings y position embeddings

En `MiniGPT.forward()` empezamos con:

```python
x = (
    self.token_embedding(idx)
    +
    self.position_embedding(positions)
)
```

El **token embedding** responde aproximadamente:

> ¿Qué token soy?

El **position embedding** añade:

> ¿En qué posición de la secuencia estoy?

Así, la letra `a` en posición 2 y la letra `a` en posición 30 comparten identidad de token, pero reciben distinta información posicional.

Shape:

```text
token_embedding(idx)
    (B, T, C)

position_embedding(positions)
    (T, C)

PyTorch broadcast
    ↓

x
    (B, T, C)
```

---

## 5. Una sola Attention Head

La clase `CausalSelfAttentionHead` crea tres proyecciones aprendibles:

```python
self.query = nn.Linear(N_EMBD, head_size, bias=False)
self.key   = nn.Linear(N_EMBD, head_size, bias=False)
self.value = nn.Linear(N_EMBD, head_size, bias=False)
```

Matemáticamente:

$$
Q=XW_Q
$$

$$
K=XW_K
$$

$$
V=XW_V
$$

Una interpretación útil —no literal— es:

- **Query:** ¿qué información está buscando este token?
- **Key:** ¿qué tipo de información ofrece este token?
- **Value:** ¿qué información entregaré si soy relevante?

Después:

```python
scores = q @ k.transpose(-2, -1)
scores = scores / math.sqrt(self.head_size)
```

Eso mide compatibilidad Query-Key.

---

## 6. Por qué existe el causal mask

Un language model que predice el próximo token no puede mirar el futuro durante entrenamiento.

Para una secuencia:

```text
a b c d
```

la máscara conceptual es:

```text
      a  b  c  d

a     ✓  ✗  ✗  ✗
b     ✓  ✓  ✗  ✗
c     ✓  ✓  ✓  ✗
d     ✓  ✓  ✓  ✓
```

Por eso `model.py` crea:

```python
torch.tril(
    torch.ones(
        BLOCK_SIZE,
        BLOCK_SIZE,
        dtype=torch.bool
    )
)
```

y coloca `-inf` en posiciones futuras antes del softmax.

Después del softmax esas posiciones reciben probabilidad prácticamente 0.

Esto es **causal self-attention**.

---

## 7. ¿Qué cambia con Multi-Head Attention?

En `03_attention` teníamos una única función de atención.

Ahora tenemos:

```text
                     X
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
    Head 1        Head 2        Head 3        Head 4
      24d           24d           24d           24d
       │             │             │             │
       └─────────────┴──────┬──────┴─────────────┘
                            ▼
                       concatenate
                            │
                            ▼
                         96 dims
                            │
                            ▼
                        projection
```

Código:

```python
self.heads = nn.ModuleList([
    CausalSelfAttentionHead(
        self.head_size
    )
    for _ in range(N_HEADS)
])
```

Cada head tiene sus propios:

```text
WQ
WK
WV
```

Por tanto, cada head puede aprender una manera distinta de buscar relaciones.

No programamos:

> Head 1 aprende palabras.
> Head 2 aprende sintaxis.

El entrenamiento decide qué representaciones resultan útiles.

---

## 8. Concatenación

Cada head produce:

```text
(B, T, 24)
```

Con cuatro heads:

```python
combined = torch.cat(
    head_outputs,
    dim=-1
)
```

obtenemos:

```text
(B, T, 96)
```

De esta forma regresamos a `N_EMBD` y podemos pasar el resultado al resto del Transformer block.

Después usamos:

```python
self.projection = nn.Linear(
    N_EMBD,
    N_EMBD
)
```

Esta proyección permite mezclar la información producida por las distintas cabezas.

---

## 9. Residual connections

El Transformer no reemplaza completamente la representación anterior.

Hace:

```python
x = x + attention_output
```

y más adelante:

```python
x = x + feed_forward_output
```

Visualmente:

```text
x ────────────────────────┐
│                         │
▼                         │
Attention                 │
│                         │
▼                         │
output                     │
│                         │
└──────────── + ◄─────────┘
              │
              ▼
            new x
```

La conexión residual crea una ruta directa para conservar información y ayuda al flujo de gradients cuando apilamos muchas capas.

Esta idea es crucial en redes profundas.

---

## 10. LayerNorm

La arquitectura usa **Pre-LayerNorm**:

```python
normalized = self.layer_norm_attention(x)

attention_output = self.attention(
    normalized
)

x = x + attention_output
```

En forma compacta:

$$
x \leftarrow x + Attention(LN(x))
$$

Después:

$$
x \leftarrow x + FFN(LN(x))
$$

LayerNorm normaliza características dentro de cada representación de token y ayuda a mantener el entrenamiento estable.

---

## 11. Feed-Forward Network

Attention permite que los tokens intercambien información.

Pero después queremos procesar la nueva representación de **cada token individualmente**.

La clase `FeedForward` hace:

```text
96
 ↓
Linear
 ↓
384
 ↓
GELU
 ↓
Linear
 ↓
96
 ↓
Dropout
```

Código:

```python
nn.Linear(
    N_EMBD,
    FF_MULTIPLIER * N_EMBD
)

nn.GELU()

nn.Linear(
    FF_MULTIPLIER * N_EMBD,
    N_EMBD
)
```

Una forma útil de pensar el bloque es:

> **Attention = comunicación entre tokens.**

> **Feed Forward = procesamiento interno de cada token.**

---

## 12. Un Transformer Block completo

Nuestro bloque ejecuta:

```text
                 x
                 │
                 ▼
             LayerNorm
                 │
                 ▼
      Multi-Head Attention
                 │
         ┌───────┘
         ▼
     x + attention
         │
         ▼
      LayerNorm
         │
         ▼
     Feed Forward
         │
         ▼
    x + feed_forward
         │
         ▼
       output
```

En código conceptual:

```python
x = x + attention(
    layer_norm_1(x)
)

x = x + feed_forward(
    layer_norm_2(x)
)
```

---

## 13. ¿Por qué cuatro Transformer blocks?

Un solo bloque puede construir una representación contextual.

Pero al apilar:

```text
Block 1
  ↓
Block 2
  ↓
Block 3
  ↓
Block 4
```

cada capa recibe representaciones ya procesadas por las anteriores.

En `MiniGPT`:

```python
self.blocks = nn.ModuleList([
    TransformerBlock()
    for _ in range(N_LAYERS)
])
```

y:

```python
for block in self.blocks:
    x = block(x)
```

Los LLM grandes hacen conceptualmente lo mismo, aunque con muchas más capas, dimensiones, optimizaciones y variaciones arquitectónicas.

---

## 14. Vocabulary head y logits

Al terminar los bloques:

```python
x = self.final_layer_norm(x)

logits = self.language_model_head(x)
```

Shape:

```text
(B, T, C)
    ↓ Linear(C, V)
(B, T, V)
```

Para **cada posición** obtenemos un score para **cada token del vocabulario**.

Esos scores son los **logits**.

Durante training no necesitamos aplicar manualmente softmax porque `F.cross_entropy` trabaja directamente con logits.

---

## 15. Targets y next-token prediction

`data.py` construye:

```text
INPUT:
language mode

TARGET:
anguage model
```

Por tanto el modelo aprende simultáneamente:

```text
l           → a
la          → n
lan         → g
lang        → u
...
language mod → e
```

Cada batch tiene shape:

```text
X = (B, T)
Y = (B, T)
```

y la loss compara todas las posiciones.

---

## 16. Cross-entropy

Para entrenar convertimos:

```text
logits:
(B, T, V)

targets:
(B, T)
```

en:

```text
logits:
(B*T, V)

targets:
(B*T)
```

y calculamos:

```python
F.cross_entropy(
    logits,
    targets
)
```

Intuitivamente, para cada posición queremos aumentar la probabilidad del token correcto.

Si el modelo asigna alta probabilidad al target, la loss disminuye.

---

## 17. Backpropagation

`train.py` contiene el ciclo esencial:

```python
_, loss = model(
    xb,
    yb
)

optimizer.zero_grad(
    set_to_none=True
)

loss.backward()

torch.nn.utils.clip_grad_norm_(
    model.parameters(),
    max_norm=GRAD_CLIP
)

optimizer.step()
```

El proceso es:

```text
forward pass
    ↓
logits
    ↓
loss
    ↓
backpropagation
    ↓
gradients para WQ, WK, WV,
embeddings, FFN, projections...
    ↓
AdamW
    ↓
nuevos pesos
```

Aquí es donde **las attention heads aprenden**.

No les decimos manualmente dónde mirar.

Los gradients modifican sus matrices `WQ`, `WK` y `WV` para reducir la next-token loss.

---

## 18. Gradient clipping

Añadimos:

```python
torch.nn.utils.clip_grad_norm_(
    model.parameters(),
    max_norm=1.0
)
```

Si el gradient global se vuelve excesivamente grande, lo limitamos.

Esto ayuda a evitar updates inestables.

---

## 19. Training vs validation

El corpus se divide:

```text
90% training
10% validation
```

Training modifica pesos.

Validation **nunca ejecuta backward**.

Queremos observar:

```text
train loss ↓
validation loss ↓
```

Si ocurre:

```text
train loss ↓↓↓
validation loss ↑
```

el modelo probablemente está haciendo overfitting.

Este dataset es deliberadamente diminuto, así que el overfitting es muy posible y es parte del experimento.

---

## 20. Cómo ejecutar la lección

Desde:

```bash
cd llm-lab/04_multihead_transformer
```

Instala dependencias si las necesitas:

```bash
pip install -r requirements.txt
```

### Paso 1 — inspeccionar los batches

```bash
python data.py
```

Debes ver shapes parecidos a:

```text
X shape: torch.Size([32, 64])
Y shape: torch.Size([32, 64])
```

### Paso 2 — entrenar

```bash
python train.py
```

En tu Apple Silicon queremos ver:

```text
Device: mps
```

El script imprime periódicamente:

```text
Step     0 | Train ... | Validation ...
Step   250 | Train ... | Validation ...
...
```

Al finalizar crea:

```text
checkpoints/mini_gpt.pt
training_loss.png
```

### Paso 3 — generar texto

```bash
python generate.py
```

También puedes experimentar:

```bash
python generate.py \
  --prompt "language model" \
  --tokens 400 \
  --temperature 0.7 \
  --top-k 10
```

### Paso 4 — mirar las attention heads

```bash
python inspect_heads.py
```

Por defecto inspecciona el primer Transformer block.

Puedes cambiar de capa:

```bash
python inspect_heads.py \
  --text "language model" \
  --layer 3
```

`--layer` usa índices desde 0:

```text
0 = block 1
1 = block 2
2 = block 3
3 = block 4
```

---

## 21. Qué muestra `inspect_heads.py`

Para una secuencia de longitud `T`, una capa devuelve:

```text
(H, T, T)
```

Con cuatro heads y el texto `language model`:

```text
(4, 14, 14)
```

Cada matriz responde:

> Para este token, ¿cuánto peso asignó esta head a cada token anterior visible?

El script también imprime la conexión con mayor atención para cada posición.

No interpretes automáticamente una attention weight como una explicación causal perfecta del modelo. Aquí la usamos como herramienta pedagógica para observar el mecanismo interno que construimos.

---

## 22. Temperature durante generación

Después del modelo tomamos los logits de la última posición:

```python
logits = logits[
    0,
    -1,
    :
]
```

y podemos modificar:

```python
logits = logits / temperature
```

En términos prácticos:

| Temperature | Comportamiento |
|---:|---|
| `0` | greedy: siempre el logit máximo |
| `0.5` | más conservador |
| `0.8` | balance razonable |
| `1.0` | distribución original |
| `>1` | más aleatorio |

`top-k` restringe el sampling a los `k` candidatos con logits más altos.

---

## 23. ¿Dónde está el conocimiento?

Después de training, el conocimiento no está guardado como reglas de texto.

Está distribuido entre parámetros como:

```text
token embeddings
position embeddings

Block 1
  Head 1 WQ/WK/WV
  Head 2 WQ/WK/WV
  Head 3 WQ/WK/WV
  Head 4 WQ/WK/WV
  projection
  FFN
  LayerNorm

Block 2
...

Block 4
...

final LayerNorm
vocabulary head
```

`loss.backward()` calcula cómo cada parámetro contribuyó al error.

`optimizer.step()` modifica todos esos parámetros.

Ese es el mecanismo de aprendizaje.

---

## 24. Checkpoint

Después de entrenar:

```text
checkpoints/mini_gpt.pt
```

guarda:

- `model_state_dict`;
- vocabulario;
- número de parámetros;
- configuración principal de arquitectura.

`generate.py` e `inspect_heads.py` exigen ese archivo.

Si no existe, verás un error explícito indicándote que primero debes ejecutar:

```bash
python train.py
```

---

## 25. Diferencia entre este modelo y un GPT grande

Nuestro Mini-GPT ya tiene los conceptos esenciales de un decoder-only Transformer, pero sigue siendo un laboratorio.

### Nuestro modelo

- tokenizer por caracteres;
- dataset de pocos miles de caracteres;
- context window 64;
- embedding 96;
- 4 heads;
- 4 layers;
- cientos de miles de parámetros;
- entrenamiento en un Mac.

### Un LLM moderno

Puede usar:

- tokenizer BPE/SentencePiece;
- datasets de cantidades enormes de tokens;
- contextos de miles o cientos de miles de tokens;
- embeddings de miles de dimensiones;
- decenas o cientos de capas;
- miles de millones de parámetros;
- entrenamiento distribuido entre muchas GPUs/accelerators;
- optimizaciones adicionales de atención, precisión y memoria.

Pero el camino conceptual sigue siendo reconocible:

```text
tokens
  ↓
embeddings
  ↓
many Transformer blocks
  ↓
logits
  ↓
next-token prediction
```

---

## 26. Experimentos recomendados

No cambies todo simultáneamente. Modifica **una variable cada vez** y compara train/validation loss.

### Experimento A — número de heads

Manteniendo `N_EMBD = 96`:

```python
N_HEADS = 1
N_HEADS = 2
N_HEADS = 4
N_HEADS = 8
```

Recuerda:

`N_EMBD` debe ser divisible por `N_HEADS`.

Pregunta:

> ¿Más heads siempre mejora validation loss?

No asumas que sí. Mídelo.

### Experimento B — profundidad

Prueba:

```python
N_LAYERS = 1
N_LAYERS = 2
N_LAYERS = 4
N_LAYERS = 6
```

Observa parámetros, velocidad y overfitting.

### Experimento C — contexto

```python
BLOCK_SIZE = 16
BLOCK_SIZE = 32
BLOCK_SIZE = 64
```

Pregunta:

> ¿El dataset tiene suficiente información para aprovechar un contexto mayor?

### Experimento D — dropout

```python
DROPOUT = 0.0
DROPOUT = 0.1
DROPOUT = 0.2
```

Compara especialmente validation loss.

---

## 27. Preguntas que debes poder responder

Antes de avanzar, intenta responder sin mirar el código:

1. ¿Qué diferencia existe entre Query, Key y Value?
2. ¿Por qué necesitamos un causal mask?
3. ¿Por qué dividimos `QK^T` por `sqrt(head_size)`?
4. ¿Qué gana el modelo usando varias attention heads?
5. Si `N_EMBD=96` y `N_HEADS=4`, ¿cuál es `head_size`?
6. ¿Por qué concatenamos las heads?
7. ¿Para qué sirve la projection después de concatenarlas?
8. ¿Qué diferencia conceptual hay entre Attention y Feed Forward?
9. ¿Por qué existen residual connections?
10. ¿Por qué usamos LayerNorm?
11. ¿Cuál es el shape de los logits?
12. ¿Por qué entrenamos con targets desplazados un token?
13. ¿Qué parámetros cambia `loss.backward()` + `optimizer.step()`?
14. ¿Qué significa que train loss baje mientras validation loss sube?
15. ¿Por qué el checkpoint permite generar sin volver a entrenar?

Si puedes explicar estas preguntas con tus propias palabras, ya entiendes el núcleo de un Transformer decoder pequeño.

---

## 28. Flujo completo

```text
training.txt
     │
     ▼
CharacterTokenizer
     │
     ▼
token ids
     │
     ▼
get_batch()
     │
     ├───────────────┐
     ▼               ▼
   input           target
  (B,T)            (B,T)
     │
     ▼
token + position embeddings
     │
     ▼
   (B,T,C)
     │
     ▼
Transformer Block × 4
     │
     ├─ LayerNorm
     ├─ Multi-Head Causal Attention
     ├─ Residual
     ├─ LayerNorm
     ├─ Feed Forward
     └─ Residual
     │
     ▼
final LayerNorm
     │
     ▼
vocabulary head
     │
     ▼
logits (B,T,V)
     │
     ▼
Cross Entropy
     │
     ▼
loss
     │
     ▼
backpropagation
     │
     ▼
gradients
     │
     ▼
AdamW
     │
     ▼
updated weights
```

Durante generation el camino cambia al final:

```text
logits for last position
       ↓
temperature / top-k
       ↓
softmax
       ↓
sample next token
       ↓
append token
       ↓
run model again
```

---

## 29. Qué sigue

Después de esta parte ya tendremos construido un **Mini-GPT desde cero**.

La siguiente fase del curso puede separarse en dos caminos:

1. mejorar el modelo desde cero con un tokenizer subword y mejores datasets/evaluaciones;
2. descargar un LLM pequeño ya preentrenado y aprender **fine-tuning, LoRA y QLoRA**.

Ese segundo camino permitirá comparar claramente:

```text
pretraining from random weights
            vs
fine-tuning pretrained weights
```

Esa comparación es una de las ideas más importantes para entender cómo se entrenan los LLM modernos.
