#

# basically do three things: download UD/PUD data, extract plain texts and simplifying Chinese

# directly run `python3 download_ud.py` (but remember to set BPE_SRC_HOME correctly)
# output:
# Parses: {en,id,ja,zh}_pud.{all,test}.conllu {en,id,ja,zh}_?.{all,train,dev,test}.conllu
# Plain: {en,id,ja,zh}_pud.{all,test}.{orig,tok}.txt {en,id,ja,zh}_?.{all,train,dev,test}.{orig,tok}.txt

import os, sys, subprocess
import re

BPE_SRC_HOME = "../bpe_analysis/"

# =====
def my_print(x):
    print(x, file=sys.stderr)

def my_system(cmd, popen=False, print=False, check=False):
    if print:
        my_print("Executing cmd: %s" % cmd)
    if popen:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        n = p.wait()
        output = p.stdout.read()
        if print:
            my_print("Output is: %s" % output)
    else:
        n = os.system(cmd)
        output = None
    if check:
        assert n==0
    return output
# =====

DATA_INFO = {
    "en": ["English", "EWT"],
    "id": ["Indonesian", "GSD"],
    "ja": ["Japanese", "GSD"],
    "zh": ["Chinese", "GSD"]
}

def file_url(lang_code, lang_name, treebank_name, split_name):
    return f"https://raw.githubusercontent.com/UniversalDependencies/UD_{lang_name}-{treebank_name}/master/{lang_code}_{str.lower(treebank_name)}-ud-{split_name}.conllu"

def deal_one(lang_code, lang_name, treebank_name):
    all_splits = ["test"] if str.lower(treebank_name)=="pud" else ["train", "dev", "test"]
    for split_name in all_splits:
        cur_conllu_fname = f"{lang_code}_{str.lower(treebank_name)}.{split_name}.conllu"
        cur_url = file_url(lang_code, lang_name, treebank_name, split_name)
        # get file
        my_system(f"wget {cur_url} -O {cur_conllu_fname}", print=True, check=True)
        # extract plain text
        cur_orig_fname = f"{lang_code}_{str.lower(treebank_name)}.{split_name}.orig.txt"
        cur_tok_fname = f"{lang_code}_{str.lower(treebank_name)}.{split_name}.tok.txt"
        my_system(f"python3 {BPE_SRC_HOME}/scripts/conllu2plain.py --mode orig <{cur_conllu_fname} >{cur_orig_fname}", print=True, check=True)
        my_system(f"python3 {BPE_SRC_HOME}/scripts/conllu2plain.py --mode tok <{cur_conllu_fname} >{cur_tok_fname}", print=True, check=True)
        # specially simplifying Chinese
        if lang_code == "zh":
            for f in [cur_conllu_fname, cur_orig_fname, cur_tok_fname]:
                my_system(f"mv {f} {f}.tmp; python3 {BPE_SRC_HOME}/scripts/zh_t2s.py <{f}.tmp >{f}; rm {f}.tmp", print=True, check=True)
    # concat all splits
    for f in [cur_conllu_fname, cur_orig_fname, cur_tok_fname]:
        my_system(f"cat {' '.join([re.sub('test', z, f) for z in all_splits])} >{re.sub('test', 'all', f)}", print=True, check=True)


def main():
    for lang_code, info in DATA_INFO.items():
        # UD
        lang_name, treebank_name = info
        deal_one(lang_code, lang_name, treebank_name)
        # PUD
        deal_one(lang_code, lang_name, "PUD")
        # merge
        my_system("for cl in en id ja zh; do cat ${cl}_*.all.orig.txt >${cl}_merge.all.orig.txt; done", print=True)
        my_system("for cl in en id ja zh; do cat ${cl}_*.all.tok.txt >${cl}_merge.all.tok.txt; done", print=True)

if __name__ == '__main__':
    main()
