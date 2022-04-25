import logging as logging
import time

from src.app_config import app_config
from src.constants import tickers
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
    print_performance_results = True
    plot_value_over_time = True

    # strategy(s) set up
    # strategy: IStrategy = MlLstmStrategy(ticker, subset_data_length)
    strategy: IStrategy = MeanSignalStrategy(subset_data_length)
    # strategy: IStrategy = VWAPSignalStrategy(5)
    # strategy: IStrategy = AllCandleStickPatternsStrategy()

    mk_data = strategy_simulator_helper.prepare_simulation_mk_data(ticker, subset_data_length, start_date, end_date, interval)
    strategy_simulator_helper.run_simulation(mk_data, subset_data_length, strategy, print_performance_results, plot_value_over_time)


if __name__ == "__main__":
    start = time.time()
    app_config.configure_app()
    log.info("App initialized")
    run()
    log.info(f"App ran for: {time.time() - start} s")
