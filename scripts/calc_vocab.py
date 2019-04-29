#

# process mono-lingual data and get vocab

import sys
import re
import gzip, bz2
from argparse import ArgumentParser
from typing import List
import numpy as np

# =====
# general helpers
def zopen(filename, mode='r', encoding="utf-8"):
    if filename.endswith('.gz'):
        # "t" for text mode of gzip
        return gzip.open(filename, mode+"t", encoding=encoding)
    elif filename.endswith('.bz2'):
        return bz2.open(filename, mode+"t", encoding=encoding)
    else:
        return open(filename, mode, encoding=encoding)

def zlog(x):
    print(x, file=sys.stderr)
# =====

# ========
# vocab sorted by Freq
class FreqVocab:
    def __init__(self, name=None, pre_words=None, no_adding=False):
        self.name = str(name)
        self.count_all = 0
        self.w2c = {}     # word -> count
        self.i2w = []     # idx -> word (only the words that survive cutting)
        self.w2i = None
        self.i2c = None
        if pre_words is not None:
            self.i2w = list(pre_words)
            self.w2c = {w:0 for w in self.i2w}
            self._calc()
        elif no_adding:
            zlog("Warn: no adding mode for an empty Vocab!!")
        self.no_adding = no_adding

    def _calc(self):
        self.w2i = {w:i for i,w in enumerate(self.i2w)}
        self.i2c = [self.w2c[w] for w in self.i2w]

    def __len__(self):
        return len(self.i2w)

    def __repr__(self):
        return f"Vocab {self.name}: size={len(self)}({len(self.w2c)})/count={self.count_all}."

    def __contains__(self, item):
        return item in self.w2i

    def __getitem__(self, item):
        return self.w2i[item]

    def get(self, item, d):
        return self.w2i.get(item, d)

    def copy(self):
        n = FreqVocab(self.name + "_Copy")
        n.count_all = self.count_all
        n.w2c = self.w2c.copy()
        n.i2w = self.i2w.copy()
        n._calc()
        return n

    def add_all(self, ws, cc=1, ensure_exist=False):
        for w in ws:
            self.add(w, cc, ensure_exist)

    def add(self, w, cc=1, ensure_exist=False):
        orig_cc = self.w2c.get(w)
        exist = (orig_cc is not None)
        if self.no_adding or ensure_exist:
            assert exist, "Non exist key %s" % (w,)
        if exist:
            self.w2c[w] = orig_cc + cc
        else:
            self.i2w.append(w)
            self.w2c[w] = cc
        self.count_all += cc

    # cur ones that are <thresh and (only when sorting) soft-rank<=soft_cut
    def sort_and_cut(self, mincount=0, soft_cut=None, sort=True, clear_w2c=False):
        zlog("Pre-cut Vocab-stat: " + str(self))
        final_i2w = [w for w, v in self.w2c.items() if v>=mincount]
        if sort:
            final_i2w.sort(key=lambda x: -self.w2c[x])
            if soft_cut and len(final_i2w)>soft_cut:
                new_minc = self.w2c[final_i2w[soft_cut-1]]          # boundary counting value
                cur_idx = soft_cut
                while cur_idx<len(final_i2w) and self.w2c[final_i2w[cur_idx]]>=new_minc:
                    cur_idx += 1
                final_i2w = final_i2w[:cur_idx]     # soft cutting by ranking & keep boundary values
        #
        self.i2w = final_i2w
        self.count_all = sum(self.w2c[w] for w in final_i2w)
        if clear_w2c:
            final_w2c = {w:self.w2c[w] for w in final_i2w}
            self.w2c = final_w2c
        self._calc()
        zlog("Post-cut Vocab-stat: " + str(self))

    #
    def yield_infos(self):
        accu_count = 0
        for i, w in enumerate(self.i2w):
            count = self.w2c[w]
            accu_count += count
            perc = count / self.count_all * 100
            accu_perc = accu_count / self.count_all * 100
            yield (i, w, count, perc, accu_count, accu_perc)

    def write_txt(self, fname):
        with zopen(fname, "w") as fd:
            for pack in self.yield_infos():
                i, w, count, perc, accu_count, accu_perc = pack
                ss = f"{i} {w} {count}({perc:.3f}) {accu_count}({accu_perc:.3f})\n"
                fd.write(ss)
        zlog("Write (txt) to %s: %s" % (fname, str(self)))

