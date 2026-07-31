import asyncio
import json
import websockets
import pandas as pd
import numpy as np

# Binance WebSocket Endpoint for Live Order Book (Millisecond speed)
SYMBOL = "btcusdt"
STREAM_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@depth20@100ms"

async def calculate_order_flow(order_book_data):
    try:
        bids = pd.DataFrame(order_book_data['bids'], columns=['price', 'quantity']).astype(float)
        asks = pd.DataFrame(order_book_data['asks'], columns=['price', 'quantity']).astype(float)
        
        total_bid_qty = bids['quantity'].sum()
        total_ask_qty = asks['quantity'].sum()
        
        imbalance_ratio = total_bid_qty / (total_ask_qty if total_ask_qty > 0 else 1)
        
        max_bid_wall = bids.loc[bids['quantity'].idxmax()]
        max_ask_wall = asks.loc[asks['quantity'].idxmax()]
        
        if imbalance_ratio > 1.5:
            signal = "BUY / BULLISH"
            expected_target = bids['price'].iloc[0] + (max_ask_wall['price'] - bids['price'].iloc[0]) * 0.5
        elif imbalance_ratio < 0.6:
            signal = "SELL / BEARISH"
            expected_target = asks['price'].iloc[0] - (asks['price'].iloc[0] - max_bid_wall['price']) * 0.5
        else:
            signal = "NEUTRAL"
            expected_target = bids['price'].iloc[0]

        print(f"[{SYMBOL.upper()}] Signal: {signal} | Ratio: {imbalance_ratio:.2f} | Target: ${expected_target:.2f}")

    except Exception as e:
        print(f"Calculation Error: {e}")

async def start_engine():
    print(f"⚡ Starting Ultra-Fast Engine for {SYMBOL.upper()}...")
    async with websockets.connect(STREAM_URL) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            await calculate_order_flow(data)

if __name__ == "__main__":
    asyncio.run(start_engine())
