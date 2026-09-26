Vamos a crear la **Parte 3** así:

```text
llm-lab/
├── 01_bigram/
├── 02_context_window/
└── 03_attention/
    ├── training.txt
    ├── config.py
    ├── tokenizer.py
    ├── data.py
    ├── model.py
    ├── train.py
    ├── generate.py
    ├── inspect_attention.py
    ├── requirements.txt
    └── checkpoints/
```

Esta vez el modelo aprenderá:

```text
varios tokens
     ↓
embeddings
     ↓
Q, K, V
     ↓
causal self-attention
     ↓
representación contextual
     ↓
predicción del siguiente token
```

Y vamos a programar nosotros mismos la ecuación:

$$
Attention(Q,K,V)
=
softmax\left(\frac{QK^T}{\sqrt{d}}\right)V
$$

---

# 1. Crear el nuevo directorio

Desde `02_context_window`:

```bash
cd ..

mkdir -p 03_attention/checkpoints

cd 03_attention
```

Comprueba:

```bash
pwd
```

---

# 2. Dataset

Para mantener este proyecto independiente, copia el dataset:

```bash
cp ../02_context_window/training.txt .
```

Ahora:

```bash
ls
```

debería mostrar:

```text
checkpoints
training.txt
```

---

# 3. `requirements.txt`

```bash
touch requirements.txt
```

Contenido:

```text
torch
numpy
matplotlib
```

---

# 4. `config.py`

```bash
touch config.py
```

Contenido:

```python
from pathlib import Path

import torch


BASE_DIR = Path(__file__).resolve().parent

TRAINING_FILE = BASE_DIR / "training.txt"

CHECKPOINT_DIR = BASE_DIR / "checkpoints"

CHECKPOINT_FILE = (
    CHECKPOINT_DIR
    / "attention_model.pt"
)


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

DEVICE = (
    "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)


# --------------------------------------------------
# DATA
# --------------------------------------------------

TRAIN_SPLIT = 0.90

BLOCK_SIZE = 32

BATCH_SIZE = 32


# --------------------------------------------------
# MODEL
# --------------------------------------------------

N_EMBD = 64


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

LEARNING_RATE = 0.003

MAX_STEPS = 5000

EVAL_INTERVAL = 250

EVAL_BATCHES = 50

RANDOM_SEED = 42
```

Ahora aumentamos:

```text
BLOCK_SIZE = 32
```

El modelo podrá mirar hasta:

```text
32 caracteres hacia atrás
```

---

# 5. `tokenizer.py`

```bash
touch tokenizer.py
```

Contenido:

```python
from config import TRAINING_FILE


class CharacterTokenizer:

    def __init__(self):

        with open(
            TRAINING_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()


        self.characters = sorted(
            list(set(text))
        )


        self.vocab_size = len(
            self.characters
        )


        self.stoi = {

            character: index

            for index, character
            in enumerate(
                self.characters
            )
        }


        self.itos = {

            index: character

            for index, character
            in enumerate(
                self.characters
            )
        }


    def encode(self, text):

        return [

            self.stoi[
                character
            ]

            for character
            in text
        ]


    def decode(self, tokens):

        return "".join(

            self.itos[token]

            for token
            in tokens
        )
```

---

# 6. `data.py`

Aquí vamos a hacer algo diferente a la Parte 2.

Antes teníamos:

```text
32 caracteres
      ↓
1 target
```

Ahora tendremos:

```text
INPUT:

language model

TARGET:

anguage model...
```

Es decir, **cada posición hace una predicción**.

Crea:

```bash
touch data.py
```

Contenido:

