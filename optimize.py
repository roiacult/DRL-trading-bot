#! python3
import sys

from cli.commun import OPTIONS
from cli.ray_tester import run_ray_tester
from cli.ray_training import run_ray_trainer
from cli.test import run_tester
from cli.train import run_trainer


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2 or args[1] not in OPTIONS:
        print(f"Usage: {args[0]} {OPTIONS}", file=sys.stderr)
    else:
        if args[1] == OPTIONS[0]:
            run_trainer()
        elif args[1] == OPTIONS[1]:
            run_tester()
        elif args[1] == OPTIONS[2]:
            run_ray_trainer()
        elif args[1] == OPTIONS[3]:
            run_ray_tester()
