import logging as logging
import time

from resources import config
from src.app_config import app_config
from src.helper import args_helper
from src.model.single_ticker_portfolio import SingleTickerPortfolio
from src.strategy import strategy_factory
from src.strategy.strategy import IStrategy
from src.strategy_simulator import strategy_simulator_helper

log = logging.getLogger(__name__)


def run(params):
    if params.simulate_strategy:
        mk_data = strategy_simulator_helper.prepare_simulation_mk_data(params.ticker, params.subset_data_length, params.start_date, params.end_date, params.interval)
        strategy: IStrategy = strategy_factory.get_concrete_strategy(params.strategy_type, params.ticker, params.subset_data_length)

        # simulate strategy
        strategy_result_portfolio: SingleTickerPortfolio = strategy_simulator_helper.simulate(mk_data, strategy, params.subset_data_length)

        # use results
        if params.print_results:
            performance = strategy_simulator_helper.get_performance_statistics(strategy.get_name(), strategy_result_portfolio, mk_data)
            log.info(f"{performance}")
        if params.plot_results:
            strategy_simulator_helper.plot_strategy_vs_market_performance(mk_data, strategy_result_portfolio)

    if params.find_best_performance:
        mk_data = strategy_simulator_helper.prepare_simulation_mk_data(params.ticker, params.max_subset_data_length, params.start_date, params.end_date, params.interval)
        performances_by_subset_data_length = strategy_simulator_helper.get_strategy_performances_by_subset_data_length(params.min_subset_data_length, params.max_subset_data_length, mk_data,
                                                                                                                       params.strategy_type)

        if params.calculate_over_market_performance:
            performances_by_subset_data_length = strategy_simulator_helper.get_strategy_over_market_performances(performances_by_subset_data_length, mk_data, config.SIMULATOR_INITIAL_CASH)

        if params.print_results:
            best_performance_subset_data_length = max(performances_by_subset_data_length, key=performances_by_subset_data_length.get)
            best_performance = performances_by_subset_data_length[best_performance_subset_data_length]

            log.info(f"All performance results found for data length: {performances_by_subset_data_length}")
            log.info(f"Best performance ({best_performance}) has been found for data length: {best_performance_subset_data_length}")

        if params.plot_results:
            strategy_simulator_helper.plot_performance_of_data_lengths(performances_by_subset_data_length)


if __name__ == "__main__":
    start = time.time()
    app_config.configure_app()
    log.info("App initialized")

    program_parameters = args_helper.parse_args_into_params()
    log.info(f"Parameters have been successfully set")

    run(program_parameters)
    log.info(f"App ran for: {time.time() - start} s")
