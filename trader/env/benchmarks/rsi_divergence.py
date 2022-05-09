import pandas as pd
from ta import momentum
from ta.trend import MACD

from trader.env.benchmarks.base_benchmark import BaseBenchmark, SIGNALS


class RsiDivergence(BaseBenchmark):

    def __init__(self, prices: pd.Series, balance: int, commission: float, period=3) -> None:
        self.rsi = momentum.rsi(prices)
        self.period = period
        super().__init__(prices, balance, commission)

    def get_label(self) -> str:
        return 'RSI divergence'

    def signal(self, i) -> SIGNALS:
        if i >= self.period:
            rsiSum = sum(self.rsi.iloc[i - self.period:i + 1].diff().cumsum().fillna(0))
            priceSum = sum(self.prices[i - self.period:i + 1].diff().cumsum().fillna(0))

            if rsiSum < 0 and priceSum >= 0:
                return SIGNALS.SELL
            elif rsiSum > 0 and priceSum <= 0:
                return SIGNALS.BUY

        return SIGNALS.HOLD
