import torch
from model import BigramLanguageModel

device = "mps" if torch.backends.mps.is_available() else "cpu"

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

# --------------------------------------------------
# GENERATE & PRINT
# --------------------------------------------------

stoi = checkpoint["stoi"]
itos = checkpoint["itos"]

def decode(tokens):
    return "".join(itos[token] for token in tokens)

# Starting character (e.g., 'j' or any character in vocabulary)
prompt = "j"
start = torch.tensor(
    [stoi[prompt]],
    dtype=torch.long,
    device=device
)

# Generate new tokens
with torch.no_grad():
    generated_tokens = model.generate(
        start,
        max_new_tokens=200
    )

# Decode generated tokens to string
generated_text = decode(generated_tokens.tolist())

print("\n--- GENERATED RESULT ---")
print(generated_text)
print("-------------------------\n")