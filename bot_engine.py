import asyncio
import json
import websockets
from strategy_formula import MasterTradingEngine

SYMBOL = "btcusdt"
STREAM_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@depth20@100ms"

async def run_bot_terminal():
    engine = MasterTradingEngine(initial_daily_balance=1000.0)
    print(f"⚡ [MASTER BOT ENGINE INITIALIZED] Connected to Binance for {SYMBOL.upper()}...")
    
    async with websockets.connect(STREAM_URL) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            evaluation = engine.evaluate_market_and_execute(data, "Heavy Wall Absorption")
            
            print(f"[{SYMBOL.upper()}] Action: {evaluation['action']} | Bids: {evaluation['bid_ratio']}% | Asks: {evaluation['ask_ratio']}% | SL: {evaluation['stop_loss']}")
            
            ai_prop = evaluation.get("ai_status", {})
            if ai_prop.get("ready_for_approval"):
                print(f"\n🔔 [AI APPROVAL REQUEST]: {ai_prop['explanation']}")
                print(f"Risk Factor: {ai_prop['risk_factor']} | Accuracy: {ai_prop['accuracy']}%\n")

            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run_bot_terminal())
