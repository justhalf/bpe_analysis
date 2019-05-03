#

import sys
from collections import Counter

def main(n=2, topk=100):
    n = int(n)
    topk = int(topk)
    c = Counter()
    accu = 0
    for line in sys.stdin:
        line = line.strip()
        for i in range(0, len(line)-n):
            c[line[i:i+n]] += 1
            accu += 1
    print(f"All {n}-grams: {len(c)}")
    for idx, p in enumerate(c.most_common(topk)):
        ww, cc = p
        print(f"{idx} {ww} {cc} {cc/accu}")

if __name__ == '__main__':
    main(*sys.argv[1:])
