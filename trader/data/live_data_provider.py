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
        raise Exception('Not implemented yet')

    def reset(self):
        raise Exception('Not implemented yet')

    def has_next_timestep(self) -> bool:
        raise Exception('Not implemented yet')

    def next_timestep(self) -> pd.DataFrame:
        raise Exception('Not implemented yet')

    def split_data(self, train_split_percentage: float = 0.8) -> Tuple:
        raise Exception('Not implemented yet')

    def all_timesteps(self) -> pd.DataFrame:
        raise Exception('Not implemented yet')

