from dataclasses import dataclass

@dataclass
class PatternParams:
    rise_min: float = 0.05         # 5%
    rise_max: float = 0.10         # 10%
    stage1_min_hours: int = 6
    stage1_max_hours: int = 12

    cons_min_hours: int = 6
    cons_max_hours: int = 30
    cons_max_range: float = 0.05   # within 5% range

    doji_body_frac: float = 0.4    # small candle body (40% of range)
    vol_compare_hours: int = 3     # Volume drop compared to previous 2 hours
