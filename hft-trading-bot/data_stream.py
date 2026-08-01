# data_stream.py

import asyncio
import random
import time
from logger import LatencyTracker

async def connect_market_stream(strategy_callback):
    """
    Exchange ka WebSocket data stream handler.
    Live environment me yahan websockets library use karke real exchange data lenge.
    Abhi ke liye yeh simulated live market ticks generate kar raha hai.
    """
    LatencyTracker.info("Connecting to Market WebSocket Data Stream...")
    
    # Simulated live ticks loop (Real market me ye exchange ka WebSocket listener ban jayega)
    base_price = 60000.0
    while True:
        try:
            # Simulate incoming price tick timestamp ke sath
            tick_time = int(time.time() * 1000)
            current_price = base_price + random.uniform(-5.0, 5.0)
            
            # Strategy callback ko tick data bhejo (Asynchronous call)
            await strategy_callback(current_price, tick_time)
            
            # Har 100ms par naya tick simulate kar rahe hain
            await asyncio.sleep(0.1)
            
        except Exception as e:
            LatencyTracker.error(f"Error in data stream: {e}")
            await asyncio.sleep(1)

