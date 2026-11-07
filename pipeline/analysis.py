"""Metrics and the hypothesis test. Every number in THESIS.md and the dashboard comes from here.

Hypothesis (H1): week-over-week changes in NEAR Intents volume track or lead NEAR's
price more closely than week-over-week changes in raw on-chain activity
(transactions, active accounts).

Method: weekly log-changes, cross-correlation at lags -8..+8 weeks (positive lag means
the activity series moves first). Significance comes from a circular-shift permutation
test, which keeps each series' own autocorrelation intact.
"""
import numpy as np
import pandas as pd

BURN_SHARE = 0.70  # NEAR protocol burns 70% of transaction fees (docs.near.org, "Tokenomics")
LAGS = range(-8, 9)
N_PERM = 2000
SEED = 7


def weekly(daily: pd.DataFrame, start: str) -> pd.DataFrame:
    d = daily.loc[start:]
    w = pd.DataFrame({
        "price_usd": d["price_usd"].resample("W-SUN").last(),
        "intents_volume_usd": d["intents_volume_usd"].resample("W-SUN").sum(min_count=7),
        "txns": d["txns"].resample("W-SUN").sum(min_count=7),
        "active_accounts": d["active_accounts"].resample("W-SUN").mean(),
    })
    return w.dropna()


def _xcorr(x: np.ndarray, y: np.ndarray, lag: int) -> float:
    """corr(x[t-lag], y[t]); positive lag means x moves first."""
    if lag > 0:
        a, b = x[:-lag], y[lag:]
    elif lag < 0:
        a, b = x[-lag:], y[:lag]
    else:
        a, b = x, y
    return float(np.corrcoef(a, b)[0, 1])


def lead_lag(w: pd.DataFrame, driver: str, lags=LAGS) -> dict:
    lr = np.log(w).diff().dropna()
    x, y = lr[driver].to_numpy(), lr["price_usd"].to_numpy()
    lags = list(lags)
    obs = {lag: _xcorr(x, y, lag) for lag in lags}
    rng = np.random.default_rng(SEED)
    n = len(x)
    null_max = np.empty(N_PERM)
    for i in range(N_PERM):
        xs = np.roll(x, int(rng.integers(2, n - 2)))
        null_max[i] = max(abs(_xcorr(xs, y, lag)) for lag in lags)
    band = float(np.quantile(null_max, 0.95))
    best_lag = max(obs, key=lambda k: abs(obs[k]))
    lead_lags = {k: v for k, v in obs.items() if k > 0}
    best_lead = max(lead_lags, key=lambda k: abs(lead_lags[k]))
    p_any = float(np.mean(null_max >= abs(obs[best_lag])))
    return {
        "driver": driver,
        "n_weeks": int(n),
        "corr_by_lag": {int(k): round(v, 3) for k, v in obs.items()},
        "lag0": round(obs[0], 3),
        "best_lag": int(best_lag),
        "best_corr": round(obs[best_lag], 3),
        "best_lead_lag": int(best_lead),
        "best_lead_corr": round(lead_lags[best_lead], 3),
        "band95_maxabs": round(band, 3),
        "p_value_best": round(p_any, 3),
        "significant": bool(abs(obs[best_lag]) > band),
    }


def supply_and_burn(daily: pd.DataFrame) -> pd.DataFrame:
    s = daily["total_supply_near"]
    burned = daily["txn_fee_near"] * BURN_SHARE
    out = pd.DataFrame(index=daily.index)
    out["supply_growth_ann_pct"] = ((s / s.shift(90)) ** (365 / 90) - 1) * 100
    gross_issuance_90 = (s - s.shift(90)) + burned.rolling(90).sum()
    out["burn_share_of_issuance_pct"] = burned.rolling(90).sum() / gross_issuance_90 * 100
    return out


def valuation(daily: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=daily.index)
    fees_ann = daily["intents_fees_usd"].rolling(30, min_periods=30).sum() * 365 / 30
    out["intents_fees_annualized_usd"] = fees_ann
    out["mcap_to_intents_fees"] = daily["market_cap_usd"] / fees_ann
    return out