```python
import torch

from config import (
    TRAINING_FILE,
    TRAIN_SPLIT,
    BLOCK_SIZE,
    BATCH_SIZE,
    DEVICE,
)

from tokenizer import CharacterTokenizer


tokenizer = CharacterTokenizer()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

with open(
    TRAINING_FILE,
    "r",
    encoding="utf-8"
) as file:

    text = file.read()


# --------------------------------------------------
# TOKENIZE
# --------------------------------------------------

data = torch.tensor(
    tokenizer.encode(text),
    dtype=torch.long
)


# --------------------------------------------------
# TRAIN / VALIDATION
# --------------------------------------------------

split_index = int(
    len(data)
    * TRAIN_SPLIT
)


train_data = (
    data[:split_index]
)

val_data = (
    data[split_index:]
)


# --------------------------------------------------
# BATCH
# --------------------------------------------------

def get_batch(split):

    source = (
        train_data
        if split == "train"
        else val_data
    )


    positions = torch.randint(

        0,

        len(source)
        - BLOCK_SIZE
        - 1,

        (BATCH_SIZE,)
    )


    x = torch.stack([

        source[
            position:
            position + BLOCK_SIZE
        ]

        for position
        in positions
    ])


    y = torch.stack([

        source[
            position + 1:
            position + BLOCK_SIZE + 1
        ]

        for position
        in positions
    ])


    return (
        x.to(DEVICE),
        y.to(DEVICE)
    )


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "Vocabulary size:",
        tokenizer.vocab_size
    )

    print(
        "Total tokens:",
        len(data)
    )

    print(
        "Training tokens:",
        len(train_data)
    )

    print(
        "Validation tokens:",
        len(val_data)
    )


    xb, yb = get_batch(
        "train"
    )


    print(
        "\nX shape:",
        xb.shape
    )

    print(
        "Y shape:",
        yb.shape
    )


    print(
        "\nExamples:\n"
    )


    for i in range(3):

        input_text = (
            tokenizer.decode(
                xb[i].tolist()
            )
        )

        target_text = (
            tokenizer.decode(
                yb[i].tolist()
            )
        )


        print(
            "INPUT :",
            repr(input_text)
        )

        print(
            "TARGET:",
            repr(target_text)
        )

        print()
```

Ejecuta:

```bash
python data.py
```

Debes obtener:

```text
X shape: torch.Size([32, 32])
Y shape: torch.Size([32, 32])
```

Ahora:

```text
B = 32
T = 32
```

---

# 7. Entiende el cambio

Imagina:

```text
x:

h e l l o
```

y:

```text
y:

e l l o _
```

Tenemos simultáneamente:

```text
h       → e
he      → l
hel     → l
hell    → o
hello   → space
```

Esto es muchísimo más parecido a cómo entrenamos un GPT.

Cada secuencia produce muchos ejemplos de entrenamiento.

---

# 8. Ahora viene Attention

Crea:

```bash
touch model.py
```

Empezaremos con una sola cabeza de atención.

Contenido:

