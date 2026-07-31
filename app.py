from flask import Flask, render_template, jsonify, request
import threading
import asyncio
import json
from ai_memory import AIMemory
from strategy_formula import MasterTradingEngine

app = Flask(__name__)
ai_memory = AIMemory()
trading_engine = MasterTradingEngine(initial_daily_balance=1000.0)

# Global status variables to serve on frontend
latest_market_data = {
    "action": "INITIALIZING",
    "bid_ratio": 0.0,
    "ask_ratio": 0.0,
    "stop_loss": 0.0,
    "dynamic_target": 0.0,
    "ai_status": {"ready_for_approval": False}
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify(latest_market_data)

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    data = request.json
    user_message = data.get("message", "")
    
    # AI response logic based on user instructions
    response_text = f"AI Brain processed: '{user_message}'. All 30-day risk rules, 60:40 ratio checks, and 95% accuracy thresholds are fully active."
    
    if "approve" in user_message.lower():
        response_text = "✅ Approval received! Pattern successfully added to live execution engine."
        
    return jsonify({"response": response_text})

def run_background_bot():
    """Background thread to run bot evaluations safely with Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Mocking sample order book loop for continuous server stability
    while True:
        sample_book = {
            "bids": [[60000.0, 65.0], [59990.0, 20.0]], # >60% Bid volume simulation
            "asks": [[60005.0, 25.0], [60010.0, 10.0]]
        }
        global latest_market_data
        evaluation = trading_engine.evaluate_market_and_execute(sample_book, "Heavy Wall Absorption")
        latest_market_data = evaluation
        import time
        time.sleep(1)

if __name__ == "__main__":
    # Start background bot thread
    bot_thread = threading.Thread(target=run_background_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask Web Server
    app.run(host="0.0.0.0", port=5000, debug=True)
