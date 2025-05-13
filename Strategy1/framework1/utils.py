# utils.py
import pandas as pd

def is_rise(df, idx, params):
    if idx < 1:
        return False
    recent_rise = (df['High'].iloc[idx] - df['Low'].iloc[idx-1]) / df['Low'].iloc[idx-1]
    return recent_rise >= params.rise_min

def is_consolidating(df, params):
    high, low = df['High'].max(), df['Low'].min()
    return (high - low) / low <= params.cons_max_range

def is_doji(row, params):
    range_ = row['High'] - row['Low']
    body = abs(row['Open'] - row['Close'])
    return body <= range_ * params.doji_body_frac

def volume_dropping(df, idx, params):
    if idx < params.vol_compare_hours:
        return False
    curr_vol = df['Volume'].iloc[idx]
    prev_vol = df['Volume'].iloc[idx - params.vol_compare_hours: idx]
    return curr_vol < prev_vol.min()
