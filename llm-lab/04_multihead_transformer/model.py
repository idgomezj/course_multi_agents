import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from config import (
    BLOCK_SIZE,
    N_EMBD,
    N_HEADS,
    N_LAYERS,
    DROPOUT,
    FF_MULTIPLIER,
)


# ==================================================
# ONE CAUSAL SELF-ATTENTION HEAD
# ==================================================

class CausalSelfAttentionHead(nn.Module):

    def __init__(
        self,
        head_size
    ):

        super().__init__()

        self.head_size = head_size

        self.query = nn.Linear(
            N_EMBD,
            head_size,
            bias=False
        )

        self.key = nn.Linear(
            N_EMBD,
            head_size,
            bias=False
        )

        self.value = nn.Linear(
            N_EMBD,
            head_size,
            bias=False
        )

        self.dropout = nn.Dropout(
            DROPOUT
        )

        self.register_buffer(
            "causal_mask",
            torch.tril(
                torch.ones(
                    BLOCK_SIZE,
                    BLOCK_SIZE,
                    dtype=torch.bool
                )
            )
        )


    def forward(
        self,
        x,
        return_attention=False
    ):

        # x shape:
        #
        # (B, T, C)

        B, T, _ = x.shape

        q = self.query(x)

        k = self.key(x)

        v = self.value(x)

        # q, k, v:
        #
        # (B, T, head_size)

        scores = (
            q
            @
            k.transpose(
                -2,
                -1
            )
        )

        scores = (
            scores
            /
            math.sqrt(
                self.head_size
            )
        )

        # scores:
        #
        # (B, T, T)

        scores = scores.masked_fill(
            ~self.causal_mask[
                :T,
                :T
            ],
            float("-inf")
        )

        attention_weights = (
            F.softmax(
                scores,
                dim=-1
            )
        )

        attention_weights = (
            self.dropout(
                attention_weights
            )
        )

        output = (
            attention_weights
            @
            v
        )

        # output:
        #
        # (B, T, head_size)

        if return_attention:

            return (
                output,
                attention_weights
            )

        return output


# ==================================================
# MULTI-HEAD SELF-ATTENTION
# ==================================================

class MultiHeadSelfAttention(nn.Module):

    def __init__(self):

        super().__init__()

        if N_EMBD % N_HEADS != 0:

            raise ValueError(
                "N_EMBD must be divisible "
                "by N_HEADS"
            )

        self.head_size = (
            N_EMBD
            //
            N_HEADS
        )

        self.heads = nn.ModuleList([
            CausalSelfAttentionHead(
                self.head_size
            )
            for _ in range(
                N_HEADS
            )
        ])

        self.projection = nn.Linear(
            N_EMBD,
            N_EMBD
        )

        self.dropout = nn.Dropout(
            DROPOUT
        )


    def forward(
        self,
        x,
        return_attention=False
    ):

        head_outputs = []

        head_weights = []

        for head in self.heads:

            if return_attention:

                output, weights = head(
                    x,
                    return_attention=True
                )

                head_outputs.append(
                    output
                )

                head_weights.append(
                    weights
                )

            else:

                head_outputs.append(
                    head(x)
                )

        combined = torch.cat(
            head_outputs,
            dim=-1
        )

        # combined:
        #
        # (B, T, N_EMBD)

        output = self.projection(
            combined
        )

        output = self.dropout(
            output
        )

        if return_attention:

            attention = torch.stack(
                head_weights,
                dim=1
            )

            # attention:
            #
            # (B, H, T, T)

            return (
                output,
                attention
            )

        return output


# ==================================================
# FEED-FORWARD NETWORK
# ==================================================

class FeedForward(nn.Module):

    def __init__(self):

        super().__init__()

        hidden_size = (
            FF_MULTIPLIER
            *
            N_EMBD
        )

        self.network = nn.Sequential(
            nn.Linear(
                N_EMBD,
                hidden_size
            ),
            nn.GELU(),
            nn.Linear(
                hidden_size,
                N_EMBD
            ),
            nn.Dropout(
                DROPOUT
            ),
        )


    def forward(self, x):

        return self.network(x)


# ==================================================
# TRANSFORMER BLOCK
# ==================================================

class TransformerBlock(nn.Module):

    def __init__(self):

        super().__init__()

        self.layer_norm_attention = (
            nn.LayerNorm(
                N_EMBD
            )
        )

        self.attention = (
            MultiHeadSelfAttention()
        )

        self.layer_norm_ff = (
            nn.LayerNorm(
                N_EMBD
            )
        )

        self.feed_forward = (
            FeedForward()
        )


    def forward(
        self,
        x,
        return_attention=False
    ):

        # Pre-LayerNorm:
        #
        # x = x + Attention(LN(x))

        normalized = (
            self.layer_norm_attention(
                x
            )
        )

        if return_attention:

            attention_output, weights = (
                self.attention(
                    normalized,
                    return_attention=True
                )
            )

        else:

            attention_output = (
                self.attention(
                    normalized
                )
            )

            weights = None

        x = (
            x
            +
            attention_output
        )

        # Second residual path:
        #
        # x = x + FFN(LN(x))

        x = (
            x
            +
            self.feed_forward(
                self.layer_norm_ff(
                    x
                )
            )
        )

        if return_attention:

            return (
                x,
                weights
            )

        return x


# ==================================================
# MINI GPT
# ==================================================

class MiniGPT(nn.Module):

    def __init__(
        self,
        vocab_size
    ):

        super().__init__()

        self.vocab_size = (
            vocab_size
        )

        self.token_embedding = (
            nn.Embedding(
                vocab_size,
                N_EMBD
            )
        )

        self.position_embedding = (
            nn.Embedding(
                BLOCK_SIZE,
                N_EMBD
            )
        )

        self.blocks = nn.ModuleList([
            TransformerBlock()
            for _ in range(
                N_LAYERS
            )
        ])

        self.final_layer_norm = (
            nn.LayerNorm(
                N_EMBD
            )
        )

        self.language_model_head = (
            nn.Linear(
                N_EMBD,
                vocab_size
            )
        )

        self.apply(
            self._init_weights
        )


    def _init_weights(
        self,
        module
    ):

        if isinstance(
            module,
            nn.Linear
        ):

            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=0.02
            )

            if module.bias is not None:

                nn.init.zeros_(
                    module.bias
                )

        elif isinstance(
            module,
            nn.Embedding
        ):

            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=0.02
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
                f"Sequence length {T} exceeds "
                f"BLOCK_SIZE {BLOCK_SIZE}."
            )

        positions = torch.arange(
            T,
            device=idx.device
        )

        x = (
            self.token_embedding(
                idx
            )
            +
            self.position_embedding(
                positions
            )
        )

        all_attention = []

        for block in self.blocks:

            if return_attention:

                x, attention = block(
                    x,
                    return_attention=True
                )

                all_attention.append(
                    attention
                )

            else:

                x = block(x)

        x = self.final_layer_norm(
            x
        )

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

            B, T, V = (
                logits.shape
            )

            loss = F.cross_entropy(
                logits.reshape(
                    B * T,
                    V
                ),
                targets.reshape(
                    B * T
                )
            )

        if return_attention:

            return (
                logits,
                loss,
                all_attention
            )

        return (
            logits,
            loss
        )
