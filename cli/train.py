from stable_baselines3 import PPO, A2C, DQN

from cli.commun import *


def create_train_arg_parser():
    parser = create_arg_parser()
    # adding train arguments
    parser.add_argument('-l', '--logs', required=False, default=LOGS_DIR, help="Log directory")
    parser.add_argument('-s', '--save', required=False, default=SAVE_DIR, help="Saving model directory")
    parser.add_argument('-t', '--time-steps', required=False, default=TIME_STEPS, help="Time steps to train the agent")
    parser.add_argument('-ts', '--time-to-save', required=False, default=TIME_TO_SAVE,
                        help="Time steps to save the model (it should be less than `--time-steps`")

    return parser


def train(args):
    # env = create_env(args, train=True)
    env = create_env({
        'data': args.data,
        'add_indicators': args.add_indicators,
        'reward': args.reward,
        'train': True,
        'initial_balance': 10000,
        'commission_percent': 0.3
    })

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
    current_id = f'BTCUSDT-{args.algo}-{args.reward}-{"ind" if args.add_indicators else ""}'
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


def run_trainer():
    parser = create_train_arg_parser()
    args = parser.parse_args()
    train(args)

