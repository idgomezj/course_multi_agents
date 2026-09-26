Para el primer proyecto usaremos **PyTorch + MPS**, así los cálculos irán a la GPU del M4 mediante Metal. PyTorch soporta entrenamiento en Apple Silicon usando el dispositivo `mps`. ([PyTorch Docs][1]) Más adelante, para entrenar modelos reales descargados, usaremos **MLX-LM**, que actualmente soporta LoRA, QLoRA, DoRA y full fine-tuning en Apple Silicon. ([GitHub][2])

## Primera práctica: crear nuestro primer modelo de lenguaje desde cero

Como ya tienes Conda, no crearía otro `venv`. Mantengamos todo separado de `(base)`.

```bash
conda create -n llm-lab python=3.12 -y
conda activate llm-lab
```

Comprueba:

```bash
python --version
which python
```

Después:

```bash
pip install torch numpy matplotlib jupyter
```

Crea nuestro proyecto:

```bash
mkdir -p ~/llm_lab/01_bigram
cd ~/llm_lab/01_bigram
```

Antes de construir nada, quiero verificar que realmente estamos usando el GPU del M4.

Crea:

```bash
touch check_gpu.py
```

Pon:

```python
import torch

print("PyTorch version:", torch.__version__)
print("MPS built:", torch.backends.mps.is_built())
print("MPS available:", torch.backends.mps.is_available())

if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

print("Selected device:", device)

x = torch.rand(3, 3, device=device)

print("\nTensor:")
print(x)

print("\nTensor device:")
print(x.device)
```

Ejecuta:

```bash
python check_gpu.py
```

Lo que queremos ver es:

```text
MPS built: True
MPS available: True
Selected device: mps
```

Si aparece eso, ya tenemos nuestra pequeña máquina de entrenamiento funcionando.

---

# Ahora sí: ¿qué vamos a construir?

Nuestro primer LLM todavía **no tendrá Transformer**.

Primero construiremos esto:

```text
           texto
             ↓
         tokenizer
             ↓
           tokens
             ↓
       neural network
             ↓
           logits
             ↓
         probabilities
             ↓
     predicted next token
```

Usaremos caracteres como tokens.

Por ejemplo:

```text
juan estudia inteligencia artificial
```

se convierte en algo similar a:

```text
i → 0
v → 1
a → 2
n → 3
  → 4
e → 5
...
```

Entonces:

```text
juan
```

se convierte en:

```python
[0, 1, 2, 3]
```

Esto nos permitirá comprender tokenización antes de utilizar tokenizers modernos.

---

# Paso 1 — Dataset

Crea:

```bash
touch training.txt
```

Para la primera prueba puedes colocar algo como esto, repetido varias veces:

```text
juan studies artificial intelligence.
juan learns how language models work.
a language model predicts the next token.
machine learning models learn from examples.
neural networks contain parameters.
training modifies the parameters of a neural network.
gradient descent reduces the training loss.
a language model receives tokens as input.
the model predicts probabilities for the next token.
artificial intelligence uses mathematical models.
```

No importa que inicialmente sea pequeño.

Más adelante utilizaremos un dataset mucho mayor.

---

# Paso 2 — nuestro tokenizer

Crea:

```bash
touch bigram.py
```

Vamos poco a poco.

Primero:

```python
import torch


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

device = "mps" if torch.backends.mps.is_available() else "cpu"

print("Device:", device)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

with open("training.txt", "r", encoding="utf-8") as f:
    text = f.read()


print("Number of characters:", len(text))
print("\nFirst characters:")
print(text[:200])


# --------------------------------------------------
# TOKENIZER
# --------------------------------------------------

characters = sorted(list(set(text)))

vocab_size = len(characters)

print("\nVocabulary:")
print(characters)

print("\nVocabulary size:", vocab_size)


# Character -> integer
stoi = {
    character: index
    for index, character in enumerate(characters)
}


# Integer -> character
itos = {
    index: character
    for index, character in enumerate(characters)
}


def encode(string):
    return [stoi[c] for c in string]


def decode(tokens):
    return "".join(itos[token] for token in tokens)


example = "juan"

encoded = encode(example)

print("\nOriginal:")
print(example)

print("\nEncoded:")
print(encoded)

print("\nDecoded:")
print(decode(encoded))
```

Ejecuta:

```bash
python bigram.py
```

Probablemente verás algo parecido a:

```text
Original:
juan

Encoded:
[10, 21, 2, 14]

Decoded:
juan
```

Los números pueden ser diferentes.

Eso no importa.

Acabas de construir tu primer tokenizer.

---

# ¿Qué acabamos de hacer?

El modelo neuronal **no entiende letras**.

No puede recibir:

```text
juan
```

Necesita números:

```text
[10, 21, 2, 14]
```

Por eso prácticamente todo LLM empieza por:

```text
TEXT
 ↓
TOKENIZER
 ↓
TOKEN IDs
```

