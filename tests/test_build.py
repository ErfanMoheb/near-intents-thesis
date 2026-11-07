"""Reproducibility checks. Run with:  python -m pytest -q"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _build_offline() -> dict:
    subprocess.run([sys.executable, "build.py", "--offline"], cwd=ROOT, check=True, capture_output=True)
    return json.loads((ROOT / "data" / "processed" / "metrics.json").read_text())


def test_offline_build_is_deterministic():
    assert _build_offline() == _build_offline()


def test_no_unfilled_placeholders():
    _build_offline()
    for f in ["THESIS.md", "docs/index.html"]:
        text = (ROOT / f).read_text()
        assert not re.search(r"\{\{\w+\}\}", text), f"unfilled placeholder in {f}"


def test_every_chart_exists_and_is_referenced():
    _build_offline()
    html = (ROOT / "docs" / "index.html").read_text()
    pngs = sorted((ROOT / "docs" / "charts").glob("*.png"))
    assert len(pngs) == 6
    for p in pngs:
        assert p.stat().st_size > 10_000
        assert f"charts/{p.name}" in html


def test_metrics_are_internally_consistent():
    m = _build_offline()
    assert 0 < m["intents_share_of_near_dex_90d_pct"] <= 100
    assert m["txns_now_30d"] <= m["txns_peak_30d"]
    assert m["verdict"] in {"SUPPORTED", "PARTLY SUPPORTED (moves with price, does not lead it)", "NOT SUPPORTED"}
