# PULLBACK re-cross on options - Dhan data - LONG and SHORT reported separately

**Status:** PARTIAL - run again  |  2023-11-03 .. 2026-11-03  |  Nifty filter: intraday  |  Cap Rs 60,000

LONG = breakout above the 10-day high, pullback, re-cross up -> buy the CALL (Nifty must be green).  SHORT = breakdown below the 10-day low, bounce, re-cross down -> buy the PUT (Nifty must be red).  ATM at the entry minute (else nearest ITM), strike locked, fill = close of the entry-minute option candle.

## LONG (calls)

No trades.

```
{
 "no_equity_id": 0,
 "too_little_daily": 0,
 "no_stock_minute_data": 2,
 "no_cross_minute": 19,
 "no_nifty_minute_data": 0,
 "nifty_filter_failed": 154,
 "no_option_candle_atm_or_itm": 0,
 "no_lot_size": 0,
 "one_lot_too_expensive": 0
}
```

## SHORT (puts)

No trades.

```
{
 "no_equity_id": 0,
 "too_little_daily": 0,
 "no_stock_minute_data": 0,
 "no_cross_minute": 0,
 "no_nifty_minute_data": 0,
 "nifty_filter_failed": 0,
 "no_option_candle_atm_or_itm": 0,
 "no_lot_size": 0,
 "one_lot_too_expensive": 0
}
```

The best of 80 variants is chosen after seeing the results, so it is optimistic: check that neighbouring variants and every year look similar. Charges and slippage are not included; option candles with no trade in a minute are missing, so illiquid-stock fills can be better than real. Files per side: summary_<SIDE>.csv, all_trades_<SIDE>.csv.gz, entries_<SIDE>.csv, best_variant_trades_<SIDE>.csv.