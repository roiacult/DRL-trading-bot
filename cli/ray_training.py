import ray
from ray.tune import register_env

from cli.ray_optimizer import RayOptimizer
from cli.commun import *


def create_ray_train_arg_parser():
    parser = create_arg_parser()
    # TODO: add specific argument for ray trainer
    parser.add_argument('-rs', '--resume', action='store_true', help='Resume training (default False)')

    return parser


def run_ray_trainer():
    parser = create_ray_train_arg_parser()
    args = parser.parse_args()
    fix_data_path(args)

    ray.init(num_cpus=12, num_gpus=1)

    register_env("TradingEnv", create_env)
    ray_optimizer = RayOptimizer(args.data, args.algo, args.reward, args.add_indicators)

    ray_optimizer.train(resume=args.resume)

