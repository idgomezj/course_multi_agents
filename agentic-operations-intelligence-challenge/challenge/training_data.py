from __future__ import annotations

import pandas as pd

from .data_api import get_data_client


def generate_training_frame(
    team_id: str,
    model_key: str,
    rows: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """Fetch the assigned public training data from the standalone Data API."""
    data = get_data_client().get_training_rows(
        team_id=team_id,
        model_key=model_key,
        rows=rows,
        seed=seed,
    )
    return pd.DataFrame(data)
