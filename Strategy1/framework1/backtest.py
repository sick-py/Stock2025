# backtest.py
import pandas as pd
from utils import to_float
import numpy as np

def run_backtest(signals):
    df = pd.DataFrame(signals)
    if df.empty:
        return df
    df["return_pct"] = (df["sell_price"] - df["buy_price"]) / df["buy_price"]
    df["cumulative_profit"] = df["profit"].cumsum()
    return df

def flatten_trade_columns(results: pd.DataFrame) -> pd.DataFrame:
    # Apply `.item()` to get scalar from each Series
    for col in ['profit', 'return_pct', 'buy_price', 'sell_price']:
        if col in results.columns:
            results[col] = results[col].apply(lambda x: x.item() if hasattr(x, "item") else x)
    return results

def evaluate_results(results: pd.DataFrame) -> float:
    #print(results)
    if results.empty:
        return 0  # harsh penalty

    results = flatten_trade_columns(results)
    results['profit'] = pd.to_numeric(results['profit'], errors='coerce')
    results.dropna(subset=['profit'], inplace=True)

    if results.empty:
        return 0

    if 'return_pct' in results.columns:
        results['return_pct'] = pd.to_numeric(results['return_pct'], errors='coerce')
        results.dropna(subset=['return_pct'], inplace=True)
        total_return = results['return_pct'].sum()
    else:
        total_return = 0

    num_trades = len(results)
    win_rate = (results['profit'] > 0).mean() if num_trades > 0 else 0

    score = total_return + (win_rate * 0.1) - (0.01 * num_trades)

    if np.isnan(score) or not np.isfinite(score):
        return 0

    return score
