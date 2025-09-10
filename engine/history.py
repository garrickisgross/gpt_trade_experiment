import pandas as pd
import yfinance as yf
from typing import List

def write_to_csv(from_db: pd.DataFrame, dest_file) -> None:
    csv = from_db.to_csv()
    with open(dest_file,'x') as f:
        f.write(csv)
    

def get_history(tickers: List[str], period: str = "1y", interval: str = "1d", auto_adjust: bool = True) -> pd.DataFrame:
    wide = yf.download(
        tickers=" ".join(tickers),
        period=period,
        interval=interval,
        auto_adjust=auto_adjust,
        group_by="ticker",
        progress=False
    )

    if not isinstance(wide.columns, pd.MultiIndex): # type: ignore
        # Single ticker came back as single-level columns -> wrap with a ticker level
        wide = pd.concat({tickers[0]: wide}, axis=1)

    # Figure out which level is the ticker, then make (Field, Ticker)
    lvl0 = set(map(str, wide.columns.get_level_values(0))) # type: ignore
    ticker_level = 0 if any(t in lvl0 for t in tickers) else 1
    if ticker_level == 0:
        wide = wide.swaplevel(0, 1, axis=1) # type: ignore
    wide = wide.sort_index(axis=1) # type: ignore
    wide.columns.names = ["Field", "Ticker"]

    wide = wide

    # Ensure the index is named/date-like for clarity
    wide.index.name = "Date" # type: ignore

    # Build a truly "tidy" dataframe: one row per date per ticker
    parts = []
    for t in tickers:
        # When multiple tickers are requested, columns are like ('Open','AAPL'), ('High','AAPL'), etc.
        # When only one ticker, we normalized above.
        # Some tickers may be missing if yfinance couldn't fetch; skip safely
        cols = [c for c in wide.columns if (isinstance(c, tuple) and c[1] == t) or (not isinstance(c, tuple))] # type: ignore
        if not cols:
            continue
        sub = wide[cols].copy() # type: ignore
        if isinstance(sub.columns, pd.MultiIndex):
            # Reorder to consistent field order and drop missing ones
            want = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
            have = [f for f, tt in sub.columns if f in want]
            sub = sub.loc[:, [(f, t) for f in have if (f, t) in sub.columns]]
            sub.columns = [f for f, _ in sub.columns]
        # Tag ticker and reset index for tidy shape
        sub["Ticker"] = t
        sub = sub.reset_index()
        parts.append(sub)

    tidy = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["Date","Ticker","Open","High","Low","Close","Adj Close","Volume"]
    )

    # Optional: sort and drop all-NaN rows (holidays, halted, etc.)
    tidy = tidy.sort_values(["Ticker", "Date"]).dropna(how="all", subset=["Open","High","Low","Close","Volume"])

    # For convenience, return both
    return tidy


