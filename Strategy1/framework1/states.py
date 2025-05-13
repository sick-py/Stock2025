import pandas as pd
from params import PatternParams
from utils import is_rise, is_consolidating, is_doji, volume_dropping

class State:
    def __init__(self, detector):
        self.detector = detector

    def next_state(self, df, idx):
        pass

class UndefinedState(State):
    def next_state(self, df, idx):
        if is_rise(df, idx, self.detector.params):
            return RisingState(self.detector, idx, 1)
        return self

class RisingState(State):
    def __init__(self, detector, start_idx, hours):
        super().__init__(detector)
        self.start_idx = start_idx
        self.hours = hours

    def next_state(self, df, idx):
        params = self.detector.params
        self.hours += 1

        if self.hours > params.stage1_max_hours:
            return UndefinedState(self.detector)

        total_rise = (df['High'].iloc[idx] - df['Low'].iloc[self.start_idx]) / df['Low'].iloc[self.start_idx]

        if total_rise >= params.rise_min and total_rise <= params.rise_max:
            if self.hours >= params.stage1_min_hours:
                return ConsolidationState(self.detector, idx + 1, 0)
            return self
        return UndefinedState(self.detector)

class ConsolidationState(State):
    def __init__(self, detector, start_idx, hours):
        super().__init__(detector)
        self.start_idx = start_idx
        self.hours = hours

    def next_state(self, df, idx):
        params = self.detector.params
        self.hours += 1

        if self.hours > params.cons_max_hours:
            return UndefinedState(self.detector)

        cons_df = df.iloc[self.start_idx:idx+1]
        if is_consolidating(cons_df, params):
            if self.hours >= params.cons_min_hours:
                return VolumeDropState(self.detector, idx + 1)
            return self
        return UndefinedState(self.detector)

class VolumeDropState(State):
    def __init__(self, detector, idx):
        super().__init__(detector)
        self.idx = idx

    def next_state(self, df, idx):
        params = self.detector.params
        if idx >= len(df):
            return UndefinedState(self.detector)

        if is_doji(df.iloc[idx], params) and volume_dropping(df, idx, params):
            self.detector.signals.append(idx)
        return UndefinedState(self.detector)
