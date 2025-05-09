# pattern.py

import pandas as pd
from dataclasses import dataclass

# We define a PatternParams class to hold all tunable parameters for the pattern definition. 
# This makes it easy to adjust thresholds or extend with new parameters. 

# is_stage3_signal(idx, daily_df): Checks if the day at idx in the daily DataFrame is an indecisive candlestick (doji) with volume lower 
# than previous days (Stage 3 criteria).

# is_consolidation(start_idx, end_idx, daily_df): Checks if the price between start_idx and end_idx (inclusive) stayed within a tight range 
# (Stage 2 criteria).

# is_big_rise(start_idx, end_idx, daily_df): Checks if there was a rise of the required percentage between start_idx and end_idx (Stage 1 criteria).

# find_signals(hourly_df): Converts hourly data to daily, then iterates through each potential Stage 3 day and verifies if preceding Stage 2 and Stage 1 
# conditions are met. Returns a list of detected pattern signals (with buy/sell info).

# pattern_hourly.py

import pandas as pd
from dataclasses import dataclass

@dataclass
class PatternParams:
    # Stage 1: Big Rise
    rise_min: float = 0.02           # 5%
    rise_max: float = 0.10           # 10%
    stage1_min_hours: int = 6
    stage1_max_hours: int = 12

    # Stage 2: Consolidation
    cons_min_hours: int = 6
    cons_max_hours: int = 30
    cons_max_range: float = 0.09     # 5% range

    # Stage 3: Doji + Volume Drop
    doji_body_frac: float = 0.6
    vol_compare_hours: int = 2       # must be lower than N previous bars

class PatternDetector:
    def __init__(self, params: PatternParams = None):
        self.params = params or PatternParams()

    def is_doji(self, row) -> bool:
        high, low = row['High'], row['Low']
        open_, close = row['Open'], row['Close']
        if high == low:
            return False
        body = abs(open_ - close)
        range_ = high - low
        return body <= self.params.doji_body_frac * range_

    def is_volume_dropped(self, idx: int, df: pd.DataFrame) -> bool:
        if idx < self.params.vol_compare_hours:
            return False
        curr_vol = df.iloc[idx]['Volume']
        prev_vol = df.iloc[idx - self.params.vol_compare_hours:idx]['Volume']
        return (prev_vol > curr_vol).all()

    def is_consolidating(self, df: pd.DataFrame) -> bool:
        high = df['High'].max()
        low = df['Low'].min()
        return (high - low) / low <= self.params.cons_max_range

    def find_signals(self, df: pd.DataFrame):
        signals = []
        n = len(df)
        for i in range(n - self.params.stage1_min_hours - self.params.cons_min_hours - 2):
            # Stage 1: Look for rise
            for h1 in range(self.params.stage1_min_hours, self.params.stage1_max_hours + 1):
                stage1 = df.iloc[i:i + h1]
                if stage1.empty:
                    continue
                low = stage1['Low'].min()
                high = stage1['High'].max()

                try:
                    low = float(low.iloc[0]) if hasattr(low, 'iloc') else float(low)
                    high = float(high.iloc[0]) if hasattr(high, 'iloc') else float(high)
                except:
                    continue

                if low == 0:
                    continue

                rise = (high - low) / low

                try:
                    rise = float(rise)
                except:
                    continue

                if not (self.params.rise_min <= rise <= self.params.rise_max):
                    continue

                # Stage 2: Look for consolidation right after Stage 1
                stage2_start = i + h1
                for h2 in range(self.params.cons_min_hours, self.params.cons_max_hours + 1):
                    if stage2_start + h2 + 1 >= n:
                        break
                    stage2 = df.iloc[stage2_start:stage2_start + h2]
                    if stage2.empty:
                        continue
                    try:
                        if not bool(self.is_consolidating(stage2)):
                            continue
                    except Exception:
                        continue

                    # Stage 3: Doji + low volume
                    stage3_idx = stage2_start + h2
                    row = df.iloc[stage3_idx]
                    if self.is_doji(row) and self.is_volume_dropped(stage3_idx, df):
                        # Buy next bar, sell one bar later
                        if stage3_idx + 2 < n:
                            buy_row = df.iloc[stage3_idx + 1]
                            sell_row = df.iloc[stage3_idx + 2]
                            trade = {
                                "stage1_range": rise,
                                "buy_time": buy_row.name,
                                "sell_time": sell_row.name,
                                "buy_price": float(buy_row['Open']),
                                "sell_price": float(sell_row['Open']),
                                "profit": float(sell_row['Open'] - buy_row['Open'])
                            }
                            signals.append(trade)
                    break  # break inner loop after valid stage2 attempt
                break  # break if stage1 found
        return signals