```python
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from config import (
    BLOCK_SIZE,
    N_EMBD,
)


# ==================================================
# SINGLE HEAD SELF ATTENTION
# ==================================================

class SelfAttentionHead(nn.Module):

    def __init__(
        self,
        embedding_size
    ):

        super().__init__()


        # ------------------------------------------
        # Q
        # ------------------------------------------

        self.query = nn.Linear(
            embedding_size,
            embedding_size,
            bias=False
        )


        # ------------------------------------------
        # K
        # ------------------------------------------

        self.key = nn.Linear(
            embedding_size,
            embedding_size,
            bias=False
        )


        # ------------------------------------------
        # V
        # ------------------------------------------

        self.value = nn.Linear(
            embedding_size,
            embedding_size,
            bias=False
        )


        # ------------------------------------------
        # CAUSAL MASK
        # ------------------------------------------

        self.register_buffer(

            "mask",

            torch.tril(
                torch.ones(
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
            )
        )


    def forward(
        self,
        x,
        return_attention=False
    ):

        # x:
        #
        # (B, T, C)

        B, T, C = x.shape


        # ------------------------------------------
        # CREATE Q K V
        # ------------------------------------------

        q = self.query(x)

        k = self.key(x)

        v = self.value(x)


        # Each:
        #
        # (B, T, C)


        # ------------------------------------------
        # Q @ K^T
        # ------------------------------------------

        scores = (
            q
            @
            k.transpose(
                -2,
                -1
            )
        )


        # shape:
        #
        # (B, T, T)


        # ------------------------------------------
        # SCALE
        # ------------------------------------------

        scores = (
            scores
            /
            math.sqrt(C)
        )


        # ------------------------------------------
        # CAUSAL MASK
        # ------------------------------------------

        scores = scores.masked_fill(

            self.mask[
                :T,
                :T
            ] == 0,

            float("-inf")
        )


        # ------------------------------------------
        # SOFTMAX
        # ------------------------------------------

        attention_weights = (
            F.softmax(
                scores,
                dim=-1
            )
        )


        # ------------------------------------------
        # WEIGHTED VALUES
        # ------------------------------------------

        output = (
            attention_weights
            @
            v
        )


        # output:
        #
        # (B, T, C)


        if return_attention:

            return (
                output,
                attention_weights
            )


        return output


# ==================================================
# LANGUAGE MODEL
# ==================================================

class AttentionLanguageModel(
    nn.Module
):

    def __init__(
        self,
        vocab_size
    ):

        super().__init__()


        # ------------------------------------------
        # TOKEN EMBEDDINGS
        # ------------------------------------------

        self.token_embedding = (
            nn.Embedding(
                vocab_size,
                N_EMBD
            )
        )


        # ------------------------------------------
        # POSITION EMBEDDINGS
        # ------------------------------------------

        self.position_embedding = (
            nn.Embedding(
                BLOCK_SIZE,
                N_EMBD
            )
        )


        # ------------------------------------------
        # SELF ATTENTION
        # ------------------------------------------

        self.attention = (
            SelfAttentionHead(
                N_EMBD
            )
        )


        # ------------------------------------------
        # NORMALIZATION
        # ------------------------------------------

        self.layer_norm = (
            nn.LayerNorm(
                N_EMBD
            )
        )


        # ------------------------------------------
        # OUTPUT
        # ------------------------------------------

        self.language_model_head = (
            nn.Linear(
                N_EMBD,
                vocab_size
            )
        )


    def forward(
        self,
        idx,
        targets=None,
        return_attention=False
    ):

        B, T = idx.shape


        if T > BLOCK_SIZE:

            raise ValueError(
                "Sequence is longer "
                "than BLOCK_SIZE"
            )


        # ------------------------------------------
        # TOKEN EMBEDDINGS
        # ------------------------------------------

        token_embeddings = (
            self.token_embedding(
                idx
            )
        )


        # ------------------------------------------
        # POSITIONS
        # ------------------------------------------

        positions = torch.arange(
            T,
            device=idx.device
        )


        position_embeddings = (
            self.position_embedding(
                positions
            )
        )


        # ------------------------------------------
        # COMBINE
        # ------------------------------------------

        x = (
            token_embeddings
            +
            position_embeddings
        )


        # x:
        #
        # (B, T, C)


        # ------------------------------------------
        # ATTENTION
        # ------------------------------------------

        if return_attention:

            attention_output, weights = (
                self.attention(
                    x,
                    return_attention=True
                )
            )

        else:

            attention_output = (
                self.attention(x)
            )

            weights = None


        # ------------------------------------------
        # RESIDUAL CONNECTION
        # ------------------------------------------

        x = (
            x
            +
            attention_output
        )


        # ------------------------------------------
        # NORMALIZE
        # ------------------------------------------

        x = (
            self.layer_norm(x)
        )


        # ------------------------------------------
        # VOCABULARY LOGITS
        # ------------------------------------------

        logits = (
            self.language_model_head(
                x
            )
        )


        # logits:
        #
        # (B, T, vocab_size)


        loss = None


        if targets is not None:

            B, T, C = (
                logits.shape
            )


            logits_flat = (
                logits.reshape(
                    B * T,
                    C
                )
            )


            targets_flat = (
                targets.reshape(
                    B * T
                )
            )


            loss = (
                F.cross_entropy(
                    logits_flat,
                    targets_flat
                )
            )


        if return_attention:

            return (
                logits,
                loss,
                weights
            )


        return (
            logits,
            loss
        )
```

---

# 9. Ahora sí: Q, K y V

Esta parte:

```python
q = self.query(x)
k = self.key(x)
v = self.value(x)
```

realmente significa:

$$
Q = XW_Q
$$

$$
K = XW_K
$$

$$
V = XW_V
$$

Tenemos tres matrices de pesos entrenables:

```text
Wq
Wk
Wv
```

El modelo aprende esos pesos mediante:

```text
backpropagation
```

---

# 10. ¿Qué significa Query?

Puedes imaginar cada token preguntando:

```text
¿Qué información necesito?
```

Eso es:

```text
Query
```

El `Key` representa aproximadamente:

```text
¿Qué información tengo?
```

Y el `Value`:

