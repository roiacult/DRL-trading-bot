#! python3
import argparse

from trader.data.fetchers.binance_fetcher import BinanceFetcher
from trader.helpers.vars import *

# only one exchange is supported for now TODO: add other exchanges
EXCHANGES = ['binance', ]


def create_arg_parser():
    parser = argparse.ArgumentParser(description="Download crypto currency dataset")

    parser.add_argument('exchange', choices=EXCHANGES, help="Exchange to download dataset from")
    parser.add_argument('-s', '--start-date', required=False, default=DATA_FETCHER_START_DATE, help="Start date")
    parser.add_argument('-e', '--end-date', required=False, default=DATA_FETCHER_END_DATE, help="End date")

    parser.add_argument('-o', '--output', required=False, default=DATASET_DIR, help="output folder")
    parser.add_argument('-k', '--key', required=True, help="secret key (API key) for the exchange")
    parser.add_argument('-sy', '--symbol', required=True, help="Crypto Currency pair symbol (EX: BTCUSDT)")
    parser.add_argument('-p', '--period', required=True, help="Period of data (EX: '1m' '1h' '1d' '1m'")
    parser.add_argument('--prefix', required=False, default="", help="Prefix added to the file name")

    return parser


if __name__ == '__main__':
    parser = create_arg_parser()
    args = parser.parse_args()

    if args.exchange == EXCHANGES[0]:
        exchange = BinanceFetcher(binance_secret_path=args.key)
        print('Fetching data ...')
        df = exchange.fetch_dataset(
            save_to=args.output,
            symbol=args.symbol,
            period=args.period,
            start_date=args.start_date,
            end_date=args.end_date,
            prefix=args.prefix,
        )
        print(f"Fetched {len(df)} entries of {args.symbol}")
        print(f"Period of {args.period} from {args.start_date} to {args.end_date}")
