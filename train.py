import os
import argparse
import glob

import gym
from stable_baselines3 import PPO, A2C, DQN

from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.reward.risk_ratio_reward import RiskRatioReward
from trader.env.reward.weighted_unrealized_pnl_reward import WeightedUnrealizedPnlReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv

TIME_STEPS = 1000000
TIME_TO_SAVE = 10000
ALGO_LIST = ['PPO', 'DQN', 'A2C']
LOGS_DIR = 'logs'
SAVE_DIR = 'models'
REWARD_TYPES = ['incremental', 'weighted_unrealized_pnl', 'sharp', 'sortino', 'calmar']
DATA_PATH = 'dataset/Binance_BTCUSDT_d.csv'

parser = argparse.ArgumentParser(description="Train a Crypto Currency trading reinforcement learning agent")
parser.add_argument('-a', '--algo', required=False, choices=ALGO_LIST, default=ALGO_LIST[0],
                    help=f"Algorithm used to train the agent choices {ALGO_LIST}")
parser.add_argument('-r', '--reward', required=False, choices=REWARD_TYPES, default=REWARD_TYPES[0],
                    help=f'Reward function to be used --- choices {REWARD_TYPES}')
parser.add_argument('-l', '--logs', required=False, default=LOGS_DIR, help="Log directory")
parser.add_argument('-s', '--save', required=False, default=SAVE_DIR, help="Saving model directory")
parser.add_argument('-t', '--time-steps', required=False, default=TIME_STEPS, help="Time steps to train the agent")
parser.add_argument('-ts', '--time-to-save', required=False, default=TIME_TO_SAVE,
                    help="Time steps to save the model (it should be less than `--time-steps`")
parser.add_argument('-data', '--data', required=False, default=DATA_PATH, help="Dataset csv file path")
parser.add_argument('--add-indicators', action='store_true')


def train(args):
    data_provider = SimulatedDataProvider(csv_data_path=args.data)

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

    env = TradingEnv(
        data_provider=data_provider,
        reward_strategy=Reward,
        trade_strategy=SimulatedStrategy,
        initial_balance=10000,
        commissionPercent=0.3,
        reward_kwargs=reward_kwargs
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

    model = ALGO('MlpPolicy', env, verbose=1, tensorboard_log=args.logs)
    current_id = f'BTCUSDT-{args.algo}-{args.reward}'
    log_dir = os.path.join(args.logs, current_id)
    save_dir = os.path.join(args.save, f'{current_id}_{get_latest_run_id(log_dir) + 1}')

    time_steps = int(args.time_steps)
    time_to_save = int(args.time_to_save)

    for i in range(int(time_steps / time_to_save)):
        model.learn(
            total_timesteps=time_to_save,
            tb_log_name=current_id,
            reset_num_timesteps=(i == 0),
            # callback=TensorboardCallback(),
        )
        model.save(os.path.join(save_dir, str(i)))


def get_latest_run_id(log_path: str = "") -> int:
    max_run_id = 0
    for path in glob.glob(f"{log_path}_[0-9]*"):
        file_name = path.split(os.sep)[-1]
        ext = file_name.split("_")[-1]
        if ext.isdigit() and int(ext) > max_run_id:
            max_run_id = int(ext)
    return max_run_id


if __name__ == '__main__':
    args = parser.parse_args()

    train(args)
