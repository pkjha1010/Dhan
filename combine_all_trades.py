"""combine_all_trades.py - merge ALL saved trade rows (every stock, every variant) into plain CSV files you can filter yourself.

No API calls, no dependency on other project files. Works on any results folder made by the d3z / n50x / n10y backtests
(the folder that contains a 'parts' sub-folder with *.csv.gz files).

  FOLDER=d3z_results python combine_all_trades.py          (FOLDER empty = first results folder found)

Output folder: combined_out/<FOLDER>/
  all_trades_01.csv, all_trades_02.csv ...  plain CSV, every file under ~45 MB (GitHub shows/stores such files fine; it truncates
                                            only the on-screen preview of big files - use 'Download raw file' or the workflow artifact)
  all_trades.csv.gz                         the same rows in ONE compressed file (open with Excel/7-zip/pandas)
  README.txt                                row counts, column list, how to filter
"""
import os, sys, glob, gzip, io
import pandas as pd

LIMIT = int(float(os.environ.get("CHUNK_MB") or 45) * 1024 * 1024)
folder = (os.environ.get("FOLDER") or "").strip().strip("/")
if not folder:
    found = [d for d in sorted(glob.glob("*_results")) if glob.glob(f"{d}/parts/*.csv.gz")]
    if not found: sys.exit("No '*_results/parts' folder with saved trades found. Set FOLDER=<results folder name>.")
    folder = found[0]
files = sorted(glob.glob(f"{folder}/parts/*.csv.gz"))
if not files: sys.exit(f"No files in {folder}/parts")
out = f"combined_out/{folder}"; os.makedirs(out, exist_ok=True)
for f in glob.glob(f"{out}/all_trades*"): os.remove(f)

header, n_rows, n_part, size, fh = None, 0, 0, 0, None
gz = gzip.open(f"{out}/all_trades.csv.gz", "wt", newline="", compresslevel=6)
try:
    for f in files:
        df = pd.read_csv(f)
        if header is None: header = list(df.columns); gz.write(",".join(header) + "\n")
        df = df.reindex(columns=header)
        text = df.to_csv(index=False, header=False)
        gz.write(text)
        if fh is None or size + len(text) > LIMIT:
            if fh: fh.close()
            n_part += 1; fh = open(f"{out}/all_trades_{n_part:02d}.csv", "w", newline=""); fh.write(",".join(header) + "\n"); size = 0
        fh.write(text); size += len(text); n_rows += len(df)
finally:
    gz.close()
    if fh: fh.close()
if n_part == 1: os.rename(f"{out}/all_trades_01.csv", f"{out}/all_trades.csv")
with open(f"{out}/README.txt", "w") as r:
    r.write(f"Source folder : {folder}  ({len(files)} part files)\nTotal rows    : {n_rows:,}\nCSV files     : {n_part} (plus all_trades.csv.gz = everything in one file)\n"
            f"Columns       : {', '.join(header)}\n\nOne row = one trade for one combination of entry type / exit rule / stop-loss / target.\n"
            "To find the best setup: filter on type, exit_rule, sl, tp (and rule when present), then sum pnl and cost.\n"
            "Example (pandas): t = pd.read_csv('all_trades.csv.gz'); t.groupby(['type','exit_rule','sl','tp']).pnl.sum()\n")
print(f"{n_rows:,} trade rows from {len(files)} part files -> {out}/  ({n_part} CSV file(s) + all_trades.csv.gz)")
for f in sorted(os.listdir(out)): print(f"  {f}  {os.path.getsize(f'{out}/{f}') / 1e6:.1f} MB")
