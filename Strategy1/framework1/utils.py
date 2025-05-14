# utils.py
import pandas as pd

def to_float(val):
    """Safely convert a scalar or Series to float."""
    if isinstance(val, pd.Series):
        return float(val.iloc[0])
    return float(val)


def is_rise(df: pd.DataFrame, idx: int, params) -> bool:
    if idx < 1 or idx >= len(df):
        return False
    high_price = to_float(df['High'].iloc[idx])
    low_price = to_float(df['Low'].iloc[idx - 1])
    rise_pct = (high_price - low_price) / low_price
    return params.rise_min <= rise_pct <= params.rise_max




def is_consolidating(df, params):
    high = df['High'].max()
    low = df['Low'].min()

    # Ensure scalar floats
    high = to_float(high)
    low = to_float(low)

    if low == 0:
        return False

    range_pct = (high - low) / low
    return range_pct <= params.cons_max_range



def is_doji(df, idx, params, min_hours=3, max_hours=6):
    """
    Check if a multi-hour doji exists ending at index `idx`.
    Doji body (|close - open|) must be < `doji_body_frac` * (high - low) over the window.
    """
    for window in range(min_hours, max_hours + 1):
        if idx - window + 1 < 0:
            continue  # not enough data

        segment = df.iloc[idx - window + 1 : idx + 1]

        high = to_float(segment['High'].max())
        low = to_float(segment['Low'].min())
        open_ = to_float(segment['Open'].iloc[0])
        close = to_float(segment['Close'].iloc[-1])

        range_ = high - low
        if range_ == 0:
            continue  # avoid divide by zero

        body = abs(close - open_)
        if body <= params.doji_body_frac * range_:
            return True  # found a qualifying multi-hour doji
    return False


def volume_dropping(df, idx, params, min_hours=3, max_hours=6):
    for window in range(min_hours, max_hours + 1):
        if idx - window - params.vol_compare_hours < 0:
            continue  # Not enough data

        curr_window = df.iloc[idx - window + 1 : idx + 1]
        prev_window = df.iloc[idx - window - params.vol_compare_hours + 1 : idx - window + 1]

        if curr_window.empty or prev_window.empty:
            continue

        try:
            curr_avg_vol = to_float(curr_window['Volume'].mean(skipna=True))
            prev_avg_vol = to_float(prev_window['Volume'].mean(skipna=True))
        except Exception as e:
            print(f"[volume_dropping] Error at idx={idx}: {e}")
            continue

        if curr_avg_vol < prev_avg_vol:
            return True

    return False


