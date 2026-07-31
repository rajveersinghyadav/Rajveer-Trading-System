import json
import os
import datetime

MEMORY_FILE = "ai_trading_rules.json"
LEARNING_LOG_FILE = "ai_pattern_testing_log.json"

class AIMemory:
    def __init__(self):
        self.rules = self.load_data(MEMORY_FILE)
        self.testing_logs = self.load_data(LEARNING_LOG_FILE)

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

    def test_and_track_pattern(self, pattern_name, outcome):
        found = False
        for log in self.testing_logs:
            if log['pattern'] == pattern_name:
                log['total_tests'] += 1
                if outcome == "SUCCESS":
                    log['success_count'] += 1
                log['accuracy'] = round((log['success_count'] / log['total_tests']) * 100, 2)
                found = True
                break
        
        if not found:
            self.testing_logs.append({
                "pattern": pattern_name,
                "total_tests": 1,
                "success_count": 1 if outcome == "SUCCESS" else 0,
                "accuracy": 100.0 if outcome == "SUCCESS" else 0.0
            })
        
        self.save_data(LEARNING_LOG_FILE, self.testing_logs)

    def check_for_approval_proposal(self, pattern_name):
        for log in self.testing_logs:
            if log['pattern'] == pattern_name:
                if log['total_tests'] >= 20 and log['accuracy'] >= 95.0:
                    risk_factor = round(100.0 - log['accuracy'], 2)
                    return {
                        "ready_for_approval": True,
                        "pattern": pattern_name,
                        "accuracy": log['accuracy'],
                        "risk_factor": f"{risk_factor}% (Controlled Slippage / Market Noise)",
                        "total_tested": log['total_tests'],
                        "explanation": f"AI Self-Learning Report: Pattern '{pattern_name}' has been tested {log['total_tests']} times with {log['accuracy']}% success rate. Built-in risk factor is {risk_factor}%. Requesting human approval for direct live execution."
                    }
        return {"ready_for_approval": False}

    def approve_and_save_rule(self, proposal):
        rule_entry = {
            "id": len(self.rules) + 1,
            "timestamp": str(datetime.datetime.now()),
            "approved_pattern": proposal['pattern'],
            "accuracy": proposal['accuracy'],
            "status": "ACTIVE_LIVE_TRADING"
        }
        self.rules.append(rule_entry)
        self.save_data(MEMORY_FILE, self.rules)
        print(f"🚀 [AI APPROVED & LIVE]: Pattern '{proposal['pattern']}' added to live execution engine.")
        return rule_entry
