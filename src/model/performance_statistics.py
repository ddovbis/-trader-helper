import json
from collections import OrderedDict

from src.constants import statistics_fields
from src.helper import formatter


class PerformanceStatistics:
    def __init__(self, strategy_name, strategy_performance, market_performance, strategy_vs_market_performance, nr_of_transactions, paid_fees):
        self.paid_fees = paid_fees
        self.nr_of_transactions = nr_of_transactions
        self.strategy_vs_market_performance = strategy_vs_market_performance
        self.market_performance = market_performance
        self.strategy_performance = strategy_performance
        self.strategy_name = strategy_name

    def __str__(self) -> str:
        dict_form = OrderedDict({
            statistics_fields.STRATEGY_NAME: self.strategy_name,
            statistics_fields.STRATEGY_PERFORMANCE: formatter.format_percentage(self.strategy_performance),
            statistics_fields.MARKET_PERFORMANCE: formatter.format_percentage(self.market_performance),
            statistics_fields.STRATEGY_VS_MARKET_PERFORMANCE: formatter.format_percentage(self.strategy_vs_market_performance),
            statistics_fields.NR_OF_TRANSACTIONS: self.nr_of_transactions,
            statistics_fields.PAID_FEES: formatter.format_currency_value(self.paid_fees)
        })
        return json.dumps(dict_form, indent=4)
