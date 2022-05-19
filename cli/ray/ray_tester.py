import ray
from ray.tune import register_env

from cli.commun import *
from cli.ray.ray_optimizer import RayOptimizer


def create_ray_test_arg_parser():
    parser = create_arg_parser()
    # TODO: add specific argument for ray trainer
    parser.add_argument('-id', '--id', required=True, help="Trained model id")
    parser.add_argument('--show-figures', action='store_true', help="Show test results figures at the end")
    parser.add_argument('--render', action='store_true', help="Render and visualise environment")
    parser.add_argument('-lstm', action='store_true', help="Wrap policy network with LSTM")
    parser.add_argument('--training-set', action='store_true', help="Test on the training set instead of the test set")
    parser.add_argument('-e', '--episodes', default=5, required=False, help="Number of episodes to test on")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-n', '--number', help='Number of checkpoint to test')
    group.add_argument('-ns', '--numbers', nargs="+", help='List of checkpoints to test')
    group.add_argument('--random', action='store_true', help="Test model without training checkpoint (random actions)")

    return parser


def ray_test(args, number, optimizer):
    algo_folder = os.path.join(RAY_RESULTS, f'{args.algo}-{args.reward}', args.id)
    checkpoint_folder = os.path.join(algo_folder, f'checkpoint_{str(number).zfill(6)}')
    checkpoint_path = os.path.join(checkpoint_folder, f'checkpoint-{number}')

    info, benchmarks = optimizer.test(checkpoint_path, render=args.render, nb_episodes=int(args.episodes))

    result_dir = os.path.join(RAY_TEST_RESULTS, f'{args.algo}-{args.reward}', args.id)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir, exist_ok=True)

    pairs = args.data.split('/')[-1]
    if pairs.endswith('.csv'):
        pairs = pairs.split('.')[0]

    number_name = str(number) if number else 'random'
    lstm_name = 'LSTM' if args.lstm else ''
    title = f"{pairs} {args.algo} {args.reward} {lstm_name} ({number_name})"
    ray_plot_test_results(
        info, benchmarks,
        save_to=os.path.join(result_dir, f'{"train" if args.training_set else "test"}-{number_name}.png'),
        title=title,
        show_figure=args.show_figures
    )


def run_ray_tester():
    parser = create_ray_test_arg_parser()
    args = parser.parse_args()
    fix_data_path(args)

    if not ray.is_initialized():
        ray.init(num_cpus=0, num_gpus=1, dashboard_host='0.0.0.0')

    register_env("TradingEnv", create_env)

    optimizer = RayOptimizer(args.data, args.algo, args.reward, args.add_indicators, args.lstm, args.training_set)

    if args.random:
        ray_test(args, None, optimizer)
    elif args.numbers:
        for n in args.numbers:
            ray_test(args, n, optimizer)
    else:
        ray_test(args, args.number, optimizer)











