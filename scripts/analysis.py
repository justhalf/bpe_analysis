#

# analyze parallel segmented files

import sys
import re
import gzip, bz2
from argparse import ArgumentParser
from typing import List
import numpy as np

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
# =====

# =====
# helper classes
class Vocab:
    def __init__(self, data: List[List[str]]):
        self.w2i = {}
        self.w2c = {}
        self.i2w = []
        # build basic units
        for toks in data:
            for t in toks:
                self.w2c[t] = self.w2c.get(t, 0) + 1
        self.i2w = sorted(self.w2c.keys(), key=lambda x: -self.w2c[x])
        self.w2i = {v:i for i,v in enumerate(self.i2w)}
        # word type properties
        self.i2props = [{"rank": self.w2i[t], "count": self.w2c[t], "len": len(t), "word": t} for t in self.i2w]
        #
        self.summary()

    def summary(self):
        num_types = len(self.i2props)
        num_tokens = 0
        len_count_on_types = {}
        len_count_on_tokens = {}
        for v in self.i2props:
            v_len = v["len"]
            v_count = v["count"]
            num_tokens += v_count
            len_count_on_types[v_len] = len_count_on_types.get(v_len, 0) + 1
            len_count_on_tokens[v_len] = len_count_on_tokens.get(v_len, 0) + v_count
        printing(f"#=====\nSummary of Vocab: Number={num_types}")
        for k in sorted(len_count_on_types.keys()):
            printing(f"Char-len={k}: type={len_count_on_types[k]}({len_count_on_types[k]/num_types*100:.2f}%), "
                     f"token={len_count_on_tokens[k]}({len_count_on_tokens[k]/num_tokens*100:.2f}%)")

class Corpus:
    def __init__(self, data: List[List[str]]):
        self.data = data
        self.chunks = []
        for toks in data:
            new_chunks = []
            cur_idx = 0
            for t in toks:
                new_chunks.append((cur_idx, cur_idx+len(t), t))  # ([start, end), word)
                cur_idx += len(t)
            self.chunks.append(new_chunks)
        self.i2props = [{"idx": i, "Ntok": len(toks), "Nchar": sum(map(len, toks))} for i, toks in enumerate(data)]
        #
        self.summary()

    def summary(self):
        sent_sum = len(self.data)
        tok_sum = sum(v['Ntok'] for v in self.i2props)
        char_sum = sum(v['Nchar'] for v in self.i2props)
        printing(f"#=====\nSummary of Corpus: #sent={sent_sum}, #tok={tok_sum}({tok_sum/sent_sum:.3f}), "
                 f"#char={char_sum}({char_sum/sent_sum:.3f})({char_sum/tok_sum:.3f})")

# =====
# parallel helpers

