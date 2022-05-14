import os
from json import loads

import pandas as pd
from binance import Client

from trader.data.fetchers.data_fetcher import DataFetcher
from trader.helpers.vars import *


class BinanceFetcher(DataFetcher):
    KLINES = [
        Client.KLINE_INTERVAL_1MINUTE,
        Client.KLINE_INTERVAL_3MINUTE,
        Client.KLINE_INTERVAL_5MINUTE,
        Client.KLINE_INTERVAL_15MINUTE,
        Client.KLINE_INTERVAL_30MINUTE,
        Client.KLINE_INTERVAL_1HOUR,
        Client.KLINE_INTERVAL_2HOUR,
        Client.KLINE_INTERVAL_4HOUR,
        Client.KLINE_INTERVAL_6HOUR,
        Client.KLINE_INTERVAL_8HOUR,
        Client.KLINE_INTERVAL_12HOUR,
        Client.KLINE_INTERVAL_1DAY,
        Client.KLINE_INTERVAL_3DAY,
        Client.KLINE_INTERVAL_1WEEK,
        Client.KLINE_INTERVAL_1MONTH,
    ]
    DATE_COL = 'Date'
    COLUMNS = [
        DATE_COL, 'Open', 'High', 'Low', 'Close', 'Volume',
    ]
    ALL_COLUMNS = COLUMNS + [
        'close_time', 'quote_av',
        'trades', 'tb_base_av', 'tb_quote_av', 'ignore',
    ]

    def __init__(
            self, binance_secret_path: str,
    ) -> None:
        super().__init__()

        if binance_secret_path is not None:
            if not os.path.isfile(binance_secret_path):
                raise ValueError(f'No file found in {binance_secret_path}; please provide a valid path')
            with open(binance_secret_path) as file:
                secrets = loads(file.read())
            binance_key, binance_secret = secrets["binance_key"], secrets["binance_secret"]
            self.binance_client = Client(api_key=binance_key, api_secret=binance_secret)
        else:
            raise ValueError(f'Not a valid file; please provide a valid path')

    def fetch_dataset(
            self, save_to: str, symbol, period,
            start_date=DATA_FETCHER_START_DATE, end_date=DATA_FETCHER_END_DATE, prefix=""):
        assert period in self.KLINES
        if prefix != '' and not prefix.startswith('-'):
            prefix = f'-{prefix}'
        file_path = os.path.join(save_to, f'binance-{symbol}-{period}{prefix}.csv')
        history = self.binance_client.get_historical_klines(symbol, period, start_str=start_date, end_str=end_date)
        data_df = pd.DataFrame(history, columns=self.ALL_COLUMNS)
        data_df = data_df[self.COLUMNS]
        data_df[self.DATE_COL] = pd.to_datetime(data_df[self.DATE_COL]/1000, unit='s')
        data_df.to_csv(file_path)
        return data_df

