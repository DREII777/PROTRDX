from __future__ import annotations

import pandas as pd
import pytest

from ..core.config import get_settings
from ..core.database import init_db, session_scope
from ..models.ticker import Ticker


@pytest.fixture(autouse=True)
def setup_db() -> None:
    init_db()
    with session_scope() as session:
        for ticker in session.exec("SELECT * FROM ticker").all():
            session.delete(ticker)
        session.commit()
    get_settings.cache_clear()  # type: ignore[attr-defined]


@pytest.fixture()
def sample_dataframe() -> pd.DataFrame:
    dates = pd.date_range("2023-01-01", periods=120, freq="D")
    data = {
        "open": [100 + i * 0.1 for i in range(120)],
        "high": [101 + i * 0.1 for i in range(120)],
        "low": [99 + i * 0.1 for i in range(120)],
        "close": [100 + i * 0.1 for i in range(120)],
        "volume": [1_000_000 + i * 10 for i in range(120)],
    }
    df = pd.DataFrame(data, index=dates)
    return df
