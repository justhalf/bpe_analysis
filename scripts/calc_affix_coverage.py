#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from tqdm import tqdm
from os import path
import argparse
import logging
import re
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

    df = pd.read_csv(args.path_input, delimiter='\t',
                     names=['id', 'affixes', 'text'])
    if verbose:
        logger.info('Read {} lines from {}'.format(len(df), args.path_input))

    # Pattern for removing punctuation and numbers
    r_punct = re.compile(r'[!"#\$%&\\\'\(\)\*\+,-\./:;<=>\?@\[\]\^_`\{\|\}~]', re.UNICODE)

    print('Counting affixes')
    counter = defaultdict(int)
    for idx, row in tqdm(df.iterrows()):
        text = ' ' + r_punct.sub('', row['text']).lower() + ' '
        for affix in row['affixes'].split(','):
            affix = affix.lower()
            if 'ja' in args.path_input or 'zh' in args.path_input:
                aff = affix
            else:
                if affix.startswith('-'):
                    aff = affix + ' '
                else:
                    aff = ' ' + affix
            aff = aff.replace('-', '')
            counter[affix] += text.count(aff)

    affixes = pd.DataFrame(counter.items(), columns=['affix', 'freq'])
    affixes.set_index('affix', inplace=True)
    affixes.sort_values('freq', ascending=False, inplace=True)

    for path_input in args.path_vocab:
        if verbose:
            logger.info(f'Read {path_input}')
        name = path.basename(path_input)
        affixes[name] = 0
        with open(path_input) as f:
            for line in f:
                line = line.split('\t')[0].lower()
                token = line.strip('▁')
                if '▁' in token:  # MWE token
                    continue

                if line.startswith('▁'):  # prefix
                    affix = token + '-'
                else:  # suffix
                    affix = '-' + token

                if affix in counter:
                    affixes.loc[affix, name] = 1

    if verbose:
        logger.info('Write {} lines to {}'.format(
            len(affixes), args.path_output))
    affixes.to_csv(args.path_output, sep='\t')

    return 0


if __name__ == '__main__':
    logger = init_logger('Count')
    parser = argparse.ArgumentParser()
    parser.add_argument('path_input', help='path to an input file')
    parser.add_argument('--vocab', dest='path_vocab',
                        nargs='+',
                        help='path to a vocabrary file')
    parser.add_argument('-o', '--output', dest='path_output',
                        help='path to output file')
    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False,
                        help='verbose output')
    args = parser.parse_args()
    main(args)
