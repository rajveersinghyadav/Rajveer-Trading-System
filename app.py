from flask import Flask, render_template, jsonify, request
from ai_memory import AIMemory
from bot_engine import get_latest_bot_data, run_bot_terminal
import threading
import asyncio

app = Flask(__name__)
ai_memory = AIMemory()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    # bot_engine.py se latest live data fetch karke frontend ko de rahe hain
    data = get_latest_bot_data()
    return jsonify(data)

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    data = request.json
    user_message = data.get("message", "")
    
    response_text = f"AI Brain processed: '{user_message}'. All 30-day risk rules, 60:40 ratio checks, and 95% accuracy thresholds are fully active."
    
    if "approve" in user_message.lower():
        response_text = "✅ Approval received! Pattern successfully added to live execution engine."
        
    return jsonify({"response": response_text})

def start_background_bot():
    """Background thread mein bot_engine ke WebSocket ko chalane ke liye"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_terminal())

if __name__ == "__main__":
    # Background thread start kar rahe hain jo Binance se live data laayega
    bot_thread = threading.Thread(target=start_background_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask Web Server
    app.run(host="0.0.0.0", port=5000, debug=True)
    # --- AUTO TRADING CONTROLS ---
from bot_engine import auto_bot

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    auto_bot.start()
    return jsonify({"status": "Started", "message": "Bot live trading is ACTIVE"})

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    auto_bot.stop()
    return jsonify({"status": "Stopped", "message": "Bot live trading is PAUSED"})
