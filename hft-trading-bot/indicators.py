# indicators.py

import numpy as np

class FastIndicators:
    @staticmethod
    def simple_moving_average(prices: list, window: int) -> float:
        """NumPy ka use karke ultra-fast SMA calculation"""
        if len(prices) < window:
            return 0.0
        arr = np.array(prices[-window:])
        return float(np.mean(arr))

    @staticmethod
    def check_crossover(fast_ma: float, slow_ma: float, prev_fast: float, prev_slow: float) -> str:
        """Crossover detect karta hai: 'BUY', 'SELL', ya 'NONE'"""
        if prev_fast <= prev_slow and fast_ma > slow_ma:
            return "BUY"
        elif prev_fast >= prev_slow and fast_ma < slow_ma:
            return "SELL"
        return "NONE"

