import argparse
import glob
import os

from matplotlib import pyplot as plt

from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.benchmarks.buy_and_hold import BuyAndHold
from trader.env.benchmarks.sma_crossover import SmaCrossover
from trader.env.benchmarks.rsi_divergence import RsiDivergence
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.reward.risk_ratio_reward import RiskRatioReward
from trader.env.reward.simple_profit_reward import SimpleProfitReward
from trader.env.reward.weighted_unrealized_pnl_reward import WeightedUnrealizedPnlReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv
from trader.helpers.vars import *

path = pathlib.Path(__file__).parent.parent.resolve()

LOGS_DIR = os.path.join(path, 'logs')
SAVE_DIR = os.path.join(path, 'models')
DATA_PATH = os.path.join(path, 'dataset', 'Binance_BTCUSDT_d.csv')
MODEL_DIR = os.path.join(path, 'models')
SAVE_RESULTS_DIR = os.path.join(path, 'results')
RAY_RESULTS = os.path.join(path, 'ray_results')

TIME_STEPS = 1000000
TIME_TO_SAVE = 10000
TEST_STEPS = 90

INDEXES = ['timestamps', 'net_worths', 'current_price', 'assets_held']
REWARD_TYPES = ['incremental', 'weighted_unrealized_pnl', 'sharp', 'sortino', 'calmar', 'simple_profit']
TEST_TYPE = ['test', 'train']
ALGO_LIST = ['PPO', 'DQN', 'A2C']
OPTIONS = ['train', 'test', 'ray_train', 'ray_test']


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

    if config.get('use_lstm', False):
        window_size = 1
    else:
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
        # TODO: Deprecated
        Reward = IncrementalProfitReward
        reward_kwargs = {}
    elif config.get('reward', None) == 'weighted_unrealized_pnl':
        Reward = WeightedUnrealizedPnlReward
        reward_kwargs = {}
    elif config.get('reward', None) == 'sharp':
        Reward = RiskRatioReward
        reward_kwargs = dict(ratio='sharp')
    elif config.get('reward', None) == 'sortino':
        Reward = RiskRatioReward
        reward_kwargs = dict(ratio='sortino')
    elif config.get('reward', None) == 'calmar':
        Reward = RiskRatioReward
        reward_kwargs = dict(ratio='calmar')
    elif config.get('reward', None) == 'simple_profit':
        Reward = SimpleProfitReward
        reward_kwargs = dict(window_size=train_provider.window_size)
    else:
        # default reward function
        Reward = SimpleProfitReward
        reward_kwargs = {}

    initial_balance = config.get('initial_balance', DEFAULT_INITIAL_BALANCE)
    commission = config.get('commission_percent', DEFAULT_COMMISSION_PERCENT)

    if config.get('render_benchmarks', True):
        render_benchmarks = [BuyAndHold, SmaCrossover, RsiDivergence]
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


def fix_data_path(args):
    if not args.data:
        args.data = DATA_PATH
    elif not args.data.startswith('/'):
        args.data = os.path.join(path, args.data)
