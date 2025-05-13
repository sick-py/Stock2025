# backtest.py
import pandas as pd

def run_backtest(signals):
    df = pd.DataFrame(signals)
    if df.empty:
        return df
    df["return_pct"] = (df["sell_price"] - df["buy_price"]) / df["buy_price"]
    df["cumulative_profit"] = df["profit"].cumsum()
    return df