Más adelante Qwen puede hacer algo equivalente a:

```text
"artificial intelligence"
        ↓
[1234, 8172, ...]
```

La diferencia es que utilizará subwords/tokens en vez de nuestro sencillo tokenizer por caracteres.

---

# Paso 3 — convertir todo el dataset a Tensor

Añade debajo de tu código:

```python
data = torch.tensor(
    encode(text),
    dtype=torch.long
)

print("\nTensor:")
print(data[:50])

print("\nTensor shape:")
print(data.shape)
```

Supongamos que obtienes:

```text
torch.Size([970])
```

Significa:

```text
970 tokens
```

Ahora tenemos:

```text
training.txt
      ↓
characters
      ↓
tokenizer
      ↓
integers
      ↓
PyTorch Tensor
```

El dataset ya puede entrar en una red neuronal.

---

# Paso 4 — ¿qué queremos que aprenda?

Supongamos que tenemos:

```text
juan
```

Queremos producir:

```text
INPUT             TARGET

i                  v
v                  a
a                  n
```

Es decir:

```python
x = [i, v, a]

y = [v, a, n]
```

Porque estamos diciendo:

> dado el token actual, predice el siguiente.

Añade:

```python
x = data[:-1]
y = data[1:]

print("\nFirst training examples:")

for t in range(10):
    input_token = x[t].item()
    target_token = y[t].item()

    print(
        repr(itos[input_token]),
        "->",
        repr(itos[target_token])
    )
```

Podrías obtener:

```text
'i' -> 'v'
'v' -> 'a'
'a' -> 'n'
'n' -> ' '
' ' -> 's'
's' -> 't'
```

Aquí ya tenemos el problema de Machine Learning perfectamente definido.

---

# Paso 5 — crear una red neuronal

Ahora llegamos al primer modelo.

Añade:

```python
import torch.nn as nn
import torch.nn.functional as F
```

Y:

```python
class BigramLanguageModel(nn.Module):

    def __init__(self, vocab_size):
        super().__init__()

        self.token_embedding_table = nn.Embedding(
            vocab_size,
            vocab_size
        )

    def forward(self, idx, targets=None):

        logits = self.token_embedding_table(idx)

        loss = None

        if targets is not None:

            loss = F.cross_entropy(
                logits,
                targets
            )

        return logits, loss
```

Luego:

```python
model = BigramLanguageModel(vocab_size)

model = model.to(device)

print(model)
```

Aquí hemos creado nuestra primera red neuronal de lenguaje.

---

# ¿Dónde están los parámetros?

Puedes imprimirlos:

```python
number_parameters = sum(
    p.numel()
    for p in model.parameters()
)

print(
    "\nNumber of parameters:",
    number_parameters
)
```

Si tenemos 30 tokens:

```text
30 × 30 = 900
```

aproximadamente.

Nuestro primer modelo puede tener solamente:

```text
~900 parámetros
```

Compara esto con:

```text
Nuestro Bigram       ~900
Mini GPT             ~1,000,000
Qwen pequeño         ~600,000,000
Llama grande         miles de millones
```

Pero conceptualmente esos son **parámetros aprendibles**.

---

# Paso 6 — mira sus pesos antes de entrenar

Añade:

```python
print("\nSome initial weights:")

print(
    model.token_embedding_table.weight[:3, :5]
)
```

Obtendrás números aleatorios:

```text
tensor([
 [ 0.383, -1.215, 0.551, ...],
 [-0.774,  0.082, 1.339, ...],
 ...
])
```

Esto es muy importante.

Antes de entrenamiento:

```text
MODEL KNOWLEDGE = prácticamente cero
```

Los pesos son aleatorios.

---

# Paso 7 — primera predicción

Mueve nuestros datos a MPS:

```python
x = x.to(device)
y = y.to(device)
```

Y:

```python
logits, loss = model(x, y)

print("\nInitial loss:")
print(loss.item())
```

Por ejemplo:

```text
Initial loss:
3.72
```

Guárdate mentalmente ese número.

Nuestro objetivo será bajarlo.

---

# Paso 8 — optimizer

Ahora aparece:

```python
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)
```

Esto es quien modificará los pesos.

---

# Paso 9 — TRAINING

Aquí están unas de las líneas más importantes de todo Machine Learning:

```python
for step in range(5000):

    logits, loss = model(x, y)

    optimizer.zero_grad()

    loss.backward()

    optimizer.step()

    if step % 500 == 0:
        print(
            f"Step {step:5d} | "
            f"Loss {loss.item():.4f}"
        )
```

Ejecuta.

Deberías ver algo parecido a:

```text
Step     0 | Loss 3.6217
Step   500 | Loss 2.3412
Step  1000 | Loss 2.1027
Step  1500 | Loss 1.9721
...
```

### Acabas de entrenar un modelo de lenguaje.

No descargaste un modelo.

No utilizaste ChatGPT.

