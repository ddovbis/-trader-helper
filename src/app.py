import logging as logging
import time

from resources import config
from src.app_config import app_config
from src.constants import tickers
from src.strategy import strategy_factory
from src.strategy.impl.mean_signal_strategy import MeanSignalStrategy
from src.strategy.strategy import IStrategy
from src.strategy_simulator import strategy_simulator_helper

log = logging.getLogger(__name__)


# TODO 1. Create input parameters for graph/text result, both, simulating and for improving the Mean Strategy

def run():
    start_date = "2017-01-01"  # including
    end_date = "2021-12-31"  # excluding

    ticker = tickers.BTC_USD
    interval = '1d'
    subset_data_length = 4
    print_results = True
    plot_results = True
    calculate_over_market_performance = True
    simulate_strategy = True
    strategy_type = MeanSignalStrategy
    min_subset_data_length = 2  # including
    max_subset_data_length = 7  # including
    find_best_performance = True

    if simulate_strategy:
        mk_data = strategy_simulator_helper.prepare_simulation_mk_data(ticker, subset_data_length, start_date, end_date, interval)
        strategy: IStrategy = strategy_factory.get_concrete_strategy(strategy_type, ticker, subset_data_length)

        # TODO 2. extract some logic from there into "print/plot_strategy_performance"
        # TODO 3. use calculate_over_market_performance
        strategy_simulator_helper.show_strategy_performance(mk_data, subset_data_length, strategy, print_results, plot_results)

    if find_best_performance:
        mk_data = strategy_simulator_helper.prepare_simulation_mk_data(ticker, max_subset_data_length, start_date, end_date, interval)
        performances_by_subset_data_length = strategy_simulator_helper.get_strategy_performances_by_subset_data_length(min_subset_data_length, max_subset_data_length, mk_data, strategy_type)

        if calculate_over_market_performance:
            performances_by_subset_data_length = strategy_simulator_helper.get_strategy_over_market_performances(performances_by_subset_data_length, mk_data, config.SIMULATOR_INITIAL_CASH)

        if print_results:
            best_performance_subset_data_length = max(performances_by_subset_data_length, key=performances_by_subset_data_length.get)
            best_performance = performances_by_subset_data_length[best_performance_subset_data_length]

            log.info(f"All performance results found for data length: {performances_by_subset_data_length}")
            log.info(f"Best performance ({best_performance}) has been found for data length: {best_performance_subset_data_length}")

        if plot_results:
            strategy_simulator_helper.plot_performance_of_data_lengths(performances_by_subset_data_length)


if __name__ == "__main__":
    start = time.time()
    app_config.configure_app()
    log.info("App initialized")
    run()
    log.info(f"App ran for: {time.time() - start} s")
