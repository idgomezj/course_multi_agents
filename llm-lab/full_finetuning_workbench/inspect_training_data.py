import json

from transformers import (
    AutoTokenizer,
)

from mlx_lm.tuner.datasets import (
    CompletionsDataset,
)

from config import (
    MODEL_DIR,
    TRAIN_FILE,
)

from model_files import (
    require_complete_model,
)


def main():

    require_complete_model()

    with open(
        TRAIN_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        first_record = json.loads(
            file.readline()
        )

    tokenizer = (
        AutoTokenizer.from_pretrained(
            MODEL_DIR,
            local_files_only=True,
        )
    )

    dataset = CompletionsDataset(
        data=[
            first_record
        ],
        tokenizer=tokenizer,
        prompt_key="prompt",
        completion_key="completion",
        mask_prompt=True,
    )

    tokens, offset = (
        dataset.process(
            first_record
        )
    )

    prompt_tokens = (
        tokens[:offset]
    )

    completion_tokens = (
        tokens[offset:]
    )

    print(
        "RAW TRAINING RECORD"
    )

    print(
        "-------------------"
    )

    print(
        "\nPrompt:"
    )

    print(
        first_record[
            "prompt"
        ]
    )

    print(
        "\nCompletion:"
    )

    print(
        first_record[
            "completion"
        ]
    )

    print(
        "\nTOKEN COUNTS"
    )

    print(
        "------------"
    )

    print(
        "All tokens:",
        len(tokens)
    )

    print(
        "Masked prompt tokens:",
        len(prompt_tokens)
    )

    print(
        "Loss-bearing completion tokens:",
        len(completion_tokens)
    )

    print(
        "\nTEXT CREATED BY THE MODEL'S "
        "CHAT TEMPLATE"
    )

    print(
        "--------------------------------"
    )

    print(
        tokenizer.decode(
            tokens,
            skip_special_tokens=False
        )
    )

    print(
        "\nMASKED REGION"
    )

    print(
        "-------------"
    )

    print(
        tokenizer.decode(
            prompt_tokens,
            skip_special_tokens=False
        )
    )

    print(
        "\nREGION USED FOR SUPERVISED LOSS"
    )

    print(
        "-------------------------------"
    )

    print(
        tokenizer.decode(
            completion_tokens,
            skip_special_tokens=False
        )
    )

    print(
        "\nWhy this matters:"
    )

    print(
        "The prompt conditions the model, but "
        "mask_prompt=True excludes prompt tokens "
        "from the supervised loss."
    )


if __name__ == "__main__":

    main()
