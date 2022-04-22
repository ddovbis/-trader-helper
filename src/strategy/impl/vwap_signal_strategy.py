from typing import Tuple

from pandas import DataFrame

from src.constants.mk_data_fields import MkDataFields
from src.helper.mk_data import yf_helper
from src.model.transaction_type import TransactionType
from src.strategy.strategy import IStrategy

"""Volume-Weighted Average Price strategy"""


class VWAPSignalStrategy(IStrategy):
    def __init__(self, mean_period):
        self.mean_period = mean_period

    def get_name(self) -> str:
        return f"VWAPSignalStrategy(subset_data_length={self.mean_period})"

    def get_transaction_advice(self, data: DataFrame) -> Tuple[TransactionType, dict]:
        """
        Determines if the trend is for the price to go up or down based on the
        volume-weighted average price
        :param data: mkdata points to determine the mean price and the last price
        :return: BUY if last price is higher than mean price (uptrend),
                 SELL if it's lower (downtrend), and HOLD if it's equal
        """
        if len(data) < self.mean_period:
            raise ValueError(f"{self.get_name()} strategy requires {self.mean_period} data points to calculate weighted mean price,"
                             f" while only {len(data)} have been provided")

        data = yf_helper.get_data_subset(data, index_start=len(data) - self.mean_period)
        total_volume = data[MkDataFields.VOLUME].sum()

        # vwap is sum of prorated prices
        # prorated price is price * volume/total_volume
        vwap = (data[MkDataFields.CLOSE] * (data[MkDataFields.VOLUME] / total_volume)).sum()

        last_price = yf_helper.get_last_close_price(data)
        if last_price > vwap:
            return TransactionType.BUY, {}
        elif last_price < vwap:
            return TransactionType.SELL, {}
        else:
            return TransactionType.HOLD, {}
