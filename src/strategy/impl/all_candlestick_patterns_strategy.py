from typing import Tuple

from pandas import DataFrame, Series

from src.helper import talib_helper
from src.model.transaction_type import TransactionType
from src.strategy.strategy import IStrategy


class AllCandleStickPatternsStrategy(IStrategy):
    def get_name(self) -> str:
        return f"AllCandleStickPatternsStrategy"

    def get_transaction_advice(self, data: DataFrame) -> Tuple[TransactionType, dict]:
        data = talib_helper.apply_all_patterns(data)

        last_entry: Series = data.iloc[-1]
        patterns_series = last_entry.filter(like='CDL')
        found_patterns = patterns_series[patterns_series != 0]

        if len(found_patterns) == 0:
            return TransactionType.HOLD, {"Reason": "No patterns found"}
        else:
            bullish_found_patterns, bearish_found_patterns = talib_helper.get_pattern_results_by_type(found_patterns)
            bullish_rating = abs(bullish_found_patterns.sum())
            bearish_rating = abs(bearish_found_patterns.sum())

            if bullish_rating > bearish_rating:
                return TransactionType.BUY, found_patterns.to_dict()
            elif bullish_rating < bearish_rating:
                return TransactionType.SELL, found_patterns.to_dict()
            else:
                return TransactionType.HOLD, {"Reason": "Results are indecisive", "Results": found_patterns.to_dict()}
