#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create a comparison table for analysis"""

from os import path
import argparse
import logging
import numpy as np
import pandas as pd

verbose = False
logger = None


def init_logger(name='logger'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    log_fmt = '%(asctime)s/%(name)s[%(levelname)s]: %(message)s'
    logging.basicConfig(format=log_fmt)
    return logger


def main(args):
    global verbose
    verbose = args.verbose

    df = pd.read_csv(args.path_sentid, delimiter='\t',
                     encoding='utf_8',
                     names=['id', 'affixes', 'text'])
    sentids = df['id'].values - 1
    max_sentid = max(sentids) + 1
    for path_input in args.path_result:
        if verbose:
            logger.info(f'Read {path_input}')
        name = path.basename(path_input)
        texts = []
        with open(path_input) as f:
            for i, line in enumerate(f):
                if i > max_sentid:
                    break
                texts.append(line.strip())
        texts = np.array(texts)
        df[name] = texts[sentids]

    if verbose:
        logger.info(f'Write {len(df)} lines to {args.path_output}')
    df.to_csv(args.path_output, sep='\t', index=False)

    return 0


if __name__ == '__main__':
    logger = init_logger('Table')
    parser = argparse.ArgumentParser()
    parser.add_argument('path_sentid', help='path to a list of sentence IDs')
    parser.add_argument('path_result', nargs='+',
                        help='path to result files')
    parser.add_argument('-o', '--output', dest='path_output',
                        required=True,
                        help='path to an output file')
    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False,
                        help='verbose output')
    args = parser.parse_args()
    main(args)
