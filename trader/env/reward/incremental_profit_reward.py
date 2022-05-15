from typing import Callable, List

import pandas as pd

from trader.env.reward.base_reward import BaseReward


class IncrementalProfitReward(BaseReward):
    last_bought: int = 0
    last_sold: int = 0

    def __init__(self):
        pass

    def reset(self):
        pass

    def get_reward(self, current_step: int, current_price: Callable[[str], float], observations: pd.DataFrame,
                   account_history: pd.DataFrame, net_worths: List[float]) -> float:
        reward = 0

        curr_balance = account_history['balance'].values[-1]
        prev_balance = account_history['balance'].values[-2] if len(account_history['balance']) > 1 else curr_balance

        if curr_balance > prev_balance:
            reward = net_worths[-1] - net_worths[self.last_bought]
            self.last_sold = current_step
        elif curr_balance < prev_balance:
            reward = observations['Close'].values[self.last_sold] - current_price('Close')
            self.last_bought = current_step

        return reward
