# bot_engine.py
import json
import time
import threading
import logging
import websocket
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY, IS_TESTNET
from risk_manager import RiskManager
from strategy import OrderBookHFTStrategy
from executor import MultiSplitHFTExecutor

logger = logging.getLogger("BotEngine")
logging.basicConfig(level=logging.INFO)

class HFTBotEngine:
    def __init__(self, symbol="btcusdt"):
        self.symbol = symbol.lower()
        self.is_running = False
        self.ws = None
        
        # Modules setup
        self.risk_manager = RiskManager(max_risk_per_trade_pct=0.01, leverage=10)
        self.strategy = OrderBookHFTStrategy(self.risk_manager)
        self.executor = MultiSplitHFTExecutor(
            api_key=BINANCE_API_KEY, 
            api_secret=BINANCE_SECRET_KEY, 
            symbol=symbol.upper(), 
            testnet=IS_TESTNET
        )
        
        # Latest State
        self.order_book = {"bids": [], "asks": []}
        self.account_balance = 100.0  # Fetch dynamic or set base balance ($100 default)
        self.last_trade_time = 0
        self.trade_cooldown_sec = 5  # Duplicate trades prevent karne ke liye 5 sec delay
        self.engine_status = {
            "symbol": symbol.upper(),
            "status": "Stopped",
            "last_signal": "NONE",
            "executed_trades": 0
        }

    def _on_ws_message(self, ws, message):
        """Binance OrderBook Ticks receive hote hi triggers strategy evaluation"""
        data = json.loads(message)
        if "bids" in data and "asks" in data:
            self.order_book["bids"] = data["bids"]
            self.order_book["asks"] = data["asks"]
            
            # Auto-Trade Execution Logic Trigger
            self._evaluate_and_trade()

    def _evaluate_and_trade(self):
        current_time = time.time()
        if current_time - self.last_trade_time < self.trade_cooldown_sec:
            return

        # Strategy evaluation using real-time book depth
        trade_params = self.strategy.analyze_ticks_and_depth(
            self.order_book, 
            self.account_balance
        )

        if trade_params:
            logger.info(f"⚡ HIGH ACCURACY SIGNAL GENERATED: {trade_params['signal']}")
            self.engine_status["last_signal"] = f"{trade_params['signal']} @ {trade_params['entry_price']}"
            
            # Parallel Multi-split Orders Execute Karein
            execution_res = self.executor.execute_multi_split_trade(trade_params)
            
            self.last_trade_time = time.time()
            self.engine_status["executed_trades"] += execution_res.get("successful", 0)

    def _run_websocket(self):
        # Binance Futures/Spot Partial Book Depth Stream (100ms updates)
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth20@100ms"
        if IS_TESTNET:
            ws_url = f"wss://stream.binancefuture.com/ws/{self.symbol}@depth20@100ms"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_ws_message,
            on_error=lambda ws, err: logger.error(f"WS Error: {err}"),
            on_close=lambda ws, c, m: logger.info("WS Connection Closed")
        )
        self.engine_status["status"] = "Running (Live Websocket)"
        self.ws.run_forever()

    def start(self):
        if not self.is_running:
            self.is_running = True
            t = threading.Thread(target=self._run_websocket, daemon=True)
            t.start()
            logger.info("Bot Engine Started Successfully.")

    def stop(self):
        if self.ws:
            self.ws.close()
        self.is_running = False
        self.engine_status["status"] = "Stopped"

# Global Instance
bot = HFTBotEngine(symbol="BTCUSDT")
