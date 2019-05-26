#

# score sentences by kenlm (one tokenized sentence per line)

import sys
import kenlm
import numpy as np

printing = lambda x: print(x, flush=True, file=sys.stderr)

#
def main(mfile, fin=None, fout=None):
    if fin is None:
        fin = sys.stdin
    else:
        fin = open(fin)
    if fout is None:
        fout = sys.stdout
    else:
        fout = open(fout, 'w')
    printing(f"read from {fin} and write to {fout}")
    # load lm model
    def _load_lm(f):
        m = kenlm.LanguageModel(f)
        printing(f"Load LM model from {m.path}, order={m.order}")
        return m
    # average prob
    def _avg_score(m, sent):
        scores = [float(z[0]) for z in m.full_scores(sent)]
        return float(np.average(scores))
    # go!
    model = _load_lm(mfile)
    for sentence in fin:
        score = _avg_score(model, sentence)
        fout.write(str(score)+"\n")
    #
    fin.close()
    fout.close()

if __name__ == '__main__':
    main(*sys.argv[1:])

# trained by: bzcat ../data_wiki/wiki_en.tok.bz2 | ./lmplz -o 4 -T ./tmp/ -S 50% >lm_en.arpa
# output: python3 score_lm.py lm_en.arpa ../data_ud2/en_ud2.tok.txt en_ud2.tok.score

# the output score file is put at "output/u2/en_ud2.tok.score"
