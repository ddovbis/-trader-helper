import logging
from collections import OrderedDict
from datetime import timedelta

import matplotlib.pyplot as plt
from pandas import Timestamp, DataFrame

from resources import config
from src.constants import statistics_fields
from src.constants.mk_data_fields import MkDataFields
from src.helper import formatter
from src.helper.mk_data import av_crypto_helper
from src.model.mk_data import MkData
from src.model.performance_statistics import PerformanceStatistics
from src.model.single_ticker_portfolio import SingleTickerPortfolio
from src.model.transaction_type import TransactionType
from src.strategy import strategy_factory
from src.strategy.strategy import IStrategy
from src.strategy_simulator.strategy_simulator import StrategySimulator

log = logging.getLogger(__name__)


# [IMPROVEMENT] make offset possible for other intervals than 1d
def prepare_simulation_mk_data(ticker, subset_data_length, start_date, end_date, interval):
    left_offset = formatter.get_timedelta(subset_data_length - 1, interval)  # get extra data for making decision for the first entry
    start_date_with_offset = start_date - left_offset

    data = av_crypto_helper.download_daily_historical_data(ticker=ticker, _from=start_date_with_offset, to=end_date)
    return MkData(ticker, start_date, end_date, interval, data)


def get_strategy_performances_by_subset_data_length(min_subset_data_length, max_subset_data_length, mk_data: MkData, strategy_type):
    orig_data = mk_data.data

    result = OrderedDict()
    for subset_data_length in range(min_subset_data_length, max_subset_data_length + 1):
        # truncate mk_data up to subset_data_length
        left_offset = timedelta(days=subset_data_length - 1)
        start_date_with_offset = formatter.extract_time_and_convert_to_string(mk_data.start_date, config.GENERAL_DATE_FORMAT, left_offset)
        mk_data.data = orig_data.truncate(before=Timestamp(start_date_with_offset))

        # get performance for this data length
        strategy = strategy_factory.get_concrete_strategy(strategy_type, mk_data.ticker, subset_data_length)
        strategy_portfolio = simulate(mk_data, strategy, subset_data_length)
        strategy_performance = _get_strategy_performance(mk_data, strategy_portfolio)
        result[subset_data_length] = strategy_performance

        if len(result) % 10 == 0:
            log.info(f"Processed strategy simulations: {len(result)}")

    log.info(f"Processed all strategy simulations: {len(result)}")
    return result


def get_strategy_over_market_performances(strategy_performances_by_subset_data_length: dict, mk_data: MkData, initial_cash):
    market_performance = _get_market_performance_from_data(mk_data, initial_cash)

    result = OrderedDict()
    for subset_data_length, strategy_performance in strategy_performances_by_subset_data_length.items():
        over_market_performance = strategy_performance - market_performance
        result[subset_data_length] = over_market_performance

    return result


def simulate(mk_data: MkData, strategy: IStrategy, subset_data_length) -> SingleTickerPortfolio:
    """
    Runs given strategy on the appropriate simulator
    :param mk_data: market data to use for simulations
    :param strategy: strategy to run
    :param subset_data_length: nr. of previous, historical data-points to give to the strategy to
                            make a decision on each every separate data-point of the market-data
    :return: performance statistics including how well the strategy worked overall, as well as how well
            it performed in comparison to the market (buy&hold)
    """
    simulator = StrategySimulator()
    return simulator.simulate(mk_data, subset_data_length, strategy)


def get_performance_statistics(strategy_name: str, portfolio: SingleTickerPortfolio, mk_data):
    """
    Generates statistics with details about how the strategy performed
    :param strategy_name: name of the strategy that has been applied
    :param portfolio: portfolio containing ticker, and final cash and holdings information
    :param mk_data: market data that has been used for simulating the transactions
    :return: PerformanceStatistics
    """
    market_performance = _get_market_performance_from_data(mk_data, portfolio.initial_cash)
    strategy_performance = _get_strategy_performance(mk_data, portfolio)
    strategy_vs_market_performance = strategy_performance - market_performance

    return PerformanceStatistics(
        strategy_name=strategy_name,
        strategy_performance=strategy_performance,
        market_performance=market_performance,
        strategy_vs_market_performance=strategy_vs_market_performance,
        nr_of_transactions=len(portfolio.transactions),
        paid_fees=portfolio.paid_fees
    )


def _get_market_performance_from_data(mk_data: MkData, initial_cash):
    market_end_value = _get_buy_and_hold_value(mk_data, initial_cash)
    return (market_end_value - initial_cash) * 100 / initial_cash


def _get_buy_and_hold_value(mk_data: MkData, initial_cash):
    buy_at = mk_data.data.loc[Timestamp(mk_data.start_date)][MkDataFields.CLOSE]
    sell_at = mk_data.data.loc[Timestamp(mk_data.end_date)][MkDataFields.CLOSE]
    return (initial_cash / buy_at) * sell_at


def _get_strategy_performance(mk_data: MkData, portfolio):
    strategy_end_value = portfolio.cash
    if portfolio.holdings > 0:
        sell_at = mk_data.data.loc[Timestamp(mk_data.end_date)][MkDataFields.CLOSE]
        strategy_end_value += (portfolio.holdings * sell_at)

    return (strategy_end_value - portfolio.initial_cash) * 100 / portfolio.initial_cash


def plot_performance_of_data_lengths(strategy_performances_by_subset_data_length: dict):
    """
    Plots strategy performances for each subset data length
    :param strategy_performances_by_subset_data_length: dict with key: subset data length -> value: performance
    :return: does not return anything but pops up a new window with the plot
    """
    plt.bar(strategy_performances_by_subset_data_length.keys(), strategy_performances_by_subset_data_length.values())

    plt.xlabel(config.PERF_BY_SUBSET_DATA_LENGTH_X_LABEL)
    plt.ylabel(config.PERF_BY_SUBSET_DATA_LENGTH_Y_LABEL)

    plt.show()


