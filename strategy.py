# strategy.py
import logging

logger = logging.getLogger("StrategyEngine")

class OrderBookHFTStrategy:
    def __init__(self, risk_manager, min_imbalance_ratio=1.8):
        self.rm = risk_manager
        self.min_imbalance_ratio = min_imbalance_ratio  # 1.8x Bid/Ask imbalance threshold

    def analyze_ticks_and_depth(self, order_book, account_balance, atr_val=0.0):
        """
        Binance WebSocket Order Book Ticks ko Real-Time Analyze karta hai:
        1. Top Bids vs Asks Volume Imbalance.
        2. High Accuracy Signal Generation.
        3. Commission & Noise-Aware SL/TP Validation.
        """
        bids = order_book.get("bids", []) # [[price, qty], ...]
        asks = order_book.get("asks", []) # [[price, qty], ...]

        if not bids or not asks:
            return None

        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        spread = best_ask - best_bid

        # Calculate top 5 depth cumulative volumes
        bid_volume_top5 = sum([float(b[1]) for b in bids[:5]])
        ask_volume_top5 = sum([float(a[1]) for a in asks[:5]])

        if ask_volume_top5 == 0 or bid_volume_top5 == 0:
            return None

        signal = None
        entry_price = 0.0
        depth_available = 0.0

        # --- VOLUME-BASED ACCURACY SIGNAL ---
        # Strong Buy Signal: Bid Volume significantly higher than Ask Volume
        if (bid_volume_top5 / ask_volume_top5) >= self.min_imbalance_ratio:
            signal = "BUY"
            entry_price = best_ask
            depth_available = ask_volume_top5

        # Strong Sell Signal: Ask Volume significantly higher than Bid Volume
        elif (ask_volume_top5 / bid_volume_top5) >= self.min_imbalance_ratio:
            signal = "SELL"
            entry_price = best_bid
            depth_available = bid_volume_top5

        if not signal:
            return None  # No high-conviction trade

        # --- CALCULATE SL & TP ---
        sl_price = self.rm.calculate_noise_adaptive_sl(entry_price, signal, spread, atr_val)
        
        # Targeting Risk-Reward Ratio (e.g. 1:1.5 to 1:2)
        risk_per_unit = abs(entry_price - sl_price)
        if signal == "BUY":
            tp_price = round(entry_price + (risk_per_unit * 1.5), 4)
        else:
            tp_price = round(entry_price - (risk_per_unit * 1.5), 4)

        # --- DYNAMIC LOT CALCULATION ---
        total_qty, num_splits, lot_qty = self.rm.calculate_dynamic_lots(
            account_balance, entry_price, sl_price, depth_available
        )

        if total_qty <= 0:
            return None

        # --- COMMISSION-AWARE NET PROFIT FILTER ---
        is_profitable, expected_net_profit = self.rm.is_net_profitable(
            entry_price, tp_price, total_qty, side=signal
        )

        if not is_profitable:
            logger.info("Signal discarded: Trade does not meet Net Profit Threshold after commission.")
            return None

        return {
            "signal": signal,
            "entry_price": entry_price,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "total_qty": total_qty,
            "num_splits": num_splits,
            "lot_qty": lot_qty,
            "expected_net_profit": expected_net_profit
        }
