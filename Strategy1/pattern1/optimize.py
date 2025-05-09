# optimize.py

#To optimize the strategy’s parameters, we implement a simple grid search over a given set of parameter values. The grid_search function will accept 
# a price dataset and a dictionary of parameter ranges to try, then evaluate the total profit for each combination. For each parameter combination, 
# it will instantiate a PatternDetector with those parameters, run find_signals and the backtest, and record the outcome. Finally, it returns the 
# best-performing parameter set and the corresponding profit. All results can also be returned or logged for analysis. We’ll also discuss how one 
# could integrate Bayesian optimization for more efficient hyperparameter tuning. Bayesian optimization can converge to optimal parameters in fewer 
# iterations by intelligently selecting combinations to evaluate which is useful if the parameter space is large or backtests are slow.

from itertools import product
from math import inf
from pattern import PatternParams, PatternDetector
from backtest import run_backtest

def grid_search(hourly_data, param_grid: dict):
    """
    Exhaustively search through the combinations of parameters in param_grid to find the best total profit.
    :param hourly_data: DataFrame of hourly data to run the backtest on.
    :param param_grid: Dictionary where keys are parameter names (matching PatternParams fields) and
                       values are lists of values to try for that parameter.
                       e.g., {"rise_min": [0.05, 0.07], "rise_max": [0.10, 0.12]}
    :return: (best_params, best_profit, results) where best_params is a PatternParams object of the best combo,
             best_profit is the total profit achieved, and results is a list of (params, profit) for all combos.
    """
    best_profit = -inf
    best_params = None
    results = []
    # Generate all combinations of parameter values
    keys = list(param_grid.keys())
    for combo in product(*(param_grid[k] for k in keys)):
        # Build a PatternParams object with this combination
        params_kwargs = {k: v for k, v in zip(keys, combo)}
        params = PatternParams(**params_kwargs)
        # Basic validity check: ensure min <= max for ranges (rise and consolidation days)
        if params.rise_min > params.rise_max or params.stage1_min_days > params.stage1_max_days or params.cons_min_days > params.cons_max_days:
            continue  # skip invalid combos
        detector = PatternDetector(params)
        signals = detector.find_signals(hourly_data)
        trades_df = run_backtest(signals)
        total_profit = trades_df.total_profit
        results.append((params, total_profit))
        if total_profit > best_profit:
            best_profit = total_profit
            best_params = params
    return best_params, best_profit, results

# Example of integrating Bayesian optimization (conceptual, not a full implementation):
try:
    from bayes_opt import BayesianOptimization
except ImportError:
    BayesianOptimization = None

def bayesian_optimize(hourly_data, param_bounds: dict, init_points=5, n_iter=25):
    """
    Optimize parameters using Bayesian Optimization to maximize total profit.
    Requires bayes_opt library. param_bounds is a dict of param name -> (min, max) range.
    """
    if BayesianOptimization is None:
        raise ImportError("bayes_opt library is required for Bayesian optimization.")
    # Define the objective function for Bayesian optimizer
    def objective(**kwargs):
        # Round any integer parameters (like days) to nearest int
        kwargs = {k: (int(v) if "days" in k else v) for k,v in kwargs.items()}
        params = PatternParams(**kwargs)
        # Ensure parameter validity
        if params.rise_min > params.rise_max or params.stage1_min_days > params.stage1_max_days or params.cons_min_days > params.cons_max_days:
            # Return a very low profit for invalid parameter sets
            return -1e9
        detector = PatternDetector(params)
        signals = detector.find_signals(hourly_data)
        trades_df = run_backtest(signals)
        return trades_df.total_profit
    # Set up the Bayesian optimizer
    optimizer = BayesianOptimization(f=objective, pbounds=param_bounds, verbose=0)
    optimizer.maximize(init_points=init_points, n_iter=n_iter)
    best = optimizer.max['params']
    # Convert best params to proper types
    best = {k: (int(v) if "days" in k else v) for k,v in best.items()}
    best_params = PatternParams(**best)
    best_profit = optimizer.max['target']
    return best_params, best_profit
