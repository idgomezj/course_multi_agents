import torch
import torch.nn.functional as F
from model import BigramLanguageModel

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


data = torch.tensor(
    encode(text),
    dtype=torch.long
)

print("\nTensor:")
print(data[:50])

print("\nTensor shape:")
print(data.shape)


n = int(0.9 * len(data))

train_data = data[:n]
val_data = data[n:]

x_train = train_data[:-1]
y_train = train_data[1:]

x_val = val_data[:-1]
y_val = val_data[1:]


x_train = x_train.to(device)
y_train = y_train.to(device)



print("\nFirst training examples:")

for t in range(10):
    input_token = x_train[t].item()
    target_token = y_train[t].item()

    print(
        repr(itos[input_token]),
        "->",
        repr(itos[target_token])
    )


# Crear una red neuronal
# Ahora llegamos al primer modelo.


model = BigramLanguageModel(vocab_size)

model = model.to(device)

print(model)

number_parameters = sum(
    p.numel()
    for p in model.parameters()
)

print(
    "\nNumber of parameters:",
    number_parameters
)


print("\nSome initial weights:")

print(
    model.token_embedding_table.weight[:3, :5]
)


x_val = x_val.to(device)
y_val = y_val.to(device)


logits, loss = model(x_train, y_train)

print("\nInitial loss:")
print(loss.item())

#Initial loss:
#3.693756580352783

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.01
)

loss_history = []


# Evaluar 
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


import math

print(
    "Random prediction baseline:",
    math.log(vocab_size)
)
print("\nFinal loss:")
print(loss.item())


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

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# 1. Primero hagamos visible lo que aprendió
# Añade esto después del entrenamiento:

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

show_next_token_probabilities(model, "i")
show_next_token_probabilities(model, "t")
show_next_token_probabilities(model, " ")



#logits
token_id = stoi["i"]
print()
print("Logits for 'i':")
print(
    model.token_embedding_table.weight[token_id]
)



# Visualizar el entrenamiento 
import matplotlib.pyplot as plt


plt.plot(loss_history)

plt.xlabel("Training Step")
plt.ylabel("Loss")
plt.title("Bigram Language Model Training")

plt.show()



# Guardemos el primer modelo 
torch.save(
    {
        "model_state_dict": model.state_dict(),
        "stoi": stoi,
        "itos": itos,
        "vocab_size": vocab_size,
    },
    "bigram_model.pt"
)

