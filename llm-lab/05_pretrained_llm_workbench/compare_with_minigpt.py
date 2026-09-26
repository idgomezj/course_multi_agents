import importlib.util
import json
from pathlib import Path

from config import MODEL_DIR


BASE_DIR = Path(
    __file__
).resolve().parent

MINIGPT_DIR = (
    BASE_DIR.parent
    / "04_multihead_transformer"
)


def load_minigpt_config():

    config_path = (
        MINIGPT_DIR
        / "config.py"
    )

    spec = (
        importlib.util.spec_from_file_location(
            "minigpt_config",
            config_path
        )
    )

    module = (
        importlib.util.module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    return module


def main():

    qwen_config_file = (
        MODEL_DIR
        / "config.json"
    )

    if not qwen_config_file.exists():

        raise FileNotFoundError(
            f"Model not found at: {MODEL_DIR}\n\n"
            "Download it first with:\n"
            "python download_model.py"
        )

    mini = (
        load_minigpt_config()
    )

    with open(
        qwen_config_file,
        "r",
        encoding="utf-8"
    ) as file:

        qwen = json.load(
            file
        )

    mini_training_file = (
        MINIGPT_DIR
        / "training.txt"
    )

    with open(
        mini_training_file,
        "r",
        encoding="utf-8"
    ) as file:

        mini_text = file.read()

    mini_vocab = len(
        set(
            mini_text
        )
    )

    rows = [
        (
            "Tokenizer",
            "character",
            "subword / BPE"
        ),
        (
            "Vocabulary",
            mini_vocab,
            qwen.get(
                "vocab_size"
            )
        ),
        (
            "Context",
            mini.BLOCK_SIZE,
            qwen.get(
                "max_position_embeddings"
            )
        ),
        (
            "Hidden size",
            mini.N_EMBD,
            qwen.get(
                "hidden_size"
            )
        ),
        (
            "Transformer layers",
            mini.N_LAYERS,
            qwen.get(
                "num_hidden_layers"
            )
        ),
        (
            "Query heads",
            mini.N_HEADS,
            qwen.get(
                "num_attention_heads"
            )
        ),
        (
            "KV heads",
            mini.N_HEADS,
            qwen.get(
                "num_key_value_heads"
            )
        ),
        (
            "Head dimension",
            mini.N_EMBD
            //
            mini.N_HEADS,
            qwen.get(
                "head_dim"
            )
        ),
        (
            "FFN size",
            mini.FF_MULTIPLIER
            *
            mini.N_EMBD,
            qwen.get(
                "intermediate_size"
            )
        ),
        (
            "Normalization",
            "LayerNorm",
            "RMSNorm"
        ),
        (
            "Position method",
            "learned embeddings",
            "RoPE"
        ),
        (
            "Activation",
            "GELU",
            qwen.get(
                "hidden_act"
            )
        ),
        (
            "Attention style",
            "MHA",
            "GQA"
        ),
    ]

    print(
        "\nOUR MINI-GPT VS PRETRAINED QWEN\n"
    )

    print(
        f"{'Feature':24} "
        f"{'04 Mini-GPT':24} "
        f"{'Qwen3-0.6B-Base':24}"
    )

    print(
        "-" * 76
    )

    for feature, left, right in rows:

        print(
            f"{str(feature):24} "
            f"{str(left):24} "
            f"{str(right):24}"
        )

    print(
        "\nThe architectures are not identical, "
        "but the conceptual path is recognizable:"
    )

    print(
        "\ntokens -> embeddings -> repeated "
        "Transformer layers -> vocabulary logits"
    )


if __name__ == "__main__":

    main()
