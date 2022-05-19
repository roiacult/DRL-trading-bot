import ray
from ray.tune import register_env

from cli.ray.ray_optimizer import RayOptimizer
from cli.commun import *


def create_ray_train_arg_parser():
    parser = create_arg_parser()
    # TODO: add specific argument for ray trainer
    parser.add_argument('-rs', '--resume', action='store_true', help='Resume training (default False)')
    parser.add_argument('-lstm', action='store_true', help="Wrap policy network with LSTM")

    return parser


def run_ray_trainer():
    parser = create_ray_train_arg_parser()
    args = parser.parse_args()
    fix_data_path(args)

    if not ray.is_initialized():
        ray.init(num_cpus=12, num_gpus=0, dashboard_host='0.0.0.0')

    register_env("TradingEnv", create_env)
    ray_optimizer = RayOptimizer(
        args.data, args.algo, args.reward,
        add_indicators=args.add_indicators,
        use_lstm=args.lstm
    )

    ray_optimizer.train(resume=args.resume)