```text
¿Cuál es la información que entregaré
si resulto relevante?
```

Visualmente:

```text
             TOKEN
               │
        ┌──────┼──────┐
        ↓      ↓      ↓

        Q      K      V

     pregunta  clave  información
```

---

# 11. Q × Kᵀ

Esta línea:

```python
scores = q @ k.transpose(-2, -1)
```

produce:

```text
(B,T,T)
```

Con:

```text
B = 32
T = 32
```

tenemos:

```text
(32,32,32)
```

Cada token está comparándose contra cada otro token.

Conceptualmente:

```text
             Tokens disponibles
           1    2    3    4    5

token 1   [ .    .    .    .    . ]
token 2   [ .    .    .    .    . ]
token 3   [ .    .    .    .    . ]
token 4   [ .    .    .    .    . ]
token 5   [ .    .    .    .    . ]
```

Es una matriz de:

```text
attention scores
```

---

# 12. ¿Por qué dividimos por √C?

Esta parte:

```python
scores = scores / math.sqrt(C)
```

implementa:

$$
\frac{QK^T}{\sqrt{d_k}}
$$

Sin esta escala, cuando la dimensión de embeddings crece, los productos internos pueden hacerse demasiado grandes.

Entonces Softmax podría convertirse en algo extremadamente agresivo:

```text
[0.0000001, 0.9999998, 0.0000001]
```

y producir gradients poco útiles.

La división estabiliza el entrenamiento.

---

# 13. Causal Mask

Esta parte es crítica:

```python
torch.tril(...)
```

produce algo como:

```text
1 0 0 0 0
1 1 0 0 0
1 1 1 0 0
1 1 1 1 0
1 1 1 1 1
```

Eso significa:

```text
token 1 puede mirar token 1

token 2 puede mirar
token 1 y 2

token 3 puede mirar
token 1, 2 y 3
```

Pero token 2 **NO puede ver token 5**.

¿Por qué?

Porque durante entrenamiento sería hacer trampa.

Si queremos predecir:

```text
hello
    ↓
?
```

no podemos enseñarle el futuro.

Esto convierte nuestro attention en:

# Causal Self-Attention

que es el tipo utilizado por modelos GPT.

---

# 14. Softmax

Después:

```python
attention_weights = F.softmax(
    scores,
    dim=-1
)
```

convertimos los scores en probabilidades.

Por ejemplo:

```text
Token actual:

"l"
```

podría asignar:

```text
token 1   5%
token 2  10%
token 3  60%
token 4  25%
```

La suma:

```text
100%
```

---

# 15. Weighted Values

Finalmente:

```python
output = attention_weights @ v
```

Es decir:

```text
información final
=
5% del value 1
+
10% del value 2
+
60% del value 3
+
25% del value 4
```

Aquí ocurre la magia de Attention:

```text
cada token construye
una nueva representación
usando información de
otros tokens relevantes.
```

---

# 16. `train.py`

Crea:

```bash
touch train.py
```

Contenido:

