import time

from ray.tune import register_env

from cli.commun import *
from cli.ray.agent_ui import RayAgentUi
from cli.ray.tickinter_ui import TkinterTradingViewà


def create_ray_test_arg_parser():
    parser = create_arg_parser()

    parser.add_argument('-id', '--id', required=True, help="Trained model id")
    parser.add_argument('-n', '--number', required=True, type=int, help='Number of checkpoint to test')

    return parser


def run_ray_renderer():
    parser = create_ray_test_arg_parser()
    args = parser.parse_args()
    register_env("TradingEnv", create_env)
    fix_data_path(args)

    algo_folder = os.path.join(RAY_RESULTS, f'{args.algo}-{args.reward}', args.id)
    checkpoint_folder = os.path.join(algo_folder, f'checkpoint_{str(args.number).zfill(6)}')
    checkpoint_path = os.path.join(checkpoint_folder, f'checkpoint-{args.number}')

    # agent_ui = RayAgentUi(args.algo, args.reward, args.data, checkpoint_path)
    agent_ui = TkinterTradingView(args.algo, args.reward, args.data, checkpoint_path)
    # time.sleep(15)

    # while input('$ ') != 'exit':
    #     pass


