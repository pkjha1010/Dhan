# Live GAP strategy backtest: 2026-08-27 to 2026-11-26

Funds Rs 1,000,000 (compounding), 7% per trade, costs 0.5% + Rs 47 per trade (estimate)

**Net PnL Rs 209,398 (20.9% on funds)**, max drawdown Rs -86,807 (-7.8%, day-end), winning days 19 / 35

## By strategy

| strategy | trades | win_pct | gross_pnl | costs | net_pnl | avg_ret_pct | profit_factor |
|---|---|---|---|---|---|---|---|
| ALL | 82 | 52.4 | 247634 | 38236 | 209398 | 4.4 | 1.32 |
| GAPL | 39 | 51.3 | 97583 | 17912 | 79671 | 3.79 | 1.21 |
| GAPS | 43 | 53.5 | 150051 | 20324 | 129727 | 4.95 | 1.47 |

## By month

| month | strategy | trades | win_pct | gross_pnl | costs | net_pnl | avg_ret_pct | profit_factor |
|---|---|---|---|---|---|---|---|---|
| 2026-09 | GAPL | 4 | 50.0 | 4924 | 1535 | 3389 | 2.89 | 1.08 |
| 2026-09 | GAPS | 20 | 55.0 | 58074 | 8935 | 49139 | 4.43 | 1.35 |
| 2026-10 | GAPL | 14 | 57.1 | 5928 | 6553 | -625 | 2.86 | 1.0 |
| 2026-10 | GAPS | 16 | 68.8 | 162390 | 8270 | 154120 | 12.73 | 3.72 |
| 2026-11 | GAPL | 21 | 47.6 | 86731 | 9824 | 76907 | 4.58 | 1.45 |
| 2026-11 | GAPS | 7 | 14.3 | -70412 | 3120 | -73532 | -11.37 | 0.08 |

## Exit reasons

| strategy | reason | trades | win_pct | gross_pnl | costs | net_pnl | avg_ret_pct | profit_factor |
|---|---|---|---|---|---|---|---|---|
| GAPL | STOP | 1 | 0.0 | -50700 | 343 | -51043 | -60.0 | 0.0 |
| GAPL | TARGET | 10 | 100.0 | 333096 | 5398 | 327698 | 40.66 | inf |
| GAPL | TIME | 28 | 35.7 | -184813 | 12171 | -196984 | -7.1 | 0.39 |
| GAPS | TARGET | 7 | 100.0 | 249127 | 3890 | 245237 | 42.58 | inf |
| GAPS | TIME | 36 | 44.4 | -99076 | 16434 | -115510 | -2.37 | 0.58 |

Trades that used the nearest month because next-month data was missing: 0

## Setups not traded

| strategy | reason | count |
|---|---|---|
| GAPL | 30% fund limit | 1 |
| GAPL | cheap option, OI below 1000 lots | 4 |
| GAPL | level not touched in the entry window | 139 |
| GAPL | max open trades | 8 |
| GAPL | no ATM candle at the entry | 12 |
| GAPL | no option candles | 1 |
| GAPL | no usable option candles for the OTM strikes | 2 |
| GAPL | not in the Dhan stock-option list | 1 |
| GAPS | 30% fund limit | 2 |
| GAPS | cheap option, OI below 1000 lots | 5 |
| GAPS | cheap option, OI below 1000 lots; price at or below Rs 1 | 1 |
| GAPS | day loss stop | 2 |
| GAPS | level not touched in the entry window | 65 |
| GAPS | max open trades | 5 |
| GAPS | no usable option candles for the OTM strikes | 5 |
| GAPS | not in the Dhan stock-option list | 4 |
| GAPS | strike step unknown | 1 |
| GAPS | touched before 09:30 | 69 |
