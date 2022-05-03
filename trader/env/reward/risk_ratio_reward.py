from typing import Callable, List

import numpy as np
import pandas as pd
from empyrical import sharpe_ratio, sortino_ratio, calmar_ratio

from trader.env.reward.base_reward import BaseReward


class RiskRatioReward(BaseReward):
    ratios = ['sharp', 'sortino', 'calmar']

    def __init__(self, ratio=ratios[0], period=365):
        self.ratio = ratio
        self.period = period

    def reset(self):
        pass

    def get_reward(self, current_step: int, current_price: Callable[[str], float], observations: pd.DataFrame,
                   account_history: pd.DataFrame, net_worths: List[float]) -> float:
        if net_worths and len(net_worths) > 1:
            returns = np.diff(net_worths)
            if self.ratio == 'sharp':
                return sharpe_ratio(returns, annualization=self.period)
            elif self.ratio == 'sortino':
                return sortino_ratio(returns, annualization=self.period)
            elif self.ratio == 'calmar':
                return calmar_ratio(returns, annualization=self.period)

        return 0.
