"""Turn raw API responses into one tidy daily table.

Output columns (one row per UTC day):
    txns, active_accounts, new_accounts      NearBlocks network activity
    price_usd, market_cap_usd                 NearBlocks (sourced by NearBlocks from market data)
    total_supply_near                         NearBlocks, converted from yoctoNEAR
    txn_fee_near                              NearBlocks, transaction fees paid, in NEAR
    intents_volume_usd, intents_fees_usd      DefiLlama, NEAR Intents
    near_dex_volume_usd                       DefiLlama, all DEX volume attributed to the NEAR chain
    near_app_fees_usd                         DefiLlama, fees paid to apps on NEAR
    tvl_usd                                   DefiLlama, NEAR chain TVL
"""
import json
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
YOCTO = 1e24


def _load(name: str):
    return json.loads((RAW / f"{name}.json").read_text())


def _llama_series(name: str, col: str) -> pd.Series:
    rows = _load(name)["totalDataChart"]
    s = pd.Series({pd.to_datetime(t, unit="s").normalize(): float(v) for t, v in rows}, name=col)
    return s.sort_index()


def nearblocks() -> pd.DataFrame:
    df = pd.DataFrame(_load("nearblocks_daily")["charts"])
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    for c in df.columns:
        if c != "date":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.set_index("date").sort_index()
    out = pd.DataFrame(index=df.index)
    out["txns"] = df["txns"]
    out["active_accounts"] = df["active_accounts"]
    out["new_accounts"] = df["new_accounts"]
    out["price_usd"] = df["near_price"].where(df["near_price"] > 0)
    out["market_cap_usd"] = df["market_cap"].where(df["market_cap"] > 0)
    out["total_supply_near"] = df["total_supply"] / YOCTO
    out["txn_fee_near"] = df["txn_fee"] / YOCTO
    return out


def tvl() -> pd.Series:
    rows = _load("defillama_tvl")
    s = pd.Series({pd.to_datetime(r["date"], unit="s").normalize(): float(r["tvl"]) for r in rows}, name="tvl_usd")
    return s.sort_index()


def build_daily() -> pd.DataFrame:
    df = nearblocks()
    for name, col in [
        ("defillama_intents_volume", "intents_volume_usd"),
        ("defillama_intents_fees", "intents_fees_usd"),
        ("defillama_dex_volume", "near_dex_volume_usd"),
        ("defillama_app_fees", "near_app_fees_usd"),
    ]:
        df = df.join(_llama_series(name, col), how="left")
    df = df.join(tvl(), how="left")
    # The last row can be a partial day; drop it so every row is a complete UTC day.
    df = df.iloc[:-1]
    df.index.name = "date"
    return df


if __name__ == "__main__":
    d = build_daily()
    print(d.tail())
