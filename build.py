"""One command rebuilds everything: data, metrics, charts, dashboard and THESIS.md.

    python build.py            fetch fresh public data, then rebuild
    python build.py --offline  rebuild from the committed snapshot in data/raw/ (exactly reproducible)
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pipeline import analysis, charts, fetch, render, transform  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="use the committed snapshot in data/raw/ instead of fetching")
    args = ap.parse_args()

    if not args.offline:
        fetch.main()
    manifest = json.loads((ROOT / "data" / "raw" / "manifest.json").read_text())
    print(f"data snapshot fetched at {manifest['fetched_at_utc']}")

    daily = transform.build_daily()
    metrics, extra = analysis.compute(daily)

    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    daily.to_csv(processed / "daily.csv", float_format="%.6g")
    extra["weekly"].to_csv(processed / "weekly.csv", float_format="%.6g")

    charts.render_all(daily, extra, analysis.BURN_SHARE)
    render.write_all(metrics)

    print(f"snapshot date: {metrics['snapshot_date']}")
    print(f"H1 verdict: {metrics['verdict']}")
    print("wrote THESIS.md, docs/index.html, docs/charts/*.png, data/processed/*")


if __name__ == "__main__":
    main()
