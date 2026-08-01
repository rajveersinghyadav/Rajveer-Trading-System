# logger.py

import time
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class LatencyTracker:
    @staticmethod
    def get_timestamp_ms() -> int:
        """Current millisecond timestamp return karta hai"""
        return int(time.time() * 1000)
    
    @staticmethod
    def log_latency(action: str, start_time_ms: int):
        """Action ko execute hone me kitna time laga, use log karta hai"""
        current_time = LatencyTracker.get_timestamp_ms()
        elapsed = current_time - start_time_ms
        logging.info(f"LATENCY [{action}]: {elapsed} ms taken.")

    @staticmethod
    def info(message: str):
        logging.info(message)

    @staticmethod
    def error(message: str):
        logging.error(message)