```python
import random

import numpy as np

import torch

import matplotlib.pyplot as plt


from config import (
    DEVICE,
    RANDOM_SEED,
    LEARNING_RATE,
    MAX_STEPS,
    EVAL_INTERVAL,
    EVAL_BATCHES,
    CHECKPOINT_DIR,
    CHECKPOINT_FILE,
)


from tokenizer import (
    CharacterTokenizer
)

from data import (
    get_batch
)

from model import (
    AttentionLanguageModel
)


# --------------------------------------------------
# REPRODUCIBILITY
# --------------------------------------------------

random.seed(
    RANDOM_SEED
)

np.random.seed(
    RANDOM_SEED
)

torch.manual_seed(
    RANDOM_SEED
)


# --------------------------------------------------
# TOKENIZER
# --------------------------------------------------

tokenizer = (
    CharacterTokenizer()
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = (
    AttentionLanguageModel(
        tokenizer.vocab_size
    )
)

model = model.to(
    DEVICE
)


print(
    "Device:",
    DEVICE
)

print(
    "Vocabulary size:",
    tokenizer.vocab_size
)


parameter_count = sum(

    parameter.numel()

    for parameter
    in model.parameters()
)


print(
    "Parameters:",
    f"{parameter_count:,}"
)


# --------------------------------------------------
# OPTIMIZER
# --------------------------------------------------

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE
)


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

@torch.no_grad()
def estimate_loss():

    model.eval()

    results = {}


    for split in [
        "train",
        "val"
    ]:

        losses = []


        for _ in range(
            EVAL_BATCHES
        ):

            xb, yb = get_batch(
                split
            )


            _, loss = model(
                xb,
                yb
            )


            losses.append(
                loss.item()
            )


        results[split] = (

            sum(losses)
            /
            len(losses)
        )


    model.train()

    return results


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

steps_history = []

train_history = []

validation_history = []


# --------------------------------------------------
# TRAIN
# --------------------------------------------------

print(
    "\nTraining...\n"
)


for step in range(
    MAX_STEPS + 1
):


    if (
        step % EVAL_INTERVAL == 0
        or
        step == MAX_STEPS
    ):

        losses = (
            estimate_loss()
        )


        print(
            f"Step {step:5d} | "
            f"Train {losses['train']:.4f} | "
            f"Validation {losses['val']:.4f}"
        )


        steps_history.append(
            step
        )

        train_history.append(
            losses["train"]
        )

        validation_history.append(
            losses["val"]
        )


    xb, yb = get_batch(
        "train"
    )


    logits, loss = model(
        xb,
        yb
    )


    optimizer.zero_grad(
        set_to_none=True
    )


    loss.backward()


    optimizer.step()


# --------------------------------------------------
# SAVE
# --------------------------------------------------

CHECKPOINT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


torch.save(

    {

        "model_state_dict":
            model.state_dict(),

        "vocab_size":
            tokenizer.vocab_size,

        "characters":
            tokenizer.characters,

    },

    CHECKPOINT_FILE
)


print(
    "\nSaved:",
    CHECKPOINT_FILE
)


# --------------------------------------------------
# GRAPH
# --------------------------------------------------

plt.figure()

plt.plot(
    steps_history,
    train_history,
    label="Training"
)

plt.plot(
    steps_history,
    validation_history,
    label="Validation"
)

plt.xlabel(
    "Training Step"
)

plt.ylabel(
    "Loss"
)

plt.title(
    "Single-Head Self-Attention"
)

plt.legend()

plt.show()
```

Ejecuta:

```bash
python train.py
```

---

# 17. `generate.py`

```bash
touch generate.py
```

Contenido:

```python
import torch

import torch.nn.functional as F


from config import (
    DEVICE,
    BLOCK_SIZE,
    CHECKPOINT_FILE,
)


from tokenizer import (
    CharacterTokenizer
)


from model import (
    AttentionLanguageModel
)


# --------------------------------------------------
# TOKENIZER
# --------------------------------------------------

tokenizer = (
    CharacterTokenizer()
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = (
    AttentionLanguageModel(
        tokenizer.vocab_size
    )
)


checkpoint = torch.load(
    CHECKPOINT_FILE,
    map_location=DEVICE
)


model.load_state_dict(
    checkpoint[
        "model_state_dict"
    ]
)


model = model.to(
    DEVICE
)

model.eval()


# --------------------------------------------------
# GENERATE
# --------------------------------------------------

@torch.no_grad()
def generate(
    prompt,
    max_new_tokens=300,
    temperature=0.8
):


    generated = (
        tokenizer.encode(
            prompt
        )
    )


    for _ in range(
        max_new_tokens
    ):


        context = (
            generated[
                -BLOCK_SIZE:
            ]
        )


        x = torch.tensor(
            [context],
            dtype=torch.long,
            device=DEVICE
        )


        logits, _ = (
            model(x)
        )


        # Only prediction
        # from final position

        logits = (
            logits[
                0,
                -1,
                :
            ]
        )


        logits = (
            logits
            /
            temperature
        )


        probabilities = (
            F.softmax(
                logits,
                dim=-1
            )
        )


        next_token = (
            torch.multinomial(
                probabilities,
                num_samples=1
            )
            .item()
        )


        generated.append(
            next_token
        )


    return tokenizer.decode(
        generated
    )


# --------------------------------------------------
# RUN
# --------------------------------------------------

prompt = (
    "artificial intelligence"
)


result = generate(
    prompt,
    max_new_tokens=300,
    temperature=0.7
)


print(
    "\nGenerated text:\n"
)

print(result)
```

