# NEAR investment thesis: usage moved to Intents, value capture has not followed (yet)

**Snapshot:** {{snapshot_date}} · **Rebuild:** `python build.py` (live data) or `python build.py --offline` (this exact snapshot)
**Dashboard:** `docs/index.html` (live at https://erfanmoheb.github.io/near-intents-thesis/) · Every number below is filled in by the build from `data/processed/metrics.json`. None are typed by hand.

*Not financial advice. This is an evidence review written for the NEAR HACKATHON Investment Thesis track.*

## 1. The claim

NEAR's long-term case now rests on one product: **NEAR Intents**, a cross-chain swap and settlement layer. Over the past two years it has become real, fee-paying demand, while raw on-chain activity on NEAR collapsed.

So the investable question is no longer "is NEAR used?" It is **"does the NEAR token capture that use?"** The data answers yes to usage. It does not yet show capture.

**Tested hypothesis (H1, from the track brief):** weekly changes in NEAR Intents volume track or lead NEAR's price better than raw on-chain activity (transactions, active accounts).

**Result: {{verdict}}.** Tested over {{test_weeks}} weeks, {{test_start}} → {{snapshot_date}}.

## 2. Evidence for the long-term case

1. **Intents is large and growing.**
   - Volume over the last 365 days: **${{intents_365d_volume_usd_bn}}B**.
   - Monthly volume went from ${{intents_first_full_month_usd_m}}M in {{intents_first_full_month}} to a peak of ${{intents_best_month_usd_bn}}B in {{intents_best_month}}.
   - The last full month ({{intents_last_full_month}}) was ${{intents_last_full_month_usd_bn}}B.
2. **It earns fees.**
   - ${{intents_fees_30d_usd_m}}M in fees over the last 30 days, about **${{intents_fees_annualized_usd_m}}M a year**.
   - That is a take rate of {{intents_take_rate_bps_30d}} basis points on volume.
3. **It is now most of NEAR's trading.** Intents was {{intents_share_of_near_dex_90d_pct}}% of all DEX volume attributed to NEAR over the last 90 days.
4. **Dilution has slowed.** Net token supply now grows about {{supply_growth_ann_now_pct}}% a year, down from a {{supply_growth_ann_2024_avg_pct}}% average in 2024.
5. **Fees set against dilution.** Annualized Intents fees equal {{intents_fees_to_issuance_pct}}% of the dollar value of all NEAR issued in the last year (${{issuance_365d_usd_m_at_now_price}}M at today's ${{price_now_usd}}). On {{days_fees_exceed_issuance_2026}} of {{days_tracked_2026}} days so far in 2026, annualized Intents fees were *larger* than the dollar value of new issuance.

## 3. Evidence against

1. **Price does not follow Intents, at any lag we tested.**
   - Weekly: same-week correlation {{intents_volume_usd_lag0}}. The strongest is {{intents_volume_usd_best_corr}} at a {{intents_volume_usd_best_lag}}-week lag, inside a 95% noise band of ±{{intents_volume_usd_band95_maxabs}} (permutation p = {{intents_volume_usd_p_value_best}}).
   - Over {{test4w_blocks}} four-week blocks: same-block correlation {{intents_volume_usd_4w_lag0}}, noise band ±{{intents_volume_usd_4w_band95_maxabs}}.
   - Raw activity does no better. The best transaction correlation is {{txns_best_corr}}; the best active-account correlation is {{active_accounts_best_corr}}. Neither is significant.
   - So H1's "better leading indicator" claim fails. No indicator here leads the price.
2. **Raw activity collapsed, and not only in the counts.** Each figure compares the 30-day average now with its peak:
   - Transactions: {{txns_now_30d}} per day, against a {{txns_peak_month}} peak of {{txns_peak_30d}} (−{{txns_drop_pct}}%).
   - Active accounts: −{{active_accounts_drop_pct}}%.
   - New accounts: −{{new_accounts_drop_pct}}%.
   - Transaction fees paid in NEAR: −{{txn_fee_drop_pct}}%. The drop shows up in money paid, not just in counting.
3. **The protocol barely burns.**
   - {{burned_365d_near_m}}M NEAR was burned in 365 days, against {{gross_issued_365d_near_m}}M issued.
   - Burn offsets {{burn_share_of_issuance_now_pct}}% of issuance (90-day window).
4. **Valuation is rich next to Intents revenue.** The market cap of ${{market_cap_now_usd_bn}}B is **{{mcap_to_intents_fees_now}}×** annualized Intents fees, and that is before asking whether those fees reach token holders at all.
5. **Price history is a drawdown, not a trend.**
   - NEAR's 30-day average peaked at ${{price_peak_30d_usd}} ({{price_peak_month}}).
   - Since 2025 it has traded as low as ${{price_low_since_2025_usd}} ({{price_low_since_2025_date}}).
   - Today's price is ${{price_now_usd}}.

## 4. What this data cannot answer

- **Where Intents fees go.** The fees could go to NEAR holders, a protocol treasury, or solvers and front-ends. Public fee data measures fees paid, not their destination. This is the most important missing piece for the thesis.
- **Why on-chain activity fell.** The drop is consistent across transactions, accounts and fees paid. The cause (incentive programs ending, apps moving, bot activity) is not visible in these series.
- **Staking yield and validator economics.** These sources don't include them.
- **Intents by chain pair or by unique user.** That needs the NEAR Intents Explorer API, which requires a partner JWT. It was left out so anyone can rebuild without credentials.

## 5. What would change my mind

**Toward bullish:**
- A verifiable mechanism routes Intents fees into NEAR (buyback or burn), and it shows up as net supply growth falling well below today's {{supply_growth_ann_now_pct}}% a year.
- Or the lead-lag test turns significant in Intents' favor as the sample grows. The test re-runs on every build.

**Toward bearish:**
- Intents monthly volume stays below half its best month (${{intents_best_month_usd_bn}}B) for three straight months.
- Or the take rate falls below half of today's {{intents_take_rate_bps_30d}} basis points, which would mean volume is being bought with fees.

## 6. Conclusion

NEAR has found product-market fit as a cross-chain settlement layer. The token is a claim on that success only if value capture is built and becomes visible on-chain.

The dashboard tracks the three numbers that would show it happening:
- Intents fees.
- Fee burn as a share of issuance.
- Net supply growth.

Until those move, the evidence supports *"NEAR the network works"* more than *"NEAR the token captures it"*.

## Method notes

- **Weekly series.** Price is the week's close (Sunday). Intents volume and transactions are weekly sums; active accounts are a weekly mean. The test window starts 60 days after Intents data begins, to skip the launch ramp.
- **Test.** Pearson correlation of weekly log-changes at lags −8…+8 weeks. Significance comes from a family-wise 95% band: the maximum |corr| across all lags under 2,000 circular shifts of the activity series, with a fixed seed so results reproduce.
- **Burn.** The NEAR protocol burns 70% of transaction fees; the remaining 30% goes to contracts. Gross issuance = change in total supply + burned fees.
- **Valuation.** Market cap is NearBlocks' figure. Intents fees are annualized as the trailing 30-day sum × 365/30.
