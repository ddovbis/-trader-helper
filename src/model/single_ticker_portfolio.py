import logging

from src.model.transaction import Transaction
from src.model.transaction_type import TransactionType


class SingleTickerPortfolio:
    log = logging.getLogger(__name__)

    def __init__(self, ticker, initial_cash, transaction_fee_percent=0.00, log_transactions=False):
        self.ticker = ticker
        self.initial_cash: float = initial_cash
        self.cash: float = initial_cash
        self.holdings: float = 0
        self.transaction_fee_percent = transaction_fee_percent
        self.paid_fees: float = 0
        self.transactions = []
        self.log_transactions = log_transactions

    def register_transaction(self, timestamp: str, price: float, transaction_type: TransactionType, details: dict) -> bool:
        """
        Registers a transaction to the portfolio in case if transaction_type is BUY/SELL,
        or does nothing if it is HOLD

        :param timestamp: timestamp of the transaction
        :param price: price of the transaction
        :param transaction_type: what kind of transaction should be registered
        :param details: details of transaction in a dictionary
        :return: True if the transaction registration has been successful, False otherwise
        """
        if transaction_type is TransactionType.BUY:
            return self._register_buy(timestamp, price, details)
        elif transaction_type is TransactionType.SELL:
            return self._register_sell(timestamp, price, details)
        elif transaction_type is TransactionType.HOLD:
            return self._handle_hold(timestamp, details)
        else:
            raise ValueError(f"Unknown TransactionType: {transaction_type}")

    def _register_buy(self, timestamp, price, details) -> bool:
        if self.cash == 0:
            if self.log_transactions:
                self.log.info(f"action_type={TransactionType.BUY}, timestamp={timestamp}: no action required; "
                              f"{self._get_transaction_statistics(details)}")
            return False

        fees = self.cash / 100 * self.transaction_fee_percent
        self.holdings += ((self.cash - fees) / price)
        self.paid_fees += fees
        self.cash = 0

        statistics = self._get_transaction_statistics(details)
        transaction = Transaction(TransactionType.BUY, timestamp, price, statistics)
        self.transactions.append(transaction)

        if self.log_transactions:
            SingleTickerPortfolio.log.info(transaction)

        return True

    def _register_sell(self, timestamp, price, details) -> bool:
        if self.holdings == 0:
            if self.log_transactions:
                self.log.info(f"action_type={TransactionType.SELL}, timestamp={timestamp}: no action required; "
                              f"{self._get_transaction_statistics(details)}")
            return False

        holdings_value = self.holdings * price
        fees = holdings_value / 100 * self.transaction_fee_percent
        self.cash += holdings_value - fees
        self.paid_fees += fees
        self.holdings = 0

        statistics = self._get_transaction_statistics(details)
        transaction = Transaction(TransactionType.SELL, timestamp, price, statistics)
        self.transactions.append(transaction)

        if self.log_transactions:
            SingleTickerPortfolio.log.info(transaction)

        return True

    def _handle_hold(self, timestamp, details):
        if self.log_transactions:
            SingleTickerPortfolio.log.info(f"action_type={TransactionType.HOLD}, timestamp={timestamp}: no action required; "
                                           f"{self._get_transaction_statistics(details)}")
        return True

    def _get_transaction_statistics(self, details):
        result = {
            "Account summary": self.get_summary()
        }

        if details:
            result["Transaction details"] = details

        return result

    def get_summary(self):
        return {
            "cash": self.cash,
            "holdings": self.holdings,
        }
