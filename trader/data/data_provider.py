import pandas as pd
from typing import Dict, Tuple
from abc import ABCMeta, abstractmethod

import ta

from trader.helpers.vars import DEFAULT_WINDOW_SIZE, MAX_EP_LENGTH


class DataProvider(object, metaclass=ABCMeta):
    columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    in_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    date_col = columns[0]
    indicators_columns = [
        # momentum indicators
        'momentum_rsi', 'momentum_tsi', 'momentum_uo', 'momentum_ao',

        # volume indicators
        'volume_mfi', 'volume_adi', 'volume_obv', 'volume_cmf', 'volume_fi', 'volume_em', 'volume_vpt', 'volume_nvi',

        # trend indicators
        'trend_macd', 'trend_vortex_ind_pos', 'trend_vortex_ind_neg', 'trend_vortex_ind_diff', 'trend_trix',
        'trend_mass_index', 'trend_cci', 'trend_dpo', 'trend_kst', 'trend_kst_sig', 'trend_kst_diff', 'trend_aroon_up',
        'trend_aroon_down', 'trend_aroon_ind',

        # volatility indicators
        'volatility_bbh', 'volatility_bbhi', 'volatility_bbli', 'volatility_bbm', 'volatility_bbl', 'volatility_kchi',
        'volatility_kcli',

        # other indicators
        'others_dr', 'others_dlr'
    ]

    @abstractmethod
    def __init__(
            self, window_size: int = DEFAULT_WINDOW_SIZE, max_ep_len: int = MAX_EP_LENGTH,
            add_indicators: bool = False, **kwargs
    ):

        self.add_indicators = add_indicators
        self.window_size = window_size
        self.max_ep_len = max_ep_len
        data_columns: Dict[str, str] = kwargs.get('data_columns', None)

        if data_columns is not None:
            self.data_columns = data_columns
            self.columns = list(data_columns.keys())
            self.in_columns = list(data_columns.values())
        else:
            self.data_columns = dict(zip(self.columns, self.in_columns))

    def prepare_data(self, data_frame: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
        column_map = dict(zip(self.in_columns, self.columns))

        formatted = data_frame[self.in_columns]
        formatted = formatted.rename(index=str, columns=column_map)

        if self.add_indicators:
            formatted = self._add_indicators(formatted)

        formatted = self._format_data(formatted, inplace=inplace)
        formatted = self._sort_data(formatted, inplace=inplace)

        # formatted = formatted.set_index(self.in_columns[0], inplace=inplace)

        return formatted

    def _add_indicators(self, df):
        df = ta.add_all_ta_features(df, open='Open', close='Close', high='High', low='Low', volume='Volume')
        all_columns = self.columns.copy()
        all_columns.extend(self.indicators_columns)
        return df[all_columns]

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

        formatted = formatted.dropna()
        formatted = formatted.reset_index(drop=True)
        formatted[self.date_col] = pd.to_datetime(formatted[self.date_col])
        return formatted

    def all_columns(self):
        all_cols = self.columns.copy()
        if self.add_indicators:
            all_cols.extend(self.indicators_columns)
        return all_cols

    @abstractmethod
    def reset(self) -> int:
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

    @abstractmethod
    def ep_timesteps(self) -> pd.DataFrame:
        """
        return all dataset
        :return: Pandas.DataFrame of all dataset
        """
        raise NotImplementedError

    def seed(self, seed: int = None):
        """
        set the seed for random generators
        :param seed:
        """
        return
