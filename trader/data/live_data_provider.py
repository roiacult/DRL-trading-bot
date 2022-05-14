from typing import Tuple

import pandas as pd
from trader.data.data_provider import DataProvider


class LiveDataProvider(DataProvider):
    """
    LiveDataProvider: data provider used to provide live data from
    an online broker or exchange
    """

    def __init__(
            self,
            **kwargs
    ):
        raise NotImplementedError

    def reset(self) -> int:
        raise NotImplementedError

    def has_next_timestep(self) -> bool:
        raise NotImplementedError

    def next_timestep(self) -> pd.DataFrame:
        raise NotImplementedError

    def split_data(self, train_split_percentage: float = 0.7) -> Tuple:
        raise NotImplementedError

    def all_timesteps(self) -> pd.DataFrame:
        raise NotImplementedError

    def ep_timesteps(self) -> pd.DataFrame:
        raise NotImplementedError
