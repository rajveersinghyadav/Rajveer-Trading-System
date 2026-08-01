# risk_manager.py

from config import config
from logger import LatencyTracker

class RiskManager:
    def __init__(self):
        self.daily_loss = 0.0
        self.is_halted = False

    def validate_trade(self, signal: str) -> bool:
        """Har trade signal ko exchange par bhejne se pahle validate karta hai"""
        if self.is_halted:
            LatencyTracker.error("Trading halted due to max daily loss limit reached.")
            return False
            
        if signal == "NONE":
            return False
            
        # Aap yahan available margin ya daily loss ka check laga sakte hain
        if self.daily_loss >= config.MAX_DAILY_LOSS:
            self.is_halted = True
            LatencyTracker.error("Max daily loss limit breached! Halting all trades.")
            return False
            
        return True

    def get_dynamic_lot_size(self, current_price: float = 0.0) -> float:
        """MetaTrader ya standard brokers ki tarah dynamic lot size calculate karta hai"""
        # Aap yahan apne account balance ya risk ke hisab se formula customize kar sakte hain
        lot_size = config.DEFAULT_LOT_SIZE
        
        # Ensure karegi ki lot size min aur max limits ke andar hi rahe
        if lot_size < config.MIN_LOT_SIZE:
            lot_size = config.MIN_LOT_SIZE
        elif lot_size > config.MAX_LOT_SIZE:
            lot_size = config.MAX_LOT_SIZE
            
        return round(lot_size, 4)

    def update_loss(self, loss_amount: int):
        self.daily_loss += loss_amount
