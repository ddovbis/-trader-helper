import logging

import numpy
from pandas import DataFrame

from src.constants.mk_data_fields import MkDataFields
from src.error.mk_data_format_error import MkDataFormatError
from src.helper import formatter


class MkData:
    DATA_COLUMNS_TO_DTYPES = {
        MkDataFields.TIMESTAMP: numpy.datetime64,
        MkDataFields.OPEN: numpy.float64,
        MkDataFields.HIGH: numpy.float64,
        MkDataFields.LOW: numpy.float64,
        MkDataFields.CLOSE: numpy.float64,
        MkDataFields.VOLUME: numpy.int64
    }

    def __init__(self, ticker: str, start_date: str, end_date: str, interval: str, data: DataFrame):
        self.log = logging.getLogger(__name__)
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.data = data
        self._validate_data()

        self.log.info(f"{self.__str__()} has been successfully initialized with {len(data)} data points")

    def _validate_data(self):
        if self.data.empty:
            raise MkDataFormatError("Data is empty!\n"
                                    f"{self}")

        # check there is the expected nr. of columns
        expected_columns = [*MkData.DATA_COLUMNS_TO_DTYPES]
        expected_columns_count = len(expected_columns)
        actual_columns = [self.data.index.name] + list(self.data.columns)
        actual_columns_count = len(actual_columns)
        if actual_columns_count != expected_columns_count:
            raise MkDataFormatError(f"Expected to have {expected_columns_count} columns in market data df: {expected_columns};\n"
                                    f"But there are {actual_columns_count}: {actual_columns}")

        # check all columns have the expected names and dtypes
        actual_column_to_dtypes = self.data.dtypes
        for column_name, dtype in MkData.DATA_COLUMNS_TO_DTYPES.items():
            if column_name != MkDataFields.TIMESTAMP and column_name not in actual_column_to_dtypes:
                raise MkDataFormatError(f"Could not find {column_name} in market data df: {actual_columns}")

    def __str__(self):
        return formatter.obj_to_str(self, ['log', 'data'])
