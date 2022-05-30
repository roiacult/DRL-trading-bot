import ray
from ray.rllib.agents import Trainer
from ray.rllib.agents.a3c import a2c
from ray.rllib.agents.ddpg import ddpg
from ray.rllib.agents.dqn import dqn
from ray.rllib.agents.ppo import ppo
from ray.tune import register_env

from cli.commun import *


class RayDeployment:

    def __init__(self, experiment: str, algo: str, reward: str, checkpoint: str) -> None:
        super().__init__()

        if experiment.endswith('LSTM'):
            data_file_name = experiment.replace('-LSTM', '')
            self.use_lstm = True
        else:
            data_file_name = experiment
            self.use_lstm = False

        self.data = fix_data_path(os.path.join('dataset', f'{data_file_name}.csv'))

        self.experiment = experiment
        self.algo = algo
        self.reward = reward.lower()

        checkpoint_file = f"checkpoint-{int(checkpoint.split('_')[1])}"
        algo_folder = os.path.join(RAY_RESULTS, f'{self.algo}-{self.reward}', self.experiment)
        checkpoint_folder = os.path.join(algo_folder, checkpoint)
        self.checkpoint = os.path.join(checkpoint_folder, checkpoint_file)

        self.env_config = {
            'data': self.data,
            'add_indicators': True,
            'reward': self.reward,
            'train': False,
            'initial_balance': DEFAULT_INITIAL_BALANCE,
            'commission_percent': DEFAULT_COMMISSION_PERCENT,
            'window_size': DEFAULT_WINDOW_SIZE if not self.use_lstm else 1,
            'max_ep_len': MAX_EP_LENGTH,
            'use_lstm': self.use_lstm,
        }

        self.model_conf = {
            # "fcnet_hiddens": FC_SIZE,  # Hyperparameter grid search defined above
            "use_lstm": self.use_lstm,
            "lstm_cell_size": 256 if self.use_lstm else None,
        }

        self.config = {
            "env": "TradingEnv",
            "env_config": self.env_config,
            "log_level": "WARNING",
            "framework": "torch",
            "num_workers": 0,
            "evaluation_num_workers": 1,
            "in_evaluation": True,
            "clip_rewards": True,
            "observation_filter": "MeanStdFilter",
            "model": self.model_conf,
            "evaluation_config": {
                "mode": "test"
            },
        }

        ray.init(include_dashboard=False, ignore_reinit_error=True)

        register_env("TradingEnv", create_env)
        self.env = create_env(self.env_config)
        self.agent = self.get_agent()

    def start(self):
        self.done = False
        self.state_init = [np.zeros(256, np.float32) for _ in range(2)]
        self.obs = self.env.reset()
        return self.next_action()

    def next_action(self):
        if self.done:
            return None
        if self.use_lstm:
            action, state_init, logits = self.agent.compute_single_action(self.obs, state=self.state_init)
        else:
            action = self.agent.compute_single_action(self.obs)
        self.obs, reward, self.done, info = self.env.step(action)

        return (
            self.env.current_step, self.env.net_worths,
            self.env.benchmarks, self.env.trades,
            self.env.balance, self.env.asset_held
        )

    def disconnect(self):
        self.agent.stop()
        self.agent.cleanup()
        self.env = None
        ray.shutdown()

    def get_agent(self) -> Trainer:
        # TODO: add other type of agents
        if self.algo == 'PPO':
            trainer = ppo.PPOTrainer(config=self.config)
        elif self.algo == 'DQN':
            trainer = dqn.DQNTrainer(config=self.config)
        elif self.algo == 'A2C':
            trainer = a2c.A3CTrainer(config=self.config)
        elif self.algo == 'DDPG':
            trainer = ddpg.DDPGTrainer(config=self.config)
        else:
            raise Exception('algorithm not implemented yet')
        if self.checkpoint is not None:
            trainer.restore(self.checkpoint)
        return trainer
