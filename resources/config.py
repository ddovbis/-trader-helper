import os
import pathlib

GENERAL_DATE_FORMAT = "%Y-%m-%d"

# mkdata configs
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_API_KEY = ""  # TODO: Add your ALPHA VANTAGE API key here
ALPHA_VANTAGE_MAX_RETRY = 5
ALPHA_VANTAGE_WAIT_SECONDS_BEFORE_RETRY = 30
ALPHA_VANTAGE_REACHED_LIMIT_ERROR_MSG = """
{
    "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency."
}
"""

RESOURCES_PATH = pathlib.Path(__file__).parent.resolve()
LSTM_MODELS_PATH = os.path.join(RESOURCES_PATH, "../models/lstm")
TEMP_DIR = os.path.join(RESOURCES_PATH, "../temp")
ERRORS_DIR = os.path.join(TEMP_DIR, "errors")

# simulator configs
SIMULATOR_LOG_TRANSACTIONS = False
SIMULATOR_TRANSACTIONS_FEE = 0.00
SIMULATOR_INITIAL_CASH = 100

# tensorflow configs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# strategy simulation plot configs
MARK_BUY_AND_SELL = True
STRATEGY_SIMULATION_X_LABEL = "Timp"
STRATEGY_SIMULATION_Y_LABEL = "Valoarea portofoliului de investiții"
STRATEGY_SIMULATION_MARKER_SIZE = 5
STRATEGY_SIMULATION_STRATEGY_PORTFOLIO_LABEL = "Evoluția portofoliului cu folosire a strategiei"
STRATEGY_SIMULATION_BUY_AND_HOLD_PORTFOLIO_LABEL = "Evoluția portofoliului fără folosire a strategiei"
STRATEGY_SIMULATION_BUY_MARK_LABEL = "Tranzacție de cumpărare"
STRATEGY_SIMULATION_SELL_MARK_LABEL = "Tranzacție de vânzare"

# performances by subset data length plot configs
PERF_BY_SUBSET_DATA_LENGTH_X_LABEL = "Nr. de intrări folosite pentru fiecare decizie"
PERF_BY_SUBSET_DATA_LENGTH_Y_LABEL = "Performanța (%)"
