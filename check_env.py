import time

from cli.commun import create_env
from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.reward.risk_ratio_reward import RiskRatioReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv
from stable_baselines3.common.env_checker import check_env

# data_provider = SimulatedDataProvider(
#     csv_data_path='dataset/binance-BTCUSDT-1h.csv',
#     window_size=10,
#     # max_ep_len=6000,
#     add_indicators=True,
# )

# env = TradingEnv(
#     data_provider=data_provider,
#     reward_strategy=RiskRatioReward,
#     trade_strategy=SimulatedStrategy,
#     initial_balance=10000,
#     commissionPercent=0.3,
#     reward_kwargs={
#         "ratio": "sharp"
#     }
# )

env = create_env({
    'data': '/opt/dev/trading/pfe/DRL-trading-bot/dataset/binance-BTCUSDT-1h.csv',
    'add_indicators': True,
    'reward': 'simple_profit',
    'train': True,
    'initial_balance': 10000,
    'commission_percent': 0.3,
    'window_size': 10,
    'max_ep_len': 720,
})

obs = env.reset()
done = False
times = []
i = 0
while not done and i< 10000:
    tic = time.time()
    action = env.sample_action()
    obs, reward, done, info = env.step(action)
    toc = time.time()
    times.append(toc - tic)
    # env.render()
    i += 1
    # print(f'\n\n\nobs => {env.current_observation}')
    # print(f'\nobs => {obs[-10:]}')
    # print(f'account history => \n{env.account_history}')
    print(f'reward => {reward}\n')
    # time.sleep(2)

print(f'\n\nepisode len => {i}')

# check_env(env)

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
# after updating environment
# exec time avg: 0.002486441922187805


# num_workers => 10 ---------------------------
# Total run time: 327.58 seconds (324.63 seconds for the tuning loop). without gpu
# Total run time: 343.84 seconds (342.20 seconds for the tuning loop). with gpu

# num_workers => 5 ---------------------------
# Total run time: 327.58 seconds (324.63 seconds for the tuning loop). without gpu
# Total run time: 343.84 seconds (342.20 seconds for the tuning loop). with gpu