def analyze_para(vocab1: Vocab, corpus1: Corpus, vocab2: Vocab, corpus2: Corpus):
    printing("#=====\nCalculating for the parallel segmentation")
    assert len(corpus1.chunks) == len(corpus2.chunks), "Non parallel data on number of sentences!"
    # =====
    # for vocabs
    def _build_props(voc):
        for v in voc.i2props:
            # TODO: the definition of these?
            # "hit" means perfect match, "small" means the current chunk is covered by the parallel large chunk,
            # "large" means the current chunk is perfectly split by several parallel chunks, "cross" means others
            v["para"] = {"hit": 0, "small": 0, "large": 0, "cross": 0}
    def _add_props(voc, w, key):
        # TODO: not efficient here!
        voc.i2props[voc.w2i[w]]["para"][key] += 1
    # for corpus
    def _add_cprops(corpus, sidx, hit):
        corpus.i2props[sidx]["hit"] = hit
    # =====
    _build_props(vocab1)
    _build_props(vocab2)
    #
    sent_idx = 0
    for chunks1, chunks2 in zip(corpus1.chunks, corpus2.chunks):
        assert "".join(z[-1] for z in chunks1) == "".join(z[-1] for z in chunks2), f"Non parallel data on #{sent_idx}!"
        # compare the chunks-pairs incrementally
        idx1, idx2 = 0, 0
        cross1, cross2 = False, False  # whether idx1 and idx2 have been crossed aligned before
        hit1, hit2 = 0, 0
        while True:
            if idx1>=len(chunks1) and idx2>=len(chunks2):
                break
            start1, end1, w1 = chunks1[idx1]
            start2, end2, w2 = chunks2[idx2]
            if end1 == end2:
                if start1 == start2:
                    # hit one segment
                    assert w1==w2, "Incorrect chunk idxes"
                    s1 = s2 = "hit"
                elif start1 > start2:
                    s1 = "small"
                    s2 = "cross" if cross2 else "large"
                else:
                    s2 = "small"
                    s1 = "cross" if cross1 else "large"
                # advance!
                _add_props(vocab1, w1, s1)
                _add_props(vocab2, w2, s2)
                idx1, idx2 = idx1 + 1, idx2 + 1
                hit1, hit2 = hit1 + 1, hit2 + 1
                cross1, cross2 = False, False
            elif end1 > end2:
                if start2 >= start1:
                    s2 = "small"
                else:
                    s2 = "cross"
                    cross1 = True  # mark as crossed
                _add_props(vocab2, w2, s2)
                idx2 += 1
            else:
                if start1 >= start2:
                    s1 = "small"
                else:
                    s1 = "cross"
                    cross2 = True  # mark as crossed
                _add_props(vocab1, w1, s1)
                idx1 += 1
        # next sentence pair
        _add_cprops(corpus1, sent_idx, hit1)
        _add_cprops(corpus2, sent_idx, hit2)
        sent_idx += 1

#
def summary_para(vocab1: Vocab, corpus1: Corpus, vocab2: Vocab, corpus2: Corpus, args):
    printing("#=====\nSummary the analysis for the parallel segmentation")
    # first sentence level
    printing("#=====\nSentence level:")
    # general
    all_prec1 = sum(z["hit"] for z in corpus1.i2props) / sum(z["Ntok"] for z in corpus1.i2props)
    all_prec2 = sum(z["hit"] for z in corpus2.i2props) / sum(z["Ntok"] for z in corpus2.i2props)
    all_f = 2*all_prec1*all_prec2 / (all_prec1+all_prec2)
    printing(f"Overall, prec1={all_prec1:.4f}, prec2={all_prec2:.4f}, f1={all_f:.4f}")
    # individuals
    sent_topk = args.sent_topk
    if sent_topk > 0:
        printing(f"And topk={sent_topk} individual rankings:")
        individual_results = {
            "prec1": [z["hit"] / z["Ntok"] for z in corpus1.i2props],
            "prec2": [z["hit"] / z["Ntok"] for z in corpus2.i2props],
        }
        individual_results["f"] = [2*a*b/(a+b) for a,b in zip(individual_results["prec1"], individual_results["prec2"])]
        for k in sorted(individual_results.keys()):
            printing(f"#-----\nIndividual ranking for key={k}")
            ranked_idxes = np.argsort(individual_results[k])
            # lowest
            for i in range(sent_topk):
                cur_idx = ranked_idxes[i]
                printing(f"#{-1-i}={individual_results[k][cur_idx]:.4f} (idx={cur_idx}):")
                printing(corpus1.data[cur_idx])
                printing(corpus2.data[cur_idx])
            # highest
            for i in range(sent_topk):
                cur_idx = ranked_idxes[-1-i]
                printing(f"#{i+1}={individual_results[k][cur_idx]:.4f} (idx={cur_idx}):")
                printing(corpus1.data[cur_idx])
                printing(corpus2.data[cur_idx])
    else:
        printing("Skip sent-topk printing")
    # Next vocab level
    printing("#=====\nVocab level:")
    vocab_topk = args.vocab_topk
    if vocab_topk > 0:
        fcode = compile(args.vocab_fcode, "", "eval")
        scode = compile(args.vocab_scode, "", "eval")
        for voc_i, cur_voc in enumerate([vocab1, vocab2]):
            printing(f"#-----\nFor Vocab {voc_i}:")
            results = []
            for e in cur_voc.i2props:
                if eval(fcode):
                    results.append((eval(scode), e))
            results.sort(key=lambda x: x[0])
            # lowest
            for i in range(vocab_topk):
                printing(f"#{-1-i}={results[i][1]}")
            # highest
            for i in range(vocab_topk):
                printing(f"#{i+1}={results[-1-i][1]}")
    else:
        printing("Skip vocab-topk printing")

