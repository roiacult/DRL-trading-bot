import datetime
import os.path
import pathlib

path = pathlib.Path(__file__).parent.parent.parent.resolve()

DATA_FETCHER_START_DATE = datetime.datetime(2017, 1, 1).strftime("%d %b, %Y")
DATA_FETCHER_END_DATE = datetime.datetime(2022, 1, 1).strftime("%d %b, %Y")

DATASET_DIR = os.path.join(path, "dataset")
BINANCE_SECRET_PATH = os.path.join(path, 'secrets.json')

MAX_EP_LENGTH = 720  # 24*30 (30 day of hour trading)
DEFAULT_WINDOW_SIZE = 10
DEFAULT_INITIAL_BALANCE = 10000
DEFAULT_COMMISSION_PERCENT = 0.25
DEFAULT_MAX_SLIPPAGE_PERCENT = 1

N_DISCRETE_ACTION = 24
