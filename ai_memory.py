import json
import os
import datetime

MEMORY_FILE = "ai_trading_rules.json"
HISTORY_FILE = "ai_trade_learning_history.json"

class AIMemory:
    def __init__(self):
        self.rules = self.load_data(MEMORY_FILE)
        self.history = self.load_data(HISTORY_FILE)

    def load_data(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def remember_rule(self, condition, action, target_move):
        """AI ko naye trading rules ya conditions sikhane ke liye"""
        rule_entry = {
            "id": len(self.rules) + 1,
            "timestamp": str(datetime.datetime.now()),
            "condition": condition,
            "action": action,
            "target_move": target_move
        }
        self.rules.append(rule_entry)
        self.save_data(MEMORY_FILE, self.rules)
        print(f"🧠 [AI MEMORY SAVED]: Rule #{rule_entry['id']} -> If {condition} THEN {action}")
        return rule_entry

    def record_trade_learning(self, pattern_name, result, profit_loss):
        """Candle pattern ya wall reaction ke baad AI kya sikha, use record karna"""
        learning_entry = {
            "timestamp": str(datetime.datetime.now()),
            "pattern": pattern_name,
            "result": result,  # "SUCCESS" ya "FAILURE"
            "pnl": profit_loss
        }
        self.history.append(learning_entry)
        self.save_data(HISTORY_FILE, self.history)
        print(f"📊 [AI LEARNING UPDATED]: Pattern '{pattern_name}' resulted in {result} (${profit_loss})")

    def get_matched_rule(self, current_market_condition):
        """Current market condition ke hisab se memory se rule match karna"""
        for rule in self.rules:
            if rule['condition'].lower() in current_market_condition.lower():
                return rule
        return None

    def get_all_memories(self):
        return {
            "total_rules": len(self.rules),
            "rules": self.rules,
            "learning_history": self.history
        }

# Testing the Memory Engine
if __name__ == "__main__":
    ai_mem = AIMemory()
    # Test adding a rule
    ai_mem.remember_rule("RSI drops below 30 and Big Bid Wall > 10 BTC", "Execute BUY / LONG", "+20 Points")
    ai_mem.record_trade_learning("Bullish Hammer at Support", "SUCCESS", +150.00)
