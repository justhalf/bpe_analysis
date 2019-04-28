Scripts for preparing data.

* `prepare_wiki.sh`: prepare the wikidump corpus, there are two bash functions in it, `get_tools` prepares the tools and `prep_wiki` can do the preperation of downloading, extracting and tokenization (by UDPipe) with `${CUR_LANG}` as the language id.
* `zh_t2s.py`: convert from traditional Chinese to Simplified Chinese, from stdin to stdout. (requires the opencc-python package)
* `conllu2plain`: extract plain text from conllu file, also from stdin to stdout. Optionally, it can accept an CMD argument denoting the mode, which can be: `tok`: UD tokenized, `detok`: detokenize by UD's SpaceAfter hint, `orig`: read UD's headline comments' text or ToDoOrigText.


# Usages

## Creating Japanese texts with normalized morphemes

```shell
python3 conllu2plain.py --mode detok-lemma < (input) > (output)
```


## Extracting sentences that contain specific affixes

```shell
python get_sentences_by_affixes.py <input file> --affix <data/affixes/{id,...}> -o data/affixes/id/sentences_ud2.tsv -v
```

Create a comparison table for analysis

```shell
python create_sentence_comparison_table.py <file containing sentence ID> <BPE results (can be multiple files)> -o <output file> -v
(Example)
mkdir ../analysis && python create_sentence_comparison_table.py ../data/affixes/id/sentences_ud2.tsv ../outputs/id_ud2.bpe_*.txt -o ../analysis/id_ud2.bpe.affix.v1.tsv -v
```
