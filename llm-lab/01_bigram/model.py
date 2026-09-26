import torch
import torch.nn as nn
import torch.nn.functional as F

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

    
    def generate(self, idx, max_new_tokens):

        for _ in range(max_new_tokens):

            # Forward pass
            logits, _ = self(idx)

            # We only care about the prediction
            # produced by the last token
            logits = logits[-1]

            # Convert logits into probabilities
            probabilities = F.softmax(
                logits,
                dim=-1
            )

            # Randomly sample the next token
            next_token = torch.multinomial(
                probabilities,
                num_samples=1
            )

            # Add new token to the sequence
            idx = torch.cat(
                [idx, next_token],
                dim=0
            )

        return idx
