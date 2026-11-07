# NEAR Intents thesis: usage vs value capture

A reproducible investment-thesis analysis of NEAR, built for the **NEAR HACKATHON, Investment Thesis track**.

**The question:** NEAR's raw on-chain activity collapsed while NEAR Intents (cross-chain swaps) grew into billions of dollars a month. Does the NEAR token capture that new usage?

**What it does:** one command pulls public, keyless data. It then computes every metric, runs a lead-lag hypothesis test, draws six charts, and writes:
- a static dashboard (`docs/index.html`);
- the thesis (`THESIS.md`), which covers the claim, the evidence for and against, and what would change the conclusion.

Every number in the thesis is filled in by the build, not typed by hand.

- **Dashboard:** https://erfanmoheb.github.io/near-intents-thesis/ (GitHub Pages, served from `docs/`)
- **Thesis:** [THESIS.md](THESIS.md)

## Try it (about 1 minute)

```bash
git clone https://github.com/ErfanMoheb/near-intents-thesis && cd near-intents-thesis
python -m pip install -r requirements.txt

python build.py --offline   # rebuild from the committed snapshot in data/raw/ (exactly reproducible)
open docs/index.html        # macOS; on Linux: xdg-open docs/index.html

python build.py             # same, but fetches today's data first (no API keys needed)
python -m pytest -q         # checks: deterministic output, no unfilled numbers, all charts present
```

Expected output of `python build.py --offline`:

```
data snapshot fetched at 2026-11-07T00:41:46+00:00
snapshot date: 2026-11-05
H1 verdict: NOT SUPPORTED
wrote THESIS.md, docs/index.html, docs/charts/*.png, data/processed/*
```

## Result in one paragraph

NEAR Intents is real, fee-paying demand: tens of billions of dollars of volume over the last year, most of all DEX volume on NEAR, and about $75M a year in fees. Meanwhile, daily transactions and active accounts fell more than 90% from their peaks.

The tested hypothesis was: *"Intents volume leads NEAR's price better than raw activity."* It is **not supported**. Neither Intents nor raw activity tracks or leads price, at weekly or at 4-week horizons.

Fee burn offsets under 1% of new issuance. The market cap is about 70× annualized Intents fees. Whether Intents fees reach NEAR holders cannot be seen in public data, and that is the open question the thesis turns on. Details and exact figures: [THESIS.md](THESIS.md).

## Data sources (all public, no keys)

| Source | Endpoint | Used for |
|---|---|---|
| NearBlocks | `https://api.nearblocks.io/v1/charts` | daily transactions, active/new accounts, fees, total supply, price, market cap (since 2020) |
| DefiLlama | `https://api.llama.fi/summary/dexs/near-intents` | NEAR Intents daily volume |
| DefiLlama | `https://api.llama.fi/summary/fees/near-intents` | NEAR Intents daily fees |
| DefiLlama | `https://api.llama.fi/overview/dexs/near` | all DEX volume attributed to NEAR |
| DefiLlama | `https://api.llama.fi/overview/fees/near` | fees paid to apps on NEAR |
| DefiLlama | `https://api.llama.fi/v2/historicalChainTvl/Near` | NEAR TVL |

- **Raw responses:** saved unchanged to `data/raw/`, with a fetch timestamp in `manifest.json`.
- **Not used:** the NEAR BigQuery public dataset (`bigquery-public-data.crypto_near_mainnet_us`), which needs a Google Cloud project, and the NEAR Intents Explorer API, which needs a partner JWT. Leaving both out means anyone can rebuild without accounts or credentials. `THESIS.md` lists what that leaves out.

## How it works

```
build.py                one command: fetch -> transform -> analyze -> charts -> dashboard + THESIS.md
pipeline/fetch.py       downloads the six public sources into data/raw/
pipeline/transform.py   joins them into one daily table (data/processed/daily.csv)
pipeline/analysis.py    metrics + lead-lag test with circular-shift permutation (seeded, deterministic)
pipeline/charts.py      six PNG charts
pipeline/render.py      fills thesis/THESIS.template.md and the dashboard from metrics.json; fails on any unfilled number
tests/test_build.py     reproducibility checks
docs/                   the dashboard (index.html + charts/), served by GitHub Pages
```

## NEAR integration

This is an analysis project, not a contract. It reads NEAR mainnet activity (via NearBlocks' indexer) and NEAR Intents activity (via DefiLlama). It deploys nothing on-chain.

## Disclosures

- **Built during the hackathon window.** All code was written in November 2026. There is no pre-hackathon baseline.
- **AI-generated code.** The code and the first draft of the text were written with Claude (Anthropic) as a coding assistant, then reviewed and run by the author.
- **Libraries:** `pandas`, `numpy`, `matplotlib`, `requests`, `pytest`.
- **Other chains:** none. This project is about NEAR only.
- **Other submissions by the same author:** none.
- **Not financial advice.**

## License

MIT, see [LICENSE](LICENSE).
