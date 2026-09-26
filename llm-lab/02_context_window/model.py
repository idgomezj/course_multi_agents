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