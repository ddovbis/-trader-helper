from src.constants import strategy_statistics_fields as ss_fields
from src.helper import formatter
from src.helper.mk_data import av_crypto_helper
from src.model.mk_data import MkData
from src.model.single_ticker_portfolio import SingleTickerPortfolio
from src.strategy.strategy import IStrategy
from src.strategy_simulator.strategy_simulator import StrategySimulator


class StrategySimulatorRunner:
    def __init__(self, mk_data: MkData):
        self.mk_data = mk_data

    def run(self, strategy: IStrategy, subset_data_length):
        """
        Runs given strategy on the appropriate simulator, using self.mkdata
        :param strategy: strategy to run
        :param subset_data_length: nr. of previous, historical data-points to give to the strategy to
                                make a decision on each every separate data-point of the market-data
        :return: performance statistics including how well the strategy worked overall, as well as how well
                it performed in comparison to the market (buy&hold)
        """
        simulator = StrategySimulator()
        portfolio: SingleTickerPortfolio = simulator.simulate(self.mk_data, subset_data_length, strategy)
        performance_statistics = self._get_performance_statistics(portfolio)
        return self._get_performance_summary(strategy, performance_statistics)

    def _get_performance_statistics(self, portfolio: SingleTickerPortfolio):
        """
        Generates statistics:
            - Strategy performance - % of final gains, comparing to the initial cash amount
            - Market performance - % of total gains over the initial amount, if the ticker
                would be bought at the first data point and sold at the last one
            - Strategy vs. Market performance - % of the difference between first two
        :param portfolio: portfolio containing ticker, and final cash and holdings information
        :return: statistics generated as a dict of statistics type -> value
        """
        market_end_value = self._get_buy_and_hold_value(portfolio.ticker, portfolio.initial_cash)
        market_performance = (market_end_value - portfolio.initial_cash) * 100 / portfolio.initial_cash
        formatted_buy_n_hold_performance = formatter.format_percentage(market_performance)

        strategy_end_value = av_crypto_helper.get_portfolio_value(portfolio, self.mk_data.end_date)
        strategy_performance = (strategy_end_value - portfolio.initial_cash) * 100 / portfolio.initial_cash
        formatted_strategy_performance = formatter.format_percentage(strategy_performance)

        strategy_vs_market_performance = strategy_performance - market_performance
        formatted_strategy_vs_market_performance = formatter.format_percentage(strategy_vs_market_performance)

        formatted_paid_fees = formatter.format_currency_value(portfolio.paid_fees)

        return {
            ss_fields.STRATEGY_PERFORMANCE: formatted_strategy_performance,
            ss_fields.MARKET_PERFORMANCE: formatted_buy_n_hold_performance,
            ss_fields.STRATEGY_VS_MARKET_PERFORMANCE: formatted_strategy_vs_market_performance,
            ss_fields.NR_OF_TRANSACTIONS: len(portfolio.transactions),
            ss_fields.PAID_FEES: formatted_paid_fees
        }

    def _get_buy_and_hold_value(self, ticker, initial_holdings_usd):
        buy_at = av_crypto_helper.get_historical_price(ticker, self.mk_data.start_date)
        sell_at = av_crypto_helper.get_historical_price(ticker, self.mk_data.end_date)
        return (initial_holdings_usd / buy_at) * sell_at

    def _get_performance_summary(self, strategy, performance_statistics):
        return {
            ss_fields.STRATEGY: strategy.get_name(),
            ss_fields.START_DATE: self.mk_data.start_date,
            ss_fields.END_DATE: self.mk_data.end_date,
            ss_fields.PERFORMANCE: performance_statistics
        }
