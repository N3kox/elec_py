# -*- coding : utf-8 -*-
import sys
import argparse
import json
from webSpider.src.ws4mission import missionTextParser


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--new', type=str, default=None)

    return parser.parse_args(argv)


def main(args):
    if args.new is not None:
        pass


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))

