# risk_manager.py
import math
import logging
from config import (
    DEFAULT_LOT_SIZE,
    MIN_LOT_SIZE,
    MAX_LOT_SIZE,
    MAKER_FEE_PCT,   # e.g., 0.02 (%)
    TAKER_FEE_PCT,   # e.g., 0.04 (%)
    MIN_NET_PROFIT_USD # e.g., 1.0 ($1 or $2)
)

logger = logging.getLogger("RiskManager")

class RiskManager:
    def __init__(self, max_risk_per_trade_pct=0.01, leverage=10):
        self.max_risk_pct = max_risk_per_trade_pct
        self.leverage = leverage

    def calculate_noise_adaptive_sl(self, entry_price, side, order_book_spread, atr_val=0.0):
        """
        Market noise me SL hit na ho, iske liye Order Book Spread + ATR/Volatility 
        ka multiplier use karke tight but safe Stop Loss price nikalta hai.
        """
        # Noise buffer = 1.5 * Spread + Small ATR Cushion
        noise_buffer = (order_book_spread * 1.5) + (atr_val * 0.2)
        
        if side.upper() in ["BUY", "LONG"]:
            sl_price = entry_price - noise_buffer
        else: # SELL / SHORT
            sl_price = entry_price + noise_buffer

        return round(sl_price, 4)

    def calculate_dynamic_lots(self, account_balance, entry_price, sl_price, available_book_depth_qty):
        """
        Account balance, Stop Loss risk, aur Order Book Depth ko consider karke
        total position size aur micro-lot split (1-100 lots) calculate karta hai.
        """
        if entry_price <= 0 or sl_price <= 0 or entry_price == sl_price:
            return 0, 1, 0

        risk_amount = account_balance * self.max_risk_pct
        price_risk = abs(entry_price - sl_price)
        
        # Risk-based total quantity
        raw_qty = (risk_amount / price_risk) * self.leverage
        
        # Book Depth Liquidity Cap: Available depth ka max 20% consume karein taaki slippage na ho
        max_allowed_qty = available_book_depth_qty * 0.20
        final_total_qty = min(raw_qty, max_allowed_qty)

        # Micro-lot sizing limits check
        if final_total_qty < MIN_LOT_SIZE:
            logger.warning("Calculated lot size below MIN_LOT_SIZE.")
            return 0, 0, 0

        # Calculate number of micro-splits (Between 1 and 100)
        # Higher volume = More splits (max 100)
        split_count = min(100, max(1, math.ceil(final_total_qty / DEFAULT_LOT_SIZE)))
        per_lot_qty = round(final_total_qty / split_count, 4)

        return final_total_qty, split_count, per_lot_qty

    def is_net_profitable(self, entry_price, expected_tp_price, total_qty, side="BUY"):
        """
        Brokerage/Exchange fees katne ke baad check karta hai ki net profit >= MIN_NET_PROFIT_USD hai ya nahi.
        """
        notional_val = entry_price * total_qty
        
        # Entry (Taker) + Exit (Maker/Taker) Total Commission Estimation
        entry_fee = notional_val * (TAKER_FEE_PCT / 100.0)
        exit_fee = (expected_tp_price * total_qty) * (TAKER_FEE_PCT / 100.0)
        total_fees = entry_fee + exit_fee

        # Gross Profit
        if side.upper() in ["BUY", "LONG"]:
            gross_profit = (expected_tp_price - entry_price) * total_qty
        else:
            gross_profit = (entry_price - expected_tp_price) * total_qty

        net_profit = gross_profit - total_fees
        logger.info(f"Gross Profit: ${gross_profit:.2f} | Est. Fees: ${total_fees:.2f} | Net Profit: ${net_profit:.2f}")

        return net_profit >= MIN_NET_PROFIT_USD, net_profit
