# -*- coding : utf-8 -*-
import sys
import argparse
import json
from ws4mission import missionTextParser, getExplanation



def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, default=None)
    parser.add_argument('--val', type=str, default=None)
    return parser.parse_args(argv)


def main(args):
    # print(args)
    if args.action is None:
        return

    # TODO: 分词查询相似度匹配
    if args.action == 'tf-idf':
        if args.val is None:
            return
        else:
            # print(getExplanation(args.val))
            print(json.dumps(getExplanation(args.val)))


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))

