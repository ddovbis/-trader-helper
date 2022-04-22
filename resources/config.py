import os
import pathlib

GENERAL_DATE_FORMAT = "%Y-%m-%d"

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_API_KEY = ""  # TODO: Add your ALPHA VANTAGE API key here

RESOURCES_PATH = pathlib.Path(__file__).parent.resolve()
LSTM_MODELS_PATH = os.path.join(RESOURCES_PATH, "../models/lstm")

# simulator configs
SIMULATOR_LOG_TRANSACTIONS = False
SIMULATOR_TRANSACTIONS_FEE = 0.00

# tensorflow configs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# plot configs
MARKER_SIZE = 5
STRATEGY_PORTFOLIO_LABEL = "Valoarea portfoliului strategiei"
BUY_AND_HOLD_PORTFOLIO_LABEL = "Valoarea portfoliului a unicii procurări"
BUY_MARK_LABEL = "Tranzacție de cumpărare"
SELL_MARK_LABEL = "Tranzacție de vânzare"
