import logging

import keras
import numpy as np
from keras import layers
from pandas import DataFrame
from sklearn.metrics import accuracy_score

from src.constants.mk_data_fields import MkDataFields

log = logging.getLogger(__name__)

FEATURE_COLUMNS = [MkDataFields.OPEN, MkDataFields.LOW, MkDataFields.HIGH, MkDataFields.CLOSE, MkDataFields.VOLUME]
DIRECTION = "Direction"
TARGET_COLUMN = DIRECTION


def compute_model(raw_data, time_steps, test_data_split_pct, epochs):
    should_test_accuracy = True if test_data_split_pct > 0 else False

    raw_data = get_clean_raw_data(raw_data)

    # extract percentage changes, since what we are actually looking for is spotting patterns in price change behavior
    data = raw_data.pct_change()

    data = clean_up_data(data)

    # add new column that shows whether the price will go up or down
    add_direction_column(data)

    if should_test_accuracy:
        train_data, test_data = train_test_split(data, test_data_split_pct)

        x_train, y_train = create_dataset(train_data, train_data[TARGET_COLUMN], time_steps)
        x_test, y_test = create_dataset(test_data, test_data[TARGET_COLUMN], time_steps)

        log.debug(f"Train shapes: {x_train.shape}, {y_train.shape}")
        log.debug(f"Test shapes: {x_test.shape}, {y_test.shape}")

        model = prepare_model(x_train)
        train_model(model, x_train, y_train, epochs)

        y_predicted = model.predict(x_test)
        y_predicted = [0 if val < 0.5 else 1 for val in y_predicted]
        log.info(f"Accuracy: {accuracy_score(y_test, y_predicted)}")
    else:
        train_data = data

        x_train, y_train = create_dataset(train_data, train_data[TARGET_COLUMN], time_steps)
        log.debug(f"Train shapes: {x_train.shape}, {y_train.shape}")

        model = prepare_model(x_train)
        train_model(model, x_train, y_train, epochs)

    return model


def get_clean_raw_data(data: DataFrame):
    indexes_with_zero_volume = data.index[data[MkDataFields.VOLUME] == 0].tolist()
    if indexes_with_zero_volume:
        last_index_to_remove = indexes_with_zero_volume[-1]
        keep_data_from_index = data.index.get_loc(last_index_to_remove) + 1

        log.warning("Found entries with volume=0; strip data from the beginning up to the last volume=0 entry...")

        old_start_index = data.index[0]
        initial_size = len(data)
        data = data[keep_data_from_index:]
        log.warning(f"Finished stripping data; statistics: "
                    f"initial_size[{initial_size}], "
                    f"current_size[{len(data)}], "
                    f"total_removed_entries[{keep_data_from_index}], "
                    f"total_entries_with_0_volume[{len(indexes_with_zero_volume)}], "
                    f"old_start_index[{old_start_index}], "
                    f"new_start_index[{data.index[0]}]")

    return data


def clean_up_data(data: DataFrame):
    data.loc[data[MkDataFields.VOLUME] > 2, MkDataFields.VOLUME] = 2
    data.loc[data[MkDataFields.VOLUME] < -2, MkDataFields.VOLUME] = -2

    return data.dropna()


def add_direction_column(data: DataFrame):
    """
    Adds new column DIRECTION with values 1/0, where:
        1 -> means the price will move up in the next entry
        0 -> the price will move down by in the next entry
    :param data: DataFrame with percentage changes of the prices, and volume
    """
    data.insert(len(data.columns), DIRECTION, 0)  # insert new column with default value 0

    close_col_index = data.columns.get_loc(MkDataFields.CLOSE)
    direction_col_index = data.columns.get_loc(DIRECTION)

    for i in range(0, len(data) - 1):
        next_close_pct_change = data.iloc[i + 1, close_col_index]

        if next_close_pct_change > 0:
            data.iloc[i, direction_col_index] = 1  # price will go up
        else:
            data.iloc[i, direction_col_index] = 0  # price will stay within target or go down


def train_test_split(data: DataFrame, test_size=0.20):
    log.debug("Split data into train and test...")
    test_data_size = int(len(data) * test_size)
    train_data_size = len(data) - test_data_size

    train_data = data.iloc[0:train_data_size].copy()
    test_data = data.iloc[train_data_size:len(data)].copy()

    log.debug(f"Done splitting data; counts: all_data[{len(data)}], train_data[{len(train_data)}], test_data[{len(test_data)}]")
    if len(data) != len(train_data) + len(test_data):
        raise Exception("Train and Test data sizes don't add up to the initial data size!")

    return train_data, test_data


def create_dataset(x, y, time_steps=1):
    xs, ys = [], []
    for i in range(len(x) - time_steps):
        xv = x.iloc[i:(i + time_steps)].to_numpy()
        xs.append(xv)
        yv = y.iloc[i + time_steps]
        ys.append(yv)
    return np.array(xs), np.array(ys)


def prepare_model(x_train):
    model = keras.Sequential()
    model.add(
        keras.layers.Bidirectional(
            # long short-term memory - artificial recurrent neural network (RNN) architecture
            keras.layers.LSTM(
                units=128,
                input_shape=(x_train.shape[1], x_train.shape[2])
            )
        )
    )
    model.add(keras.layers.Dropout(rate=0.2))
    model.add(keras.layers.Dense(units=1))

    model.compile(loss="mean_squared_error", optimizer="adam", metrics='accuracy')

    return model


def train_model(model, x_train, y_train, epochs):
    model.fit(
        x_train, y_train,
        epochs=epochs,
        batch_size=32,
        validation_split=0.1,
        shuffle=False
    )
