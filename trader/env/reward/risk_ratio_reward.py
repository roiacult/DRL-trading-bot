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

    def get_reward(self, current_step: int, current_price: Callable[[str], float],
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


class RiskAdjustedReturns(BaseReward):
    """A reward scheme that rewards the agent for increasing its net worth,
    while penalizing more volatile strategies.

    Parameters
    ----------
    return_algorithm : {'sharpe', 'sortino'}, Default 'sharpe'.
        The risk-adjusted return metric to use.
    risk_free_rate : float, Default 0.
        The risk free rate of returns to use for calculating metrics.
    target_returns : float, Default 0
        The target returns per period for use in calculating the sortino ratio.
    window_size : int
        The size of the look back window for computing the reward.
    """

    def __init__(self,
                 ratio: str = 'sharpe',
                 risk_free_rate: float = 0.,
                 target_returns: float = 0.,
                 window_size: int = 1) -> None:
        self.algorithm = ratio

        assert self.algorithm in ['sharp', 'sortino']

        if self.algorithm == 'sharp':
            return_algorithm = self._sharpe_ratio
        else:
            return_algorithm = self._sortino_ratio

        self._return_algorithm = return_algorithm
        self._risk_free_rate = risk_free_rate
        self._target_returns = target_returns
        self._window_size = window_size

    def reset(self):
        pass

    def _sharpe_ratio(self, returns: 'pd.Series') -> float:
        """Computes the sharpe ratio for a given series of a returns.

        Parameters
        ----------
        returns : `pd.Series`
            The returns for the `portfolio`.

        Returns
        -------
        float
            The sharpe ratio for the given series of a `returns`.

        References
        ----------
        .. [1] https://en.wikipedia.org/wiki/Sharpe_ratio
        """
        return (np.mean(returns) - self._risk_free_rate + 1e-9) / (np.std(returns) + 1e-9)

    def _sortino_ratio(self, returns: 'pd.Series') -> float:
        """Computes the sortino ratio for a given series of a returns.

        Parameters
        ----------
        returns : `pd.Series`
            The returns for the `portfolio`.

        Returns
        -------
        float
            The sortino ratio for the given series of a `returns`.

        References
        ----------
        .. [1] https://en.wikipedia.org/wiki/Sortino_ratio
        """
        downside_returns = returns.copy()
        downside_returns[returns < self._target_returns] = returns ** 2

        expected_return = np.mean(returns)
        downside_std = np.sqrt(np.std(downside_returns))

        return (expected_return - self._risk_free_rate + 1e-9) / (downside_std + 1e-9)

    def get_reward(self, current_step: int, current_price: Callable[[str], float],
                   account_history: pd.DataFrame, net_worths: List[float]) -> float:

        net_worths_adj = net_worths[-(self._window_size + 1):]
        returns = pd.Series(net_worths_adj).pct_change().dropna()
        risk_adjusted_return = self._return_algorithm(returns)
        return risk_adjusted_return
