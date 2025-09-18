from __future__ import annotations

import pandas as pd

from ..services import features


def test_compute_indicators(sample_dataframe: pd.DataFrame) -> None:
    indicators = features.compute_indicators(sample_dataframe)
    assert "rsi" in indicators
    assert "atr_pct" in indicators
    assert indicators["levels"]["sma_20"] > 0
