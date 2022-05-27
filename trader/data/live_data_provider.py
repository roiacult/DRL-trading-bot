import datetime
import time
from typing import Tuple

import pandas as pd

from trader.data.data_provider import DataProvider
from trader.data.fetchers.binance_fetcher import BinanceFetcher


class LiveBinanceDataProvider(DataProvider):
    time_delta = 2  # 3 days window
    period = '1h'
    sleep_time = 3600  # in seconds (3600s => 1h)

    def __init__(self, secret_path, symbol, **kwargs):
        DataProvider.__init__(self, **kwargs)

        self.symbol = symbol
        self.secret_path = secret_path
        self.binance_fetcher = BinanceFetcher(self.secret_path)

    def reset(self) -> int:
        self.timestep_index = 0
        return self.timestep_index

    def has_next_timestep(self) -> bool:
        return True

    def next_timestep(self) -> pd.DataFrame:
        tic = int(time.time())

        current_date = datetime.datetime.now()
        start_date = current_date - datetime.timedelta(days=self.time_delta)
        df = self.binance_fetcher.fetch_dataset(
            symbol=self.symbol,
            period=self.period,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=None  # fetch until now
        )

        df = self.prepare_data(data_frame=df)
        observation = df[-self.window_size:]

        toc = int(time.time())

        time.sleep(self.sleep_time - (toc-tic))

        return observation

    def split_data(self, train_split_percentage: float = 0.7) -> Tuple:
        pass

    def all_timesteps(self) -> pd.DataFrame:
        pass

    def ep_timesteps(self) -> pd.DataFrame:
        pass
