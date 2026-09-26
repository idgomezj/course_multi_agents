Perfecto. Ahora que el Bigram ya entrena y genera texto, el siguiente objetivo es **ver exactamente qué aprendió** y luego superar su principal limitación: que solo mira un carácter hacia atrás.

## 1. Primero hagamos visible lo que aprendió

Añade esto después del entrenamiento:

```python
def show_next_token_probabilities(model, character, top_k=10):
    model.eval()

    token_id = stoi[character]

    idx = torch.tensor(
        [token_id],
        dtype=torch.long,
        device=device
    )

    with torch.no_grad():
        logits, _ = model(idx)

    logits = logits[-1]

    probabilities = F.softmax(logits, dim=-1)

    values, indices = torch.topk(
        probabilities,
        k=min(top_k, vocab_size)
    )

    print(f"\nMost probable characters after {repr(character)}:\n")

    for probability, token in zip(values, indices):
        predicted_character = itos[token.item()]

        print(
            f"{repr(predicted_character):>6}"
            f" -> {probability.item() * 100:6.2f}%"
        )
```

Y llama:

```python
show_next_token_probabilities(model, "i")
show_next_token_probabilities(model, "t")
show_next_token_probabilities(model, " ")
```

Esto es importante porque ahora no estamos preguntándole al modelo que genere texto.

Estamos mirando directamente:

```text
P(next_character | current_character)
```

Por ejemplo podrías obtener:

```text
Most probable characters after 't':

   'h' -> 32.14%
   'i' -> 18.72%
   'r' -> 12.05%
   'e' ->  9.51%
```

Eso significa que el modelo ha aprendido estadísticamente que en tu dataset:

```text
t → h
```

ocurre frecuentemente.

---

# 2. ¿Dónde está almacenado ese conocimiento?

Aquí:

```python
model.token_embedding_table.weight
```

Recuerda que creamos:

```python
nn.Embedding(
    vocab_size,
    vocab_size
)
```

Supongamos:

```text
vocab_size = 35
```

Entonces la matriz es:

```text
35 × 35
```

Algo conceptualmente así:

```text
                  próximo carácter

             a     b     c     d     e ...
           ┌────────────────────────────
actual a   │ 0.3  -1.2   0.7   ...
actual b   │ 1.1   0.4  -0.2   ...
actual c   │ ...
actual d   │ ...
...
```

Cada fila corresponde al token actual.

Cada columna corresponde a un posible siguiente token.

Esos números son los:

# logits

Por ejemplo:

```python
token_id = stoi["i"]

print(
    model.token_embedding_table.weight[token_id]
)
```

Podrías tener:

```text
[-1.3, 0.2, 2.8, -0.7, 1.9, ...]
```

No son probabilidades todavía.

Tenemos que aplicar:

```python
softmax(...)
```

para obtener:

```text
[0.01, 0.04, 0.42, 0.02, 0.25, ...]
```

---

# 3. Logits vs probabilidades

Este concepto es fundamental para todo LLM.

Un modelo normalmente **no produce directamente probabilidades**.

Produce:

```text
logits
```

Por ejemplo:

```text
A = 1.2
B = 4.7
C = -0.8
D = 2.1
```

Luego:

```python
F.softmax(logits)
```

produce algo como:

```text
A = 2.7%
B = 88.2%
C = 0.4%
D = 8.7%
```

Y:

```text
sum(probabilities) = 1
```

Puedes comprobarlo:

```python
with torch.no_grad():

    token = torch.tensor(
        [stoi["i"]],
        device=device
    )

    logits, _ = model(token)

    probabilities = F.softmax(
        logits[-1],
        dim=-1
    )


print("Logits:")
print(logits[-1])

print("\nProbabilities:")
print(probabilities)

print(
    "\nSum:",
    probabilities.sum().item()
)
```

Debe quedar muy cerca de:

```text
1.0
```

---

# 4. ¿Qué hace Cross Entropy?

Ahora podemos entender:

```python
loss = F.cross_entropy(logits, targets)
```

Supongamos que la respuesta correcta era:

```text
"v"
```

pero nuestro modelo produjo:

```text
P("v") = 5%
```

