# backtest_hourly.py

import pandas as pd

def run_backtest(signals: list) -> pd.DataFrame:
    """
    Run a backtest on a list of trade signals.
    Each signal should have buy_time, sell_time, buy_price, sell_price, and profit.
    """
    if not signals:
        return pd.DataFrame(columns=[
            "buy_time", "sell_time", "buy_price", "sell_price", "profit"
        ])

    df = pd.DataFrame(signals)
    df["return_pct"] = (df["sell_price"] - df["buy_price"]) / df["buy_price"] * 100
    df["cumulative_profit"] = df["profit"].cumsum()
    df["cumulative_return"] = df["return_pct"].cumsum()
    return df

