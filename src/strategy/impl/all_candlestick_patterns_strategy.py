from typing import Tuple

import talib
from pandas import DataFrame, Series

from src.constants import ta_lib_candlestick_patterns
from src.constants.mk_data_fields import MkDataFields
from src.model.transaction_type import TransactionType
from src.strategy.strategy import IStrategy


class AllCandleStickPatternsStrategy(IStrategy):
    def get_name(self) -> str:
        return f"AllCandleStickPatternsStrategy"

    def get_transaction_advice(self, data: DataFrame) -> Tuple[TransactionType, dict]:
        data = self._apply_all_patterns(data)

        last_entry: Series = data.iloc[-1]
        patterns_series = last_entry.filter(like='CDL')
        found_patterns = patterns_series[patterns_series != 0]

        if len(found_patterns) == 0:
            return TransactionType.HOLD, {"Reason": "No patterns found"}
        else:
            bullish_found_patterns, bearish_found_patterns = self._get_pattern_results_by_type(found_patterns)
            bullish_rating = abs(bullish_found_patterns.sum())
            bearish_rating = abs(bearish_found_patterns.sum())

            if bullish_rating > bearish_rating:
                return TransactionType.BUY, found_patterns.to_dict()
            elif bullish_rating < bearish_rating:
                return TransactionType.SELL, found_patterns.to_dict()
            else:
                return TransactionType.HOLD, {"Reason": "Results are indecisive", "Results": found_patterns.to_dict()}

    @staticmethod
    def _apply_all_patterns(data: DataFrame) -> DataFrame:
        """
        Extends provided data with new columns, each representing a specific pattern
        Each pattern column will give a value to each row, where:
            - -200 -> strong SELL
            - -100 -> SELL
            - 0 - Pattern has not been recognized for the row
            - 100 - BUY
            - 200 - strong BUY
        :param data: dataframe with MkDataFields as columns, and mk data entries as rows
        :return: original dataframe with added columns with pattern recognition results
        """
        result = data.copy()
        for function_name, pattern_name in ta_lib_candlestick_patterns.candlestick_patterns.items():
            function = getattr(talib, function_name)
            result[function_name] = function(data[MkDataFields.OPEN], data[MkDataFields.HIGH], data[MkDataFields.LOW], data[MkDataFields.CLOSE])

        return result

    @staticmethod
    def _get_pattern_results_by_type(found_patterns: Series) -> Tuple[Series, Series]:
        """
        Filters bearish and bullish pattern from a series
        Bullish patterns in ta-lib have rating greater than 0, typically 100 or 200
        While bearish have rating below 0, typically -100, or -200
        :param found_patterns: a series of pattern recognition results
        :return: a tuple with bullish and bearish patterns
        """
        bullish = found_patterns[found_patterns > 0]
        bearish = found_patterns[found_patterns < 0]

        return bullish, bearish
