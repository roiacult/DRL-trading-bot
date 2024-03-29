import sys
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import style
from pandas.plotting import register_matplotlib_converters

from trader.env.benchmarks.base_benchmark import BaseBenchmark

style.use('ggplot')
register_matplotlib_converters()

VOLUME_CHART_HEIGHT = 0.33


class TradingGraph:
    """An OHLCV trading visualization using matplotlib made to render gym environments"""

    def __init__(self, df):
        self.df = df

        # Create a figure on screen and set the title
        self.fig = plt.figure(figsize=(16, 10), dpi=80)

        shape = (6, 6)

        # Create top subplot for net worth axis
        self.net_worth_ax = plt.subplot2grid(shape, (0, 0), rowspan=2, colspan=5)
        # Create bottom subplot for shared price/volume axis
        self.price_ax = plt.subplot2grid(shape, (2, 0), rowspan=4, colspan=5, sharex=self.net_worth_ax)
        # Create a new axis for volume which shares its x-axis with price
        self.volume_ax = self.price_ax.twinx()

        # balance and asset held subplot
        self.balance = plt.subplot2grid(shape, (0, 5), rowspan=6, colspan=1)

        # Add padding to make graph easier to view
        plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)

        # Show the graph without blocking the rest of the program
        plt.show(block=False)

    def _render_net_worth(self, step_range, times, current_step, net_worths,
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

        last_time = self.df['Date'].values[current_step]
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

    def _render_price(self, step_range, times, current_step):
        self.price_ax.clear()

        # TODO: Plot price using candlestick graph from mpl_finance
        self.price_ax.plot(times, self.df['Close'].values[step_range], color="black")
        # mpf_data: pd.DataFrame = self.df[['Date', 'Open', 'Close', 'High', 'Low']].iloc[step_range].copy()
        # mpf_data = mpf_data.set_index('Date', drop=True)
        # mpf.plot(mpf_data, ax=self.price_ax, type='line', )
        # candlesticks = zip(times,
        #                    self.df['Open'].values[step_range], self.df['Close'].values[step_range],
        #                    self.df['High'].values[step_range], self.df['Low'].values[step_range])
        # Plot price using candlestick graph from mpl_finance
        # candlestick(self.price_ax, candlesticks, width=1, colorup='#27A59A', colordown='#EF534F')

        last_time = self.df['Date'].values[current_step]
        last_close = self.df['Close'].values[current_step]
        last_high = self.df['High'].values[current_step]

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

    def _render_volume(self, step_range, times):
        self.volume_ax.clear()

        volume = np.array(self.df['Volume'].values[step_range])

        self.volume_ax.plot(times, volume, color='blue')
        self.volume_ax.fill_between(times, volume, color='blue', alpha=0.5)

        self.volume_ax.set_ylim(0, max(volume) / VOLUME_CHART_HEIGHT)
        self.volume_ax.yaxis.set_ticks([])

    def _render_trades(self, step_range, trades):
        for trade in trades:
            if trade['step'] in range(sys.maxsize)[step_range]:
                date = self.df['Date'].values[trade['step']]
                close = self.df['Close'].values[trade['step']]

                if trade['type'] == 'buy':
                    color = 'g'
                else:
                    color = 'r'

                self.price_ax.annotate(' ', (date, close),
                                       xytext=(date, close),
                                       size="large",
                                       arrowprops=dict(arrowstyle='simple', facecolor=color))

    def _render_balance(self, step_range, current_step, balance, asset_held):
        self.balance.clear()
        current_price = self.df['Close'].iloc[current_step]
        x = ['USDT', 'ASSET']
        y = [balance, asset_held*current_price]

        self.balance.bar(x, y, color=['#ffa929', '#ff297f'])
        self.balance.set_title("Balance")

    def render(self, current_step: int,
               net_worths: List[float],
               benchmarks: List[BaseBenchmark],
               trades: List[dict],
               balance: float, asset_held: float,
               window_size: int = 200):

        net_worth = round(net_worths[-1], 2)
        initial_net_worth = round(net_worths[0], 2)
        profit_percent = round((net_worth - initial_net_worth) / initial_net_worth * 100, 2)

        self.fig.suptitle('Net worth: $' + str(net_worth) + ' | Profit: ' + str(profit_percent) + '%')

        window_start = max(current_step - window_size, 0)
        step_range = slice(window_start, current_step + 1)

        times = self.df['Date'].values[step_range]

        self._render_net_worth(step_range, times, current_step, net_worths, benchmarks)
        self._render_price(step_range, times, current_step)
        self._render_volume(step_range, times)
        self._render_trades(step_range, trades)
        self._render_balance(step_range, current_step, balance, asset_held)

        date_col = pd.to_datetime(self.df['Date'], unit='s').dt.strftime('%m/%d/%Y %H:%M')
        date_labels = date_col.values[step_range]

        self.price_ax.set_xticklabels(date_labels, rotation=45, horizontalalignment='right')

        # Hide duplicate net worth date labels
        plt.setp(self.net_worth_ax.get_xticklabels(), visible=False)

        # Necessary to view frames before they are un-rendered
        plt.pause(0.001)

    def close(self):
        plt.close()
