import math
import re
from collections import Counter
from pathlib import Path


TOKEN_RE = re.compile(
    r"[a-zA-Z0-9_]+"
)


def tokenize(text):

    return [
        token.lower()
        for token in TOKEN_RE.findall(
            text
        )
    ]


class LocalRetriever:

    def __init__(
        self,
        docs_dir
    ):

        self.docs_dir = Path(
            docs_dir
        )

        self.documents = []

        for path in sorted(
            self.docs_dir.glob(
                "*.txt"
            )
        ):

            text = path.read_text(
                encoding="utf-8"
            )

            self.documents.append(
                {
                    "name": path.name,
                    "text": text,
                    "tokens": tokenize(
                        text
                    ),
                }
            )

        if not self.documents:

            raise RuntimeError(
                f"No .txt files found in {self.docs_dir}"
            )

        self.document_frequency = Counter()

        for document in self.documents:

            for token in set(
                document[
                    "tokens"
                ]
            ):

                self.document_frequency[
                    token
                ] += 1

    def _vector(
        self,
        tokens
    ):

        counts = Counter(
            tokens
        )

        total = max(
            len(tokens),
            1,
        )

        vector = {}

        n_docs = len(
            self.documents
        )

        for token, count in counts.items():

            tf = count / total

            df = self.document_frequency.get(
                token,
                0,
            )

            idf = math.log(
                (n_docs + 1)
                /
                (df + 1)
            ) + 1

            vector[token] = (
                tf
                *
                idf
            )

        return vector

    @staticmethod
    def _cosine(
        left,
        right
    ):

        common = (
            set(left)
            &
            set(right)
        )

        dot = sum(
            left[token]
            *
            right[token]
            for token in common
        )

        left_norm = math.sqrt(
            sum(
                value * value
                for value in left.values()
            )
        )

        right_norm = math.sqrt(
            sum(
                value * value
                for value in right.values()
            )
        )

        if (
            left_norm == 0
            or
            right_norm == 0
        ):

            return 0.0

        return (
            dot
            /
            (
                left_norm
                *
                right_norm
            )
        )

    def search(
        self,
        query,
        top_k=2,
    ):

        query_vector = self._vector(
            tokenize(
                query
            )
        )

        scored = []

        for document in self.documents:

            score = self._cosine(
                query_vector,
                self._vector(
                    document[
                        "tokens"
                    ]
                ),
            )

            scored.append(
                {
                    "name":
                        document[
                            "name"
                        ],
                    "score":
                        score,
                    "text":
                        document[
                            "text"
                        ],
                }
            )

        scored.sort(
            key=lambda item: item[
                "score"
            ],
            reverse=True,
        )

        return scored[
            :top_k
        ]
