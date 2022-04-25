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
from src.strategy.strategy import IStrategy
from src.strategy_simulator.strategy_simulator import StrategySimulator

log = logging.getLogger(__name__)


def prepare_simulation_mk_data(ticker, subset_data_length, start_date, end_date, interval):
    left_offset = timedelta(days=subset_data_length - 1)
    start_date_with_offset = formatter.extract_time_from_str_date(start_date, config.GENERAL_DATE_FORMAT, left_offset)
    data = av_crypto_helper.download_daily_historical_data(ticker=ticker, _from=start_date_with_offset, to=end_date)
    return MkData(ticker, start_date, end_date, interval, data)


def run_simulation(mk_data, subset_data_length, strategy, print_performance_results, plot_value_over_time):
    """
    Runs simulation and outputs appropriate results based on the parameters
    :param mk_data: market data over which should the simulation to be run
    :param subset_data_length: how many historical mk_data entry points should be used for each transaction decision
    :param strategy: strategy that needs to be applied to decide what type of transaction should be made for each step
    :param print_performance_results: parameter, if enabled strategy performance results will be logged
    :param plot_value_over_time: parameter, if enabled value over time will be plotted for both strategy results, and buy&hold results
    :return:
    """
    if not print_performance_results and not plot_value_over_time:
        log.error(f"Nothing to do: print_performance_results[{print_performance_results}], plot_value_over_time[{plot_value_over_time}]")
        return

    # simulate strategy
    strategy_result_portfolio: SingleTickerPortfolio = _simulate(mk_data, strategy, subset_data_length)

    # use results
    if print_performance_results:
        performance = get_performance_statistics(strategy.get_name(), strategy_result_portfolio, mk_data.start_date, mk_data.end_date)
        log.info(f"{performance}")
    if plot_value_over_time:
        plot_strategy_vs_market_performance(mk_data, strategy_result_portfolio)


def _simulate(mk_data: MkData, strategy: IStrategy, subset_data_length) -> SingleTickerPortfolio:
    """
    Runs given strategy on the appropriate simulator, using self.mkdata
    :param mk_data: market data to use for simulations
    :param strategy: strategy to run
    :param subset_data_length: nr. of previous, historical data-points to give to the strategy to
                            make a decision on each every separate data-point of the market-data
    :return: performance statistics including how well the strategy worked overall, as well as how well
            it performed in comparison to the market (buy&hold)
    """
    simulator = StrategySimulator()
    return simulator.simulate(mk_data, subset_data_length, strategy)


def get_performance_statistics(strategy_name: str, portfolio: SingleTickerPortfolio, start_date, end_date):
    """
    Generates statistics:
        - Strategy performance - % of final gains, comparing to the initial cash amount
        - Market performance - % of total gains over the initial amount, if the ticker
            would be bought at the first data point and sold at the last one
        - Strategy vs. Market performance - % of the difference between first two
    :param strategy_name: name of the strategy that has been applied
    :param end_date: timestamp when transacting started
    :param start_date: timestamp when transacting ended
    :param portfolio: portfolio containing ticker, and final cash and holdings information
    :return: statistics generated as a dict of statistics type -> value
    """
    market_end_value = _get_buy_and_hold_value(portfolio.ticker, portfolio.initial_cash, start_date, end_date)
    market_performance = (market_end_value - portfolio.initial_cash) * 100 / portfolio.initial_cash
    formatted_buy_n_hold_performance = formatter.format_percentage(market_performance)

    strategy_end_value = av_crypto_helper.get_portfolio_value(portfolio, end_date)
    strategy_performance = (strategy_end_value - portfolio.initial_cash) * 100 / portfolio.initial_cash
    formatted_strategy_performance = formatter.format_percentage(strategy_performance)

    strategy_vs_market_performance = strategy_performance - market_performance
    formatted_strategy_vs_market_performance = formatter.format_percentage(strategy_vs_market_performance)

    formatted_paid_fees = formatter.format_currency_value(portfolio.paid_fees)

    return PerformanceStatistics(
        strategy_name=strategy_name,
        strategy_performance=formatted_strategy_performance,
        market_performance=formatted_buy_n_hold_performance,
        strategy_vs_market_performance=formatted_strategy_vs_market_performance,
        nr_of_transactions=len(portfolio.transactions),
        paid_fees=formatted_paid_fees
    )


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
    plt.plot(portfolio_value_over_time.keys(), portfolio_value_over_time.values(), color='skyblue', label=config.STRATEGY_PORTFOLIO_LABEL)
    plt.plot(buy_data_points.keys(), buy_data_points.values(), marker=".", color='red', linestyle='None', markersize=config.MARKER_SIZE, label=config.BUY_MARK_LABEL)
    plt.plot(sell_data_points.keys(), sell_data_points.values(), marker=".", color='green', linestyle='None', markersize=config.MARKER_SIZE, label=config.SELL_MARK_LABEL)

    # plot buy and hold data
    plt.plot(buy_and_hold_value_over_time.keys(), buy_and_hold_value_over_time.values(), label=config.BUY_AND_HOLD_PORTFOLIO_LABEL)

    # display plotted data
    plt.legend()
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


def _get_buy_and_hold_value(ticker, initial_holdings_usd, start_date, end_date):
    buy_at = av_crypto_helper.get_historical_price(ticker, start_date)
    sell_at = av_crypto_helper.get_historical_price(ticker, end_date)
    return (initial_holdings_usd / buy_at) * sell_at


def _get_performance_summary(self, strategy, performance_statistics):
    return {
        statistics_fields.STRATEGY: strategy.get_name(),
        statistics_fields.START_DATE: self.mk_data.start_date,
        statistics_fields.END_DATE: self.mk_data.end_date,
        statistics_fields.PERFORMANCE: performance_statistics
    }
