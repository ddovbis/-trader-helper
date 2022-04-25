from src.strategy.impl.mean_signal_strategy import MeanSignalStrategy
from src.strategy.strategy import IStrategy


def get_concrete_strategy(strategy_type, ticker, subset_data_length) -> IStrategy:
    if strategy_type == MeanSignalStrategy:
        return MeanSignalStrategy(subset_data_length)
    else:
        raise NotImplementedError()
