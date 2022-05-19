import argparse
import glob
import os
from typing import List

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import EngFormatter

from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.benchmarks.base_benchmark import BaseBenchmark
from trader.env.benchmarks.buy_and_hold import BuyAndHold
from trader.env.benchmarks.sma_crossover import SmaCrossover
from trader.env.benchmarks.rsi_divergence import RsiDivergence
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.reward.risk_ratio_reward import RiskRatioReward, RiskAdjustedReturns
from trader.env.reward.simple_profit_reward import SimpleProfitReward
from trader.env.reward.weighted_unrealized_pnl_reward import WeightedUnrealizedPnlReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv
from trader.helpers.vars import *

import matplotlib
from pandas.plotting import register_matplotlib_converters

# matplotlib.style.use('ggplot')
# font = {
#     'family': 'normal',
#     'weight': 'normal',
#     'size': 22
# }
# matplotlib.rc('font', **font)
register_matplotlib_converters()

PATH = pathlib.Path(__file__).parent.parent.resolve()

LOGS_DIR = os.path.join(PATH, 'logs')
SAVE_DIR = os.path.join(PATH, 'models')
DATA_PATH = os.path.join(PATH, 'dataset', 'Binance_BTCUSDT_d.csv')
MODEL_DIR = os.path.join(PATH, 'models')
SAVE_RESULTS_DIR = os.path.join(PATH, 'results')
RAY_RESULTS = os.path.join(PATH, 'ray_results')
RAY_TEST_RESULTS = os.path.join(PATH, 'ray_test_results')

TIME_STEPS = 1000000
TIME_TO_SAVE = 10000
TEST_STEPS = 90

INDEXES = ['timestamps', 'net_worths', 'current_price', 'assets_held']
REWARD_TYPES = ['incremental', 'weighted_unrealized_pnl', 'sharp', 'sortino', 'calmar', 'simple_profit']
TEST_TYPE = ['test', 'train']
ALGO_LIST = ['PPO', 'DQN', 'A2C']
OPTIONS = ['train', 'test', 'ray_train', 'ray_test']
BENCHMARKS_COLORS = ["#7FB5B5", "#F8F32B", "#826C34"]
NETWORTH_COLOR = "#AF2B1E"
ASSET_HELD_COLOR = "#AF2B1E"
BENCHMARKS = [BuyAndHold, SmaCrossover, RsiDivergence]


def create_arg_parser():
    parser = argparse.ArgumentParser(description="Train/Test Crypto currency trading agent")

    parser.add_argument('process', choices=OPTIONS)

    parser.add_argument('-a', '--algo', required=False, choices=ALGO_LIST, default=ALGO_LIST[0],
                        help=f"Algorithm used to train the agent choices {ALGO_LIST}")
    parser.add_argument('-r', '--reward', required=False, choices=REWARD_TYPES, default=REWARD_TYPES[0],
                        help=f'Reward function to be used --- choices {REWARD_TYPES}')

    parser.add_argument('-data', '--data', required=False, default=DATA_PATH, help="Dataset csv file path")
    parser.add_argument('--add-indicators', action='store_true')
    return parser


def create_env(config):
    """
    :param config: {
            'data': path to the dataset
            'add_indicators': boolean indicate where to add indicators or not,
            'reward': type of reward function used options: REWARD_TYPES,
            'train': boolean to indicate if env is for training or testing,
            'initial_balance': initial balance to start trading with,
            'commission_percent': trading commissions percent,
            'window_size': number of windows_size (price lookback),
            'max_ep_len': maximum episode len,
            'use_lstm': boolean indicate whether wrapping policy with lstm or not,
        }

    :return: TradingEnv
    """
    window_size = config.get('window_size', DEFAULT_WINDOW_SIZE)

    train_provider, test_provider = SimulatedDataProvider(
        csv_data_path=config.get('data', None),
        add_indicators=config.get('add_indicators', False),
        max_ep_len=config.get('max_ep_len', MAX_EP_LENGTH),
        window_size=window_size,
    ).split_data()

    provider = train_provider if config.get('train', False) else test_provider

    # selecting reward function
    if config.get('reward', None) == 'incremental':
        raise Exception('Deprecated reward: please use simple_profit instead')
    elif config.get('reward', None) == 'weighted_unrealized_pnl':
        Reward = WeightedUnrealizedPnlReward
        reward_kwargs = {}
    elif config.get('reward', None) == 'sharp':
        Reward = RiskAdjustedReturns
        reward_kwargs = dict(ratio='sharp', window_size=window_size)
    elif config.get('reward', None) == 'sortino':
        Reward = RiskAdjustedReturns
        reward_kwargs = dict(ratio='sortino', window_size=window_size)
    elif config.get('reward', None) == 'calmar':
        raise Exception('Deprecated reward: please use either sharp or sortino ratio')
    elif config.get('reward', None) == 'simple_profit':
        Reward = SimpleProfitReward
        reward_kwargs = dict(window_size=window_size)
    else:
        # default reward function
        Reward = SimpleProfitReward
        reward_kwargs = {}

    initial_balance = config.get('initial_balance', DEFAULT_INITIAL_BALANCE)
    commission = config.get('commission_percent', DEFAULT_COMMISSION_PERCENT)

    if config.get('render_benchmarks', True):
        render_benchmarks = BENCHMARKS
    else:
        render_benchmarks = []

    return TradingEnv(
        data_provider=provider,
        reward_strategy=Reward,
        trade_strategy=SimulatedStrategy,
        initial_balance=initial_balance,
        commissionPercent=commission,
        maxSlippagePercent=0.,
        reward_kwargs=reward_kwargs,
        render_benchmarks=render_benchmarks,
    )


