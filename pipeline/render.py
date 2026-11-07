"""Write THESIS.md and dashboard/index.html from computed metrics.

Numbers are never typed by hand: templates use {{metric_name}} and the build fails
if any placeholder has no computed value.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/ErfanMoheb/near-intents-thesis"

LLAMA = "https://api.llama.fi"
NB = "https://api.nearblocks.io/v1/charts"


def fill(template: str, m: dict) -> str:
    def sub(match):
        key = match.group(1)
        if key not in m:
            raise KeyError(f"template placeholder {{{{{key}}}}} has no computed value")
        v = m[key]
        if isinstance(v, float):
            return f"{v:,.2f}".rstrip("0").rstrip(".") if abs(v) < 1000 else f"{v:,.0f}"
        if isinstance(v, int) and not isinstance(v, bool):
            return f"{v:,}"
        return str(v)
    out = re.sub(r"\{\{(\w+)\}\}", sub, template)
    return out


def lead_lag_sentence(m: dict) -> str:
    names = {"intents_volume_usd": "Intents volume", "txns": "transactions", "active_accounts": "active accounts"}
    sig = [names[k] for k in names if m[f"{k}_significant"]]
    if not sig:
        return (f"No bar leaves the grey noise band for any series: over {m['test_weeks']} weeks, none of them "
                f"moves with or ahead of NEAR's price (Intents best: {m['intents_volume_usd_best_corr']} "
                f"at lag {m['intents_volume_usd_best_lag']} vs a noise band of ±{m['intents_volume_usd_band95_maxabs']}).")
    return (f"Significant at the 95% level: {', '.join(sig)}. Intents best correlation "
            f"{m['intents_volume_usd_best_corr']} at lag {m['intents_volume_usd_best_lag']} weeks.")


def chart_cards(m: dict) -> list[dict]:
    return [
        {
            "file": "01_activity_vs_intents.png",
            "title": "Usage moved: raw activity fell, Intents rose",
            "takeaway": fill("Daily transactions are down {{txns_drop_pct}}% from their {{txns_peak_month}} peak and active "
                             "accounts are down {{active_accounts_drop_pct}}%, while monthly Intents volume went from "
                             "${{intents_first_full_month_usd_m}}M ({{intents_first_full_month}}) to "
                             "${{intents_best_month_usd_bn}}B ({{intents_best_month}}).", m),
            "source": [f"{NB} → txns, active_accounts (30-day mean)", f"{LLAMA}/summary/dexs/near-intents → monthly sum"],
            "code": "pipeline/charts.py::activity_vs_intents",
        },
        {
            "file": "02_intents_share.png",
            "title": "Intents is now most of NEAR's trading",
            "takeaway": fill("Over the last 90 days, NEAR Intents was {{intents_share_of_near_dex_90d_pct}}% of all DEX "
                             "volume DefiLlama attributes to the NEAR chain.", m),
            "source": [f"{LLAMA}/summary/dexs/near-intents", f"{LLAMA}/overview/dexs/near", "share = Intents ÷ NEAR DEX volume, monthly"],
            "code": "pipeline/charts.py::intents_share",
        },
        {
            "file": "03_price_vs_intents.png",
            "title": "Price vs Intents, week by week",
            "takeaway": fill("Week-over-week changes in Intents volume and in NEAR's price are essentially uncorrelated "
                             "(same-week correlation {{intents_volume_usd_lag0}}).", m),
            "source": [f"{NB} → near_price (weekly close)", f"{LLAMA}/summary/dexs/near-intents → weekly sum"],
            "code": "pipeline/charts.py::price_vs_intents",
        },
        {
            "file": "04_lead_lag.png",
            "title": "The test: does any activity series lead price?",
            "takeaway": lead_lag_sentence(m),
            "source": ["weekly log-changes, corr(series[t−lag], price[t]) for lag −8…+8",
                       "95% band: max |corr| under 2,000 circular-shift permutations (seed 7)"],
            "code": "pipeline/analysis.py::lead_lag",
        },
        {
            "file": "05_supply_burn.png",
            "title": "Issuance vs burn",
            "takeaway": fill("Net supply now grows about {{supply_growth_ann_now_pct}}% a year (it averaged "
                             "{{supply_growth_ann_2024_avg_pct}}% in 2024), and fee burn offsets only "
                             "{{burn_share_of_issuance_now_pct}}% of new issuance.", m),
            "source": [f"{NB} → total_supply, txn_fee (yoctoNEAR ÷ 1e24)", "burn = 70% of transaction fees (NEAR protocol rule)"],
            "code": "pipeline/analysis.py::supply_and_burn",
        },
        {
            "file": "06_fees_vs_issuance.png",
            "title": "Revenue vs dilution",
            "takeaway": fill("Annualized Intents fees (${{intents_fees_annualized_usd_m}}M) equal "
                             "{{intents_fees_to_issuance_pct}}% of the dollar value of NEAR issued over the last year "
                             "(${{issuance_365d_usd_m_at_now_price}}M at today's price); on {{days_fees_exceed_issuance_2026}} of "
                             "{{days_tracked_2026}} days in 2026, fees ran above issuance. Whether those fees reach NEAR "
                             "holders is not visible in this data.", m),
            "source": [f"{LLAMA}/summary/fees/near-intents → 30-day sum × 365/30", f"{NB} → supply change + burn, × price"],
            "code": "pipeline/charts.py::valuation",
        },
    ]


TILES = [
    ("Intents volume, last 30 days", "${{intents_30d_volume_usd_bn}}B"),
    ("Intents fees, annualized", "${{intents_fees_annualized_usd_m}}M"),
    ("Market cap ÷ Intents fees", "{{mcap_to_intents_fees_now}}×"),
    ("Transactions vs peak", "−{{txns_drop_pct}}%"),
    ("Net supply growth / yr", "{{supply_growth_ann_now_pct}}%"),
    ("Fee burn ÷ issuance", "{{burn_share_of_issuance_now_pct}}%"),
]


def dashboard_html(m: dict) -> str:
    tiles = "".join(
        f'<div class="tile"><div class="v">{html.escape(fill(v, m))}</div><div class="l">{html.escape(l)}</div></div>'
        for l, v in TILES)
    cards = []
    for c in chart_cards(m):
        src = "".join(f"<li><code>{html.escape(s)}</code></li>" for s in c["source"])
        cards.append(f"""
