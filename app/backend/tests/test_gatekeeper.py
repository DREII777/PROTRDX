from __future__ import annotations

from ..services import gatekeeper


def test_gatekeeper_blocks_on_spread(monkeypatch) -> None:
    monkeypatch.setenv("MAX_SPREAD_PCT", "0.01")
    status, reasons = gatekeeper.apply_gatekeeper({"spread_pct": 0.5, "vol_rel": 2}, {"status": "OK", "n": 100, "sharpe": 1.0, "max_dd": 0.05, "hit_rate": 0.6})
    assert status == "BLOCK"
    assert "spread" in reasons[0]
