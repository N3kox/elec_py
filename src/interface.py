# -*- coding = UTF-8 -*-
import sys
import argparse
import json
import os
from ws4mission import termSearch, termSearchExact, solutionSearch
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, default=None)
    parser.add_argument('--val', type=str, default=None)
    return parser.parse_args(argv)


def main(args):
    if args.action is None:
        return

    if args.action == 'term-search':
        if args.val is not None:
            print(json.dumps(termSearch(args.val[1:-1])))

    if args.action == 'term-search-exact':
        if args.val is not None:
            print(json.dumps(termSearchExact(args.val[1:-1])))

    if args.action == 'solution-search':
        if args.val is not None:
            print(json.dumps(solutionSearch(args.val[1:-1])))


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))