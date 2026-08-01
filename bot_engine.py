# bot_engine.py
import asyncio
import json
import websockets
from config import config
from risk_manager import RiskManager
from executor import OrderExecutor
from strategy import TradingStrategy
from logger import LatencyTracker

# Global variable taaki latest market evaluation ko Flask app tak pahuncha sakein
latest_market_data = {
    "symbol": config.SYMBOL.upper(),
    "action": "WAITING",
    "bid_ratio": 0.0,
    "ask_ratio": 0.0,
    "stop_loss": 0.0,
    "price": 0.0
}

async def run_bot_terminal():
    global latest_market_data
    
    # HFT Modules Initialize karein
    risk_manager = RiskManager()
    executor = OrderExecutor()
    strategy = TradingStrategy(risk_manager, executor)
    
    LatencyTracker.info(f"⚡ [HFT MASTER BOT ENGINE INITIALIZED] Connected for {config.SYMBOL.upper()}...")
    
    stream_url = f"wss://stream.binance.com:9443/ws/{config.SYMBOL}@depth20@100ms"
    
    async with websockets.connect(stream_url) as websocket:
        while True:
            try:
                message = await websocket.recv()
                raw_data = json.loads(message)
                
                # Market data ko standard tick format me convert karein
                bids = raw_data.get("bids", [])
                asks = raw_data.get("asks", [])
                
                if not bids or not asks:
                    continue
                    
                best_bid = float(bids[0][0])
                best_ask = float(asks[0][0])
                current_price = (best_bid + best_ask) / 2.0
                
                tick_data = {
                    "price": current_price,
                    "bids": bids,
                    "asks": asks
                }
                
                # Strategy ke zariye tick process karein
                action = await strategy.on_tick(tick_data)
                
                # Global variable update kar rahe hain taaki Flask ise read kar sake
                latest_market_data = {
                    "symbol": config.SYMBOL.upper(),
                    "action": action if action else "HOLD",
                    "bid_ratio": 50.0,  # Real-time calculation se update hoga
                    "ask_ratio": 50.0,
                    "stop_loss": round(current_price * 0.99, 2),
                    "price": round(current_price, 2)
                }
                
                await asyncio.sleep(0.01) # Ultra-fast 10ms loop
            except Exception as e:
                LatencyTracker.error(f"WebSocket Error: {e}")
                await asyncio.sleep(1)

# Flask app ke liye yeh function banaya hai jo latest data return karega
def get_latest_bot_data():
    return latest_market_data

if __name__ == "__main__":
    asyncio.run(run_bot_terminal())

# --- AUTOMATIC TRADING ENGINE EXTENSION ---
import json
import threading
import websocket
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY, IS_TESTNET
from risk_manager import RiskManager
from strategy import OrderBookHFTStrategy
from executor import MultiSplitHFTExecutor

class AutoTradingBot:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol.lower()
        self.is_running = False
        self.ws = None
        self.order_book = {"bids": [], "asks": []}
        self.account_balance = 100.0  # Default test balance
        self.last_trade_time = 0
        
        # Modules Connect
        self.risk_mgr = RiskManager(max_risk_per_trade_pct=0.01, leverage=10)
        self.strat = OrderBookHFTStrategy(self.risk_mgr)
        self.exec = MultiSplitHFTExecutor(
            api_key=BINANCE_API_KEY, 
            api_secret=BINANCE_SECRET_KEY, 
            symbol=symbol.upper(), 
            testnet=IS_TESTNET
        )
        self.status = "Stopped"

    def _on_message(self, ws, message):
        data = json.loads(message)
        if "bids" in data and "asks" in data:
            self.order_book["bids"] = data["bids"]
            self.order_book["asks"] = data["asks"]
            self._check_and_trade()

    def _check_and_trade(self):
        if not self.is_running:
            return
            
        trade_params = self.strat.analyze_ticks_and_depth(self.order_book, self.account_balance)
        if trade_params:
            print(f"⚡ [AUTO-TRADE SIGNAL]: {trade_params['signal']} @ {trade_params['entry_price']}")
            self.exec.execute_multi_split_trade(trade_params)

    def start(self):
        if not self.is_running:
            self.is_running = True
            ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth20@100ms"
            if IS_TESTNET:
                ws_url = f"wss://stream.binancefuture.com/ws/{self.symbol}@depth20@100ms"
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=lambda ws, e: print(f"WS Error: {e}")
            )
            t = threading.Thread(target=self.ws.run_forever, daemon=True)
            t.start()
            self.status = "Running"
            print("🚀 Auto Trading Engine Started!")

    def stop(self):
        if self.ws:
            self.ws.close()
        self.is_running = False
        self.status = "Stopped"
        print("🛑 Auto Trading Engine Stopped.")

# Automatic Bot Instance Create
auto_bot = AutoTradingBot(symbol="BTCUSDT")
