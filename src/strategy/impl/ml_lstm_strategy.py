import collections
import logging
import os
from os import path
from typing import Tuple

import tensorflow as tf
from pandas import DataFrame, Timestamp

from resources import config
from src.error.ml_setup_error import MlSetupError
from src.helper import pandas_helper, ml_lstm_helper
from src.helper.mk_data import av_crypto_helper
from src.model.transaction_type import TransactionType
from src.strategy.strategy import IStrategy


class MlLstmStrategy(IStrategy):
    log = logging.getLogger(__name__)

    def __init__(self, ticker, data_set_length, epochs=10, hold_range=0.0):
        self.models = collections.OrderedDict()
        self.ticker = ticker
        self.data_set_length = data_set_length
        self.time_steps = data_set_length - 2
        self.epochs = epochs
        self.buy_threshold, self.sell_threshold = self._get_buy_sell_thresholds(hold_range)

    @staticmethod
    def _get_buy_sell_thresholds(hold_range):
        if hold_range < 0 or hold_range > 1:
            raise MlSetupError("hold_range must be between 0 and 1")

        return 0.5 + (hold_range / 2), 0.5 - (hold_range / 2)

    def get_name(self) -> str:
        return f"MlLstmStrategy(subset_data_length={self.data_set_length})"

    def get_transaction_advice(self, data: DataFrame) -> Tuple[TransactionType, dict]:
        if len(data) < self.data_set_length:
            raise ValueError(f"{self.get_name()} strategy requires {self.data_set_length} data points to calculate mean price,"
                             f" while only {len(data)} have been provided")

        # strip only the data withing the length of the necessary data set
        data = pandas_helper.get_data_subset(data, index_start=len(data) - self.data_set_length)

        # transform to percentage
        data = data.pct_change()

        # drop nulls (the first row, as there would not be pct change)
        data = data.dropna()

        ml_lstm_helper.clean_up_data(data)

        # add new column that shows whether the price for historical prices would go up or down
        ml_lstm_helper.add_direction_column(data)

        # create one single entry point based on the subset
        # steps should be the total number of entries minus 1 (removed nulls) minus 1 (the actual entry that will include the time steps)
        time_steps = self.data_set_length - 1 - 1
        x_test, _ = ml_lstm_helper.create_dataset(data, data[ml_lstm_helper.TARGET_COLUMN], time_steps)

        # extract the latest model created based on the data set prior to the first date in the analyzed data
        first_data_set_date = data.index[0]

        model = self._get_model(first_data_set_date)
        # model = self._get_latest_available_model_before_date(first_data_set_date)

        # feed data set into model to get prediction
        y_predicted = model.predict(x_test)

        # result is a value between 0 and 1, where closer to 0 is SELL, and closer to 1 is BUY
        prediction = y_predicted[0][0]

        # return transaction advice based on the prediction value range
        if prediction < self.sell_threshold:
            return TransactionType.SELL, {"prediction": prediction}
        elif prediction > self.buy_threshold:
            return TransactionType.BUY, {"prediction": prediction}
        else:
            return TransactionType.HOLD, {"prediction": prediction}

    def _get_model(self, date: Timestamp):
        # model date should be Dec 31 of the previous year
        model_year = int(date.year) - 1
        model_timestamp = f"{model_year}-12-31"

        # check if model is already in the dict
        if model_timestamp in self.models:
            return self.models[model_timestamp]

        # check if model is already computed, and load it if so
        model_dir_name = f"model_{self.ticker}_{self.time_steps}-steps_{self.epochs}-epochs_until-{model_timestamp}"
        model_path = os.path.join(config.LSTM_MODELS_PATH, model_dir_name)
        if path.exists(model_path):
            self.log.info(f"Saved model found, load Model by path: {model_path}")
            model = tf.keras.models.load_model(model_path)
            self.models[model_timestamp] = model
            self.log.info(f"Model loaded")
            return model

        # compute, and save new model
        self.log.info(f"New model required, train and save model by path: {model_path}")
        raw_model_data = av_crypto_helper.download_daily_historical_data(ticker=self.ticker, _from=None, to=Timestamp(model_timestamp))
        model = ml_lstm_helper.compute_model(raw_data=raw_model_data, time_steps=self.time_steps, test_data_split_pct=0, epochs=self.epochs)
        model.save(model_path)
        self.models[model_timestamp] = model
        self.log.info(f"Model created")
        return model

    def _get_latest_available_model_before_date(self, date):
        """
        Finds the newest model before the provided date
        :param date: the date the model should precede
        :return: the newest model
        """
        latest_model = None
        for model_date, model in self.models.items():
            model_date = Timestamp(model_date)
            if model_date < date:
                latest_model = model
            else:
                if not latest_model:
                    raise MlSetupError(f"Could not find a model for data set before date: {date}")
                else:
                    return latest_model
