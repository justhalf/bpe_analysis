#

# extract examples which contains affixes

import sys
import re
import gzip, bz2
from argparse import ArgumentParser
from typing import List
import numpy as np
from collections import defaultdict

from mosestokenizer import MosesDetokenizer

import argparse

# =====
# general helpers
def smart_open(filename, mode='r', encoding="utf-8"):
    if filename.endswith('.gz'):
        # "t" for text mode of gzip
        return gzip.open(filename, mode+"t", encoding=encoding)
    elif filename.endswith('.bz2'):
        return bz2.open(filename, mode+"t", encoding=encoding)
    else:
        return open(filename, mode, encoding=encoding)

def printing(x):
    print(x, file=sys.stderr)

def random_stream(batch=1024):
    while True:
        for x in np.random.random_sample(batch):
            yield x

# =====

def get_detoker(lang):
    if lang == "ja" or lang == "zh":
        return lambda x: "".join(x)
    else:
        d = MosesDetokenizer(lang)
        return lambda x: d(x)

PREFIXES = {
    "en": [],
    "id": [],
    "ja": [],
    "zh": ["可", "重", "地", "老", "小", "第", "初", "好", "难", "非", "反", "泛", "超", "大", "高", "多"],
}

SUFFIXES = {
    "en": [],
    "id": [],
    "ja": [],
    "zh": ["儿", "子", "头", "们", "地", "化", "学", "家", "者", "着", "性", "主义", "员", "手", "热", "度", "坛", "感"],
}

def main():
    # args
    parser = ArgumentParser()
    parser.add_argument('-f', type=str, required=True, help='Input file (Must be tokenized)')
    parser.add_argument('-o', type=str, required=True, help='Ouput file (detokenized by Moses)')
    parser.add_argument('-l', type=str, required=True, help='Input language code')
    parser.add_argument('-n', type=int, default=20, help='Number of examples to output per affix')
    parser.add_argument('-d', type=float, default=0., help='Drop rate of examples')
    args = parser.parse_args()
    #
    file, output, num, drop, lang = args.f, args.o, args.n, args.d, args.l
    detoker = get_detoker(lang)
    rs = random_stream()
    prefixes, suffixes = PREFIXES[lang], SUFFIXES[lang]
    prefix_examples, suffix_examples = defaultdict(list), defaultdict(list)
    #
    full_number = len(prefixes) + len(suffixes)
    cur_number = 0
    # todo: really naive loop, may be not efficient
    with smart_open(file) as fd:
        for line in fd:
            hit_prefixes, hit_suffixes = set(), set()
            tokens = line.strip().split()
            for t in tokens:
                for pf in prefixes:
                    if t.startswith(pf):
                        hit_prefixes.add(pf)
                for sf in suffixes:
                    if t.endswith(sf):
                        hit_suffixes.add(sf)
            detok_str = detoker(tokens)
            for pf in hit_prefixes:
                if len(prefix_examples[pf]) < num and next(rs) > drop:
                    prefix_examples[pf].append(detok_str)
                    if len(prefix_examples[pf]) >= num:
                        cur_number += 1
            for sf in hit_suffixes:
                if len(suffix_examples[sf]) < num and next(rs) > drop:
                    suffix_examples[sf].append(detok_str)
                    if len(suffix_examples[sf]) >= num:
                        cur_number += 1
            if cur_number >= full_number:
                break
    with smart_open(output, "w") as fd:
        for pf in prefixes:
            fd.write("\n".join([f"# {pf}-"] + prefix_examples[pf])+"\n\n")
        for sf in suffixes:
            fd.write("\n".join([f"# -{sf}"] + suffix_examples[sf]) + "\n\n")

if __name__ == '__main__':
    main()

#
# pre-request: pip install mosestokenizer
# for example, to extract "20" examples for each affix for the language of "zh"
#   from input file "../data_ud2/zh_ud2.tok.txt" to output file "zh.examples" with example-drop rate of "0."
# * example-drop rate can be useful for larger dataset to avoid examples clustered in one portion
#
# python3 extract_affix_examples.py -f ../data_ud2/zh_ud2.tok.txt -o zh.examples -l zh -n 20 -d 0.
#
# after this, again use spm_encode to BPE the output file to see the BPE results on those examples