def main(fname, vname):
    line_count, token_count, char_count = 0, 0, 0
    voc = FreqVocab()
    with zopen(fname) as fd:
        for line in fd:
            line = line.strip()
            if len(line) == 0:
                continue
            line_count += 1
            for w in line.split():
                token_count += 1
                char_count += len(w)
                voc.add(w)
            if line_count % 1000000 == 0:
                zlog(f"Read {line_count} lines, {token_count} tokens, {char_count} chars.")
    zlog(f"Final read {line_count} lines, {token_count} tokens, {char_count} chars.")
    zlog(f"Final tok/sent={token_count/line_count}, char/sent={char_count/line_count}, char/token={char_count/token_count}.")
    # vocab
    voc.sort_and_cut(sort=True)
    zlog(f"Vocab info: {voc}")
    zlog(f"TTR: {len(voc)/token_count}")
    voc.write_txt(vname)

# python3 calc_vocab.py *.txt(input-corpus) *.voc(output-vocab)
if __name__ == '__main__':
    main(*sys.argv[1:])

# scripts
"""
# =====
# collect data and vocab info
# (in dir data_ud2/../)
for f in data_ud/*.all.tok.txt data_wiki/*.txt; do 
echo; echo == calculating for $f; python3 calc_vocab.py $f $f.voc; 
done |& tee log.vocab
# =====
# rename the data to make things clear
# (in dir data_ud2)
for cl in en id ja zh; do
if [[ $cl == en ]]; then
tn=ewt
else
tn=gsd
fi
for suffix in conllu orig.txt tok.txt; do
cat ../data_ud/${cl}_{${tn},pud}.all.${suffix} > ${cl}_ud2.${suffix}
done
done
# =====
# BPE for UD
# (in dir data_ud2)
declare -A vsizes=( ["en"]=24884 ["id"]=23923 ["ja"]=26460 ["zh"]=22396 )
for cl in en id ja zh; do
curvs=${vsizes[$cl]}
for vs in $(($curvs/2)) $curvs $(($curvs*2)); do
../../bin/spm_train --input=${cl}_ud2.orig.txt --model_prefix=./models/${cl}_ud2_${vs} --vocab_size=${vs} --model_type=bpe --split_by_whitespace=0 |& tee ./models/${cl}_ud2_${vs}.log
../../bin/spm_encode --model=./models/${cl}_ud2_${vs}.model <${cl}_ud2.orig.txt >./outputs/${cl}_ud2.bpe_${vs}.txt
done
done
# =====
# BPE for WIKI
# (in dir data_wiki)
for cl in id ja zh en; do
infix=cut
for vs in 10000 30000 60000 90000; do
../../bin/spm_train --input=wiki_${cl}.detok.${infix}.txt --model_prefix=./models/${cl}_wiki_${vs} --vocab_size=${vs} --model_type=bpe --split_by_whitespace=0 >./models/${cl}_wiki_${vs}.log 2>&1
../../bin/spm_encode --model=./models/${cl}_wiki_${vs}.model <../data_ud2/${cl}_ud2.orig.txt >./outputs/${cl}_ud2.bpe_${vs}.txt
done
done
# =====
# apply BPE for wiki
for cl in id ja zh en; do
infix=cut
for vs in 10000 30000 60000 90000; do
../../bin/spm_encode --model=./models/${cl}_wiki_${vs}.model <wiki_${cl}.detok.${infix}.txt >./outputs/${cl}_wikicut.bpe_${vs}.txt
done
done
# =====
# BPE with normed data
# (in dir data_wiki2)
# for cl in ja; do
infix=cut
for vs in 10000 30000 60000 90000; do
cl=ja
f=wiki_ja.detok.norm.cut.txt
../../bin/spm_train --input=$f --model_prefix=./models/${cl}_norm_wiki_${vs} --vocab_size=${vs} --model_type=bpe --split_by_whitespace=0 >./models/${cl}_norm_wiki_${vs}.log 2>&1
../../bin/spm_encode --model=./models/${cl}_norm_wiki_${vs}.model <./udnorm/ja_merge.all.orig.norm.txt >./outputs/${cl}_norm_ud2.bpe_${vs}.txt
../../bin/spm_encode --model=./models/${cl}_norm_wiki_${vs}.model <$f >./outputs/${cl}_norm_wikicut.bpe_${vs}.txt
done
"""
