# ORB (LONG call + SHORT put) - stop-loss x target x time-exit grid

**Status:** 2371 ORB entries in 2025-11-01..2026-11-10, 1286 with option data (68 dropped for option-candle coverage < 90%), 2 skipped

**Period (entry dates):** 2025-11-01 to 2026-11-10  |  **Stocks:** top10

## Rules

ORB.  ORB = High / Low of the 1-minute candles from 09:15 to 09:30.  LONG (ATM call): first 1-minute candle from 09:30 (to 15:20) that CLOSES above the ORB high; SHORT (ATM put): first one that CLOSES below the ORB low; volume filter: breakout candle volume >= 1.5 x the average of the previous 10 one-minute candles.  One trade per stock per day (first side to signal).  Option = ATM at the entry minute (ITM-1..3 if the ATM series has no candle), price = close of the entry minute.  Stop-loss ORB = stock beyond the ORB low (LONG) / high (SHORT); BRK = stock beyond the low (LONG) / high (SHORT) of the breakout candle; fixed % = % of the option premium; mixes (ORB+20 ...) close at whichever hits first.

LONG and SHORT are reported separately: `long/` and `short/`.

## Best variant by total PnL (per direction)

| strategy   | exit_rule   | sl   |   tp |   trades |   win_pct |   total_pnl |   roi_pct |   profit_factor |   max_drawdown |
|:-----------|:------------|:-----|-----:|---------:|----------:|------------:|----------:|----------------:|---------------:|
| ORB_LONG   | 15:30       | BRK  |   20 |      570 |     26.84 |      176395 |      0.58 |            1.2  |         -75626 |
| ORB_SHORT  | 15:30       | 60%  |   60 |      648 |     49.85 |      915538 |      2.6  |            1.27 |        -360698 |
