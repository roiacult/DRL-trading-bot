import ray
import ray.rllib.agents.ppo as ppo
from ray.tune import register_env

from cli.commun import *
from cli.ray_optimizer import RayOptimizer


def create_ray_test_arg_parser():
    parser = create_arg_parser()
    # TODO: add specific argument for ray trainer
    parser.add_argument('-id', '--id', required=True, help="Trained model id")
    parser.add_argument('-rs', '--resume', action='store_true', help='Resume training (default False)')
    parser.add_argument('-st', '--steps', required=False, default=TEST_STEPS, help='Number of steps to test on')
    parser.add_argument('--show-figures', action='store_true')
    parser.add_argument('--render', action='store_true')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-n', '--number', help='Number of checkpoint')
    group.add_argument('-ns', '--numbers', nargs="+", help='Number of model to test')
    group.add_argument('--random', action='store_true')

    return parser


def ray_test(args, number, optimizer):
    algo_folder = os.path.join(RAY_RESULTS, f'{args.algo}-{args.reward}', args.id)
    checkpoint_folder = os.path.join(algo_folder, f'checkpoint_{str(number).zfill(6)}')
    checkpoint_path = os.path.join(checkpoint_folder, f'checkpoint-{number}')

    info = optimizer.test(checkpoint_path, test_steps=int(args.steps), render=args.render)

    result_dir = os.path.join(algo_folder, 'results')
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    plot_testing_results(
        info, save_to=os.path.join(result_dir, f'test-{number}.png'),
        title=f"BTC-USDT {args.algo} {args.reward} ({number if number else 'random'})",
        show_figure=args.show_figures
    )


def run_ray_tester():
    parser = create_ray_test_arg_parser()
    args = parser.parse_args()
    fix_data_path(args)

    ray.init(num_cpus=12, num_gpus=1)

    register_env("TradingEnv", create_env)

    optimizer = RayOptimizer(args.data, args.algo, args.reward, args.add_indicators)

    if args.random:
        ray_test(args, None, optimizer)
    elif args.numbers:
        for n in args.numbers:
            ray_test(args, n, optimizer)
    else:
        ray_test(args, args.number, optimizer)
