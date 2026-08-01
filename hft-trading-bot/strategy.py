# strategy.py

import asyncio
from indicators import FastIndicators
from risk_manager import RiskManager
from executor import OrderExecutor
from logger import LatencyTracker

class TradingStrategy:
    def __init__(self, risk_manager: RiskManager, executor: OrderExecutor):
        self.risk_manager = risk_manager
        self.executor = executor
        self.price_window = []
        self.max_window_size = 50
        
        # Previous MA values crossover track karne ke liye
        self.prev_fast_ma = 0.0
        self.prev_slow_ma = 0.0

    async def on_tick(self, price: float, timestamp_ms: int):
        """Jaise hi naya tick aayega, yeh function turant execute hoga"""
        # 1. Price ko memory list me add karein
        self.price_window.append(price)
        if len(self.price_window) > self.max_window_size:
            self.price_window.pop(0)

        # Agar data kam hai toh skip karein
        if len(self.price_window) < 20:
            return

        # 2. Fast Indicators Calculate Karein (e.g., SMA 5 and SMA 20)
        fast_ma = FastIndicators.simple_moving_average(self.price_window, 5)
        slow_ma = FastIndicators.simple_moving_average(self.price_window, 20)

        # 3. Signal Generate Karein
        signal = FastIndicators.check_crossover(fast_ma, slow_ma, self.prev_fast_ma, self.prev_slow_ma)
        
        # Update previous values for next tick
        self.prev_fast_ma = fast_ma
        self.prev_slow_ma = slow_ma

        if signal != "NONE":
            LatencyTracker.info(f"Signal Generated: {signal} at Price: {price}")
            
            # 4. Risk Check Karein
            if self.risk_manager.validate_trade(signal):
                # 5. Execute Order
                asyncio.create_task(self.executor.execute_order(signal, price, timestamp_ms))

