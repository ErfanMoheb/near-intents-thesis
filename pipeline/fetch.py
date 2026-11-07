"""Fetch raw public data for the NEAR thesis. No API keys needed.

Every source is a public, keyless HTTP endpoint. Raw responses are saved
unchanged to data/raw/ with a fetch timestamp so any run can be audited.
"""
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

SOURCES = {
    # NearBlocks: one row per day since 2020-07-21 (txns, active accounts, fees, supply, price)
    "nearblocks_daily": "https://api.nearblocks.io/v1/charts",
    # DefiLlama: total value locked on the NEAR chain, daily
    "defillama_tvl": "https://api.llama.fi/v2/historicalChainTvl/Near",
    # DefiLlama: DEX volume executed on the NEAR chain, daily
    "defillama_dex_volume": "https://api.llama.fi/overview/dexs/near?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true",
    # DefiLlama: NEAR Intents cross-chain swap volume, daily
    "defillama_intents_volume": "https://api.llama.fi/summary/dexs/near-intents?excludeTotalDataChart=false",
    # DefiLlama: fees paid by users of apps on NEAR, daily
    "defillama_app_fees": "https://api.llama.fi/overview/fees/near?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true",
    # DefiLlama: NEAR Intents fees, daily
    "defillama_intents_fees": "https://api.llama.fi/summary/fees/near-intents?excludeTotalDataChart=false",
}


def fetch(name: str, url: str) -> dict:
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "near-thesis/1.0"})
            if r.status_code == 200:
                return r.json()
            print(f"  {name}: HTTP {r.status_code}, retrying", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  {name}: {e}, retrying", file=sys.stderr)
        time.sleep(2 * (attempt + 1))
    raise SystemExit(f"Could not fetch {name} from {url}")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest = {"fetched_at_utc": stamp, "sources": {}}
    for name, url in SOURCES.items():
        print(f"fetching {name}")
        data = fetch(name, url)
        (RAW / f"{name}.json").write_text(json.dumps(data))
        manifest["sources"][name] = url
    (RAW / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"saved {len(SOURCES)} sources to {RAW} at {stamp}")


if __name__ == "__main__":
    main()
