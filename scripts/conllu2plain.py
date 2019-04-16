#

# extracting the plain text in conllu format
# - again simply from stdin to stdout
# use "pip install opencc-python-reimplemented" to install opencc

import sys
import re
# from opencc import OpenCC
from argparse import ArgumentParser

HEADLINE_PATTERN = re.compile(r"^# ([a-zA-Z_]*) = (.*)$")

def iter_file(fin):
    ret = {"len": 0, "word": [], "pos": [], "head": [], "type": [], "space_after": [], "info": {}}
    for line in fin:
        line = line.strip()
        # yield and reset
        if len(line) == 0:
            if ret["len"] > 0:
                yield ret
            ret = {"len": 0, "word": [], "pos": [], "head": [], "type": [], "space_after": [], "info": {}}
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

def main(fin, fout, mode, replace_space, replace_char, lowercase):
    MY_SPACE = chr(0x2590)
    tok_mode = (mode=="tok")
    orig_mode = (mode=="orig")
    if replace_char is None:
        replace_char = MY_SPACE
    for one_parse in iter_file(fin):
        if orig_mode:
            # prefer "ToDoOrigText"
            if "ToDoOrigText" in one_parse["info"]:
                s = one_parse["info"]["ToDoOrigText"]
            else:
                s = one_parse["info"]["text"]
        else:
            ts = []
            for i in range(len(one_parse["word"])-1):
                ts.append(one_parse["word"][i])
                if tok_mode or one_parse["space_after"][i]:
                    ts.append(" ")
            ts.append(one_parse["word"][-1])
            s = "".join(ts)
        if lowercase:
            s = str.lower(s)
        if replace_space:
            s = re.sub(" ", replace_char, s)
        fout.write(s+"\n")

# put the first arg as "tok" if want the output to be tokenized (by UD)
#   or "detok" to make it de-tokenized (by UD's SpaceAfter)
#   or "orig" to read headline comments
#
# python3 conllu2plain --mode tok <? >?
# python3 conllu2plain --mode detok <? >?
# python3 conllu2plain --mode orig <? >?
if __name__ == '__main__':
    parser = ArgumentParser(description='Converting conllu file to plain text files with several modes.')
    parser.add_argument("--mode", type=str, default="orig", choices=["tok", "detok", "orig"],
                        help="tok: UD tokenized, detok: De-tok by UD's SpaceAfter, orig: read from headline comments")
    parser.add_argument("--replace_space", type=int, default=0,
                        help="Whether replace spaces with special token, which can be useful for extending MWE")
    parser.add_argument("--replace_char", type=str, help="Replace with other chars.")
    parser.add_argument("--lowercase", type=int, default=0,
                        help="Whether lowercase things")
    args = parser.parse_args()
    #
    main(sys.stdin, sys.stdout, args.mode, args.replace_space, args.replace_char, args.lowercase)

# some useful one liners
# split line and put one token one line
# python3 -c "import sys; print('\n'.join(['\n'.join(line.split()) for line in sys.stdin]))"
# training BPE without whitespace splitting
# ../bin/spm_train --model_type=bpe --vocab_size=10000 --split_by_whitespace=0 --input=en.raw --model_prefix=model
# ../bin/spm_encode --model=./model.model <en.raw
