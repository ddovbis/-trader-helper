from pandas import Timestamp

from src.helper import formatter
from src.model.transaction_type import TransactionType


class Transaction:
    def __init__(self, action_type: TransactionType, timestamp: Timestamp, price: float, statistics: dict):
        self.action_type = action_type
        self.timestamp = timestamp
        self.price = price
        self.statistics = statistics

    def __str__(self) -> str:
        return formatter.obj_to_str(self)
