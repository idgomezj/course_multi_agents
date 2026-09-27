import sqlite3
from pathlib import Path


class SQLiteMemory:

    def __init__(
        self,
        path
    ):

        self.path = Path(
            path
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    def _connect(self):

        return sqlite3.connect(
            self.path
        )

    def _initialize(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def set(
        self,
        key,
        value
    ):

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO memory(key, value)
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value = excluded.value
                """,
                (
                    key,
                    value,
                ),
            )

    def get(
        self,
        key
    ):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT value
                FROM memory
                WHERE key = ?
                """,
                (
                    key,
                ),
            ).fetchone()

        if row is None:

            return None

        return row[0]

    def all(
        self
    ):

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT key, value
                FROM memory
                ORDER BY key
                """
            ).fetchall()

        return dict(
            rows
        )
