# executor.py
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from binance.client import Client

logger = logging.getLogger("OrderExecutor")

class MultiSplitHFTExecutor:
    def __init__(self, api_key, api_secret, symbol="BTCUSDT", testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.symbol = symbol

    def _place_single_micro_order(self, side, qty, entry_price, sl_price, tp_price):
        """
        Single micro-lot order execute karta hai aur saath me SL/TP OCO attach karta hai.
        """
        try:
            # 1. Market Entry Order
            order = self.client.create_order(
                symbol=self.symbol,
                side=side,
                type=Client.ORDER_TYPE_MARKET,
                quantity=qty
            )
            
            # 2. Attach Stop-Loss Order for protection
            sl_side = Client.SIDE_SELL if side == "BUY" else Client.SIDE_BUY
            self.client.create_order(
                symbol=self.symbol,
                side=sl_side,
                type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=qty,
                stopPrice=str(sl_price),
                price=str(sl_price)
            )

            # 3. Attach Take-Profit Limit Order
            self.client.create_order(
                symbol=self.symbol,
                side=sl_side,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=qty,
                price=str(tp_price)
            )

            return True, order.get("orderId")

        except Exception as e:
            logger.error(f"Micro-lot order failed: {str(e)}")
            return False, str(e)

    def execute_multi_split_trade(self, trade_params):
        """
        ThreadPoolExecutor ka use karke 1 se 100 micro-lots ek saath parallel execute karta hai.
        """
        signal = trade_params["signal"]
        num_splits = trade_params["num_splits"]
        lot_qty = trade_params["lot_qty"]
        entry_price = trade_params["entry_price"]
        sl_price = trade_params["sl_price"]
        tp_price = trade_params["tp_price"]

        logger.info(f"Executing {num_splits} micro-lots of {lot_qty} Qty each for {signal} signal...")

        successful_orders = 0
        failed_orders = 0

        # High-Speed Parallel Execution
        with ThreadPoolExecutor(max_workers=min(num_splits, 20)) as executor:
            futures = [
                executor.submit(
                    self._place_single_micro_order,
                    signal,
                    lot_qty,
                    entry_price,
                    sl_price,
                    tp_price
                )
                for _ in range(num_splits)
            ]

            for future in as_completed(futures):
                success, details = future.result()
                if success:
                    successful_orders += 1
                else:
                    failed_orders += 1

        logger.info(f"Multi-Split Execution Summary: {successful_orders}/{num_splits} Succeeded, {failed_orders} Failed.")
        return {
            "total_requested": num_splits,
            "successful": successful_orders,
            "failed": failed_orders
        }
