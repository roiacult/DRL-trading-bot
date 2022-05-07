import time

from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv
from stable_baselines3.common.env_checker import check_env

data_provider = SimulatedDataProvider(csv_data_path='dataset/BTCUSDT-15m-dataset.csv', add_indicators=True)

env = TradingEnv(
    data_provider=data_provider,
    reward_strategy=IncrementalProfitReward,
    trade_strategy=SimulatedStrategy,
    initial_balance=10000,
    commissionPercent=0.3,
)

obs = env.reset()
# done = False
# times = []
# while not done:
#     tic = time.time()
#     action = env.sample_action()
#     obs, reward, done, info = env.step(action)
#     toc = time.time()
#     times.append(toc - tic)
#     env.render()
#     # time.sleep(2)

check_env(env)

# print(f'\n\ntimes     => {times}')
# print(f'mean time => {sum(times) / len(times)}\n\n')
# mean time => 0.009554459657462388
# mean time => 0.009704582757625048
# 0.000112371826171875
# 0.00019017312526702882


# _next_observation benchmark
# crypto
# exec time avg: 0.001525591230392456 with timesteps
# exec time avg: 0.0014362977027893066 without timesteps
# -----------------------------------------
# stocks
# exec time avg: 0.0006113991260528564 stocks

# step(action) benchmark
# exec time avg: 0.004067301273345947


# num_workers => 10 ---------------------------
# Total run time: 327.58 seconds (324.63 seconds for the tuning loop). without gpu
# Total run time: 343.84 seconds (342.20 seconds for the tuning loop). with gpu

# num_workers => 5 ---------------------------
# Total run time: 327.58 seconds (324.63 seconds for the tuning loop). without gpu
# Total run time: 343.84 seconds (342.20 seconds for the tuning loop). with gpu

