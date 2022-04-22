from datetime import timedelta

import yfinance as yf
from pandas import DataFrame

from src.constants.mk_data_fields import MkDataFields
from src.error.mk_data_format_error import MkDataFormatError
from src.helper import formatter
from src.model.single_ticker_portfolio import SingleTickerPortfolio

"""Helper functions for yfinance library and its data"""

_DATE_FORMAT = "%Y-%m-%d"
_INTRA_DAY_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']


def download(ticker, interval, start_date, end_date=None, left_offset: timedelta = None):
    """
    Extends original 'yfinance.download' function by presetting
    progress, auto_adjust, and resetting index, which results in adding "Date" column
    :param ticker: ticker of the data to download
    :param interval: interval between downloaded data points
    :param start_date: start date of the data to download
    :param end_date: download end date string (YYYY-MM-DD) or _datetime; default is now
    :param left_offset: offsets start_date to left by the provided timedelta;
                        can be used for
                           - getting data for strategies, e.g.,
                             if strategy checks t-5..t to make a decision on t, where t is one day,
                             then left_offset should be timedelta(days=5);
                           - to get more historical data, which then is used to get the price on end_date, or the last price before that,
                             if end_date was not a trading day;
    :return: mkdata
    """
    if left_offset is not None:
        start_date = formatter.extract_time_from_str_date(start_date, _DATE_FORMAT, left_offset)

    # start_date, end_date = _normalize_start_end_dates(start_date, end_date, interval)
    raw_data = yf.download(ticker, start=start_date, end=end_date, progress=False, interval=interval, auto_adjust=True)
    return _normalize_data(raw_data)


def _normalize_data(raw_data: DataFrame):
    """
    Normalizes data by:
     - Resetting index, thus making the indexed column a regular one, which makes df manipulations more consistent
     - Renaming either previosly indexed column to :func:MkDataFields.TIMESTAMP for consistency
    :param raw_data: dataframe indexed on either 'Date' (if data interval is greater than 1d) or 'Datatime' (otherwise)
    :return: normalized data
    """
    normalized_data = raw_data.reset_index()  # move "Date/Datetime" to a column instead of index

    if "Date" in normalized_data.columns:
        normalized_data.rename(columns={"Date": MkDataFields.TIMESTAMP}, inplace=True)
    elif "Datetime" in normalized_data.columns:
        normalized_data.rename(columns={"Datetime": MkDataFields.TIMESTAMP}, inplace=True)
    elif "index" in normalized_data.columns:
        normalized_data.rename(columns={"index": MkDataFields.TIMESTAMP}, inplace=True)
    else:
        raise MkDataFormatError(f"Neither 'Date' nor 'Datetime' column is in data, "
                                f"could not create {MkDataFields.TIMESTAMP} column; "
                                f"data:\n"
                                f"{normalized_data}")

    return normalized_data


def get_historical_price(ticker, asof):
    """
    Gets historical price for the provided date
    If provided date has no data (e.g., because it's a bank holiday), the method will return the most recent price prior to the provided date
    :param ticker: ticker for which the price should be provided
    :param asof: date for which the price should be provided
    :return: last available price of the provided date, or the most recent one prior to this date
    """
    left_offset = timedelta(days=5)  # 5d to account for any bank holidays/weekends
    data = download(ticker, interval='1d', start_date=asof, end_date=asof, left_offset=left_offset)
    if data.empty:
        raise MkDataFormatError(f"Got empty market data while retrieving last historical price for ticker[{ticker}] as of: {asof}")

    return get_last_close_price(data)


def get_current_price(ticker):
    yf_ticker = yf.Ticker(ticker)
    data = yf_ticker.history(period='5d')  # 5d to account for any bank holidays/weekends
    return get_last_close_price(data)


def get_last_close_price(data: DataFrame):
    return data[MkDataFields.CLOSE].iloc[-1]


def get_portfolio_value(portfolio: SingleTickerPortfolio, asof: str = None) -> float:
    """
    Calculates portfolio value summing up the cash and holdings
    :param portfolio: portfolio that holds ticker amounts and cash
    :param asof: date for which to calculate the value, if not provided "today" date will be used
    :return: value of the portfolio
    """
    total_value = portfolio.cash
    if portfolio.holdings > 0:
        if asof:
            price = get_historical_price(portfolio.ticker, asof)
        else:
            price = get_current_price(portfolio.ticker)

        total_value += (portfolio.holdings * price)

    return total_value
