# run.py
from detector import PatternDetector
from data import fetch_data
from backtest import run_backtest

symbols = ["AAPL", "MSFT"]
detector = PatternDetector()

import yfinance as yf

df = yf.download("TSLA", period="10d", interval="1d", progress=False)
print(df.head())

if df.empty:
    print("No data returned")


for symbol in symbols:
    df = fetch_data(symbol, "yf")
    signals = detector.find_signals(df)
    results = run_backtest(signals)
    print(f"\n--- {symbol} ---\n{results}")