def get_latest_run_id(log_path: str = "") -> int:
    max_run_id = 0
    for path in glob.glob(f"{log_path}_[0-9]*"):
        file_name = path.split(os.sep)[-1]
        ext = file_name.split("_")[-1]
        if ext.isdigit() and int(ext) > max_run_id:
            max_run_id = int(ext)
    return max_run_id


def plot_testing_results(info, save_to=None, title='Testing trading rl agent', show_figure=False):
    fig, axs = plt.subplots(ncols=1, nrows=len(INDEXES) - 1, figsize=(10, 8), constrained_layout=True)
    fig.suptitle(title)
    for i in range(len(INDEXES) - 1):
        ax = axs[i]
        ax.plot(info[:, i].flatten(), label=INDEXES[i + 1])
        legend = ax.legend(loc=2, ncol=2, prop={'size': 8})
        legend.get_frame().set_alpha(0.4)
    if save_to:
        plt.savefig(save_to)
    if show_figure:
        plt.show()


def ray_plot_test_results(
        info_list: dict, benchmarks: List[BaseBenchmark], save_to=None,
        title='Testing trading rl agent', show_figure=False
):
    fig = plt.figure(figsize=(20, 15))
    plt.figtext(0.5, 0.01, title, wrap=True, horizontalalignment='center', fontsize=16)
    shape = (6, 6)

    net_worth_ax = plt.subplot2grid(shape, (0, 0), rowspan=2, colspan=6)
    price_ax = plt.subplot2grid(shape, (2, 0), rowspan=2, colspan=6, sharex=net_worth_ax)
    plt.subplots_adjust(wspace=0.2, hspace=0.2)
    asset_held_ax = plt.subplot2grid(shape, (4, 0), rowspan=2, colspan=6, sharex=net_worth_ax)

    net_worths = info_list.get('net_worths')
    prices = info_list.get('current_price')
    asset_held = info_list.get('asset_held')
    times = info_list['times']

    # plotting networth/asset-held
    for i in range(net_worths.shape[1]):
        y_points = np.trim_zeros(net_worths[:, i], 'b')
        x_points = times[0:len(y_points)]
        label = f'Net Worth of RL agent for {net_worths.shape[1]} episodes' if i == 0 else ""
        net_worth_ax.plot(
            x_points, y_points,
            label=label, color=NETWORTH_COLOR
        )
    asset_held_ax.plot(times, asset_held[:, 0], label=f'Asset held for episode 1', color=ASSET_HELD_COLOR)
    asset_held_ax.legend(loc=3, ncol=2, prop={'size': 10})
    formatter = EngFormatter(unit=' USDT', sep="")
    net_worth_ax.yaxis.set_major_formatter(formatter)

    # plotting benchmarks
    for i, benchmark in enumerate(benchmarks):
        y_points = np.trim_zeros(benchmark.net_worths, 'b')
        x_points = times[0:len(y_points)]
        label = f'{benchmark.get_label()} Benchmark'
        net_worth_ax.plot(
            x_points, y_points,
            label=label, color=BENCHMARKS_COLORS[i % len(BENCHMARKS_COLORS)]
        )
    net_worth_ax.legend(loc=3, ncol=2, prop={'size': 10})

    # plotting prices
    y_points = np.trim_zeros(prices, 'b')
    x_points = times[0:len(y_points)]
    price_ax.plot(x_points, y_points, label=f"Asset price", color="black")
    price_ax.legend(loc=3, ncol=2, prop={'size': 10})
    price_ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))

    # fixing view
    plt.setp(net_worth_ax.get_xticklabels(), visible=False)
    plt.setp(price_ax.get_xticklabels(), visible=False)
    # net_worth_ax.set_ylim(np.amin(net_worths) / 1.1, np.amax(net_worths) * 1.1)

    # suptile information's
    last_networth = []
    for i in range(net_worths.shape[1]):
        last_networth.append(np.trim_zeros(net_worths[:, i], 'b')[-1])
    min_networth = round(np.amin(last_networth), 2)
    max_networth = round(np.amax(last_networth), 2)
    avg_networth = round(np.average(last_networth), 2)
    initial_networth = net_worths[0, 0]
    profit = round((avg_networth - initial_networth) / initial_networth * 100, 2)
    plt.suptitle(
        f'min networth: {min_networth}| max networth: {max_networth}| avg networth: {avg_networth}| profit {profit}%',
        size=16
    )

    # showing & saving figure
    fig.tight_layout(rect=[0, 0.03, 1, 0.98])
    if save_to:
        fig.savefig(save_to)
    if show_figure:
        plt.show()


def fix_data_path(args):
    if not args.data:
        args.data = DATA_PATH
    elif not args.data.startswith('/'):
        args.data = os.path.join(PATH, args.data)
