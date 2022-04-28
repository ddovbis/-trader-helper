from pandas import Timestamp


class ProgramParameters:
    def __init__(self,
                 start_date: Timestamp, end_date: Timestamp, interval: str, ticker: str,  # mkdata parameters
                 strategy_type: type,  # strategy that needs to be simulated
                 simulate_strategy: bool, find_best_performance: bool,  # simulation type
                 print_results: bool, plot_results: bool, calculate_over_market_performance: bool,  # results reporting setup
                 subset_data_length: int, min_subset_data_length: int, max_subset_data_length: int  # simulation setup
                 ):
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.ticker = ticker
        self.strategy_type = strategy_type
        self.simulate_strategy = simulate_strategy
        self.find_best_performance = find_best_performance
        self.print_results = print_results
        self.plot_results = plot_results
        self.calculate_over_market_performance = calculate_over_market_performance
        self.subset_data_length = subset_data_length
        self.min_subset_data_length = min_subset_data_length
        self.max_subset_data_length = max_subset_data_length
