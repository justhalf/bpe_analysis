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

# extra information (only temporaily recorded here, not related to MWE)
# PREFIXES = {
#     "zh": ["可", "重", "地", "老", "小", "第", "初", "好", "难", "非", "反", "泛", "超", "大", "高", "多"],
# }
# SUFFIXES = {
#     "zh": ["儿", "子", "头", "们", "地", "化", "学", "家", "者", "着", "性", "主义", "员", "手", "热", "度", "坛", "感"],
# }
#

HEADLINE_PATTERN = re.compile(r"^# ([a-zA-Z_]*) = (.*)$")

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

def iter_file(fin):
    ret = {"len": 0, "word": [], "lemma": [], "pos": [],
           "head": [], "type": [], "space_after": [], "info": {}}
    for line in fin:
        line = line.strip()
        # yield and reset
        if len(line) == 0:
            if ret["len"] > 0:
                yield ret
            ret = {"len": 0, "word": [], "lemma": [], "pos": [],
                   "head": [], "type": [], "space_after": [], "info": {}}
        elif line[0] == "#":
            # read head lines
            match = re.match(HEADLINE_PATTERN, line)
            if match:
                n,v = match.group(1), match.group(2)
                ret["info"][n] = v
        else:
            fields = line.split('\t')
            # skip special lines
            try:
                idx = int(fields[0])
            except:
                continue
            #
            ret["len"] += 1
            ret["word"].append(fields[1])
            ret["lemma"].append(fields[2])
            ret["pos"].append(fields[3])
            ret["head"].append(int(fields[6]))
            ret["type"].append(fields[7].split(":")[0])
            #
            if "SpaceAfter=No" in fields[-1]:
                ret["space_after"].append(False)
            else:
                ret["space_after"].append(True)

    if ret["len"] > 0:
        yield ret


def init_logger(name='logger'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    log_fmt = '%(asctime)s/%(name)s[%(levelname)s]: %(message)s'
    logging.basicConfig(format=log_fmt)
    return logger


def main(args):
    global verbose
    verbose = args.verbose
    if verbose:
        logger.info('Read ' + args.path_input)
        logger.info('Write to ' + args.path_output)
    #
    mwe_types = set(["fixed", "flat", "compound"])
    with smart_open(args.path_input) as fd, smart_open(args.path_output, "w") as wfd:
        for inst_idx, inst in enumerate(iter_file(fd), start=1):
            # prefer "ToDoOrigText"
            if "ToDoOrigText" in inst["info"]:
                sent = inst["info"]["ToDoOrigText"]
            else:
                sent = inst["info"]["text"]
            # find MWE
            pairs = []
            for i in range(inst["len"]):
                real_i = i+1  # shift one considering ROOT
                real_h = inst["head"][i]
                real_type = inst["type"][i]
                if real_type in mwe_types and abs(real_h-real_i)==1:
                    pairs.append("-".join((inst["word"][real_h-1], inst["word"][real_i-1], real_type)))
            # output
            if len(pairs) > 0:
                buff = [str(inst_idx), ",".join(pairs), sent]
                wfd.write('\t'.join(buff) + '\n')
    return 0


if __name__ == '__main__':
    logger = init_logger('Search')
    parser = argparse.ArgumentParser()
    parser.add_argument('path_input', help='path to an input file')
    parser.add_argument('-o', '--output', dest='path_output',
                        required=True,
                        help='path to an output file')
    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False,
                        help='verbose output')
    args = parser.parse_args()
    main(args)

# examples
# for cl in en id zh ja; do mkdir -p mwe/${cl}; python get_sentences_by_mwe.py ../data_ud2/${cl}_ud2.conllu -o mwe/${cl}/sentences_ud2.tsv -v; done
# for cl in en id zh ja; do python3 create_sentence_comparison_table.py ./mwe/${cl}/sentences_ud2.tsv ../data_ud2/outputs/${cl}_ud2.bpe_*.txt -v -o ./analysis/mwe/${cl}_ud2.bpe.mwe.v1.tsv; done
