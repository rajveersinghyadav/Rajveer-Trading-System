# config.py

import os

class Config:
    # Exchange / Broker Settings
    API_KEY = os.getenv("BROKER_API_KEY", "apni_api_key_yahan_dalein")
    API_SECRET = os.getenv("BROKER_API_SECRET", "apna_secret_key_yahan_dalein")
    
    # WebSocket aur REST Endpoints
    WS_ENDPOINT = "wss://stream.example.com/ws"
    REST_ENDPOINT = "https://api.example.com"
    
    # Trading Parameters
    SYMBOL = "BTCUSDT"
    QUANTITY = 0.001
    
    # Dynamic Lot Size / Quantity Settings (MetaTrader style)
    DEFAULT_LOT_SIZE = 0.01  # Apni zaroorat ke mutabiq default lot set karein
    MIN_LOT_SIZE = 0.01
    MAX_LOT_SIZE = 10.0
    
    # Risk Limits
    MAX_DAILY_LOSS = 50.0
    STOP_LOSS_PCT = 0.01
    TAKE_PROFIT_PCT = 0.02
    
    # Redis Configuration
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0

config = Config()
