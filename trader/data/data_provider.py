import pandas as pd
from typing import Dict, Tuple
from abc import ABCMeta, abstractmethod


class DataProvider(object, metaclass=ABCMeta):
    columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    in_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

    @abstractmethod
    def __init__(self, **kwargs):

        data_columns: Dict[str, str] = kwargs.get('data_columns', None)

        if data_columns is not None:
            self.data_columns = data_columns
            self.columns = list(data_columns.keys())
            self.in_columns = list(data_columns.values())
        else:
            self.data_columns = dict(zip(self.columns, self.in_columns))

    def prepare_data(self, data_frame: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
        column_map = self.data_columns

        formatted = data_frame[self.in_columns]
        formatted = formatted.rename(index=str, columns=column_map)

        formatted = self._format_data(formatted, inplace=inplace)
        formatted = self._sort_data(formatted, inplace=inplace)

        return formatted

    def _sort_data(self, data_frame: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
        if inplace is True:
            formatted = data_frame
        else:
            formatted = data_frame.copy()

        formatted = formatted.sort_values(self.data_columns['Date'])

        return formatted

    def _format_data(self, data_frame: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
        if inplace is True:
            formatted = data_frame
        else:
            formatted = data_frame.copy()

        date_col = self.data_columns['Date']

        formatted[date_col] = pd.to_datetime(formatted[date_col])
        return formatted

    @abstractmethod
    def reset(self):
        """
        This function is used to reset object internal state
        reset is always called when gym.Env reset method is called
        """
        raise NotImplementedError

    @abstractmethod
    def has_next_timestep(self) -> bool:
        """
        Indicated whether there is a next timestep or not
        """
        raise NotImplementedError

    @abstractmethod
    def next_timestep(self) -> pd.DataFrame:
        """
        return next time step values
        :return: Pandas.Dataframe of the next observation (OHLCV data)
        """
        raise NotImplementedError

    @abstractmethod
    def split_data(self, train_split_percentage: float = 0.8) -> Tuple:
        """
        split dataset to train/test datasets
        :param train_split_percentage: percentage of the training data
        :return: tuple, first element is Training data provider and the second
        is Testing data provider
        """
        raise NotImplementedError

    @abstractmethod
    def all_timesteps(self) -> pd.DataFrame:
        """
        return all dataset
        :return: Pandas.DataFrame of all dataset
        """
        raise NotImplementedError
