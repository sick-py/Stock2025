import optuna
import pandas as pd
import numpy as np
from dataclasses import dataclass
from detector import PatternDetector
from data import fetch_data
from backtest import run_backtest, evaluate_results
import matplotlib.pyplot as plt
import os
from utils import to_float
from params import PatternParams


url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
df = pd.read_html(url)[0]
symbol_list = df['Symbol'].tolist()[0:20]
#print(symbol_list)

symbol_list = ["ADBE", "AMD", "AES", "AFL", "APD", "ANET", "APO", "APA", "AMAT", "AMP", "GOOGL", "AME", "AAPL", "GOOG", "ALLE", "AIG"]

detector = PatternDetector()


# === Step 1: Define Optuna Search Objective ===
def objective(trial):
    # Suggest params
    params = PatternParams(
        rise_min=trial.suggest_float("rise_min", 0.06, 0.10),
        rise_max=trial.suggest_float("rise_max", 0.10, 0.30),
        stage1_min_hours=trial.suggest_int("stage1_min_hours", 3, 9),
        stage1_max_hours=trial.suggest_int("stage1_max_hours", 6, 18),
        cons_min_hours=trial.suggest_int("cons_min_hours", 3, 10),
        cons_max_hours=trial.suggest_int("cons_max_hours", 20, 40),
        cons_max_range=trial.suggest_float("cons_max_range", 0.01, 0.10),
        doji_body_frac=trial.suggest_float("doji_body_frac", 0.05, 0.5),
        vol_compare_hours=trial.suggest_int("vol_compare_hours", 3, 6),
    )

    total_score = 0
    for symbol in symbol_list:
        df = fetch_data(symbol, "yf")
        detector = PatternDetector(params)
        signals = detector.find_signals(df)
        results = run_backtest(signals)
        score = evaluate_results(results)
        total_score += score

    return total_score

# === Step 2: Run Optimization ===
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=50)  # ← try 100+ for better results

# === Step 3: Print Best Params ===
print("\n✅ Best Params Found:")
print(study.best_params)
print(f"Score: {study.best_value}")