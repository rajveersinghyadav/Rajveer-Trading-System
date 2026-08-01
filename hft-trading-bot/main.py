# main.py

import asyncio
from config import config
from logger import LatencyTracker
from risk_manager import RiskManager
from executor import OrderExecutor
from strategy import TradingStrategy
from data_stream import connect_market_stream

async def main():
    LatencyTracker.info("Starting High-Frequency Trading System...")
    
    # 1. Sabhi modules ko initialize karein
    risk_manager = RiskManager()
    executor = OrderExecutor()
    strategy = TradingStrategy(risk_manager, executor)
    
    LatencyTracker.info(f"Connected to target symbol: {config.SYMBOL}")
    
    # 2. Data Stream Start Karein aur Strategy callback pass karein
    try:
        await connect_market_stream(strategy.on_tick)
    except KeyboardInterrupt:
        LatencyTracker.info("Trading System Stopped Manually by User.")
    except Exception as e:
        LatencyTracker.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    # uvloop agar available ho toh speed aur tez karne ke liye use karenge
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        LatencyTracker.info("Using uvloop for ultra-fast async execution.")
    except ImportError:
        LatencyTracker.info("uvloop not found, using standard asyncio event loop.")

    # Main event loop run karein
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSystem Shutdown Successfully.")

