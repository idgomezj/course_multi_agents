Vamos a separarlo así:

```text
llm-lab/
├── 01_bigram/                 # Parte 1 — ya terminada
│   ├── bigram.py
│   ├── training.txt
│   └── bigram_model.pt
│
└── 02_context_window/         # Parte 2 — nueva
    ├── training.txt
    ├── config.py
    ├── tokenizer.py
    ├── data.py
    ├── model.py
    ├── train.py
    ├── generate.py
    ├── requirements.txt
    └── checkpoints/
```

La idea ahora cambia de:

```text
BIGRAM

1 carácter
   ↓
modelo
   ↓
siguiente carácter
```

a:

```text
CONTEXT MODEL

16 caracteres anteriores
        ↓
Token Embeddings
        +
Position Embeddings
        ↓
Neural Network
        ↓
siguiente carácter
```

Todavía **no Attention**. Primero quiero que veas qué significa realmente darle contexto al modelo.

---

# 1. Crear la nueva carpeta

Desde tu carpeta actual `01_bigram`:

```bash
cd ..
mkdir -p 02_context_window/checkpoints
cd 02_context_window
```

Comprueba:

```bash
pwd
```

Deberías estar en algo terminado en:

```text
llm-lab/02_context_window
```

---

# 2. `requirements.txt`

Crea:

```bash
touch requirements.txt
```

Contenido:

```text
torch
numpy
matplotlib
```

Como probablemente ya lo tienes instalado en `llm-lab`, no necesitas reinstalarlo.

---

# 3. `training.txt`

Crea:

```bash
touch training.txt
```

Pon este contenido inicialmente:

```text
artificial intelligence learns patterns from data.
language models predict the next token in a sequence.
machine learning uses data to adjust model parameters.
neural networks contain layers of mathematical operations.
training changes the weights of a neural network.
gradient descent attempts to reduce the loss function.
a language model receives tokens and predicts probabilities.
tokens are numerical representations of pieces of text.
embeddings convert tokens into vectors of numbers.
vectors allow neural networks to represent information.
a model begins training with mostly random parameters.
the optimizer changes parameters using calculated gradients.
backpropagation calculates gradients through the network.
cross entropy measures prediction error in classification.
a lower training loss usually means better predictions.
validation data helps measure generalization.
a model can memorize training data and still perform poorly.
overfitting happens when training improves but validation worsens.
a context window determines how much previous text is visible.
larger context allows a model to use more previous information.
position embeddings describe where tokens occur in a sequence.
token embeddings represent the identity of each token.
attention allows tokens to exchange information with other tokens.
transformers use attention to process sequences efficiently.
multi head attention creates several attention representations.
queries keys and values are central parts of self attention.
a transformer contains multiple mathematical processing blocks.
language model training requires many examples.
large language models contain millions or billions of parameters.
small models are useful for understanding machine learning.
python is frequently used for machine learning experiments.
pytorch provides automatic differentiation.
automatic differentiation calculates gradients automatically.
apple silicon can accelerate pytorch using metal.
the mps device allows pytorch to use apple graphics hardware.
the cpu can also execute neural network operations.
training consists of many repeated optimization steps.
each optimization step attempts to reduce prediction error.
the learning rate controls the size of parameter updates.
a learning rate that is too large can make training unstable.
a learning rate that is too small can make training very slow.
batching allows multiple examples to be processed together.
a batch contains several training examples.
the batch size controls how many examples are processed together.
the sequence length controls the number of tokens in a context.
a character tokenizer treats individual characters as tokens.
modern language models usually use subword tokenization.
a vocabulary contains all tokens understood by a tokenizer.
each vocabulary token is assigned an integer identifier.
neural networks operate on numbers rather than raw text.
text must therefore be converted into numerical representations.
the model output before softmax is called logits.
softmax converts logits into probabilities.
probabilities describe possible next tokens.
sampling selects one token from a probability distribution.
temperature can modify the randomness of token sampling.
model checkpoints store learned parameters.
a checkpoint can be loaded without training again.
training and inference are different phases.
training modifies model parameters.
inference uses existing parameters to generate predictions.
machine learning experiments should be reproducible.
random seeds can help make experiments reproducible.
evaluation compares model predictions with expected results.
model quality should be measured rather than guessed.
a good experiment separates training and validation data.
language models learn statistical relationships between tokens.
a bigram model only observes one previous token.
a context model observes several previous tokens.
context makes more complex predictions possible.
attention will later provide a better way to process context.
transformers scale context processing more effectively.
learning how small models work helps explain large models.
```