No utilizaste Hugging Face.

No utilizaste un Transformer.

Partimos de:

```text
random weights
```

y mediante datos:

```text
training data
```

modificamos:

```text
weights
```

para reducir:

```text
loss
```

---

# Quiero que entiendas especialmente estas 4 líneas

```python
logits, loss = model(x, y)
```

### Forward pass

El modelo hace predicciones.

---

```python
optimizer.zero_grad()
```

Limpiamos los gradients anteriores.

---

```python
loss.backward()
```

### BACKPROPAGATION

PyTorch calcula:

```text
∂Loss
─────
∂W
```

para todos los parámetros.

Es decir:

> ¿Cómo cambiaría el error si modificamos cada peso?

---

```python
optimizer.step()
```

AdamW usa esos gradients para modificar los pesos.

Entonces:

```text
W₀
 ↓
W₁
 ↓
W₂
 ↓
W₃
 ↓
...
```

El modelo está aprendiendo.

---

# Paso 10 — hacer que genere texto

Agrega este método dentro de `BigramLanguageModel`:

```python
def generate(self, idx, max_new_tokens):

    for _ in range(max_new_tokens):

        logits, _ = self(idx)

        logits = logits[-1]

        probabilities = F.softmax(
            logits,
            dim=-1
        )

        next_token = torch.multinomial(
            probabilities,
            num_samples=1
        )

        idx = torch.cat(
            [idx, next_token],
            dim=0
        )

    return idx
```

Entonces después del entrenamiento:

```python
start = torch.tensor(
    [stoi["i"]],
    dtype=torch.long,
    device=device
)

generated = model.generate(
    start,
    max_new_tokens=300
)

generated_text = decode(
    generated.tolist()
)

print("\nGENERATED TEXT:\n")

print(generated_text)
```

Probablemente produzca algo bastante malo:

```text
juan learal model praining intell...
```

Y eso es **exactamente lo que quiero**.

No queremos que sea bueno todavía.

Queremos preguntarnos:

> ¿Por qué es malo?

---

# La limitación fundamental del Bigram

Nuestro modelo solamente ve:

```text
token actual
```

para predecir:

```text
siguiente token
```

Por ejemplo:

```text
current = "t"
```

Puede aprender:

```text
t → h  45%
t → i  20%
t → r  10%
...
```

Pero no sabe si estamos escribiendo:

```text
artificial int...
```

o:

```text
the cat...
```

Porque no tiene **contexto**.

Nuestro modelo es:

```text
Xₜ
 ↓
Xₜ₊₁
```

Lo que queremos eventualmente es:

```text
X₁ X₂ X₃ X₄ X₅ X₆
            ↓
      Transformer
            ↓
          X₇
```

Y ahí es donde aparecerá:

# Attention

---

## Nuestro recorrido ahora será progresivo

No saltaremos mágicamente a un GPT.

```text
HOY
│
├── dataset
├── tokenizer
├── tensors
├── parameters
├── forward pass
├── logits
├── probabilities
├── loss
├── gradients
├── backpropagation
├── optimizer
└── training
       │
       ▼
   BIGRAM LM
       │
       ▼

SIGUIENTE
Embeddings
       │
       ▼
Context Window
       │
       ▼
Self Attention
       │
       ▼
Query / Key / Value
       │
       ▼
Masked Attention
       │
       ▼
Multi-Head Attention
       │
       ▼
Feed Forward
       │
       ▼
Transformer Block
       │
       ▼
Mini GPT
```

Y cuando terminemos ese Mini-GPT, haremos el segundo proyecto:

```text
Qwen3-0.6B u otro modelo pequeño
            ↓
          download
            ↓
        base evaluation
            ↓
         dataset propio
            ↓
             LoRA
            ↓
        fine-tuned model
            ↓
    before vs after evaluation
```

MLX-LM incluso usa actualmente `Qwen/Qwen3-0.6b` como modelo predeterminado en su script de fine-tuning y permite seleccionar `lora`, `dora` o `full`, por lo que tu M4 es una plataforma especialmente conveniente para esa segunda parte. ([GitHub][3])

**Empieza ahora únicamente con `check_gpu.py`.** Si me pegas el resultado, seguimos inmediatamente con `bigram.py`, pero lo construiremos **por secciones y entendiendo cada tensor**, incluyendo shapes, logits, Softmax, Cross Entropy y los gradients; no quiero simplemente darte un archivo enorme para ejecutar sin entenderlo.

[1]: https://docs.pytorch.org/docs/stable/notes/mps.html?utm_source=chatgpt.com "MPS backend — PyTorch 2.14 documentation"
[2]: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md?utm_source=chatgpt.com "mlx-lm/mlx_lm/LORA.md at main · ml-explore/mlx-lm · GitHub"
[3]: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/lora.py?utm_source=chatgpt.com "mlx-lm/mlx_lm/lora.py at main · ml-explore/mlx-lm · GitHub"
