# bot_engine.py
import asyncio
import json
import websockets
from strategy_formula import MasterTradingEngine

SYMBOL = "btcusdt"
STREAM_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@depth20@100ms"

# Global variable taaki latest market evaluation ko Flask app tak pahuncha sakein
latest_market_data = {
    "symbol": SYMBOL.upper(),
    "action": "WAITING",
    "bid_ratio": 0.0,
    "ask_ratio": 0.0,
    "stop_loss": 0.0,
    "price": 0.0
}

async def run_bot_terminal():
    global latest_market_data
    engine = MasterTradingEngine(initial_daily_balance=1000.0)
    print(f"⚡ [MASTER BOT ENGINE INITIALIZED] Connected to Binance for {SYMBOL.upper()}...")
    
    async with websockets.connect(STREAM_URL) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                evaluation = engine.evaluate_market_and_execute(data, "Heavy Wall Absorption")
                
                # Global variable update kar rahe hain taaki Flask ise read kar sake
                latest_market_data = {
                    "symbol": SYMBOL.upper(),
                    "action": evaluation.get('action', 'HOLD'),
                    "bid_ratio": evaluation.get('bid_ratio', 0.0),
                    "ask_ratio": evaluation.get('ask_ratio', 0.0),
                    "stop_loss": evaluation.get('stop_loss', 0.0),
                    "price": evaluation.get('price', 0.0)
                }
                
                print(f"[{SYMBOL.upper()}] Action: {evaluation['action']} | Bids: {evaluation['bid_ratio']}% | Asks: {evaluation['ask_ratio']}% | SL: {evaluation['stop_loss']}")
                
                ai_prop = evaluation.get("ai_status", {})
                if ai_prop.get("ready_for_approval"):
                    print(f"\n🔔 [AI APPROVAL REQUEST]: {ai_prop['explanation']}")
                    print(f"Risk Factor: {ai_prop['risk_factor']} | Accuracy: {ai_prop['accuracy']}%\n")

                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"WebSocket Error: {e}")
                await asyncio.sleep(1)

# Flask app ke liye yeh function banaya hai jo latest data return karega
def get_latest_bot_data():
    return latest_market_data

if __name__ == "__main__":
    asyncio.run(run_bot_terminal())
