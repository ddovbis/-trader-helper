import logging
import time
from datetime import timedelta
from io import StringIO

import pandas as pd
import requests
from pandas import DataFrame, Timestamp, Timedelta
from requests import Response

from resources import config
from resources.config import ALPHA_VANTAGE_BASE_URL, ALPHA_VANTAGE_API_KEY, GENERAL_DATE_FORMAT
from src.constants.mk_data_fields import MkDataFields
from src.error.mk_data_format_error import MkDataFormatError
from src.error.mk_data_request_error import MkDataRequestError
from src.helper import formatter

log = logging.getLogger(__name__)


def get_historical_price(ticker, asof):
    """
    Gets historical price for the provided date
    If provided date has no data (e.g., because it's a bank holiday), the method will return the most recent price prior to the provided date
    :param ticker: ticker for which the price should be provided
    :param asof: date for which the price should be provided
    :return: last available price of the provided date, or the most recent one prior to this date
    """
    left_offset = timedelta(days=5)  # 5d to account for any bank holidays/weekends
    start_date = formatter.extract_time_and_convert_to_string(asof, GENERAL_DATE_FORMAT, left_offset)

    data = download_daily_historical_data(ticker, _from=start_date, to=asof)
    if data.empty:
        raise MkDataFormatError(f"Got empty market data while retrieving last historical price for ticker[{ticker}] as of: {asof}")

    # last close price
    return data[MkDataFields.CLOSE].iloc[-1]


def download_daily_historical_data(ticker, _from: str = None, to: str = None) -> DataFrame:
    """
    :param ticker: ticker (e.g., symbol) for which the data should be downloaded
    :param _from: the earliest date for which the data should be included (included into result) - format "YYYY-mm-dd"
    :param to: up to what date the data should be downloaded (excluded from result) - format "YYYY-mm-dd"
    :return: daily historical data for the given ticker and given period
    :raises MkDataRequestError: if there is no data for the '_from' or 'to' dates

    Note: to take into account that present day is not returned
    """
    start_date = Timestamp(_from) if _from else None
    end_date = Timestamp(to) if to else None
    end_date_including = (end_date - pd.Timedelta(days=1)) if end_date else None  # last date to be included into the result

    output_size = _get_req_output_size(start_date, end_date_including)
    params = _get_av_daily_historical_data_params(ticker, output_size)

    response_text = _request_mk_data_with_retry(params)

    df = _av_csv_text_to_df(response_text)
    _validate_timeframe(df, start_date, end_date_including)
    df = _get_slice(df, start_date, end_date_including)

    return df


def _request_mk_data_with_retry(params):
    for i in range(0, config.ALPHA_VANTAGE_MAX_RETRY):
        response: Response = _send_request_with_check(ALPHA_VANTAGE_BASE_URL, params)
        response_text = response.text
        if response_text.strip() == config.ALPHA_VANTAGE_REACHED_LIMIT_ERROR_MSG.strip():
            log.info(f"Reached api-key limit of requesting Market Data (try {i + 1} out of {config.ALPHA_VANTAGE_MAX_RETRY})")
            if i < config.ALPHA_VANTAGE_MAX_RETRY - 1:
                log.info(f"Sleep {config.ALPHA_VANTAGE_WAIT_SECONDS_BEFORE_RETRY} seconds before retry...")
                time.sleep(config.ALPHA_VANTAGE_WAIT_SECONDS_BEFORE_RETRY)
                continue
            else:
                raise MkDataRequestError("Reached limit of retries to request market data")
        else:
            return response_text

    raise MkDataRequestError("Could not get proper response for market data request")


def _get_req_output_size(start_date: pd.Timestamp, end_date: pd.Timestamp):
    def requires_data_older_than_100_days():
        return start_date < Timestamp.now() - Timedelta(days=100)

    def contains_more_than_100_days_of_data():
        return (end_date - start_date).days >= 100

    if start_date is None or requires_data_older_than_100_days() or contains_more_than_100_days_of_data():
        return "full"
    else:
        return "compact"


def _get_av_daily_historical_data_params(ticker, output_size):
    return {
        'function': "TIME_SERIES_DAILY",
        'symbol': ticker,
        'outputsize': output_size,
        'datatype': "csv",
        'apikey': ALPHA_VANTAGE_API_KEY
    }


def _send_request_with_check(base_url, params):
    response: Response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise MkDataRequestError(f"Got an unexpected response when pooling market data: {str(response)}")
    return response


def _av_csv_text_to_df(raw_csv_text):
    try:
        raw_data = StringIO(raw_csv_text)
        df = pd.read_csv(raw_data, parse_dates=['timestamp'], index_col='timestamp') \
            .sort_index() \
            .rename(
            columns={
                "open": MkDataFields.OPEN,
                "high": MkDataFields.HIGH,
                "low": MkDataFields.LOW,
                "close": MkDataFields.CLOSE,
                "volume": MkDataFields.VOLUME
            }
        )
        df.index.names = [MkDataFields.TIMESTAMP]
        return df
    except ValueError:
        raise MkDataFormatError(content=raw_csv_text, save_to_file=True)


def _validate_timeframe(data: DataFrame, start_date: Timestamp, end_date: Timestamp) -> None:
    first_available_date = data.index[0]
    if start_date is not None and start_date < first_available_date:
        raise MkDataRequestError(f"The first available data timestamp is '{first_available_date}', "
                                 f"while the date has been requested from '{start_date}' (including)")

    last_available_date = data.index[-1]
    if end_date is not None and end_date > last_available_date:
        raise MkDataRequestError(f"The last available data timestamp is '{last_available_date}', "
                                 f"while the date has been requested for up to '{end_date}' (excluding)")


def _get_slice(full_data: DataFrame, start_date: Timestamp, end_date: Timestamp) -> DataFrame:
    if start_date is None and end_date is None:
        return full_data

    start_index = 0
    if start_date is not None:
        start_index = full_data.index.get_loc(start_date)

    end_index = len(full_data)
    if end_date is not None:
        end_index = full_data.index.get_loc(end_date)

    return full_data[start_index:end_index + 1]
