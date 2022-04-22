import json
import logging as logging
import time
from datetime import timedelta

from resources import config
from src.app_config import app_config
from src.constants import tickers
from src.helper import formatter
from src.helper.mk_data import av_crypto_helper
from src.model.mk_data import MkData
from src.model.single_ticker_portfolio import SingleTickerPortfolio
from src.strategy.impl.mean_signal_strategy import MeanSignalStrategy
from src.strategy.strategy import IStrategy
from src.strategy_simulator import strategy_simulator_helper

log = logging.getLogger(__name__)


# TODO 1. Create input parameters for graph/text result, both, and for improving the Mean Strategy

# TODO 2. Create logic (module) for running multiple simulations w/ mean strategy to get the best parameter

def run():
    # mkdata params
    start_date = "2017-01-01"  # including
    end_date = "2019-01-01"  # excluding
    ticker = tickers.BTC_USD
    interval = '1d'
    subset_data_length = 4

    # strategy(s) set up
    # strategy: IStrategy = MlLstmStrategy(ticker, subset_data_length)
    strategy: IStrategy = MeanSignalStrategy(subset_data_length)
    # strategy: IStrategy = VWAPSignalStrategy(5)
    # strategy: IStrategy = AllCandleStickPatternsStrategy()

    # data preparation
    left_offset = timedelta(days=subset_data_length - 1)
    start_date_with_offset = formatter.extract_time_from_str_date(start_date, config.GENERAL_DATE_FORMAT, left_offset)
    data = av_crypto_helper.download_daily_historical_data(ticker=ticker, _from=start_date_with_offset, to=end_date)
    mk_data = MkData(ticker, start_date, end_date, interval, data)

    # simulate strategy
    strategy_result_portfolio: SingleTickerPortfolio = strategy_simulator_helper.run(mk_data, strategy, subset_data_length)

    # use results
    performance = strategy_simulator_helper.get_performance_statistics(strategy_result_portfolio, start_date, end_date)
    formatted_performance_data = json.dumps(performance, indent=4)
    log.info(f"{formatted_performance_data}")
    strategy_simulator_helper.plot_strategy_vs_market_performance(mk_data, strategy_result_portfolio)


if __name__ == "__main__":
    start = time.time()
    app_config.config()
    log.info("App initialized")
    run()
    log.info(f"App ran for: {time.time() - start} s")
