from typing import Callable, List

import pandas as pd

from trader.env.reward.base_reward import BaseReward


class SimpleProfitReward(BaseReward):
    def __init__(self, window_size: int, **kwargs):
        self.window_size = window_size

    def reset(self):
        pass

    def get_reward(self, current_step: int, current_price: Callable[[str], float], account_history: pd.DataFrame,
                   net_worths: List[float]) -> float:
        if len(net_worths) > 1:
            return net_worths[-1] / net_worths[-min(len(net_worths), self.window_size + 1)] - 1.0
        else:
            return 0.0
