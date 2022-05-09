import pandas as pd
from ta.trend import MACD

from trader.env.benchmarks.base_benchmark import BaseBenchmark, SIGNALS


class SmaCrossover(BaseBenchmark):

    def __init__(self, prices: pd.Series, balance: int, commission: float) -> None:
        self.macd = MACD(prices).macd()
        super().__init__(prices, balance, commission)

    def get_label(self) -> str:
        return 'SMA crossover'

    def signal(self, i) -> SIGNALS:
        if self.macd.iloc[i] > 0 and self.macd.iloc[i - 1] <= 0:
            return SIGNALS.SELL
        elif self.macd.iloc[i] < 0 and self.macd.iloc[i - 1] >= 0:
            return SIGNALS.BUY

        return SIGNALS.HOLD
