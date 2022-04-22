from abc import ABC, abstractmethod
from typing import Union

from pandas import DataFrame

from src.model.transaction_type import TransactionType

"""
Interface to mark other more specific strategy interfaces or
classes so they can be identified across the app
"""


class IStrategy(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """
        :return: Readable name of the strategy
        """
        pass

    @abstractmethod
    def get_transaction_advice(self, data: DataFrame) -> Union[TransactionType, dict]:
        """
        Analyzes the whole provided data set to generate a transaction advice on the last entry
        of the data set
        :param data: timestamp/open/close/low/high/volume data for a certain period,
                    the last entry is considered to be the current data point,
                    on which the advice should be generated
        :return: a TransactionType which represents the advised action, and the details of the decision, if any
        """
        pass
