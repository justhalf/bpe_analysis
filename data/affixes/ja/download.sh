# Download tsutsuji dictionary
wget http://www.cl.inf.uec.ac.jp/lr/tsutsuji/tsutsuji-1.1u.tar.gz
tar xf tsutsuji-1.1u.tar.gz
cut -d ',' -f 1 tsutsuji-1.1u/L9.list | LC_ALL=C sort | LC_ALL=C uniq > suffixes.txt
