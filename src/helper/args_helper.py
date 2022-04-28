import argparse
import sys
from argparse import RawTextHelpFormatter

from pandas import Timestamp

from src.error.simulator_parameters_error import SimulatorParametersError
from src.model.program_parameters import ProgramParameters
from src.strategy.strategy import IStrategy

SAMPLE_USAGE = '2017-01-01 2021-12-31 1d BTCUSD MeanSignalStrategy ' \
               '--simulate_strategy --find_best_performance --print_results --plot_results --calculate_over_market_performance ' \
               '-subset_data_length 4 -min_subset_data_length 2 -max_subset_data_length 10'

START_DATE_PARAM = "start_date"
END_DATE_PARAM = "end_date"
INTERVAL_PARAM = "interval"
TICKER_PARAM = "ticker"
STRATEGY_NAME_PARAM = "strategy_name"

SIMULATE_STRATEGY_PARAM = "--simulate_strategy"
FIND_BEST_PERFORMANCE_PARAM = "--find_best_performance"
PRINT_RESULTS_PARAM = "--print_results"
PLOT_RESULTS_PARAM = "--plot_results"
CALCULATE_OVER_MARKET_PERFORMANCE_PARAM = "--calculate_over_market_performance"

SUBSET_DATA_LENGTH_PARAM = "-subset_data_length"
MIN_SUBSET_DATA_LENGTH_PARAM = "-min_subset_data_length"
MAX_SUBSET_DATA_LENGTH_PARAM = "-max_subset_data_length"


def parse_args_into_params():
    parser = _get_parser()
    args = parser.parse_args()
    params = _generate_params(args)
    _validate_params(params)

    return params


# noinspection PyTypeChecker
def _get_parser():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                     description="Trader helper este un program menit să ajute investitorii individuali să testeze stragiile pe date istorice\n"
                                                 "Set de argumente exemplu:\n"
                                                 f"{SAMPLE_USAGE}")

    # required positional argument
    parser.add_argument(START_DATE_PARAM, type=Timestamp, help="Data de start folosită pentru simulări pe date istorice")
    parser.add_argument(END_DATE_PARAM, type=Timestamp, help="Data de sfârșire a perioadei folosite pentru simulări pe date istorice")
    parser.add_argument(INTERVAL_PARAM, type=str, help="Intervalul de timp reprezentat de fiecare intrare a datelor istorice")
    parser.add_argument(TICKER_PARAM, type=str, help="Simbolul bunului pentru care trebuie făcute simulările")
    parser.add_argument(STRATEGY_NAME_PARAM, type=str, help="Denumirea strategiei aplicate")

    flags = parser.add_argument_group('flags')
    flags.add_argument(SIMULATE_STRATEGY_PARAM, action="store_true", help="Parametru pentru executarea unei simulări")
    flags.add_argument(FIND_BEST_PERFORMANCE_PARAM, action="store_true", help="Parametru pentru executarea mai multor simulări cu ajustarea parametrilor în scopul de a găsi performanța optimă")
    flags.add_argument(PRINT_RESULTS_PARAM, action="store_true", help="Parametru pentru afișarea rezultatelor simulării (sau simulărilor) în formă de text")
    flags.add_argument(PLOT_RESULTS_PARAM, action="store_true", help="Parametru pentru afișarea rezultatelor simulării (sau simulărilor) în formă grafică")
    flags.add_argument(CALCULATE_OVER_MARKET_PERFORMANCE_PARAM, action="store_true", help="Parametru pentru afișarea rezultatelor în raport cu performanța naturală a bunului pe bursă")

    conditionally_optional_args = parser.add_argument_group('conditionally optional arguments')
    conditionally_optional_args.add_argument(SUBSET_DATA_LENGTH_PARAM, type=int, required=SIMULATE_STRATEGY_PARAM in sys.argv,
                                             help="Numărul de intrări precedente folosite pentru analiză și luare a fiecărei decizii de tranzacționare; "
                                                  f"acest parametru este obligatoriu în cazul în care parametrul `{SIMULATE_STRATEGY_PARAM}` a fost inclus")

    conditionally_optional_args.add_argument(MIN_SUBSET_DATA_LENGTH_PARAM, type=int, required=FIND_BEST_PERFORMANCE_PARAM in sys.argv,
                                             help="Numărul minim de intrări precedente folosite pentru analiză și luare a fiecărei decizii de tranzacționare; "
                                                  f"acest parametru este obligatoriu în cazul în care parametrul `{FIND_BEST_PERFORMANCE_PARAM}` a fost inclus")

    conditionally_optional_args.add_argument(MAX_SUBSET_DATA_LENGTH_PARAM, type=int, required=FIND_BEST_PERFORMANCE_PARAM in sys.argv,
                                             help="Numărul maxim de intrări precedente folosite pentru analiză și luare a fiecărei decizii de tranzacționare; "
                                                  f"acest parametru este obligatoriu în cazul în care parametrul `{FIND_BEST_PERFORMANCE_PARAM}` a fost inclus")

    return parser


def _generate_params(args):
    return ProgramParameters(
        start_date=_get_arg_value(args, START_DATE_PARAM),
        end_date=_get_arg_value(args, END_DATE_PARAM),
        interval=_get_arg_value(args, INTERVAL_PARAM),
        ticker=_get_arg_value(args, TICKER_PARAM),
        strategy_type=_get_strategy_type(_get_arg_value(args, STRATEGY_NAME_PARAM)),
        simulate_strategy=_get_arg_value(args, SIMULATE_STRATEGY_PARAM),
        find_best_performance=_get_arg_value(args, FIND_BEST_PERFORMANCE_PARAM),
        print_results=_get_arg_value(args, PRINT_RESULTS_PARAM),
        plot_results=_get_arg_value(args, PLOT_RESULTS_PARAM),
        calculate_over_market_performance=_get_arg_value(args, CALCULATE_OVER_MARKET_PERFORMANCE_PARAM),
        subset_data_length=_get_arg_value(args, SUBSET_DATA_LENGTH_PARAM),
        min_subset_data_length=_get_arg_value(args, MIN_SUBSET_DATA_LENGTH_PARAM),
        max_subset_data_length=_get_arg_value(args, MAX_SUBSET_DATA_LENGTH_PARAM))


def _get_arg_value(args, arg_key):
    return getattr(args, arg_key.replace("-", ""))


def _get_strategy_type(strategy_name):
    strategy_name_to_class_dict = {strategy_class.__name__: strategy_class for strategy_class in IStrategy.__subclasses__()}
    if strategy_name not in strategy_name_to_class_dict:
        raise SimulatorParametersError(f"Strategy name '{strategy_name}' is not in the list of available strategies: {list(strategy_name_to_class_dict.keys())}")

    return strategy_name_to_class_dict[strategy_name]


def _validate_params(params):
    """
    Additional validation that is not covered by argparse setup
    :param params: program parameters to validate
    :return: None
    """
    if not params.print_results and not params.plot_results:
        raise SimulatorParametersError("Nothing to do, both print_results and plot_results flags are disabled")
    if params.interval != "1d":
        raise NotImplementedError(f"Only '1d' interval is supported yet")