# =====

#
def parse_cmd(args=None):
    parser = ArgumentParser(description='Analysis on segmentation results.')
    parser.add_argument('--f1', type=str, required=True, help='Analysis file 1')
    parser.add_argument('--f2', type=str, required=False, help='Analysis file 2 (optional)')
    parser.add_argument('--delete_spm_space', type=int, default=0, help="Whether delete special space chars of SentencePieces")
    parser.add_argument('--sent_topk', type=int, default=10, help="Print topk sentences")
    parser.add_argument('--vocab_topk', type=int, default=10, help="Print topk vocab entries")
    # using local variable "e" as vocab entry
    parser.add_argument('--vocab_fcode', type=str, default="True", help="Filter code for vocab")
    parser.add_argument('--vocab_scode', type=str, default="e['para']['hit']", help="Sort code for vocab")
    opts = parser.parse_args(args)
    printing(opts)
    return opts

# read tokens from file
def read_tokens(file, delete_spm_space):
    printing(f"#=====\nRead tokens from {file} with delete_spm_space={delete_spm_space}")
    with smart_open(file) as fd:
        SPM_SPACE = chr(0x2581)
        ret = []
        for line in fd:
            line = line.rstrip()
            if delete_spm_space:
                line = re.sub(SPM_SPACE, "", line)
            toks = line.split(" ")
            ret.append(toks)
    printing(f"Read #sent={len(ret)}, #toks={sum(map(len, ret))}")
    return ret

#
def main():
    args = parse_cmd()
    # read file1
    data1 = read_tokens(args.f1, args.delete_spm_space)
    vocab1, corpus1 = Vocab(data1), Corpus(data1)
    if args.f2:
        # read file2
        data2 = read_tokens(args.f2, args.delete_spm_space)
        vocab2, corpus2 = Vocab(data2), Corpus(data2)
        # analyze the parallel ones
        analyze_para(vocab1, corpus1, vocab2, corpus2)
        summary_para(vocab1, corpus1, vocab2, corpus2, args)

if __name__ == '__main__':
    main()

"""
Some explanation:
Compare two segmented files, provided by --f1 and --f2.
    For example, python3 analysis.py --f1 seg1.txt --f2 seg2.txt
"--delete_spm_space 0/1" provides the option to delete all SentencePieces generated special "_" tokens 
    so that we can compare seg outputs with original files easily
"--sent_topk" and "--vocab_topk" specify how many examples we want to print 
    for the best and worst resulted corpus and vocab entries
Finally, "--vocab_fcode" and "--vocab_scode" specifies the filtering and scoring code we want for the vocab-printing,
    they both assume local variable "e" as vocab entries and use Python's compile()/eval(). 
    For more details, please refer to `Vocab.i2props' and the second part of `summary_para'.
Here is a full example for running:
    python3 analysis.py --f1 seg1.txt --f2 seg2.txt --delete_spm_space 1 --sent_topk 15 --vocab_topk 15 --vocab_fcode "e['rank']<1000 and e['count']>10" --vocab_scode "e['para']['hit']/sum(e['para'].values())"
"""
