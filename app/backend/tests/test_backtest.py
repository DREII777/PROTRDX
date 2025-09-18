from __future__ import annotations

import pandas as pd

from ..services import backtest


def test_quick_backtest_returns_metrics(sample_dataframe: pd.DataFrame) -> None:
    result = backtest.quick_backtest(sample_dataframe)
    assert result.metrics["status"] == "OK"
    assert result.metrics["n"] > 0
