from abc import abstractmethod
from enum import Enum

import pandas as pd


class SIGNALS(Enum):
    HOLD = 0
    BUY = 1
    SELL = 2


class BaseBenchmark:

    def __init__(self, prices: pd.Series, balance: int, commission: float, **kwargs) -> None:
        self.prices = prices
        self.balance = balance
        self.commission = commission
        self.net_worths = self.trade_strategy()

    @abstractmethod
    def get_label(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def signal(self, i) -> SIGNALS:
        raise NotImplementedError

    def trade_strategy(self):
        net_worths = [self.balance]
        balance = self.balance
        amount_held = 0

        commission_adj = self.commission/100

        for i in range(1, len(self.prices)):
            if amount_held > 0:
                net_worths.append(balance + amount_held * self.prices.iloc[i])
            else:
                net_worths.append(balance)

            signal = self.signal(i)

            if signal == SIGNALS.SELL and amount_held > 0:
                balance = amount_held * (self.prices.iloc[i] * (1 - commission_adj))
                amount_held = 0
            elif signal == SIGNALS.BUY and amount_held == 0:
                amount_held = balance / (self.prices.iloc[i] * (1 + commission_adj))
                balance = 0
        return net_worths