Ejecuta:

```bash
python generate.py
```

---

# 18. Pero quiero que literalmente veamos Attention

Vamos a crear una herramienta especial para eso.

```bash
touch inspect_attention.py
```

Contenido:

```python
import torch


from config import (
    DEVICE,
    CHECKPOINT_FILE,
)


from tokenizer import (
    CharacterTokenizer
)


from model import (
    AttentionLanguageModel
)


# --------------------------------------------------
# LOAD
# --------------------------------------------------

tokenizer = (
    CharacterTokenizer()
)


model = (
    AttentionLanguageModel(
        tokenizer.vocab_size
    )
)


checkpoint = torch.load(
    CHECKPOINT_FILE,
    map_location=DEVICE
)


model.load_state_dict(
    checkpoint[
        "model_state_dict"
    ]
)


model = model.to(
    DEVICE
)

model.eval()


# --------------------------------------------------
# TEXT
# --------------------------------------------------

text = (
    "language model"
)


tokens = (
    tokenizer.encode(
        text
    )
)


x = torch.tensor(
    [tokens],
    dtype=torch.long,
    device=DEVICE
)


# --------------------------------------------------
# ATTENTION
# --------------------------------------------------

with torch.no_grad():

    logits, loss, attention = (
        model(
            x,
            return_attention=True
        )
    )


attention = (
    attention[0]
    .cpu()
)


# --------------------------------------------------
# PRINT MATRIX
# --------------------------------------------------

print(
    "\nText:",
    repr(text)
)

print(
    "\nAttention Matrix:\n"
)


print(
    "     ",
    end=""
)


for character in text:

    print(
        f"{character!r:>7}",
        end=""
    )


print()


for row_index, character in enumerate(
    text
):

    print(
        f"{character!r:>5}",
        end=""
    )


    for column_index in range(
        len(text)
    ):

        value = (
            attention[
                row_index,
                column_index
            ]
            .item()
        )


        print(
            f"{value:7.2f}",
            end=""
        )


    print()
```

Ejecuta:

```bash
python inspect_attention.py
```

Y deberías obtener algo parecido a:

```text
          'l'   'a'   'n'   'g'   'u' ...

'l'      1.00  0.00  0.00  0.00  0.00

'a'      0.42  0.58  0.00  0.00  0.00

'n'      0.20  0.31  0.49  0.00  0.00

'g'      0.11  0.18  0.35  0.36  0.00
```

Observa el triángulo superior:

```text
0
```

porque esos son:

```text
future tokens
```

y nuestro modelo no puede verlos.

---

# 19. Lo que acabamos de construir

Ahora nuestra evolución es:

```text
01_BIGRAM

token
 ↓
next token
```

Luego:

```text
02_CONTEXT_WINDOW

todos los embeddings
 ↓
flatten
 ↓
MLP
 ↓
next token
```

Y ahora:

```text
03_ATTENTION

tokens
 ↓
embeddings
 ↓
Q K V
 ↓
QKᵀ / √d
 ↓
causal mask
 ↓
softmax
 ↓
Attention @ V
 ↓
prediction
```

Esto ya contiene el **mecanismo central de un Transformer**.

Todavía nos faltan varias piezas.

---

# Lo siguiente será `04_multihead_transformer`

Ahí vamos a crear otro directorio completamente independiente:

```text
04_multihead_transformer/
```

Y sustituiremos:

```text
1 Self-Attention Head
```

por:

```text
           input
             │
   ┌─────────┼─────────┐
   ↓         ↓         ↓
 Head 1    Head 2    Head 3    Head 4
   │         │         │         │
   └─────────┼─────────┼─────────┘
             ↓
         concatenate
             ↓
          projection
```

Además añadiremos:

```text
LayerNorm
Residual connections
Feed Forward Network
Dropout
Transformer Block
Multiple Transformer Blocks
```

Y en ese punto ya tendremos un **Mini-GPT real construido por nosotros desde cero**.

Primero ejecuta en este orden:

```bash
python data.py
python train.py
python generate.py
python inspect_attention.py
```

Lo más interesante de esta parte no es todavía qué tan bonito sea el texto generado: es mirar `inspect_attention.py` y entender que acabas de construir una red neuronal que **aprende automáticamente cuánto debe mirar cada token anterior**.
