import argparse
import glob
import os
import pathlib

from matplotlib import pyplot as plt

from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.reward.risk_ratio_reward import RiskRatioReward
from trader.env.reward.weighted_unrealized_pnl_reward import WeightedUnrealizedPnlReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv

path = pathlib.Path(__file__).parent.parent.resolve()

LOGS_DIR = os.path.join(path, 'logs')
SAVE_DIR = os.path.join(path, 'models')
DATA_PATH = os.path.join(path, 'dataset', 'Binance_BTCUSDT_d.csv')
MODEL_DIR = os.path.join(path, 'models')
SAVE_RESULTS_DIR = os.path.join(path, 'results')

TIME_STEPS = 1000000
TIME_TO_SAVE = 10000

INDEXES = ['timestamps', 'net_worths', 'current_price', 'assets_held']
REWARD_TYPES = ['incremental', 'weighted_unrealized_pnl', 'sharp', 'sortino', 'calmar']
TEST_TYPE = ['test', 'train']
ALGO_LIST = ['PPO', 'DQN', 'A2C']


def create_arg_parser():
    parser = argparse.ArgumentParser(description="Train/Test Crypto currency trading agent")

    parser.add_argument('process', choices=['train', 'test'])

    parser.add_argument('-a', '--algo', required=False, choices=ALGO_LIST, default=ALGO_LIST[0],
                        help=f"Algorithm used to train the agent choices {ALGO_LIST}")
    parser.add_argument('-r', '--reward', required=False, choices=REWARD_TYPES, default=REWARD_TYPES[0],
                        help=f'Reward function to be used --- choices {REWARD_TYPES}')

    parser.add_argument('-data', '--data', required=False, default=DATA_PATH, help="Dataset csv file path")
    parser.add_argument('--add-indicators', action='store_true')
    return parser


def create_env(args, train=True, initial_balance=10000, commissionPercent=0.3):
    train_provider, test_provider = SimulatedDataProvider(csv_data_path=args.data).split_data()

    # selecting reward function
    if args.reward == 'incremental':
        Reward = IncrementalProfitReward
        reward_kwargs = {}
    elif args.reward == 'weighted_unrealized_pnl':
        Reward = WeightedUnrealizedPnlReward
        reward_kwargs = {}
    elif args.reward == 'sharp':
        Reward = RiskRatioReward
        reward_kwargs = dict(ratio='sharp')
    elif args.reward == 'sortino':
        Reward = RiskRatioReward
        reward_kwargs = dict(ratio='sortino')
    elif args.reward == 'calmar':
        Reward = RiskRatioReward
        reward_kwargs = dict(ratio='calmar')
    else:
        # default reward function
        Reward = IncrementalProfitReward
        reward_kwargs = {}

    return TradingEnv(
        data_provider=train_provider if train else test_provider,
        reward_strategy=Reward,
        trade_strategy=SimulatedStrategy,
        initial_balance=initial_balance,
        commissionPercent=commissionPercent,
        reward_kwargs=reward_kwargs
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