<section class="card">
  <h2>{html.escape(c['title'])}</h2>
  <img src="charts/{c['file']}" alt="{html.escape(c['title'])}">
  <p class="take">{html.escape(c['takeaway'])}</p>
  <details><summary>Source and method</summary><ul>{src}</ul>
  <p>Code: <a href="{REPO_URL}/blob/main/{c['code'].split('::')[0]}"><code>{html.escape(c['code'])}</code></a></p></details>
</section>""")
    verdict = html.escape(m["verdict"])
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NEAR Intents thesis: usage vs value capture</title>
<style>
:root{{--ink:#1d2433;--muted:#6b7385;--line:#e6e8ee;--green:#00a37a;--bg:#f7f8fa}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}}
main{{max-width:1080px;margin:0 auto;padding:40px 20px 80px}}
h1{{font-size:30px;line-height:1.2;margin:0 0 8px}}.sub{{color:var(--muted);margin:0 0 24px}}
.verdict{{background:#fff;border:1px solid var(--line);border-left:5px solid var(--green);border-radius:10px;padding:16px 20px;margin:0 0 24px}}
.verdict b{{font-size:18px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 28px}}
.tile{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px}}.tile .v{{font-size:24px;font-weight:700}}.tile .l{{color:var(--muted);font-size:13px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px;margin:0 0 20px}}
.card h2{{font-size:19px;margin:0 0 12px}}.card img{{width:100%;height:auto;border-radius:6px}}
.take{{font-size:16px;margin:12px 0 6px}}details{{color:var(--muted);font-size:14px}}code{{font-size:13px;word-break:break-all}}
footer{{color:var(--muted);font-size:14px;margin-top:32px}}a{{color:#3b6fd8}}
</style></head><body><main>
<h1>NEAR: usage moved to Intents. Has value capture followed?</h1>
<p class="sub">Snapshot {m['snapshot_date']} · every number and chart is rebuilt from public, keyless data with <code>python build.py</code> · built at NEAR HACKATHON (Investment Thesis track)</p>
<div class="verdict"><b>H1: “NEAR Intents volume leads NEAR's price better than raw on-chain activity.” → {verdict}</b><br>
Tested over {m['test_weeks']} weeks ({m['test_start']} → {m['snapshot_date']}). Intents is real, fee-paying demand; the token's link to it is not visible in the data yet. Full argument, counter-evidence and falsifiers: <a href="{REPO_URL}/blob/main/THESIS.md">THESIS.md</a>.</div>
<div class="tiles">{tiles}</div>
{''.join(cards)}
<footer>Sources: NearBlocks public charts API, DefiLlama public API. No API keys. Not financial advice. Code and data: <a href="{REPO_URL}">{REPO_URL}</a></footer>
</main></body></html>
"""


def write_all(m: dict) -> None:
    tpl = (ROOT / "thesis" / "THESIS.template.md").read_text()
    (ROOT / "THESIS.md").write_text(fill(tpl, m))
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "index.html").write_text(dashboard_html(m))
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "processed" / "metrics.json").write_text(json.dumps(m, indent=2, sort_keys=True))
