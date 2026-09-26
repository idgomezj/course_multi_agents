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