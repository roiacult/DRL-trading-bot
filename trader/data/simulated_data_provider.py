import os
from typing import Tuple

import pandas as pd
from trader.data.data_provider import DataProvider


class SimulatedDataProvider(DataProvider):
    """
    SimulatedDataProvider: data provider used to simulate
    exchanges observations, each timestep SimulatedDataProvider will
    emit (Date, Open, High, Low, Close, Volume) data from historical dataset
    """

    timestep_index = 0

    def __init__(
            self,
            data_frame: pd.DataFrame = None,
            csv_data_path: str = None,
            prepare: bool = True,
            **kwargs
    ):
        DataProvider.__init__(self, **kwargs)

        self.kwargs = kwargs

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

    @staticmethod
    def create(data_frame: pd.DataFrame, **kwargs):
        return SimulatedDataProvider(data_frame=data_frame, prepare=False, **kwargs)

    def reset(self):
        self.timestep_index = 0

    def has_next_timestep(self) -> bool:
        return self.timestep_index < len(self.data_frame)

    def next_timestep(self) -> pd.DataFrame:
        # columns = self.all_columns()
        # frame = self.data_frame[columns].values[self.timestep_index]
        # frame = pd.DataFrame([frame], columns=columns)
        frame = self.data_frame.iloc[[self.timestep_index]].reset_index(drop=True)
        self.timestep_index += 1

        return frame

    def split_data(self, train_split_percentage: float = 0.8) -> Tuple[DataProvider, DataProvider]:
        train_len = int(train_split_percentage * len(self.data_frame))

        train_df = self.data_frame[:train_len].copy()
        test_df = self.data_frame[train_len:].copy()

        train_provider = SimulatedDataProvider.create(
            data_frame=train_df, **self.kwargs)
        test_provider = SimulatedDataProvider.create(
            data_frame=test_df, **self.kwargs)

        return train_provider, test_provider

    def all_timesteps(self) -> pd.DataFrame:
        return self.data_frame