def compute(daily: pd.DataFrame) -> tuple[dict, dict]:
    m: dict = {}
    last = daily.index[-1]
    m["snapshot_date"] = last.strftime("%Y-%m-%d")

    roll = daily[["txns", "active_accounts", "new_accounts"]].rolling(30).mean()
    for col in ["txns", "active_accounts", "new_accounts"]:
        peak_date = roll[col].idxmax()
        m[f"{col}_peak_30d"] = int(round(roll[col].max()))
        m[f"{col}_peak_month"] = peak_date.strftime("%b %Y")
        m[f"{col}_now_30d"] = int(round(roll[col].iloc[-1]))
        m[f"{col}_drop_pct"] = round((1 - roll[col].iloc[-1] / roll[col].max()) * 100, 1)

    iv = daily["intents_volume_usd"]
    m["intents_first_date"] = iv.first_valid_index().strftime("%Y-%m-%d")
    monthly_iv = iv.resample("MS").sum(min_count=1)
    full_months = monthly_iv.iloc[:-1]  # last month is partial
    m["intents_best_month"] = full_months.idxmax().strftime("%b %Y")
    m["intents_best_month_usd_bn"] = round(full_months.max() / 1e9, 2)
    m["intents_last_full_month"] = full_months.index[-1].strftime("%b %Y")
    m["intents_last_full_month_usd_bn"] = round(full_months.iloc[-1] / 1e9, 2)
    m["intents_30d_volume_usd_bn"] = round(iv.iloc[-30:].sum() / 1e9, 2)
    m["intents_365d_volume_usd_bn"] = round(iv.iloc[-365:].sum() / 1e9, 2)
    first_full = full_months[full_months > 0]
    m["intents_first_full_month"] = first_full.index[1].strftime("%b %Y")
    m["intents_first_full_month_usd_m"] = round(first_full.iloc[1] / 1e6, 1)

    dex90 = daily["near_dex_volume_usd"].iloc[-90:].sum()
    m["intents_share_of_near_dex_90d_pct"] = round(iv.iloc[-90:].sum() / dex90 * 100, 1)

    fees30 = daily["intents_fees_usd"].iloc[-30:].sum()
    m["intents_fees_30d_usd_m"] = round(fees30 / 1e6, 2)
    m["intents_fees_annualized_usd_m"] = round(fees30 * 365 / 30 / 1e6, 1)
    m["intents_take_rate_bps_30d"] = round(fees30 / iv.iloc[-30:].sum() * 1e4, 2)

    m["price_now_usd"] = round(float(daily["price_usd"].iloc[-1]), 2)
    m["market_cap_now_usd_bn"] = round(float(daily["market_cap_usd"].iloc[-1]) / 1e9, 2)
    p = daily["price_usd"]
    m["price_peak_30d_usd"] = round(float(p.rolling(30).mean().max()), 2)
    m["price_peak_month"] = p.rolling(30).mean().idxmax().strftime("%b %Y")
    since = p.loc["2025-01-01":]
    m["price_low_since_2025_usd"] = round(float(since.min()), 2)
    m["price_low_since_2025_date"] = since.idxmin().strftime("%b %d, %Y")

    val = valuation(daily)
    m["mcap_to_intents_fees_now"] = round(float(val["mcap_to_intents_fees"].iloc[-1]), 1)

    sb = supply_and_burn(daily)
    m["supply_now_bn"] = round(float(daily["total_supply_near"].iloc[-1]) / 1e9, 4)
    m["supply_growth_ann_now_pct"] = round(float(sb["supply_growth_ann_pct"].iloc[-1]), 2)
    m["supply_growth_ann_2024_avg_pct"] = round(float(sb.loc["2024-01-01":"2024-12-31", "supply_growth_ann_pct"].mean()), 2)
    m["burn_share_of_issuance_now_pct"] = round(float(sb["burn_share_of_issuance_pct"].iloc[-1]), 2)
    burned_365 = float(daily["txn_fee_near"].iloc[-365:].sum() * BURN_SHARE)
    minted_365 = float(daily["total_supply_near"].iloc[-1] - daily["total_supply_near"].iloc[-366]) + burned_365
    m["burned_365d_near_m"] = round(burned_365 / 1e6, 3)
    m["gross_issued_365d_near_m"] = round(minted_365 / 1e6, 1)
    m["issuance_365d_usd_m_at_now_price"] = round(minted_365 * m["price_now_usd"] / 1e6, 1)

    m["tvl_now_usd_m"] = round(float(daily["tvl_usd"].dropna().iloc[-1]) / 1e6, 1)

    start = (iv[iv > 0].first_valid_index() + pd.Timedelta(days=60)).strftime("%Y-%m-%d")
    w = weekly(daily, start)
    tests = {d: lead_lag(w, d) for d in ["intents_volume_usd", "txns", "active_accounts"]}
    m["test_start"] = start
    m["test_weeks"] = tests["intents_volume_usd"]["n_weeks"]
    for d, r in tests.items():
        for k in ["lag0", "best_lag", "best_corr", "best_lead_lag", "best_lead_corr", "band95_maxabs", "p_value_best", "significant"]:
            m[f"{d}_{k}"] = r[k]
    ranked = sorted(tests.values(), key=lambda r: abs(r["best_corr"]), reverse=True)
    m["strongest_driver"] = ranked[0]["driver"]
    # Robustness: same test on 4-week blocks, lags -2..+2 blocks.
    w4 = pd.DataFrame({
        "price_usd": w["price_usd"].resample("4W-SUN").last(),
        "intents_volume_usd": w["intents_volume_usd"].resample("4W-SUN").sum(),
        "txns": w["txns"].resample("4W-SUN").sum(),
        "active_accounts": w["active_accounts"].resample("4W-SUN").mean(),
    }).iloc[1:-1]
    tests4 = {d: lead_lag(w4, d, lags=range(-2, 3)) for d in ["intents_volume_usd", "txns", "active_accounts"]}
    m["test4w_blocks"] = tests4["intents_volume_usd"]["n_weeks"]
    for d, r in tests4.items():
        for k in ["lag0", "best_lag", "best_corr", "band95_maxabs", "significant"]:
            m[f"{d}_4w_{k}"] = r[k]
    fee_roll = daily["txn_fee_near"].rolling(30).mean()
    m["txn_fee_peak_30d_near"] = round(float(fee_roll.max()), 0)
    m["txn_fee_now_30d_near"] = round(float(fee_roll.iloc[-1]), 0)
    m["txn_fee_drop_pct"] = round((1 - fee_roll.iloc[-1] / fee_roll.max()) * 100, 1)
    fees_ann = val["intents_fees_annualized_usd"]
    s_ = daily["total_supply_near"]
    iss_ann = ((s_ - s_.shift(90)) + (daily["txn_fee_near"] * BURN_SHARE).rolling(90).sum()) * 365 / 90 * daily["price_usd"]
    both = pd.DataFrame({"f": fees_ann, "i": iss_ann}).loc["2026-01-01":].dropna()
    m["days_fees_exceed_issuance_2026"] = int((both["f"] > both["i"]).sum())
    m["days_tracked_2026"] = int(len(both))
    m["intents_fees_to_issuance_pct"] = round(m["intents_fees_annualized_usd_m"] / m["issuance_365d_usd_m_at_now_price"] * 100, 1)
    intents_wins = ranked[0]["driver"] == "intents_volume_usd" and tests["intents_volume_usd"]["significant"]
    intents_leads = tests["intents_volume_usd"]["significant"] and tests["intents_volume_usd"]["best_lag"] > 0
    if intents_leads and intents_wins:
        m["verdict"] = "SUPPORTED"
    elif intents_wins:
        m["verdict"] = "PARTLY SUPPORTED (moves with price, does not lead it)"
    else:
        m["verdict"] = "NOT SUPPORTED"
    return m, {"weekly": w, "tests": tests, "tests4w": tests4, "supply_burn": sb, "valuation": val}
