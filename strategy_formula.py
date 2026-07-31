from ai_memory import AIMemory

class MasterTradingEngine:
    def __init__(self, initial_daily_balance):
        self.daily_balance = initial_daily_balance
        self.max_survival_days = 30
        self.ai_memory = AIMemory()

    def calculate_30_day_survival_risk(self, current_balance, entry_price, stop_loss):
        daily_budget = self.daily_balance / self.max_survival_days
        trade_risk_allowance = daily_budget * (current_balance / self.daily_balance)
        
        price_diff = abs(entry_price - stop_loss)
        if price_diff == 0:
            return 0.01, 0.0
        
        total_split_lots = (trade_risk_allowance * 0.25) / price_diff
        return round(total_split_lots, 4), round(trade_risk_allowance, 2)

    def evaluate_market_and_execute(self, order_book, current_pattern):
        bids = order_book['bids']
        asks = order_book['asks']
        
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        
        total_bid_vol = sum([float(qty) for price, qty in bids])
        total_ask_vol = sum([float(qty) for price, qty in asks])
        total_vol = total_bid_vol + total_ask_vol
        
        if total_vol == 0:
            return {"action": "HOLD", "reason": "No Volume Data"}
            
        bid_ratio = (total_bid_vol / total_vol) * 100
        ask_ratio = (total_ask_vol / total_vol) * 100
        
        proposal = self.ai_memory.check_for_approval_proposal(current_pattern)
        
        action = "WAIT / NO TRADE"
        stop_loss = 0.0
        target = 0.0
        
        if bid_ratio >= 60.0 and proposal.get("ready_for_approval", False):
            action = "EXECUTE 4-5 SPLIT BUY TRADES"
            stop_loss = round(best_bid - 10.0, 2)
            target = round(best_bid + (best_ask - best_bid) * 4.0, 2)
            
        elif ask_ratio >= 60.0 and proposal.get("ready_for_approval", False):
            action = "EXECUTE 4-5 SPLIT SELL TRADES"
            stop_loss = round(best_ask + 10.0, 2)
            target = round(best_ask - (best_ask - best_bid) * 4.0, 2)

        return {
            "action": action,
            "bid_ratio": round(bid_ratio, 1),
            "ask_ratio": round(ask_ratio, 1),
            "stop_loss": stop_loss,
            "dynamic_target": target,
            "ai_status": proposal
        }
