import re
import gzip, bz2
from argparse import ArgumentParser
from typing import List
import numpy as np
from collections import defaultdict
import sys

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


#
def main(pfile, bpefile):
    with open(pfile) as fd:
        parses = list(iter_file(fd))
    with open(bpefile) as fd:
        bpe_results = [re.sub(chr(0x2581), "", line.strip()).split(" ") for line in fd]
    #
    assert len(parses) == len(bpe_results)
    mwe_types = ["compound", "flat", "fixed"]
    counts = {k:0 for k in mwe_types}
    mwe_sets = {k:set() for k in mwe_types}
    hits = {k:0 for k in mwe_types}
    # read contents
    for one_parse, one_bpe_result in zip(parses, bpe_results):
        # find MWE
        inst = one_parse
        for i in range(inst["len"]):
            real_i = i + 1  # shift one considering ROOT
            real_h = inst["head"][i]
            real_type = inst["type"][i]
            if real_type in mwe_types and abs(real_h - real_i) == 1:
                i1, i2 = min(real_h, real_i), max(real_h, real_i)
                w1, w2 = inst["word"][i1-1], inst["word"][i2-1]
                #
                mwe_sets[real_type].add((w1, w2))
                counts[real_type] += 1
                if (w1+w2) in one_bpe_result or (w1+" "+w2) in one_bpe_result:
                    hits[real_type] += 1
    # all
    counts["all"] = sum(counts[k] for k in mwe_types)
    hits["all"] = sum(hits[k] for k in mwe_types)
    mwe_sets["all"] = set()
    for k in mwe_types:
        for z in mwe_sets[k]:
            mwe_sets["all"].add(z)
    # report
    print(f"{pfile} {bpefile}")
    for k in mwe_types + ["all"]:
        print(f"Type={k}, #set={len(mwe_sets[k])}, {hits[k]}/{counts[k]} {hits[k]/(counts[k]+1e-5)}:")

if __name__ == '__main__':
    main(*sys.argv[1:])

"""
for cl in en id ja zh; do
for f in ../data_wiki/outputs/${cl}_ud2.bpe_*.txt; do
python3 mwe_acc.py ../data_ud2/${cl}_ud2.conllu $f
done
done |& tee log
"""
