import re
import gzip, bz2
from argparse import ArgumentParser
from typing import List
import numpy as np
from collections import defaultdict

import argparse
import json

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
            ret["type"].append(fields[7])
            #
            if "SpaceAfter=No" in fields[-1]:
                ret["space_after"].append(False)
            else:
                ret["space_after"].append(True)

    if ret["len"] > 0:
        yield ret

# =====
def main():
    # args
    parser = ArgumentParser()
    parser.add_argument('-f', type=str, required=True, help='Input file (conllu format)')
    parser.add_argument('-o', type=str, required=True, help='Ouput file (original sentence)')
    parser.add_argument("--types", type=str, nargs="*", default=["fixed", "flat", "compound"], help="Extracting UD-MWE types")
    args = parser.parse_args()
    #
    file, output, mwe_types = args.f, args.o, set(args.types)
    with smart_open(file) as fd, smart_open(output, "w") as wfd:
        for inst in iter_file(fd):
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
                    pairs.append((inst["word"][real_h-1], inst["word"][real_i-1], real_type))
            # output
            if len(pairs) > 0:
                wfd.write(f"# {json.dumps(pairs, ensure_ascii=False)}\n{sent}\n")

if __name__ == '__main__':
    main()

#
# python3 extract_multi_examples.py -f ../data_ud2/zh_ud2.conllu -o zh.examples
