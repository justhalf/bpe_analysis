# -*- coding: utf-8 -*-
"""
15 Apr 2019
To separate punctuations occuring not inside words
"""

# Import statements
from __future__ import print_function, division
import sys
from argparse import ArgumentParser
import re

def separate_punct(text):
    tokens = re.findall(r'([-A-Za-z0-9]+|[^A-Za-z0-9 ]+)', text)
    return ' '.join(tokens)

def main():
    parser = ArgumentParser(description='To separate punctuations occuring not inside words')
    parser.add_argument('--inpath', help='The input file')
    parser.add_argument('--outpath', help='The output file')
    args = parser.parse_args()
    with open(args.inpath, 'r') as infile:
        with open(args.outpath, 'w') as outfile:
            for line in infile:
                outfile.write(separate_punct(line))

if __name__ == '__main__':
    main()

