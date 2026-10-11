Source folder : d3z_results  (1879 part files)
Total rows    : 387,927
CSV files     : 1 (plus all_trades.csv.gz = everything in one file)
Columns       : stock, direction, type, date, first_touch, entry_time, strike, entry, exit_rule, sl, tp, lots, cost, exit_time, exit_price, reason, pnl, thin_data, stock_price

One row = one trade for one combination of entry type / exit rule / stop-loss / target.
To find the best setup: filter on type, exit_rule, sl, tp (and rule when present), then sum pnl and cost.
Example (pandas): t = pd.read_csv('all_trades.csv.gz'); t.groupby(['type','exit_rule','sl','tp']).pnl.sum()
