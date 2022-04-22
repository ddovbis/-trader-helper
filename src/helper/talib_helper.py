from typing import Tuple

import talib
from pandas import DataFrame, Series

from src.constants import ta_lib_candlestick_patterns
from src.constants.mk_data_fields import MkDataFields


# pandas.options.mode.chained_assignment = None


def apply_all_patterns(data: DataFrame) -> DataFrame:
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


def get_pattern_results_by_type(found_patterns: Series) -> Tuple[Series, Series]:
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