def plot_strategy_vs_market_performance(mk_data: MkData, strategy_portfolio: SingleTickerPortfolio):
    """
    Computes strategy portfolio value over time
    Extracts the data points when BUY/SELL transactions took place
    Computes buy&hold value over time for the same period
    Plots all data above into a comparison diagram

    :param mk_data: market data for the period when portfolio had been trading
    :param strategy_portfolio: portfolio used to trade using the strategy
    :return: does not return anything but pops up a new window with the plot
    """

    # make sure there is no offset data
    data = mk_data.data.truncate(before=Timestamp(mk_data.start_date), after=Timestamp(mk_data.end_date))

    # calculate value over time for both
    portfolio_value_over_time = _get_portfolio_value_over_time(data, strategy_portfolio)
    buy_and_hold_value_over_time = _get_buy_and_hold_value_over_time(data, strategy_portfolio.initial_cash)

    # extract buy/sell data points to highlight them
    buy_data_points = _get_data_points_by_transaction_type(strategy_portfolio.transactions, portfolio_value_over_time, TransactionType.BUY)
    sell_data_points = _get_data_points_by_transaction_type(strategy_portfolio.transactions, portfolio_value_over_time, TransactionType.SELL)

    # plot strategy portfolio data
    plt.plot(portfolio_value_over_time.keys(), portfolio_value_over_time.values(), color='skyblue', label=config.STRATEGY_SIMULATION_STRATEGY_PORTFOLIO_LABEL)
    plt.plot(buy_data_points.keys(), buy_data_points.values(), marker=".", color='red', linestyle='None', markersize=config.STRATEGY_SIMULATION_MARKER_SIZE,
             label=config.STRATEGY_SIMULATION_BUY_MARK_LABEL)
    plt.plot(sell_data_points.keys(), sell_data_points.values(), marker=".", color='green', linestyle='None', markersize=config.STRATEGY_SIMULATION_MARKER_SIZE,
             label=config.STRATEGY_SIMULATION_SELL_MARK_LABEL)

    # plot buy and hold data
    plt.plot(buy_and_hold_value_over_time.keys(), buy_and_hold_value_over_time.values(), label=config.STRATEGY_SIMULATION_BUY_AND_HOLD_PORTFOLIO_LABEL)

    # plot explanations
    plt.xlabel(config.STRATEGY_SIMULATION_X_LABEL)
    plt.ylabel(config.STRATEGY_SIMULATION_Y_LABEL)
    plt.legend()

    # display plotted data
    plt.show()


def _get_portfolio_value_over_time(data: DataFrame, strategy_portfolio: SingleTickerPortfolio) -> OrderedDict:
    # get a map of key: Timestamp / value: Transaction
    timestamp_to_transaction_dict = {transaction.timestamp: transaction for transaction in strategy_portfolio.transactions}

    first_entry_processed = False
    last_registered_transaction = None
    result = OrderedDict()
    for timestamp, row in data.iterrows():
        if timestamp in timestamp_to_transaction_dict:
            # calculate value based on the cash, and holdings found in the transaction's account summary
            transaction = timestamp_to_transaction_dict[timestamp]
            account_summary = transaction.statistics[statistics_fields.ACCOUNT_SUMMARY]
            portfolio_value = _get_portfolio_value_from_account_summary(account_summary, row[MkDataFields.CLOSE])
            last_registered_transaction = transaction
        else:
            if first_entry_processed:
                if not last_registered_transaction:
                    # if no transactions have been found yet, there is still only initial cash in portfolio
                    portfolio_value = next(reversed(result.values()))
                else:
                    # find out the holdings of the portfolio from the latest transaction and calculate value based on current price
                    account_summary = last_registered_transaction.statistics[statistics_fields.ACCOUNT_SUMMARY]
                    portfolio_value = _get_portfolio_value_from_account_summary(account_summary, row[MkDataFields.CLOSE])
            else:
                # if first entry has not been processed yet, the portfolio value is initial cash
                portfolio_value = strategy_portfolio.initial_cash
                first_entry_processed = True

        result[timestamp] = portfolio_value

    return result


def _get_portfolio_value_from_account_summary(account_summary, price):
    cash = account_summary[statistics_fields.CASH]
    holdings = account_summary[statistics_fields.HOLDINGS]
    holdings_value = holdings * price
    return cash + holdings_value


def _get_buy_and_hold_value_over_time(data: DataFrame, initial_cash: float) -> OrderedDict:
    holdings = initial_cash / data.iloc[0][MkDataFields.CLOSE]

    result = OrderedDict()
    for timestamp, row in data.iterrows():
        portfolio_value = holdings * row[MkDataFields.CLOSE]
        result[timestamp] = portfolio_value

    return result


def _get_data_points_by_transaction_type(transactions, portfolio_value_over_time, transaction_type):
    transactions_timestamps = [transaction.timestamp for transaction in transactions if transaction.action_type is transaction_type]
    return {timestamp: portfolio_value_over_time[timestamp] for timestamp in transactions_timestamps}


def _get_performance_summary(self, strategy, performance_statistics):
    return {
        statistics_fields.STRATEGY: strategy.get_name(),
        statistics_fields.START_DATE: self.mk_data.start_date,
        statistics_fields.END_DATE: self.mk_data.end_date,
        statistics_fields.PERFORMANCE: performance_statistics
    }
