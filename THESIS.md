# NEAR investment thesis: usage moved to Intents, value capture has not followed (yet)

**Snapshot:** 2026-11-05 · **Rebuild:** `python build.py` (live data) or `python build.py --offline` (this exact snapshot)
**Dashboard:** `docs/index.html` (live at https://erfanmoheb.github.io/near-intents-thesis/) · Every number below is filled in by the build from `data/processed/metrics.json`. None are typed by hand.

*Not financial advice. This is an evidence review written for the NEAR HACKATHON Investment Thesis track.*

## 1. The claim

NEAR's long-term case now rests on one product: **NEAR Intents**, a cross-chain swap and settlement layer. Over the past two years it has become real, fee-paying demand, while raw on-chain activity on NEAR collapsed.

So the investable question is no longer "is NEAR used?" It is **"does the NEAR token capture that use?"** The data answers yes to usage. It does not yet show capture.

**Tested hypothesis (H1, from the track brief):** weekly changes in NEAR Intents volume track or lead NEAR's price better than raw on-chain activity (transactions, active accounts).

**Result: NOT SUPPORTED.** Tested over 89 weeks, 2025-02-08 → 2026-11-05.

## 2. Evidence for the long-term case

1. **Intents is large and growing.**
   - Volume over the last 365 days: **$32.92B**.
   - Monthly volume went from $6.4M in Jan 2025 to a peak of $4.8B in Sep 2026.
   - The last full month (Oct 2026) was $3.99B.
2. **It earns fees.**
   - $6.13M in fees over the last 30 days, about **$74.5M a year**.
   - That is a take rate of 15.31 basis points on volume.
3. **It is now most of NEAR's trading.** Intents was 83.9% of all DEX volume attributed to NEAR over the last 90 days.
4. **Dilution has slowed.** Net token supply now grows about 2.5% a year, down from a 4.91% average in 2024.
5. **Fees set against dilution.** Annualized Intents fees equal 57.8% of the dollar value of all NEAR issued in the last year ($128.9M at today's $4.01). On 68 of 309 days so far in 2026, annualized Intents fees were *larger* than the dollar value of new issuance.

## 3. Evidence against

1. **Price does not follow Intents, at any lag we tested.**
   - Weekly: same-week correlation -0.04. The strongest is 0.2 at a 8-week lag, inside a 95% noise band of ±0.27 (permutation p = 0.53).
   - Over 21 four-week blocks: same-block correlation 0.02, noise band ±0.6.
   - Raw activity does no better. The best transaction correlation is -0.2; the best active-account correlation is -0.14. Neither is significant.
   - So H1's "better leading indicator" claim fails. No indicator here leads the price.
2. **Raw activity collapsed, and not only in the counts.** Each figure compares the 30-day average now with its peak:
   - Transactions: 682,915 per day, against a Jan 2025 peak of 8,296,230 (−91.8%).
   - Active accounts: −97%.
   - New accounts: −98.2%.
   - Transaction fees paid in NEAR: −89.7%. The drop shows up in money paid, not just in counting.
3. **The protocol barely burns.**
   - 0.42M NEAR was burned in 365 days, against 32.1M issued.
   - Burn offsets 0.84% of issuance (90-day window).
4. **Valuation is rich next to Intents revenue.** The market cap of $5.25B is **70.4×** annualized Intents fees, and that is before asking whether those fees reach token holders at all.
5. **Price history is a drawdown, not a trend.**
   - NEAR's 30-day average peaked at $15.98 (Jan 2022).
   - Since 2025 it has traded as low as $0.96 (Feb 12, 2026).
   - Today's price is $4.01.

## 4. What this data cannot answer

- **Where Intents fees go.** The fees could go to NEAR holders, a protocol treasury, or solvers and front-ends. Public fee data measures fees paid, not their destination. This is the most important missing piece for the thesis.
- **Why on-chain activity fell.** The drop is consistent across transactions, accounts and fees paid. The cause (incentive programs ending, apps moving, bot activity) is not visible in these series.
- **Staking yield and validator economics.** These sources don't include them.
- **Intents by chain pair or by unique user.** That needs the NEAR Intents Explorer API, which requires a partner JWT. It was left out so anyone can rebuild without credentials.

## 5. What would change my mind

**Toward bullish:**
- A verifiable mechanism routes Intents fees into NEAR (buyback or burn), and it shows up as net supply growth falling well below today's 2.5% a year.
- Or the lead-lag test turns significant in Intents' favor as the sample grows. The test re-runs on every build.

**Toward bearish:**
- Intents monthly volume stays below half its best month ($4.8B) for three straight months.
- Or the take rate falls below half of today's 15.31 basis points, which would mean volume is being bought with fees.

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
