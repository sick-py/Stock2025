# run.py
from detector import PatternDetector
from data import fetch_data
from backtest import run_backtest, evaluate_results
import pandas as pd
import matplotlib.pyplot as plt
import os
from utils import to_float

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
df = pd.read_html(url)[0]
symbol_list = df['Symbol'].tolist()[0:50]
#print(symbol_list)

symbol_list = ["ADBE", "AMD", "AES", "AFL", "APD", "ANET", "APO", "APA", "AMAT", "AMP", "GOOGL", "AME", "AAPL", "GOOG", "ALLE", "AIG"]

detector = PatternDetector()

for symbol in symbol_list:
        df = fetch_data(symbol, "yf")
        signals = detector.find_signals(df)
        results = run_backtest(signals)
        score = evaluate_results(results)
        print(f"{score} for symbol {symbol}")


'''summary = []
all_trades = []

for symbol in symbol_list:
    try:
        print(f"Using yfinance for {symbol}")
        df = fetch_data(symbol, "yf")
        signals = detector.find_signals(df)
        results = run_backtest(signals)

        if not results.empty:
            num_trades = len(results)
            return_pct = to_float(results['return_pct'].sum()) if 'return_pct' in results.columns else None
            avg_return_pct = return_pct / num_trades if num_trades > 0 and return_pct is not None else 0


            if return_pct is None or return_pct == 0:
                continue

            # Summary per stock
            summary.append({
                "Symbol": symbol,
                "Return %": return_pct,
                "Trades": num_trades,
                "Avg Return %": avg_return_pct
            })

            # All trades (exportable)
            results = results.copy()
            results["Symbol"] = symbol
            cols = ["Symbol", "buy_time", "sell_time", "buy_price", "sell_price", "profit", "return_pct"]
            available_cols = [col for col in cols if col in results.columns]
            all_trades.append(results[available_cols])

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# ---------------------- 📤 Export trades to CSV ----------------------
if all_trades:
    trades_df = pd.concat(all_trades, ignore_index=True)
    trades_df.to_csv("all_trades.csv", index=False)
    print("✅ Exported all trades to all_trades.csv")
else:
    print("⚠️ No trades generated.")

# ---------------------- 📊 Plot top N stocks by Return % ----------------------
if summary:
    summary_df = pd.DataFrame(summary)
    summary_df.sort_values(by="Return %", ascending=False, inplace=True)

    top_n = 30
    top_df = summary_df.head(top_n)

    plt.figure(figsize=(16, 6))
    bars = plt.bar(top_df["Symbol"], top_df["Return %"], color="darkorange")

    for bar, trades in zip(bars, top_df["Trades"]):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{trades}T', ha='center', va='bottom', fontsize=8)

    plt.xticks(rotation=90)
    plt.ylabel("Total Return %")
    plt.title(f"Top {top_n} Stocks by Total Return %")
    plt.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.savefig("return_pct_chart.png")
    plt.show()
    print("✅ Saved chart to return_pct_chart.png") '''
