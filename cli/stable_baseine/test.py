from stable_baselines3 import PPO, A2C, DQN
import numpy as np

from cli.commun import *


def create_test_arg_parser():
    parser = create_arg_parser()

    # adding train arguments
    parser.add_argument('-t', '--type', required=False, default=TEST_TYPE[0], choices=TEST_TYPE,
                        help='Dataset to test the agent on')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--show-figures', action='store_true')

    parser.add_argument('-id', '--id', required=True, help="Trained model id")
    parser.add_argument('-m', '--model-dir', required=False, default=MODEL_DIR, help="Models directory")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--number', help='Number of model to test')
    group.add_argument('-ns', '--numbers', nargs="+", help='Number of model to test')
    group.add_argument('--random', action='store_true')

    parser.add_argument('-d', '--days', required=False, default=TEST_STEPS, help='Number of days to test on')

    parser.add_argument('-s', '--save-dir', required=False, default=SAVE_RESULTS_DIR, help="Saving result directory")

    return parser


def test(args, number, env):
    # selecting training algorithm
    if args.algo == 'PPO':
        ALGO = PPO
    elif args.algo == 'A2C':
        ALGO = A2C
    elif args.algo == 'DQN':
        ALGO = DQN
    else:
        ALGO = PPO

    saving_dir = os.path.join(args.save_dir, args.id)
    if not os.path.exists(saving_dir):
        os.makedirs(saving_dir)

    if not number:
        saving_dir = os.path.join(saving_dir, 'random.png')
    else:
        saving_dir = os.path.join(saving_dir, f'{args.type}-{number}.png')

    if not number:
        model = ALGO('MlpPolicy', env, verbose=1)
    else:
        model_dir = os.path.join(args.model_dir, args.id, number)
        model = ALGO.load(model_dir, env, verbose=1)

    obs = env.reset()
    info_list = None

    days = min(int(args.days), len(env.data_provider.all_timesteps()) - env.window_size)
    for i in range(days):
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

    plot_testing_results(
        info_list, save_to=saving_dir,
        title=f"BTC-USDT {args.algo} {args.reward} ({number if number else 'random'})",
        show_figure=args.show_figures
    )


def run_tester():
    parser = create_test_arg_parser()
    args = parser.parse_args()
    # env = create_env(args, train=args.type == 'train')
    env = create_env({
        'data': args.data,
        'add_indicators': args.add_indicators,
        'reward': args.reward,
        'train': args.type == 'train',
        'initial_balance': 10000,
        'commission_percent': 0.3
    })
    if args.random:
        test(args, None, env)
    elif args.numbers:
        for n in args.numbers:
            test(args, n, env)
    else:
        test(args, args.number, env)
