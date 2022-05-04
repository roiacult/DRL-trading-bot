from trader.data.simulated_data_provider import SimulatedDataProvider
from trader.env.reward.incremental_profit_reward import IncrementalProfitReward
from trader.env.strategy.simulated_strategy import SimulatedStrategy
from trader.env.trading_env import TradingEnv
from stable_baselines3.common.env_checker import check_env

data_provider = SimulatedDataProvider(csv_data_path='dataset/Binance_BTCUSDT_d.csv', add_indicators=True)

env = TradingEnv(
    data_provider=data_provider,
    reward_strategy=IncrementalProfitReward,
    trade_strategy=SimulatedStrategy,
    initial_balance=10000,
    commissionPercent=0.3,
)

# obs = env.reset()
# done = False
# while not done:
#     action = env.sample_action()
#     obs, reward, done, info = env.step(action)
#     env.render()

check_env(env)
