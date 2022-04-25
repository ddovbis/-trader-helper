from pandas import DataFrame


def get_data_subset(data: DataFrame, index_start: int, index_end: int = None) -> DataFrame:
    """
    Extracts a subset of rows from a DataFrame
    :param data: df to extract subset from
    :param index_start: beginning of the subset (inclusive)
    :param index_end: end of the subset (exclusive)
    :return: DataFrame with resulted rows
    """
    if not index_end:
        index_end = len(data)

    return data.iloc[index_start:index_end]


def get_last_value(data: DataFrame, column_name: str):
    return data[column_name].iloc[-1]
