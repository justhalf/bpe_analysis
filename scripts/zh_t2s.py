#

# traditional chinese to simplified chinese: stdin -> stdout
# pip install opencc-python-reimplemented

import sys
from opencc import OpenCC

def main(fin, fout):
    cc = OpenCC('t2s')
    for line in fin:
        line2 = cc.convert(line)
        fout.write(line2)

if __name__ == '__main__':
    main(sys.stdin, sys.stdout)
