from typing import Tuple

from pandas import DataFrame

from src.constants.mk_data_fields import MkDataFields
from src.helper import pandas_helper
from src.model.transaction_type import TransactionType
from src.strategy.strategy import IStrategy


class MeanSignalStrategy(IStrategy):
    def __init__(self, mean_period):
        self.mean_period = mean_period

    def get_name(self) -> str:
        return f"MeanSignalStrategy(subset_data_length={self.mean_period})"

    def get_transaction_advice(self, data: DataFrame) -> Tuple[TransactionType, dict]:
        """
        Determines if the trend is for the price to go up or down based on the mean price
        :param data: mkdata points to determine the mean price and the last price
        :return: BUY if last price is higher than mean price (uptrend),
                 SELL if it's lower (downtrend), and HOLD if it's equal
         """
        if len(data) < self.mean_period:
            raise ValueError(f"{self.get_name()} strategy requires {self.mean_period} data points to calculate mean price,"
                             f" while only {len(data)} have been provided")

        data = pandas_helper.get_data_subset(data, index_start=len(data) - self.mean_period)
        mean_price = data[MkDataFields.CLOSE].mean()
        last_price = pandas_helper.get_last_value(data, MkDataFields.CLOSE)
        if last_price > mean_price:
            return TransactionType.BUY, {}
        elif last_price < mean_price:
            return TransactionType.SELL, {}
        else:
            return TransactionType.HOLD, {}
