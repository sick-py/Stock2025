from params import PatternParams
from states import UndefinedState

class PatternDetector:
    def __init__(self, params=None):
        self.params = params or PatternParams()
        self.signals = [] # Whenever a pattern is matched (inside VolumeDropState), the index is added to self.signals.

    def find_signals(self, df):
        state = UndefinedState(self)
        for idx in range(len(df)):
            state = state.next_state(df, idx)

        # Once done looping → call generate_trades() to convert signal indices into actual trades.
        return self.generate_trades(df)

    def generate_trades(self, df):
        trades = []
        for signal_idx in self.signals:
            if signal_idx + 6 < len(df):
                buy_row = df.iloc[signal_idx + 1]
                sell_row = df.iloc[signal_idx + 6]
                trade = {
                    "buy_time": buy_row.name,
                    "sell_time": sell_row.name,
                    "buy_price": buy_row['Open'],
                    "sell_price": sell_row['Open'],
                    "profit": sell_row['Open'] - buy_row['Open']
                }
                trades.append(trade)
            else:
                print("should buy at " + signal_idx + " but it's the newest day")
        return trades
