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