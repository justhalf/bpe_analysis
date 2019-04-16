# -*- coding: utf-8 -*-
"""
16 Apr 2019
To process text morphologically using MorphInd
"""

# Import statements
from __future__ import print_function, division
import sys
from argparse import ArgumentParser
from separate_punct import separate_punct
import subprocess
import re

def main():
    parser = ArgumentParser(description='Process text through MorphInd')
    parser.add_argument('--inpath',
                        help='The input file one sentence per line')
    parser.add_argument('--outprefix',
                        help=('The output file prefix. This script will produce '
                              'multiple files: .tokens, .morph, and .morphnorm'))
    args = parser.parse_args()
    tok_path = '{}.tokens'.format(args.outprefix)
    morph_path = '{}.morph'.format(args.outprefix)
    norm_path = '{}.morphnorm'.format(args.outprefix)
    with open(args.inpath, 'r') as infile:
        with open(tok_path, 'w') as outfile:
            for line in infile:
                line = separate_punct(line.rstrip('\n'))+'\n'
                outfile.write(line)
    subprocess.call('cat {} | perl MorphInd.pl > {}'.format(
                        tok_path, morph_path), shell=True)
    with open(morph_path, 'r') as infile:
        with open(norm_path, 'w') as outfile:
            for line in infile:
                line = re.sub('<[^>]+>', '', line)
                line = re.sub('_...', '', line)
                line = re.sub(r'\+dia', '+nya', line)
                line = re.sub(r'\+', '', line)
                line = re.sub(r'(^| )\^', r'\1', line)
                line = re.sub(r'\$( |$)', r'\1', line)
                line = re.sub(r'\.\.', '.', line)
                outfile.write(line)

if __name__ == '__main__':
    main()

