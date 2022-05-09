from enum import Enum
from typing import Type, List, Dict

import gym
import numpy as np
import pandas as pd
from trader.data.data_provider import DataProvider
from trader.env.benchmarks.base_benchmark import BaseBenchmark
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.reward.base_reward import BaseReward
from trader.env.strategy.base_strategy import BaseStrategy
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.helpers.logger import init_logger
from trader.helpers.trading_graph import TradingGraph
from trader.helpers.vars import *

np.seterr(invalid='ignore')


class TradingEnvAction(Enum):
    BUY = 0
    SELL = 1
    HOLD = 2


class TradingEnv(gym.Env):
    """A reinforcement trading environment made for use with gym-enabled algorithms"""

    metadata = {'render.modes': ['human', 'system', 'none']}

    viewer = None

    def __init__(
            self,
            data_provider: DataProvider,
            reward_strategy: Type[BaseReward] = IncrementalProfitReward,
            trade_strategy: Type[BaseStrategy] = SimulatedStrategy,
            initial_balance: int = DEFAULT_INITIAL_BALANCE,
            commissionPercent: float = DEFAULT_COMMISSION_PERCENT,
            maxSlippagePercent: float = DEFAULT_MAX_SLIPPAGE_PERCENT,
            **kwargs,
    ):
        self._max_episode_steps = data_provider.max_ep_len
        super(TradingEnv, self).__init__()

        self.logger = kwargs.get('logger', init_logger(__name__, show_debug=kwargs.get('show_debug', True)))

        self.base_precision: int = kwargs.get('base_precision', 8)
        self.asset_precision: int = kwargs.get('asset_precision', 8)
        self.min_cost_limit: float = kwargs.get('min_cost_limit', 1E-3)
        self.min_amount_limit: float = kwargs.get('min_amount_limit', 1E-3)

        self.initial_balance = round(initial_balance, self.base_precision)
        self.commissionPercent = commissionPercent
        self.maxSlippagePercent = maxSlippagePercent
        self.window_size = data_provider.window_size
        self.max_ep_len = data_provider.max_ep_len

        self.data_provider = data_provider
        reward_kwargs = kwargs.get('reward_kwargs', {})
        self.reward_strategy = reward_strategy(**reward_kwargs)
        self.trade_strategy = trade_strategy(
            commissionPercent=self.commissionPercent,
            maxSlippagePercent=self.maxSlippagePercent,
            base_precision=self.base_precision,
            asset_precision=self.asset_precision,
            min_cost_limit=self.min_cost_limit,
            min_amount_limit=self.min_amount_limit
        )

        self.render_benchmarks: List[Type[BaseBenchmark]] = kwargs.get('render_benchmarks', [])
        self.n_discrete_actions: int = kwargs.get('n_discrete_actions', N_DISCRETE_ACTION)

        self.action_space = gym.spaces.Discrete(self.n_discrete_actions)

        self.n_features = 6 + (len(self.data_provider.all_columns()) - 1) * self.window_size
        self.obs_shape = (self.n_features,)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=self.obs_shape, dtype=np.float16)

    def sample_action(self):
        return int(np.random.uniform(0, self.n_discrete_actions))

    def reset(self):
        self.initial_timestep = self.data_provider.reset()
        self.reward_strategy.reset()

        self.benchmarks = [
            Benchmark(
                self.data_provider.ep_timesteps()['Close'],
                self.initial_balance, self.commissionPercent
            ) for Benchmark in self.render_benchmarks
        ]

        self.balance = self.initial_balance
        self.net_worths: List[float] = [self.initial_balance]
        self.timestamps = []
        self.asset_held = 0
        self.current_step = 0

        self.account_history = pd.DataFrame([{
            'balance': self.balance,
            'asset_held': self.asset_held,
            'asset_bought': 0,
            'purchase_cost': 0,
            'asset_sold': 0,
            'sale_revenue': 0,
        }])
        self.trades = []
        self.rewards = [0]

        # reset trading viewer
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

        return self._next_timestep_observation()

    def _current_price(self, column_key: str = 'Close'):
        return float(self.current_timestep[column_key])

    def _next_timestep_observation(self):
        self.current_observation = self.data_provider.next_timestep()
        self.current_timestep = self.current_observation.iloc[[-1]]
        self.timestamps.append(self.current_timestep[self.data_provider.date_col])

        columns = self.data_provider.all_columns()
        columns.remove(self.data_provider.date_col)

        obs = self.current_observation[columns].to_numpy().flatten()
        obs = np.insert(obs, len(obs), self.account_history.values[-1], axis=0)

        obs = np.reshape(obs.astype('float32'), self.obs_shape)
        obs[np.bitwise_not(np.isfinite(obs))] = 0

        return obs

    def step(self, action: int) -> tuple:
        self._take_action(action)

        self.current_step += 1

        obs = self._next_timestep_observation()
        reward = self._reward()
        done = self._done()

        return obs, reward, done, {
            'timestamps': self.timestamps,
            'net_worths': self.net_worths,
            'current_price': self._current_price(),
            'asset_held': self.asset_held,
        }

    def _take_action(self, action: int):
        amount_asset_to_buy, amount_asset_to_sell = self._get_trade(action)

        asset_bought, asset_sold, purchase_cost, sale_revenue = self.trade_strategy.trade(
            buy_amount=amount_asset_to_buy,
            sell_amount=amount_asset_to_sell,
            balance=self.balance,
            asset_held=self.asset_held,
            current_price=self._current_price
        )

        if asset_bought:
            self.asset_held += asset_bought
            self.balance -= purchase_cost
            self.trades.append({
                'step': self.current_step,
                'amount': asset_bought,
                'total': purchase_cost,
                'type': 'buy'
            })
        elif asset_sold:
            self.asset_held -= asset_sold
            self.balance += sale_revenue
            self.trades.append({
                'step': self.current_step,
                'amount': asset_sold,
                'total': sale_revenue,
                'type': 'sell'
            })

        current_net_worth = round(self.balance + self.asset_held * self._current_price(), self.base_precision)
        self.net_worths.append(current_net_worth)
        self.account_history = self.account_history.append({
            'balance': self.balance,
            'asset_held': self.asset_held,
            'asset_bought': asset_bought,
            'purchase_cost': purchase_cost,
            'asset_sold': asset_sold,
            'sale_revenue': sale_revenue,
        }, ignore_index=True)

    def _get_trade(self, action: int):
        n_action_types = 3
        n_amount_bins = int(self.n_discrete_actions / n_action_types)

        action_type: TradingEnvAction = TradingEnvAction(action % n_action_types)
        action_amount = float(1 / (action % n_amount_bins + 1))

        amount_asset_to_buy = 0
        amount_asset_to_sell = 0

        if action_type == TradingEnvAction.BUY and self.balance >= self.min_cost_limit:
            price_adjustment = (1 + (self.commissionPercent / 100)) * (1 + (self.maxSlippagePercent / 100))
            buy_price = round(self._current_price() * price_adjustment, self.base_precision)
            amount_asset_to_buy = round(self.balance * action_amount / buy_price, self.asset_precision)
        elif action_type == TradingEnvAction.SELL and self.asset_held >= self.min_amount_limit:
            amount_asset_to_sell = round(self.asset_held * action_amount, self.asset_precision)

        return amount_asset_to_buy, amount_asset_to_sell

    def _done(self):
        # lost 90% of the initial balance
        loss_threshold = float(self.net_worths[-1]) < (self.initial_balance / 10)
        has_next_timestep = self.data_provider.has_next_timestep()

        return loss_threshold or not has_next_timestep

    def _reward(self):
        reward = self.reward_strategy.get_reward(
            current_step=self.current_step,
            current_price=self._current_price,
            account_history=self.account_history,
            net_worths=self.net_worths
        )

        reward = float(reward) if np.isfinite(float(reward)) else 0

        self.rewards.append(reward)

        return float(self.rewards[-1])

    def seed(self, seed=None):
        self.data_provider.seed(seed)
        return super().seed(seed)

    def render(self, mode='human'):
        if mode == 'system':
            self.logger.info('Price: ' + str(self._current_price()))
            self.logger.info('Bought: ' + str(self.account_history['asset_bought'][self.current_step]))
            self.logger.info('Sold: ' + str(self.account_history['asset_sold'][self.current_step]))
            self.logger.info('Net worth: ' + str(self.net_worths[-1]))
        elif mode == 'human':
            if self.viewer is None:
                self.viewer = TradingGraph(self.data_provider.ep_timesteps())
            self.viewer.render(
                self.current_step, self.net_worths,
                self.benchmarks, self.trades,
                self.balance, self.asset_held,
            )
            print(f'balance => {self.balance}')

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None