Esto sigue siendo diminuto comparado con un dataset real, pero es suficiente para nuestro laboratorio.

---

# 4. `config.py`

Ahora vamos a centralizar la configuración.

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

CHECKPOINT_FILE = CHECKPOINT_DIR / "context_model.pt"


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

DEVICE = (
    "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

BLOCK_SIZE = 16

N_EMBD = 32

HIDDEN_SIZE = 128


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

BATCH_SIZE = 32

LEARNING_RATE = 0.003

MAX_STEPS = 5000

EVAL_INTERVAL = 250

EVAL_BATCHES = 50

TRAIN_SPLIT = 0.90

RANDOM_SEED = 42
```

Aquí aparecerán conceptos que utilizaremos constantemente.

```text
BLOCK_SIZE = 16
```

significa:

> El modelo podrá observar los 16 caracteres anteriores.

Mientras que:

```text
N_EMBD = 32
```

significa:

> Cada carácter será representado mediante un vector de 32 números.

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
        ) as f:
            text = f.read()

        self.characters = sorted(
            list(set(text))
        )

        self.vocab_size = len(
            self.characters
        )

        self.stoi = {
            character: index
            for index, character
            in enumerate(self.characters)
        }

        self.itos = {
            index: character
            for index, character
            in enumerate(self.characters)
        }


    def encode(self, text):

        return [
            self.stoi[c]
            for c in text
        ]


    def decode(self, tokens):

        return "".join(
            self.itos[token]
            for token in tokens
        )
```

Ahora nuestro tokenizer está separado del modelo.

Eso empieza a parecer una arquitectura de proyecto real:

```text
TEXT
 ↓
tokenizer.py
 ↓
TOKEN IDs
```

---

# 6. `data.py`

Aquí vamos a introducir el **context window** y los batches.

```bash
touch data.py
```

Contenido:

```python
import torch

from config import (
    TRAINING_FILE,
    BLOCK_SIZE,
    BATCH_SIZE,
    TRAIN_SPLIT,
    DEVICE,
)

from tokenizer import CharacterTokenizer


tokenizer = CharacterTokenizer()


# --------------------------------------------------
# LOAD TEXT
# --------------------------------------------------

with open(
    TRAINING_FILE,
    "r",
    encoding="utf-8"
) as f:

    text = f.read()


# --------------------------------------------------
# ENCODE TEXT
# --------------------------------------------------

data = torch.tensor(
    tokenizer.encode(text),
    dtype=torch.long
)


# --------------------------------------------------
# TRAIN / VALIDATION SPLIT
# --------------------------------------------------

split_index = int(
    len(data) * TRAIN_SPLIT
)

train_data = data[:split_index]

val_data = data[split_index:]


# --------------------------------------------------
# CREATE BATCH
# --------------------------------------------------

def get_batch(split):

    source = (
        train_data
        if split == "train"
        else val_data
    )

    max_start = (
        len(source)
        - BLOCK_SIZE
        - 1
    )

    positions = torch.randint(
        0,
        max_start,
        (BATCH_SIZE,)
    )

    x = torch.stack([
        source[
            position:
            position + BLOCK_SIZE
        ]

        for position in positions
    ])


    y = torch.stack([
        source[
            position + BLOCK_SIZE
        ]

        for position in positions
    ])


    return (
        x.to(DEVICE),
        y.to(DEVICE)
    )
```

Hay una diferencia importantísima respecto a nuestro Bigram.

Antes:

```text
x = "a"
y = "r"
```

Ahora podemos tener:

```text
x = "artificial intel"
y = "l"
```

Es decir:

```text
16 tokens
    ↓
modelo
    ↓
1 target
```

---

# 7. Comprobemos el dataset antes de construir el modelo

Temporalmente añade al final de `data.py`:

```python
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


    xb, yb = get_batch("train")


    print(
        "\nX shape:",
        xb.shape
    )

    print(
        "Y shape:",
        yb.shape
    )


    print(
        "\nFirst batch examples:\n"
    )


    for i in range(5):

        context = tokenizer.decode(
            xb[i].tolist()
        )

        target = tokenizer.decode(
            [yb[i].item()]
        )

        print(
            repr(context),
            "->",
            repr(target)
        )
```

Ejecuta:

```bash
python data.py
```

Deberías obtener algo parecido a:

```text
Vocabulary size: 30
Total tokens: 5000
Training tokens: 4500
Validation tokens: 500

X shape: torch.Size([32, 16])
Y shape: torch.Size([32])
```

Y luego:

```text
'neural networks ' -> 'c'
'model parameter' -> 's'
'artificial intel' -> 'l'
...
```

Aquí quiero que observes:

```text
X = [32, 16]

32 = BATCH
16 = CONTEXT
```

En notación Transformer:

```text
(B, T)

B = Batch
T = Time / Sequence Length
```

---

# 8. `model.py`

Ahora vamos a construir el nuevo modelo.

```bash
touch model.py
```

Contenido:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

from config import (
    BLOCK_SIZE,
    N_EMBD,
    HIDDEN_SIZE,
)


class ContextLanguageModel(nn.Module):

    def __init__(
        self,
        vocab_size
    ):

        super().__init__()


        # --------------------------------------------------
        # TOKEN EMBEDDINGS
        # --------------------------------------------------

        self.token_embedding = nn.Embedding(
            vocab_size,
            N_EMBD
        )


        # --------------------------------------------------
        # POSITION EMBEDDINGS
        # --------------------------------------------------

        self.position_embedding = nn.Embedding(
            BLOCK_SIZE,
            N_EMBD
        )


        # --------------------------------------------------
        # SIMPLE NEURAL NETWORK
        # --------------------------------------------------

        input_size = (
            BLOCK_SIZE * N_EMBD
        )


        self.network = nn.Sequential(

            nn.Linear(
                input_size,
                HIDDEN_SIZE
            ),

            nn.ReLU(),

            nn.Linear(
                HIDDEN_SIZE,
                vocab_size
            )
        )


    def forward(
        self,
        idx,
        targets=None
    ):

        B, T = idx.shape


        if T != BLOCK_SIZE:

            raise ValueError(
                f"Expected context length "
                f"{BLOCK_SIZE}, got {T}"
            )


        # ----------------------------------------------
        # TOKEN EMBEDDINGS
        # ----------------------------------------------

        token_embeddings = (
            self.token_embedding(idx)
        )


        # Shape:
        #
        # (B, T, C)


        # ----------------------------------------------
        # POSITION EMBEDDINGS
        # ----------------------------------------------

        positions = torch.arange(
            T,
            device=idx.device
        )


        position_embeddings = (
            self.position_embedding(
                positions
            )
        )


        # ----------------------------------------------
        # COMBINE
        # ----------------------------------------------

        x = (
            token_embeddings
            +
            position_embeddings
        )


        # x shape:
        #
        # (B, T, C)


        # ----------------------------------------------
        # FLATTEN CONTEXT
        # ----------------------------------------------

        x = x.reshape(
            B,
            T * N_EMBD
        )


        # ----------------------------------------------
        # PREDICT NEXT TOKEN
        # ----------------------------------------------

        logits = self.network(x)


        loss = None


        if targets is not None:

            loss = F.cross_entropy(
                logits,
                targets
            )


        return logits, loss
```

Este es nuestro primer modelo que realmente utiliza:

```text
varios tokens
+
sus posiciones
```

---

# 9. ¿Qué son Token Embeddings?

Esto:

```python
self.token_embedding = nn.Embedding(
    vocab_size,
    32
)
```

significa que cada carácter deja de representarse solamente como:

```text
a = 3
```

Ahora:

```text
a
↓
[
  0.123,
 -0.832,
  0.227,
  ...
  0.391
]
```

32 números.

Conceptualmente:

```text
TOKEN ID
   ↓
Embedding Table
   ↓
VECTOR
```

---

# 10. Position Embeddings

Ahora tenemos otro problema.

Observa:

```text
cat
```

y:

```text
tac
```

Contienen:

```text
c
a
t
```

pero el orden cambia.

Por eso añadimos:

```text
Position 0
Position 1
Position 2
...
Position 15
```

Cada posición también tiene un vector.

Entonces hacemos:

```text
Token embedding
       +

Position embedding

       ↓

Representation
```

Por ejemplo:

```text
token "a"
en posición 2
```

obtiene:

```text
Embedding("a")
      +
Embedding(position=2)
```

---

# 11. Shapes: extremadamente importante

Supongamos:

```text
BATCH_SIZE = 32
BLOCK_SIZE = 16
N_EMBD = 32
```

Los tokens empiezan:

```text
(B,T)

(32,16)
```

Después del embedding:

```text
(B,T,C)

(32,16,32)
```

donde:

```text
B = Batch
T = Time
C = Channels / Embedding Dimension
```

Después hacemos:

```python
x.reshape(
    B,
    T * N_EMBD
)
```

Entonces:

```text
32 × 16 × 32
```

se transforma en:

```text
32 × 512
```

porque:

```text
16 × 32 = 512
```

Cada ejemplo ahora representa todo su contexto mediante:

```text
512 números
```

---

# 12. `train.py`

Ahora el entrenamiento completo.

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

from tokenizer import CharacterTokenizer

from data import get_batch

from model import ContextLanguageModel


# --------------------------------------------------
# RANDOM SEEDS
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

tokenizer = CharacterTokenizer()


print(
    "Device:",
    DEVICE
)

print(
    "Vocabulary size:",
    tokenizer.vocab_size
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = ContextLanguageModel(
    tokenizer.vocab_size
)

model = model.to(
    DEVICE
)


# --------------------------------------------------
# PARAMETERS
# --------------------------------------------------

number_parameters = sum(
    parameter.numel()
    for parameter
    in model.parameters()
)


print(
    "Number of parameters:",
    f"{number_parameters:,}"
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
            / len(losses)
        )


    model.train()

    return results


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

training_history = []

validation_history = []

steps_history = []


print(
    "\nStarting training...\n"
)


for step in range(
    MAX_STEPS + 1
):


    # ----------------------------------------------
    # EVALUATE
    # ----------------------------------------------

    if (
        step % EVAL_INTERVAL == 0
        or
        step == MAX_STEPS
    ):

        losses = estimate_loss()


        train_loss = (
            losses["train"]
        )

        val_loss = (
            losses["val"]
        )


        print(
            f"Step {step:5d} | "
            f"Train {train_loss:.4f} | "
            f"Validation {val_loss:.4f}"
        )


        steps_history.append(
            step
        )

        training_history.append(
            train_loss
        )

        validation_history.append(
            val_loss
        )


    # ----------------------------------------------
    # GET BATCH
    # ----------------------------------------------

    xb, yb = get_batch(
        "train"
    )


    # ----------------------------------------------
    # FORWARD
    # ----------------------------------------------

    logits, loss = model(
        xb,
        yb
    )


    # ----------------------------------------------
    # BACKPROPAGATION
    # ----------------------------------------------

    optimizer.zero_grad(
        set_to_none=True
    )

    loss.backward()


    # ----------------------------------------------
    # UPDATE PARAMETERS
    # ----------------------------------------------

    optimizer.step()


# --------------------------------------------------
# SAVE MODEL
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
    "\nCheckpoint saved:"
)

print(
    CHECKPOINT_FILE
)


# --------------------------------------------------
# TRAINING GRAPH
# --------------------------------------------------

plt.figure()

plt.plot(
    steps_history,
    training_history,
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
    "Context Language Model"
)

plt.legend()

plt.show()
```

Ejecuta:

```bash
python train.py
```

---

# 13. Mira cuántos parámetros tiene ahora

Nuestro Bigram tenía aproximadamente:

```text
~1,000 parámetros
```

Este probablemente tendrá:

```text
~70,000 parámetros
```

dependiendo del vocabulario.

Pero sigue siendo diminuto.

Puedes pensar:

```text
Bigram
~1K

Context model
~70K

Mini Transformer
~1M

Qwen small
~600M

Large LLM
billions
```

Estamos creciendo gradualmente.

---

# 14. `generate.py`

Ahora vamos a utilizar el modelo entrenado sin volver a entrenarlo.

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

from tokenizer import CharacterTokenizer

from model import ContextLanguageModel


# --------------------------------------------------
# TOKENIZER
# --------------------------------------------------

tokenizer = CharacterTokenizer()


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = ContextLanguageModel(
    tokenizer.vocab_size
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
# GENERATION
# --------------------------------------------------

@torch.no_grad()
def generate(
    prompt,
    max_new_tokens=300,
    temperature=1.0
):

    generated = tokenizer.encode(
        prompt
    )


    space_token = (
        tokenizer.stoi[" "]
    )


    for _ in range(
        max_new_tokens
    ):


        # ------------------------------------------
        # KEEP LAST BLOCK_SIZE TOKENS
        # ------------------------------------------

        context = generated[
            -BLOCK_SIZE:
        ]


        # ------------------------------------------
        # LEFT PAD IF CONTEXT IS TOO SHORT
        # ------------------------------------------

        if (
            len(context)
            < BLOCK_SIZE
        ):

            missing = (
                BLOCK_SIZE
                - len(context)
            )

            context = (
                [space_token] * missing
                +
                context
            )


        x = torch.tensor(
            [context],
            dtype=torch.long,
            device=DEVICE
        )


        # ------------------------------------------
        # MODEL PREDICTION
        # ------------------------------------------

        logits, _ = model(x)


        logits = (
            logits[0]
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
    "artificial intel"
)


text = generate(
    prompt,
    max_new_tokens=300,
    temperature=0.8
)


print(
    "\nGenerated text:\n"
)

print(text)
```

Ejecuta:

```bash
python generate.py
```

---

# 15. Ahora tenemos dos modelos muy diferentes

### Parte 1

```text
01_bigram

"a"
 ↓
model
 ↓
next character
```

Matemáticamente aprende:

```text
P(next | current)
```

### Parte 2

```text
02_context_window

"artificial intel"
        ↓
       model
        ↓
       "l"
```

Ahora aprende aproximadamente:

```text
P(
    next_token
    |
    token₁,
    token₂,
    token₃,
    ...
    token₁₆
)
```

Eso ya es un salto enorme.

---

# Pero nuestro nuevo modelo tiene un problema

Mira esto:

```python
x = x.reshape(
    B,
    T * N_EMBD
)
```

Estamos agarrando:

```text
Token 1 vector
Token 2 vector
Token 3 vector
...
Token 16 vector
```

y pegándolos:

```text
[vector1 | vector2 | vector3 | ...]
```

Funciona para aprender.

Pero es bastante bruto.

Si aumentamos:

```text
BLOCK_SIZE

16
 ↓
128
 ↓
1024
 ↓
100,000
```

la red crecería de manera absurda.

Además, todavía no existe una forma elegante para que:

```text
token 3
```

pregunte:

> ¿Qué información relevante existe en token 1, 2, 4, 5...?

Eso nos lleva exactamente al siguiente capítulo:

```text
03_attention/
```

Ahí vamos a sustituir esta parte:

```text
flatten entire context
       ↓
MLP
```

por:

```text
tokens
  ↓
Query
Key
Value
  ↓
QKᵀ
  ↓
Attention weights
  ↓
weighted Values
```

Y no voy a empezar usando:

```python
nn.MultiheadAttention(...)
```

Vamos a programar nosotros mismos:

```python
Q = X @ Wq
K = X @ Wk
V = X @ Wv

scores = Q @ K.transpose(-2, -1)

scores = scores / sqrt(head_size)

weights = softmax(scores)

output = weights @ V
```

Ese será el momento donde nuestro proyecto empiece realmente a convertirse en un **Transformer**.

Por ahora ejecuta primero:

```bash
python data.py
```

y después:

```bash
python train.py
```

Lo más importante que quiero ver de tu ejecución es algo similar a:

```text
Device:
Vocabulary size:
Number of parameters:

Step     0 | Train ... | Validation ...
Step   250 | Train ... | Validation ...
...
Step  5000 | Train ... | Validation ...
```

y después el resultado de:

```bash
python generate.py
```

Con eso pasamos a `03_attention`, también en su propia carpeta, y ahí sí construiremos **Self-Attention desde la matemática**.
