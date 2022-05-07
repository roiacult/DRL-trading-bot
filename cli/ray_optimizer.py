import numpy as np
from ray import tune
from ray.rllib.agents import Trainer
from ray.rllib.utils.typing import TrainerConfigDict
import ray.rllib.agents.ppo as ppo

from cli.commun import *

# Let's define some tuning parameters
# FC_SIZE = tune.grid_search([[256, 256], [1024], [128, 64, 32]])  # Those are the alternatives that ray.tune will try
# LEARNING_RATE = tune.grid_search([0.001, 0.0005, 0.00001])  # ... and they will be combined with these ones ...
# LEARNING_RATE = tune.grid_search([0.001, 0.0005])


# MINIBATCH_SIZE = tune.grid_search([5, 10, 20])  # ... and these ones, in a cartesian product.


class RayOptimizer:

    def __init__(self, data: str, algo: str, reward='sharp', add_indicators=False):
        self.algo = algo
        self.reward = reward
        self.env_train_config = {
            'data': data,
            'add_indicators': add_indicators,
            'reward': reward,
            'train': True,
            'initial_balance': 10000,
            'commission_percent': 0.3
        }

        self.env_test_config = {
            'data': data,
            'add_indicators': add_indicators,
            'reward': reward,
            'train': False,
            'initial_balance': 10000,
            'commission_percent': 0.3
        }

        self.config: TrainerConfigDict = {
            "env": "TradingEnv",
            "env_config": self.env_train_config,  # The dictionary we built before
            "log_level": "WARNING",
            "framework": "torch",
            "ignore_worker_failures": True,
            # One worker per agent. You can increase this but it will run fewer parallel trainings.
            "num_workers": 10,
            "num_envs_per_worker": 1,
            "evaluation_num_workers": 1,
            "num_gpus": 1,
            "clip_rewards": True,
            # "lr": LEARNING_RATE,  # Hyperparameter grid search defined above
            # This can have a big impact on the result and needs to be properly tuned (range is 0 to 1)
            # "gamma": 0.50,
            "observation_filter": "MeanStdFilter",  # normalizing observation space
            # "model": {
            #     "fcnet_hiddens": FC_SIZE,  # Hyperparameter grid search defined above
            # },
            # "sgd_minibatch_size": MINIBATCH_SIZE,  # Hyperparameter grid search defined above
            "evaluation_interval": 5,  # Run evaluation on every iteration
            "evaluation_config": {
                "env_config": self.env_test_config,
                "explore": False,  # We don't want to explore during evaluation. All actions have to be repeatable.
            },
            "render_env": False,
        }

        self.test_config = {
            "env": "TradingEnv",
            "framework": "torch",
            "num_workers": 0,
            "env_config": self.env_test_config,
            "evaluation_num_workers": 1,
            "in_evaluation": True,
            "evaluation_config": {
                "mode": "test"
            },
        }

    def train(self, resume=False):
        return tune.run(
            self.algo,
            name=f'{self.algo}-{self.reward}',
            # stop={"episode_reward_mean": 500},
            config=self.config,
            local_dir=RAY_RESULTS,
            checkpoint_freq=5,
            checkpoint_at_end=True,
            resume=resume,
        )

    def test(self, checkpoint: str, test_steps=TEST_STEPS, render=False):
        trainer = self._get_agent()
        if checkpoint is not None:
            trainer.restore(checkpoint)
        env = create_env(self.env_test_config)
        done = False
        obs = env.reset()
        step = 0
        info_list = None
        while not done and step < test_steps:
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
            step += 1
        return info_list

    def _get_agent(self) -> Trainer:
        # TODO: add other type of agents
        if self.algo == 'PPO':
            return ppo.PPOTrainer(config=self.test_config)
        else:
            Exception('algorithm not implemented yet')


