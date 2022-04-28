from src.strategy.impl.all_candlestick_patterns_strategy import AllCandleStickPatternsStrategy
from src.strategy.impl.mean_signal_strategy import MeanSignalStrategy
from src.strategy.impl.ml_lstm_strategy import MlLstmStrategy
from src.strategy.strategy import IStrategy


def get_concrete_strategy(strategy_type, ticker, subset_data_length) -> IStrategy:
    if strategy_type == MeanSignalStrategy:
        return MeanSignalStrategy(subset_data_length)
    elif strategy_type == MlLstmStrategy:
        return MlLstmStrategy(ticker, subset_data_length)
    elif strategy_type == AllCandleStickPatternsStrategy:
        return AllCandleStickPatternsStrategy()
    else:
        raise NotImplementedError(f"No such strategy: {strategy_type}")
