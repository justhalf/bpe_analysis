#

# extracting the plain text in conllu format
# - again simply from stdin to stdout
# use "pip install opencc-python-reimplemented" to install opencc

import sys
import re
from opencc import OpenCC

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

def main(fin, fout, mode):
    tok_mode = (mode=="tok")
    orig_mode = (mode=="orig")
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
        fout.write(s+"\n")

# put the first arg as "tok" if want the output to be tokenized (by UD)
#   or "detok" to make it de-tokenized (by UD's SpaceAfter)
#   or "orig" to read headline comments
#
# python3 conllu2plain tok <? >?
# python3 conllu2plain detok <? >?
# python3 conllu2plain orig <? >?
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv)>=2 else "tok"
    main(sys.stdin, sys.stdout, mode)

# some useful one liners
# split line and put one token one line
# python3 -c "import sys; print('\n'.join(['\n'.join(line.split()) for line in sys.stdin]))"
