import logging

from resources import config
from src.constants.mk_data_fields import MkDataFields
from src.error.simulator_parameters_error import SimulatorParametersError
from src.helper import pandas_helper
from src.model.mk_data import MkData
from src.model.single_ticker_portfolio import SingleTickerPortfolio
from src.strategy.strategy import IStrategy


class StrategySimulator:
    log = logging.getLogger(__name__)

    @staticmethod
    def simulate(mk_data: MkData, subset_data_length: int, strategy: IStrategy) -> SingleTickerPortfolio:
        """
        Simulates applying a trend strategy on historical data
        :param mk_data: historical data to use
        :param subset_data_length: length of data points on which the trend should be checked
        :param strategy: trend strategy to simulate
        :return: a simulated portfolio, with remaining cash, holdings, and all buy/sell transactions
        """
        data = mk_data.data
        data_length = len(data.index)
        if subset_data_length > data_length:
            raise SimulatorParametersError(f"Mk data length[{data_length}] is smaller than target subset data length[{subset_data_length}]!")

        portfolio = SingleTickerPortfolio(mk_data.ticker, config.SIMULATOR_INITIAL_CASH, config.SIMULATOR_TRANSACTIONS_FEE, config.SIMULATOR_LOG_TRANSACTIONS)

        for start_index in range(0, data_length):
            if start_index > data_length - subset_data_length:
                break

            data_subset = pandas_helper.get_data_subset(data, index_start=start_index, index_end=start_index + subset_data_length)

            transaction_advice, details = strategy.get_transaction_advice(data_subset)

            reference_timestamp = data_subset.index[-1]
            reference_price = data_subset[MkDataFields.CLOSE][-1]

            portfolio.register_transaction(reference_timestamp, reference_price, transaction_advice, details)

        return portfolio
