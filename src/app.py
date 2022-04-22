import json
import logging as logging
import time
from datetime import timedelta
from typing import List

from resources import config
from src.app_config import app_config
from src.constants import tickers
from src.helper import formatter
from src.helper.mk_data import av_crypto_helper
from src.model.mk_data import MkData
from src.strategy.impl.all_candlestick_patterns_strategy import AllCandleStickPatternsStrategy
from src.strategy.impl.mean_signal_strategy import MeanSignalStrategy
from src.strategy.impl.ml_lstm_strategy import MlLstmStrategy
from src.strategy.strategy import IStrategy
from src.strategy_simulator.strategy_simulator_runner import StrategySimulatorRunner

log = logging.getLogger(__name__)


# TODO 1. Graph for comparing market performance
#    Resources
#       Basis of plotting data: https://python-graph-gallery.com/basic-time-series-with-matplotlib
#       How to add second line: https://www.geeksforgeeks.org/plot-multiple-lines-in-matplotlib/

# TODO 2. Create input parameters for graph/text result, both, and for improving the Mean Strategy

# TODO 3. Create logic (module) for running multiple simulations w/ mean strategy to get the best parameter

def run():
    # mkdata params
    start_date = "2017-01-01"
    end_date = "2021-12-31"
    ticker = tickers.BTC_USD
    interval = '1d'
    subset_data_length = 4

    # simulator and strategy(s) set up
    strategies: List[IStrategy] = [
        # MlLstmStrategy(ticker, subset_data_length)
        MeanSignalStrategy(subset_data_length),
        # VWAPSignalStrategy(5),
        # AllCandleStickPatternsStrategy()
    ]

    # data preparation
    left_offset = timedelta(days=subset_data_length - 1)
    start_date_with_offset = formatter.extract_time_from_str_date(start_date, config.GENERAL_DATE_FORMAT, left_offset)
    data = av_crypto_helper.download_daily_historical_data(ticker=ticker, _from=start_date_with_offset, to=end_date)
    mk_data = MkData(ticker, start_date, end_date, interval, data)

    strategy_simulator_runner = StrategySimulatorRunner(mk_data)
    for strategy in strategies:
        performance = strategy_simulator_runner.run(strategy, subset_data_length)
        log.info(f"{json.dumps(performance, indent=4)}")


if __name__ == "__main__":
    start = time.time()
    app_config.config()
    log.info("App initialized")
    run()
    log.info(f"App ran for: {time.time() - start} s")