Eso es malo.

Cross entropy penaliza al modelo.

A grandes rasgos:

```text
loss = -log(P(correct_answer))
```

Si:

```text
P(correct) = 0.90
```

entonces:

```text
-loss = -log(0.90)
≈ 0.105
```

Muy pequeño.

Pero si:

```text
P(correct) = 0.01
```

entonces:

```text
-loss = -log(0.01)
≈ 4.605
```

Mucho mayor.

Por eso queremos:

```text
LOSS ↓
```

---

# 5. Visualicemos el entrenamiento

Ahora vamos a guardar los losses.

Cambia:

```python
for step in range(5000):
```

por:

```python
loss_history = []

for step in range(5000):

    logits, loss = model(x, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    loss_history.append(loss.item())

    if step % 500 == 0:

        print(
            f"Step {step:5d} | "
            f"Loss {loss.item():.4f}"
        )
```

Después:

```python
import matplotlib.pyplot as plt


plt.plot(loss_history)

plt.xlabel("Training Step")
plt.ylabel("Loss")
plt.title("Bigram Language Model Training")

plt.show()
```

Deberías ver:

```text
Loss
 │\
 │ \
 │  \
 │   \______
 │          \______
 │
 └──────────────────── Training steps
```

Eso es literalmente visualizar el aprendizaje.

---

# 6. Pero ahora tenemos un problema serio

Nuestro modelo está entrenando con:

```python
x = data[:-1]
y = data[1:]
```

utilizando **todo el dataset**.

Después medimos el mismo dataset.

Eso no nos dice si el modelo aprendió algo generalizable.

Podría simplemente estar memorizando.

Aquí aparece otro concepto fundamental:

# Training set vs validation set

Vamos a dividir:

```text
Dataset
│
├── 90% training
│
└── 10% validation
```

Cambia:

```python
x = data[:-1]
y = data[1:]
```

por:

```python
n = int(0.9 * len(data))

train_data = data[:n]
val_data = data[n:]

x_train = train_data[:-1]
y_train = train_data[1:]

x_val = val_data[:-1]
y_val = val_data[1:]
```

Luego mueve todo:

```python
x_train = x_train.to(device)
y_train = y_train.to(device)

x_val = x_val.to(device)
y_val = y_val.to(device)
```

---

# 7. Entrenamos únicamente con training

Ahora:

```python
for step in range(5000):

    logits, loss = model(
        x_train,
        y_train
    )

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

Nunca:

```python
x_val
```

durante `backward()`.

La validación se utiliza solamente para comprobar si el modelo aprendió algo útil.

---

# 8. Evaluemos correctamente

Crea:

```python
@torch.no_grad()
def evaluate(model):

    model.eval()

    _, train_loss = model(
        x_train,
        y_train
    )

    _, val_loss = model(
        x_val,
        y_val
    )

    model.train()

    return (
        train_loss.item(),
        val_loss.item()
    )
```

Después:

```python
for step in range(5000):

    logits, loss = model(
        x_train,
        y_train
    )

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % 500 == 0:

        train_loss, val_loss = evaluate(model)

        print(
            f"Step {step:5d} | "
            f"Train {train_loss:.4f} | "
            f"Validation {val_loss:.4f}"
        )
```

Ahora podrías ver:

```text
Step     0 | Train 3.68 | Validation 3.71

Step   500 | Train 2.46 | Validation 2.83

Step  1000 | Train 2.31 | Validation 2.75

Step  2000 | Train 2.25 | Validation 2.76

Step  4000 | Train 2.20 | Validation 2.81
```

Esto empieza a mostrarnos algo interesante.

Si:

```text
Train loss ↓
Validation loss ↓
```

bien.

Pero si:

```text
Train loss ↓↓↓↓↓
Validation loss ↑↑↑↑
```

estamos viendo:

# Overfitting

El modelo aprende demasiado específicamente el training set.

---

# 9. Guardemos nuestro primer modelo

Cuando terminemos:

```python
torch.save(
    {
        "model_state_dict": model.state_dict(),
        "stoi": stoi,
        "itos": itos,
        "vocab_size": vocab_size,
    },
    "bigram_model.pt"
)
```

Ahora tendrás:

```text
bigram_model.pt
```

Ese archivo contiene principalmente:

```text
los pesos aprendidos
+
información necesaria para reconstruirlo
```

Acabas de crear un **checkpoint**.

---

# 10. Puedes volverlo a cargar

En otro programa:

```python
checkpoint = torch.load(
    "bigram_model.pt",
    map_location=device
)

