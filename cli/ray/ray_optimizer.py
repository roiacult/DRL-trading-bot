import numpy as np
from ray import tune
from ray.rllib.agents import Trainer
from ray.rllib.agents.a3c import a2c
from ray.rllib.agents.ddpg import ddpg
from ray.rllib.agents.dqn import dqn
from ray.rllib.utils.typing import TrainerConfigDict
import ray.rllib.agents.ppo as ppo
from ray.tune.trial import Trial

from cli.commun import *


# Let's define some tuning parameters
# FC_SIZE = tune.grid_search([[256, 256], [1024], [128, 64, 32]])  # Those are the alternatives that ray.tune will try
# LEARNING_RATE = tune.grid_search([0.001, 0.0005, 0.00001])  # ... and they will be combined with these ones ...
# LEARNING_RATE = tune.grid_search([0.001, 0.0005])


# MINIBATCH_SIZE = tune.grid_search([5, 10, 20])  # ... and these ones, in a cartesian product.


class RayOptimizer:

    def __init__(self, data: str, algo: str, reward='sharp', add_indicators=False, use_lstm=False,
                 test_on_training_set=False):
        self.algo = algo
        self.reward = reward
        self.use_lstm = use_lstm
        self.data = data
        self.env_train_config = {
            'data': data,
            'add_indicators': add_indicators,
            'reward': reward,
            'train': True,
            'initial_balance': DEFAULT_INITIAL_BALANCE,
            'commission_percent': DEFAULT_COMMISSION_PERCENT,
            'window_size': DEFAULT_WINDOW_SIZE if not use_lstm else 1,
            'max_ep_len': MAX_EP_LENGTH,
            'use_lstm': use_lstm,
        }

        self.env_test_config = self.env_train_config.copy()
        self.env_test_config['train'] = test_on_training_set
        self.model_conf = {
            # "fcnet_hiddens": FC_SIZE,  # Hyperparameter grid search defined above
            "use_lstm": use_lstm,
            "lstm_cell_size": 256 if use_lstm else None,
        }

        self.config: TrainerConfigDict = {
            "env": "TradingEnv",
            "env_config": self.env_train_config,  # The dictionary of environment config
            "horizon": MAX_EP_LENGTH,
            "soft_horizon": True,
            "no_done_at_end": False,
            "log_level": "WARNING",
            "framework": "torch",
            "ignore_worker_failures": True,
            "num_workers": 11,
            "num_envs_per_worker": 1,
            # "evaluation_num_workers": 1,
            "num_gpus": 0,
            "clip_rewards": True,
            # "lr": LEARNING_RATE,  # Hyperparameter grid search defined above
            # This can have a big impact on the result and needs to be properly tuned (range is 0 to 1)
            # "gamma": 0.50,
            "observation_filter": "ConcurrentMeanStdFilter",  # normalizing observation space
            "model": self.model_conf,
            # "sgd_minibatch_size": MINIBATCH_SIZE,  # Hyperparameter grid search defined above
            "evaluation_interval": 2,  # Run evaluation on every iteration
            "evaluation_config": {
                "env_config": self.env_test_config,
                "explore": False,  # We don't want to explore during evaluation. All actions have to be repeatable.
            },
            "render_env": False,
        }

        self.test_config = {
            "env": "TradingEnv",
            "env_config": self.env_test_config,
            "log_level": "WARNING",
            "framework": "torch",
            "num_workers": 2,
            "evaluation_num_workers": 1,
            "in_evaluation": True,
            "clip_rewards": True,
            "observation_filter": "ConcurrentMeanStdFilter",
            "model": self.model_conf,
            "evaluation_config": {
                "mode": "test"
            },
        }

    def train(self, resume=False):
        return tune.run(
            self.algo,
            name=f'{self.algo}-{self.reward}',
            trial_name_creator=self._trail_name_creator,
            # stop={"episode_reward_mean": 500},
            config=self.config,
            local_dir=RAY_RESULTS,
            checkpoint_freq=5,
            checkpoint_at_end=True,
            resume=resume,
        )

    def test(self, checkpoint: str, render=False, nb_episodes=1):
        trainer = self.get_agent(checkpoint)
        env = create_env(self.env_test_config)

        if render:
            nb_episodes = 1

        info_list = {
            'net_worths': None,
            'asset_held': None,
            'current_price': None,
        }
        episode_timesteps = env.data_provider.ep_timesteps()
        episode_max_len = len(episode_timesteps)

        for i in range(nb_episodes):
            info = self._test_episode(env, trainer, render)
            if info.shape[0] != episode_max_len:
                # episode ended with early stop
                info = np.append(info, np.zeros((episode_max_len - info.shape[0], 3)), axis=0)
            if info_list['net_worths'] is None:
                info_list['net_worths'] = info[:, 0:1]
            else:
                info_list['net_worths'] = np.append(info_list['net_worths'], info[:, 0:1], axis=1)

            if info_list['asset_held'] is None:
                info_list['asset_held'] = info[:, 2:3]
            else:
                info_list['asset_held'] = np.append(info_list['asset_held'], info[:, 2:3], axis=1)

            if info_list.get('current_price') is None:
                info_list['current_price'] = info[:, 1]

        info_list['times'] = episode_timesteps['Date'].values

        return info_list, env.benchmarks

    def _test_episode(self, env, trainer, render):
        done = False
        info_list = None
        state_init = [np.zeros(256, np.float32) for _ in range(2)]
        obs = env.reset()
        while not done:
            if self.use_lstm:
                action, state_init, logits = trainer.compute_single_action(obs, state=state_init)
            else:
                action = trainer.compute_single_action(obs)
            obs, reward, done, info = env.step(action)
            if info_list is None:
                info_list = np.array([[
                    info['net_worths'][-1], info['current_price'], info['asset_held']
                ]])
            else:
                info_list = np.append(info_list, [[
                    info['net_worths'][-1], info['current_price'], info['asset_held']
                ]], axis=0)
            if render:
                env.render()
        return info_list

    def get_agent(self, checkpoint: str) -> Trainer:
        # TODO: add other type of agents
        if self.algo == 'PPO':
            trainer = ppo.PPOTrainer(config=self.test_config)
        elif self.algo == 'DQN':
            trainer = dqn.DQNTrainer(config=self.test_config)
        elif self.algo == 'A2C':
            trainer = a2c.A3CTrainer(config=self.test_config)
        elif self.algo == 'DDPG':
            trainer = ddpg.DDPGTrainer(config=self.test_config)
        else:
            raise Exception('algorithm not implemented yet')
        if checkpoint is not None:
            trainer.restore(checkpoint)
        return trainer

    def _trail_name_creator(self, trail: Trial) -> str:
        data_name = self.data.split('/')[-1]
        if data_name.endswith('.csv'):
            data_name = data_name.split('.')[0]
        trail_name = f"{data_name}{'-LSTM' if self.use_lstm else ''}"
        return trail_name
