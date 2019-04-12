#!/usr/bin/env bash

# some commands to prepare wikidump corpus

# =====
# obtain tools
function get_tools () {
# for extracting wiki-xml
git clone https://github.com/attardi/wikiextractor
# for Chinese traditional to simplified
pip install opencc-python-reimplemented
# for sentence splitting and tokenization (one step)
git clone https://github.com/ufal/udpipe
cd udpipe/src; make; ln -s udpipe ..; cd ../..;
# download UDPipe models
wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2898/english-ewt-ud-2.3-181115.udpipe -O udpipe/en.udpipe
wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2898/indonesian-gsd-ud-2.3-181115.udpipe -O udpipe/id.udpipe
wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2898/japanese-gsd-ud-2.3-181115.udpipe -O udpipe/ja.udpipe
# todo(warning): when I(zs) am preparing Chinese, I retrained a udpipe model after converting all to simplified Chinese
wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2898/chinese-gsd-ud-2.3-181115.udpipe -O udpipe/zh.udpipe
# moses detokenizer
wget https://raw.githubusercontent.com/moses-smt/mosesdecoder/master/scripts/tokenizer/detokenizer.perl
}

# =====
# the preparing steps
# with ${CUR_LANG} as the language id

function prep_wiki () {
# step 1: xml data to raw text
echo "Step 1: xml2raw for the language of ${CUR_LANG}"
# prepare data dir
mkdir -p "wiki_${CUR_LANG}"
mkdir -p "wiki_${CUR_LANG}/extracted"
# download the data
wget -nc https://dumps.wikimedia.org/${CUR_LANG}wiki/20181120/${CUR_LANG}wiki-20181120-pages-articles.xml.bz2 -O "wiki_${CUR_LANG}/wiki_${CUR_LANG}.xml.bz2"
# extract
# todo(warning): with the current splitting size (150M), all languages will be within 100 pieces, thus all files are in dir AA
python3 wikiextractor/WikiExtractor.py "wiki_${CUR_LANG}/wiki_${CUR_LANG}.xml.bz2" -c -b 150M -o "wiki_${CUR_LANG}/extracted" --no-template --processes 8
# remove <*> tags
for f in wiki_${CUR_LANG}/extracted/AA/*.bz2; do
    echo `basename $f .bz2`; bzcat $f | sed '/^<[^>]*>$/d' | bzip2 >wiki_${CUR_LANG}/extracted/"`basename $f .bz2`.c.bz2";
done
#
# step 2: sentence splitting and tokenization with UDPipe
mkdir -p "wiki_${CUR_LANG}/tokenized"
for f in wiki_${CUR_LANG}/extracted/wiki_*.c.bz2; do
#echo "bzcat $f | bash $ZZ/ztools/udpipe/model/models/udpipe_tok.sh ${CUR_LANG} | bzip2 >zr_${CUR_LANG}/tokenized/`basename $f .c.bz2`.ct.bz2"
bzcat $f | udpipe/udpipe --tokenize --output horizontal udpipe/${CUR_LANG}.udpipe | bzip2 >wiki_${CUR_LANG}/tokenized/`basename $f .c.bz2`.ct.bz2
done
# concat them together (also, delete one token (no spaces) lines)
bzcat wiki_${CUR_LANG}/tokenized/*.ct.bz2 | grep "\s" | bzip2 >wiki_${CUR_LANG}/wiki_${CUR_LANG}.tok.bz2
#
# step 3: detokenize (simple for zh and ja to delete spaces, but for en and id, use Moses ok?)
if [[ ${CUR_LANG} == "zh" ]] || [[ ${CUR_LANG} == "ja" ]]; then
bzcat wiki_${CUR_LANG}/wiki_${CUR_LANG}.tok.bz2 | sed "s/\s//g" | bzip2 >wiki_${CUR_LANG}/wiki_${CUR_LANG}.detok.bz2
else
bzcat wiki_${CUR_LANG}/wiki_${CUR_LANG}.tok.bz2 | perl detokenizer.perl -l ${CUR_LANG} | bzip2 >wiki_${CUR_LANG}/wiki_${CUR_LANG}.detok.bz2
fi
}

# =====

# go!
get_tools
CUR_LANG=id prep_wiki