model = BigramLanguageModel(
    checkpoint["vocab_size"]
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()
```

Ya no necesitas volver a entrenarlo.

Esto es conceptualmente lo mismo que haremos después cuando descarguemos:

```text
Qwen
Llama
Gemma
Mistral
```

La gran diferencia será el tamaño y la arquitectura.

---

# Ahora viene el siguiente salto importante

Tu Bigram piensa así:

```text
actual token
     ↓
prediction
```

Si ve:

```text
"t"
```

solo sabe:

```text
P(h | t)
P(r | t)
P(i | t)
...
```

Pero compara:

```text
the cat
```

con:

```text
artificial intelligence
```

Si ambos terminan momentáneamente en:

```text
t
```

el Bigram no sabe absolutamente nada sobre lo anterior.

Queremos algo así:

```text
input:

"artificial int"

                 ↓

       usar TODO el contexto

                 ↓

              "e"
```

Por eso vamos a introducir:

# Context Window

---

# 11. Nuestro primer context window

En lugar de:

```text
1 carácter → próximo carácter
```

queremos:

```text
8 caracteres → próximo carácter
```

Por ejemplo:

```text
texto:

artificial
```

con:

```python
block_size = 4
```

obtenemos:

```text
INPUT      TARGET

arti       f
rtif       i
tifi       c
ific       i
fici       a
icia       l
```

Eso cambia radicalmente el problema.

Ahora el modelo puede aprender:

```text
P(next_token | previous tokens)
```

y no solamente:

```text
P(next_token | current token)
```

---

# 12. Hagamos batching

Los modelos reales tampoco entrenan procesando todo el dataset en cada paso.

Procesan:

```text
batch
```

Supongamos:

```python
block_size = 8
batch_size = 4
```

Creamos:

```python
def get_batch(split):

    source = (
        train_data
        if split == "train"
        else val_data
    )

    ix = torch.randint(
        len(source) - block_size,
        (batch_size,)
    )

    x = torch.stack(
        [
            source[i:i + block_size]
            for i in ix
        ]
    )

    y = torch.stack(
        [
            source[i + 1:i + block_size + 1]
            for i in ix
        ]
    )

    return (
        x.to(device),
        y.to(device)
    )
```

Prueba:

```python
xb, yb = get_batch("train")

print("X shape:")
print(xb.shape)

print("\nY shape:")
print(yb.shape)

print("\nX:")
print(xb)

print("\nY:")
print(yb)
```

Deberías obtener:

```text
X shape:
torch.Size([4, 8])

Y shape:
torch.Size([4, 8])
```

Significa:

```text
4 secuencias
×
8 tokens cada una
```

---

# Aquí aparece una notación que debes dominar

Desde ahora vamos a usar:

```text
B = Batch
T = Time / sequence length
C = Channels / embedding dimension
```

Verás constantemente:

```text
(B, T)
```

o:

```text
(B, T, C)
```

Por ejemplo:

```text
(4, 8)
```

significa:

```text
B = 4
T = 8
```

Más adelante:

```text
(32, 128, 256)
```

significará:

```text
32 sequences
128 tokens cada una
256 números representando cada token
```

Esto es crítico para entender Transformers.

---

## El siguiente modelo ya no será Bigram

Ahora vamos a pasar de:

```text
token
  ↓
embedding table
  ↓
next token
```

a:

```text
tokens
   ↓
Token Embeddings
   +
Position Embeddings
   ↓
context representation
   ↓
prediction
```

Y inmediatamente después construiremos nosotros mismos:

```text
Q = XWq
K = XWk
V = XWv

Attention(Q,K,V)
=
softmax(QKᵀ / √d)V
```

Ahí empezamos formalmente a construir nuestro **primer Transformer**.
