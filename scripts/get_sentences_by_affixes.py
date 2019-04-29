#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Search for sentences by affixes"""

from collections import defaultdict
from os import listdir
from os import path
from tqdm import tqdm
import argparse
import logging
import re

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


    # Read affixes
    if verbose:
        logger.info('Read affixes from ' + args.dir_affixes)
    affixes = defaultdict(list)
    for filename in listdir(args.dir_affixes):
        cat = filename.split('.')[0]
        if cat not in {'prefixes', 'suffixes'}:
            print('Skip ', filename)
            continue
        filename = path.join(args.dir_affixes, filename)
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):  # comment out
                    continue
                if 'zh/' not in filename and 'ja/' not in filename:
                    if len(line) == 1:  # ignore one-character affixes
                        continue
                affixes[cat].append(line)
            if verbose:
                logger.info(f'Read {len(affixes[cat])} items'
                            ' from {filename}')

    # Sort
    for key, val in affixes.items():
        affixes[key] = sorted(val, key=lambda s: len(s), reverse=True)
    # Defining patterns
    pattern = {}
    s = '(' + '|'.join(affixes['prefixes']) + ')'
    pattern['prefix'] = re.compile(r'^{s}\w|\s{s}\w'.format(s=s))
    s = '(' + '|'.join(affixes['suffixes']) + ')'
    pattern['suffix'] = re.compile(r'\w{s}$|\w{s}\s'.format(s=s))

    # Pattern for removing punctuation and numbers
    r_punct = re.compile(r'[!"#\$%&\\\'\(\)\*\+,-\./:;<=>\?@\[\]\^_`\{\|\}~]', re.UNICODE)

    if verbose:
        logger.info('Read ' + args.path_input)
        logger.info('Write to ' + args.path_output)
    with open(args.path_output, 'w') as fout:
        with open(args.path_input) as fin:
            for i, line in tqdm(enumerate(fin, start=1)):
                line = line.strip()
                text = r_punct.sub('', line)
                buff = [str(i)]
                cats = []
                for m in pattern['prefix'].finditer(text):
                    for g in [1, 2]:
                        if m.group(g) is None:
                            continue
                        cats.append(f'{m.group(g).strip()}-')
                for m in pattern['suffix'].finditer(text):
                    for g in [1, 2]:
                        if m.group(g) is None:
                            continue
                        cats.append(f'-{m.group(g).strip()}')
                if len(cats) == 0:
                    continue
                buff.append(','.join(sorted(list(set(cats)))))
                if args.del_space:
                    line = line.replace(' ', '')
                buff.append(line)
                fout.write('\t'.join(buff) + '\n')
    return 0


if __name__ == '__main__':
    logger = init_logger('Search')
    parser = argparse.ArgumentParser()
    parser.add_argument('path_input', help='path to an input file')
    parser.add_argument('--affixes', dest='dir_affixes',
                        required=True,
                        help='path to a directory containing lists of affixes')
    parser.add_argument('-o', '--output', dest='path_output',
                        required=True,
                        help='path to an output file')
    parser.add_argument('--del-space', action='store_true',
                        help='delete spaces in output texts [for zh/ja]')
    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False,
                        help='verbose output')
    args = parser.parse_args()
    main(args)
