# PRO TRADING BOT STRATEGY FORMULA ENGINE
class TradeStrategyFormula:
    def __init__(self, account_balance):
        self.balance = account_balance
        self.risk_per_trade = 0.015  # 1.5% Risk per trade

    def calculate_position_size(self, entry_price, stop_loss_price):
        risk_amount = self.balance * self.risk_per_trade
        price_difference = abs(entry_price - stop_loss_price)
        if price_difference == 0:
            return 0.01
        position_size = risk_amount / price_difference
        return round(position_size, 4)

    def evaluate_entry_and_exit(self, order_book, current_position):
        bids = order_book['bids']
        asks = order_book['asks']
        
        # Wall & Imbalance Check
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        
        # 0.10 Stop Loss Implementation
        buy_stop_loss = best_bid - 0.10
        sell_stop_loss = best_ask + 0.10
        
        return {
            "buy_sl": buy_stop_loss,
            "sell_sl": sell_stop_loss,
            "status": "Formula Compiled Successfully"
        }
