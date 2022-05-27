import time

from ray.tune import register_env

from cli.commun import create_env
from cli.ray.ray_optimizer import RayOptimizer

register_env("TradingEnv", create_env)
optimizer = RayOptimizer(
    '/opt/dev/trading/pfe/DRL-trading-bot/dataset/binance-BTCUSDT-1h-2019-01__2021-01.csv',
    'PPO', 'sortino', True, False, False,
)

agent = optimizer.get_agent(
    "/opt/dev/trading/pfe/DRL-trading-bot/ray_results/PPO-sortino/"
    "binance-BTCUSDT-1h-2019-01__2021-01_0_2022-05-20_11-34-06/checkpoint_000390/checkpoint-390"
)

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
i = 0
start = 10
while not done and i < 10000:
    action = agent.compute_single_action(obs)
    obs, reward, done, info = env.step(action)
    env.render()
    if i > start:
        time.sleep(2)
    i += 1

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
