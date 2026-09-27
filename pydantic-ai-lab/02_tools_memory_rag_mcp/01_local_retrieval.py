from pathlib import Path

from retrieval import LocalRetriever


def main():

    docs_dir = (
        Path(__file__).resolve().parent
        / "knowledge"
    )

    retriever = LocalRetriever(
        docs_dir
    )

    query = (
        "What database does Atlas use "
        "and where is project state stored?"
    )

    print(
        "QUERY"
    )

    print(
        query
    )

    print(
        "\nLOCAL RETRIEVAL RESULTS"
    )

    for result in retriever.search(
        query,
        top_k=3,
    ):

        print(
            "\n"
            + result[
                "name"
            ]
        )

        print(
            "score:",
            round(
                result[
                    "score"
                ],
                4,
            )
        )

        print(
            result[
                "text"
            ]
        )

    print(
        "\nNo LLM API was called."
    )


if __name__ == "__main__":

    main()
