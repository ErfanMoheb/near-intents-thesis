"""Render every chart as a PNG. Each chart maps to one entry in CHARTS (used by the dashboard)."""
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "charts"

INK, MUTED, GRID = "#1d2433", "#6b7385", "#e6e8ee"
GREEN, BLUE, ORANGE, RED, GREY = "#00a37a", "#3b6fd8", "#e08a1e", "#d64545", "#9aa1af"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
    "axes.titlesize": 13, "axes.titlecolor": INK, "legend.frameon": False, "axes.axisbelow": True,
})


def _usd(x, _=None):
    for div, suf in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(x) >= div:
            return f"${x/div:,.0f}{suf}" if x / div >= 10 else f"${x/div:,.1f}{suf}"
    return f"${x:,.0f}"


def _num(x, _=None):
    for div, suf in [(1e6, "M"), (1e3, "K")]:
        if abs(x) >= div:
            return f"{x/div:,.1f}{suf}"
    return f"{x:,.0f}"


def _dates(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


def _save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def activity_vs_intents(d: pd.DataFrame):
    d = d.loc["2023-01-01":]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [1, 1]})
    r = d[["txns", "active_accounts"]].rolling(30).mean()
    a1.plot(r.index, r["txns"], color=BLUE, lw=2, label="Transactions per day")
    a1.plot(r.index, r["active_accounts"], color=GREY, lw=2, label="Active accounts per day")
    a1.set_yscale("log")
    a1.yaxis.set_major_formatter(mticker.FuncFormatter(_num))
    a1.set_title("Raw on-chain activity (30-day average, log scale)", loc="left")
    a1.legend(loc="lower left")
    mv = d["intents_volume_usd"].resample("MS").sum(min_count=1).iloc[:-1]
    a2.bar(mv.index + pd.Timedelta(days=14), mv.values, width=24, color=GREEN)
    a2.yaxis.set_major_formatter(mticker.FuncFormatter(_usd))
    a2.set_title("NEAR Intents cross-chain volume (per month)", loc="left")
    _dates(a2)
    fig.tight_layout()
    _save(fig, "01_activity_vs_intents")


def intents_share(d: pd.DataFrame):
    d = d.loc["2024-12-01":]
    m = d[["intents_volume_usd", "near_dex_volume_usd"]].resample("MS").sum(min_count=1).iloc[:-1]
    share = (m["intents_volume_usd"] / m["near_dex_volume_usd"] * 100).clip(upper=100)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(share.index, share.values, color=GREEN, lw=2.5, marker="o")
    ax.set_ylim(0, 105)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_title("NEAR Intents as a share of all DEX volume attributed to NEAR (monthly)", loc="left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.tight_layout()
    _save(fig, "02_intents_share")


def price_vs_intents(w: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(w.index, w["intents_volume_usd"], width=5, color=GREEN, alpha=0.55, label="Intents volume (weekly)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_usd))
    ax.set_ylabel("Weekly Intents volume")
    ax2 = ax.twinx()
    ax2.plot(w.index, w["price_usd"], color=INK, lw=2, label="NEAR price (week close)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.2f}"))
    ax2.set_ylabel("NEAR price")
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    ax.set_title("NEAR price vs weekly Intents volume", loc="left")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.tight_layout()
    _save(fig, "03_price_vs_intents")


def lead_lag(tests: dict):
    labels = {"intents_volume_usd": ("Intents volume", GREEN), "txns": ("Transactions", BLUE),
              "active_accounts": ("Active accounts", GREY)}
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, (k, r) in zip(axes, tests.items()):
        lags = list(r["corr_by_lag"].keys())
        vals = list(r["corr_by_lag"].values())
        name, col = labels[k]
        ax.bar(lags, vals, color=[col if v >= 0 else RED for v in vals], width=0.8)
        b = r["band95_maxabs"]
        ax.axhspan(-b, b, color=GRID, alpha=0.7, zorder=0)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_title(name, loc="left")
        ax.set_xlabel("weeks the series leads price  (→)")
        ax.set_ylim(-0.6, 0.6)
        ax.set_xticks(range(-8, 9, 2))
    axes[0].set_ylabel("correlation with NEAR price change")
    fig.suptitle("Do weekly changes in activity lead NEAR's price?  Grey band = 95% noise range",
                 x=0.01, ha="left", fontweight="bold", color=INK)
    fig.tight_layout()
    _save(fig, "04_lead_lag")


def supply_burn(sb: pd.DataFrame):
    sb = sb.loc["2023-01-01":]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(sb.index, sb["supply_growth_ann_pct"], color=ORANGE, lw=2.5, label="Net supply growth, annualized (90-day)")
    ax.plot(sb.index, sb["burn_share_of_issuance_pct"], color=RED, lw=2, label="Fees burned as % of new issuance (90-day)")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_ylim(bottom=0)
    ax.set_title("Token supply: issuance vs fee burn", loc="left")
    ax.legend(loc="center left")
    _dates(ax)
    fig.tight_layout()
    _save(fig, "05_supply_burn")


def valuation(d: pd.DataFrame, val: pd.DataFrame, issuance_usd_ann: pd.Series):
    v = val.dropna(subset=["intents_fees_annualized_usd"])
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(v.index, v["intents_fees_annualized_usd"], color=GREEN, lw=2.5, label="Intents fees, annualized (trailing 30 days)")
    iss = issuance_usd_ann.reindex(v.index)
    ax.plot(iss.index, iss.values, color=ORANGE, lw=2, label="Value of new NEAR issued, annualized (90-day, at that day's price)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_usd))
    ax.set_title("Revenue vs dilution: Intents fees against the dollar value of new token issuance", loc="left")
    ax.legend(loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.tight_layout()
    _save(fig, "06_fees_vs_issuance")


def issuance_usd_annualized(d: pd.DataFrame, burn_share: float) -> pd.Series:
    s = d["total_supply_near"]
    minted_90 = (s - s.shift(90)) + (d["txn_fee_near"] * burn_share).rolling(90).sum()
    return minted_90 * 365 / 90 * d["price_usd"]


def render_all(d: pd.DataFrame, extra: dict, burn_share: float) -> None:
    activity_vs_intents(d)
    intents_share(d)
    price_vs_intents(extra["weekly"])
    lead_lag(extra["tests"])
    supply_burn(extra["supply_burn"])
    valuation(d, extra["valuation"], issuance_usd_annualized(d, burn_share))
