#! python3
import sys

from cli.test import run_tester
from cli.train import run_trainer

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2 or args[1] not in ['train', 'test']:
        print(f"Usage: {args[0]} [train|test]", file=sys.stderr)
    else:
        if args[1] == 'train':
            run_trainer()
        elif args[1] == 'test':
            run_tester()
