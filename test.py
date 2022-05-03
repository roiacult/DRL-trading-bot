import collections
import os
import argparse
from time import sleep

import gym
from matplotlib import pyplot as plt
from stable_baselines3 import PPO, A2C, DQN
import numpy as np

from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.reward.weighted_unrealized_pnl_reward import WeightedUnrealizedPnlReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv

TIME_TO_SAVE = 10000
ALGO_LIST = ['PPO', 'DQN', 'A2C']
MODEL_DIR = 'models'
SAVE_DIR = 'results'
# INDEXES = ['net_worth', 'profit', 'shares_held']
REWARD_TYPES = ['incremental', 'weighted_unrealized_pnl', 'sharp_ratio']
DATA_PATH = 'dataset/Binance_BTCUSDT_d.csv'
INDEXES = ['timestamps', 'net_worths', 'current_price', 'assets_held']

parser = argparse.ArgumentParser(description="Test a Crypto currency trading reinforcement learning agent")

parser.add_argument('-a', '--algo', required=False, choices=ALGO_LIST, default=ALGO_LIST[0],
                    help=f"Algorithm used to test the agent --- choices {ALGO_LIST}")
parser.add_argument('--render', action='store_true')
parser.add_argument('--random', action='store_true')

parser.add_argument('-r', '--reward', required=False, choices=REWARD_TYPES, default=REWARD_TYPES[2],
                    help=f'Reward function to be used --- choices {REWARD_TYPES}')

parser.add_argument('-id', '--id', required=True, help="Trained model id")
parser.add_argument('-m', '--model-dir', required=False, default=MODEL_DIR, help="Models directory")
parser.add_argument('-n', '--number', required=True, help='Number of model to test')

parser.add_argument('-s', '--save-dir', required=False, default=SAVE_DIR, help="Saving result directory")
parser.add_argument('-data', '--data', required=False, default=DATA_PATH, help="Dataset csv file path")
parser.add_argument('--add-indicators', action='store_true')


def test(args):
    data_provider = SimulatedDataProvider(csv_data_path=args.data)

    # selecting reward function
    if args.reward == 'incremental':
        Reward = IncrementalProfitReward
    elif args.reward == 'weighted_unrealized_pnl':
        Reward = WeightedUnrealizedPnlReward
    elif args.reward == 'sharp_ratio':
        raise Exception('sharp ration reward function not implemented yet')
    else:
        # default reward function
        Reward = IncrementalProfitReward

    env = TradingEnv(
        data_provider=data_provider,
        reward_strategy=Reward,
        trade_strategy=SimulatedStrategy,
        initial_balance=10000,
        commissionPercent=0.3,
    )

    # selecting training algorithm
    if args.algo == 'PPO':
        ALGO = PPO
    elif args.algo == 'A2C':
        ALGO = A2C
    elif args.algo == 'DQN':
        ALGO = DQN
    else:
        ALGO = PPO

    if args.random:
        saving_dir = os.path.join(args.save_dir, f'{args.id}-random.png')
    else:
        saving_dir = os.path.join(args.save_dir, f'{args.id}-{args.number}.png')

    model_dir = os.path.join(args.model_dir, args.id, args.number)

    if args.random:
        model = ALGO('MlpPolicy', env, verbose=1)
    else:
        model = ALGO.load(model_dir, env, verbose=1)

    obs = env.reset()
    info_list = None
    for i in range(90):
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        if info_list is None:
            info_list = np.array([[
                info['net_worths'][-1], info['current_price'], info['asset_held']
            ]])
        else:
            info_list = np.append(info_list, [[
                info['net_worths'][-1], info['current_price'], info['asset_held']
            ]], axis=0)
        if args.render:
            env.render(mode='human')
        if done:
            break

    plot_testing_results(info_list, save_to=saving_dir, title=f"BTC-USDT {args.algo} {args.reward}")


def plot_testing_results(info, save_to=None, title='Testing trading rl agent'):
    fig, axs = plt.subplots(ncols=1, nrows=len(INDEXES) - 1, figsize=(10, 8), constrained_layout=True)
    fig.suptitle(title)
    for i in range(len(INDEXES) - 1):
        ax = axs[i]
        ax.plot(info[:, i].flatten(), label=INDEXES[i + 1])
        legend = ax.legend(loc=2, ncol=2, prop={'size': 8})
        legend.get_frame().set_alpha(0.4)
    if save_to:
        plt.savefig(save_to)
    plt.show()


if __name__ == '__main__':
    args = parser.parse_args()
    # print(args.__dict__)
    test(args)
    sleep(1000000)
