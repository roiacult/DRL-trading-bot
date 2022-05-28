import sys
import tkinter as tk
from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ray.rllib.agents.ppo import ppo

from cli.commun import create_env
from trader.env.benchmarks.base_benchmark import BaseBenchmark
from trader.helpers.vars import DEFAULT_COMMISSION_PERCENT, DEFAULT_WINDOW_SIZE, MAX_EP_LENGTH

VOLUME_CHART_HEIGHT = 0.33


class TkinterTradingView:

    def __init__(self, algo: str, reward: str, data: str,
                 checkpoint: str, add_indicators=True) -> None:
        super().__init__()

        self.algo = algo
        self.reward = reward
        self.checkpoint = checkpoint
        self.data = data
        self.add_indicators = add_indicators
        self.env = None
        self.agent = None
        self.done = True

        self.root = tk.Tk()
        self.root.title('Trading Ui')
        self.root.geometry('1400x900+50+50')

        self.topFrame = self.init_topframe()
        self.topFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.figFrame = self.init_axes()
        self.figFrame.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        self.bottomFrame = self.init_bottomframe()
        self.bottomFrame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

        self.root.mainloop()

    def init_topframe(self):
        topFrame = tk.Frame(self.root, cnf={'bg': 'blue'})
        return topFrame

    def init_bottomframe(self):
        bottomBarFrame = tk.Frame(self.root, cnf={'bg': 'white', 'height': 100})

        self.startButton = tk.Button(bottomBarFrame, cnf={
            'text': 'Start', 'bg': 'green', 'command': self.start_trading
        })
        self.startButton.pack(side=tk.RIGHT)

        return bottomBarFrame

    def start_trading(self):
        self.env, self.agent = self._create_env(10000)
        self.obs = self.env.reset()
        self.done = False

        max_iter = 60
        i = 0
        while i < max_iter and not self.done:
            self.trade()
            i += 1

    def trade(self):
        action = self.agent.compute_single_action(self.obs)
        self.obs, reward, self.done, info = self.env.step(action)
        self.render(
            self.env.data_provider.ep_timesteps(), self.env.current_step, self.env.net_worths,
            self.env.benchmarks, self.env.trades,
            self.env.balance, self.env.asset_held
        )

    def _create_env(self, balance):
        env_config = {
            'data': self.data,
            'add_indicators': self.add_indicators,
            'reward': self.reward,
            'train': False,
            'initial_balance': balance,
            'commission_percent': DEFAULT_COMMISSION_PERCENT,
            'window_size': DEFAULT_WINDOW_SIZE,
            'max_ep_len': MAX_EP_LENGTH,
            # 'use_lstm': use_lstm,
            'use_lstm': False,
        }

        test_config = {
            "env": "TradingEnv",
            "env_config": env_config,
            "log_level": "WARNING",
            "framework": "torch",
            "num_workers": 0,
            "evaluation_num_workers": 1,
            "in_evaluation": True,
            "clip_rewards": True,
            "observation_filter": "MeanStdFilter",
            "model": {
                # "fcnet_hiddens": FC_SIZE,  # Hyperparameter grid search defined above
                # "use_lstm": use_lstm,
                # "lstm_cell_size": 256 if use_lstm else None,
            },
            "evaluation_config": {
                "mode": "test"
            },
        }

        if self.algo == 'PPO':
            agent = ppo.PPOTrainer(config=test_config)
            if self.checkpoint is not None:
                agent.restore(self.checkpoint)
        else:
            raise Exception('algorithm not implemented yet')

        return create_env(env_config), agent

    def init_axes(self):
        shape = (6, 6)

        # Create a figure on screen and set the title
        # plt.ion()
        fig = plt.figure(0)
        # self.fig.tight_layout(rect=[0, 0.03, 1, 0.98])

        # Create top subplot for net worth axis
        self.net_worth_ax = plt.subplot2grid(shape, (0, 0), rowspan=2, colspan=5)

        # Create bottom subplot for shared price/volume axis
        self.price_ax = plt.subplot2grid(shape, (2, 0), rowspan=4, colspan=5, sharex=self.net_worth_ax)
        # Create a new axis for volume which shares its x-axis with price
        self.volume_ax = self.price_ax.twinx()

        # balance and asset held subplot
        self.balance_ax = plt.subplot2grid(shape, (0, 5), rowspan=6, colspan=1)

        # Add padding to make graph easier to view
        plt.subplots_adjust(left=0.03, right=0.97, bottom=0.06, top=0.94, wspace=0.2, hspace=0)
        plt.pause(0.001)

        return FigureCanvasTkAgg(fig, self.topFrame)

    def render(self, df: pd.DataFrame, current_step: int,
               net_worths: List[float],
               benchmarks: List[BaseBenchmark],
               trades: List[dict],
               balance: float, asset_held: float,
               window_size: int = 200,
               ):
        net_worth = round(net_worths[-1], 2)
        initial_net_worth = round(net_worths[0], 2)
        profit_percent = round((net_worth - initial_net_worth) / initial_net_worth * 100, 2)

        self.figFrame.figure.suptitle('Net worth: $' + str(net_worth) + ' | Profit: ' + str(profit_percent) + '%')

        window_start = max(current_step - window_size, 0)
        step_range = slice(window_start, current_step + 1)

        times = df['Date'].values[step_range]

        self._render_net_worth(df, step_range, times, current_step, net_worths, benchmarks)
        self._render_price(df, step_range, times, current_step)
        self._render_volume(df, step_range, times)
        self._render_trades(df, step_range, trades)
        self._render_balance(df, step_range, current_step, balance, asset_held)

        date_col = pd.to_datetime(df['Date'], unit='s').dt.strftime('%m/%d/%Y %H:%M')
        date_labels = date_col.values[step_range]

        self.price_ax.set_xticklabels(date_labels, rotation=45, horizontalalignment='right')

        # Hide duplicate net worth date labels
        plt.setp(self.net_worth_ax.get_xticklabels(), visible=False)

        # plt.draw()
        self.figFrame.draw()

    def _render_net_worth(self, df: pd.DataFrame, step_range, times, current_step, net_worths,
                          benchmarks: List[BaseBenchmark]):
        # Clear the frame rendered last step
        self.net_worth_ax.clear()

        # Plot net worths
        self.net_worth_ax.plot(times, net_worths[step_range], label='Net Worth', color="g")

        self._render_benchmarks(step_range, times, benchmarks)

        # Show legend, which uses the label we defined for the plot above
        # self.net_worth_ax.legend()
        legend = self.net_worth_ax.legend(loc=2, ncol=2, prop={'size': 8})
        legend.get_frame().set_alpha(0.4)

        last_time = df['Date'].values[current_step]
        last_net_worth = net_worths[current_step]

        # Annotate the current net worth on the net worth graph
        self.net_worth_ax.annotate('{0:.2f}'.format(last_net_worth), (last_time, last_net_worth),
                                   xytext=(last_time, last_net_worth),
                                   bbox=dict(boxstyle='round',
                                             fc='w', ec='k', lw=1),
                                   color="black",
                                   fontsize="small")

        # Add space above and below min/max net worth
        self.net_worth_ax.set_ylim(min(net_worths) / 1.25, max(net_worths) * 1.25)

    def _render_benchmarks(self, step_range, times, benchmarks: List[BaseBenchmark]):
        colors = ['orange', 'cyan', 'purple', 'blue',
                  'magenta', 'yellow', 'black', 'red', 'green']

        for i, benchmark in enumerate(benchmarks):
            self.net_worth_ax.plot(times, benchmark.net_worths[step_range],
                                   label=benchmark.get_label(), color=colors[i % len(colors)], alpha=0.3)

    def _render_price(self, df: pd.DataFrame, step_range, times, current_step):
        self.price_ax.clear()

        # TODO: Plot price using candlestick graph from mpl_finance
        self.price_ax.plot(times, df['Close'].values[step_range], color="black")
        last_time = df['Date'].values[current_step]
        last_close = df['Close'].values[current_step]
        last_high = df['High'].values[current_step]

        # Print the current price to the price axis
        self.price_ax.annotate('{0:.2f}'.format(last_close), (last_time, last_close),
                               xytext=(last_time, last_high),
                               bbox=dict(boxstyle='round',
                                         fc='w', ec='k', lw=1),
                               color="black",
                               fontsize="small")

        # Shift price axis up to give volume chart space
        ylim = self.price_ax.get_ylim()
        self.price_ax.set_ylim(ylim[0] - (ylim[1] - ylim[0]) * VOLUME_CHART_HEIGHT, ylim[1])

    def _render_volume(self, df: pd.DataFrame, step_range, times):
        self.volume_ax.clear()

        volume = np.array(df['Volume'].values[step_range])

        self.volume_ax.plot(times, volume, color='blue')
        self.volume_ax.fill_between(times, volume, color='blue', alpha=0.5)

        self.volume_ax.set_ylim(0, max(volume) / VOLUME_CHART_HEIGHT)
        self.volume_ax.yaxis.set_ticks([])

    def _render_trades(self, df: pd.DataFrame, step_range, trades):
        for trade in trades:
            if trade['step'] in range(sys.maxsize)[step_range]:
                date = df['Date'].values[trade['step']]
                close = df['Close'].values[trade['step']]

                if trade['type'] == 'buy':
                    color = 'g'
                else:
                    color = 'r'

                self.price_ax.annotate(' ', (date, close),
                                       xytext=(date, close),
                                       size="large",
                                       arrowprops=dict(arrowstyle='simple', facecolor=color))

    def _render_balance(self, df: pd.DataFrame, step_range, current_step, balance, asset_held):
        self.balance_ax.clear()
        current_price = df['Close'].iloc[current_step]
        x = ['USDT', 'ASSET']
        y = [balance, asset_held * current_price]

        self.balance_ax.bar(x, y, color=['#ffa929', '#ff297f'])
        self.balance_ax.set_title("Balance")
