# run_hourly_pattern.py

from pattern import PatternDetector, PatternParams
from backtest import run_backtest
import data
import sys
from yahoo_fin import stock_info as si
import pandas as pd
import yfinance as yf

# df1 = pd.DataFrame(si.tickers_sp500())
# df1 = pd.DataFrame( si.tickers_nasdaq() )
df1 = pd.DataFrame( si.tickers_dow() )
symbols = df1[0].tolist()[:2]
print(len(df1))

start_date = "2024-01-01"
end_date = "2025-03-01"


for symbol in symbols:
    print(f"\n=== Running for {symbol} ===")
    try:
        df = data.fetch_data_Alpha(symbol)
        detector = PatternDetector(PatternParams())
        signals = detector.find_signals(df)
        results = run_backtest(signals)

        print("\n--- Trade Summary ---")
        print(results)
        print("\nTotal Trades:", len(results))
        print("Total Profit:", results['profit'].sum() if 'profit' in results else 0)
        if 'return_pct' in results.columns:
            print("Total Return %:", results['return_pct'].sum())
        else:
            print("Total Return %: 0")

    except Exception as e:
        print(f"Error processing {symbol}: {e}")
