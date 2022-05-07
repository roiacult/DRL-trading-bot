from abc import abstractmethod

from trader.helpers.vars import DATA_FETCHER_START_DATE, DATA_FETCHER_END_DATE


class DataFetcher:

    def __init__(self, **kwargs,) -> None:
        super().__init__()
        self.kwargs = kwargs

    @abstractmethod
    def fetch_dataset(
            self, save_to: str, symbol, period: str,
            start_date=DATA_FETCHER_START_DATE,
            end_date=DATA_FETCHER_END_DATE, ):
        raise NotImplementedError
