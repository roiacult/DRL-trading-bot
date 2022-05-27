import os
from typing import Tuple

import numpy as np
import pandas as pd
from trader.data.data_provider import DataProvider


class SimulatedDataProvider(DataProvider):
    """
    SimulatedDataProvider: data provider used to simulate
    exchanges observations, each timestep SimulatedDataProvider will
    emit (Date, Open, High, Low, Close, Volume) data from historical dataset
    """

    def __init__(
            self,
            data_frame: pd.DataFrame = None,
            csv_data_path: str = None,
            prepare: bool = True,
            test: bool = False,
            **kwargs
    ):
        DataProvider.__init__(self, **kwargs)

        self.kwargs = kwargs
        self.test = test

        if data_frame is not None:
            self.data_frame = data_frame
        elif csv_data_path is not None:
            if not os.path.isfile(csv_data_path):
                raise ValueError(
                    f'No file found in {csv_data_path}; please provide a valid path')
            self.data_frame = pd.read_csv(csv_data_path)
        else:
            raise ValueError(
                "Please provide either a 'data_frame' :Pandas.DataFrame or csv_data_path: str (dataset csv file path)")

        if prepare:
            self.data_frame = self.prepare_data(self.data_frame)
        self.reset()

    @staticmethod
    def create(data_frame: pd.DataFrame, **kwargs):
        return SimulatedDataProvider(data_frame=data_frame, prepare=False, **kwargs)

    def reset(self, ) -> int:
        # initialize initial step to a random value if this provider is for
        # training environment otherwise initialize it to self.window_size
        # self.initial_timestep = int(np.random.uniform(
        #     self.window_size - 1, len(self.data_frame) - self.max_ep_len
        # )) if not self.test else self.window_size - 1
        self.initial_timestep = self.window_size - 1
        self.timestep_index = self.initial_timestep
        return self.initial_timestep

    def has_next_timestep(self) -> bool:
        # is_max_len = (self.timestep_index - self.initial_timestep) >= self.max_ep_len
        is_max_len = False
        is_last_index = self.timestep_index >= len(self.data_frame)

        if self.test:
            return not is_last_index
        else:
            return not is_last_index and not is_max_len

    def next_timestep(self) -> pd.DataFrame:
        frame = self.data_frame.iloc[
                self.timestep_index - self.window_size + 1:self.timestep_index + 1].reset_index(drop=True)
        self.timestep_index += 1

        return frame

    def split_data(self, train_split_percentage: float = 0.5) -> Tuple[DataProvider, DataProvider]:
        train_len = int(train_split_percentage * len(self.data_frame))

        train_df = self.data_frame[:train_len].copy()
        test_df = self.data_frame[train_len:].copy()

        train_provider = SimulatedDataProvider.create(
            data_frame=train_df, test=False, **self.kwargs)
        test_provider = SimulatedDataProvider.create(
            data_frame=test_df, test=True, **self.kwargs)

        return train_provider, test_provider

    def all_timesteps(self) -> pd.DataFrame:
        return self.data_frame

    def ep_timesteps(self) -> pd.DataFrame:
        # if self.test:
        #     return self.data_frame.iloc[self.initial_timestep::]
        # else:
        #     return self.data_frame.iloc[self.initial_timestep:self.initial_timestep + self.max_ep_len]
        return self.data_frame.iloc[self.initial_timestep::]

    def seed(self, seed: int = None):
        super().seed(seed)
        np.random.seed(seed)
