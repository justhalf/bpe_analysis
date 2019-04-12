Scripts for preparing data.

* `prepare_wiki.sh`: prepare the wikidump corpus, there are two bash functions in it, `get_tools` prepares the tools and `prep_wiki` can do the preperation of downloading, extracting and tokenization (by UDPipe) with `${CUR_LANG}` as the language id.
* `zh_t2s.py`: convert from traditional Chinese to Simplified Chinese, from stdin to stdout. (requires the opencc-python package)
* `conllu2plain`: extract plain text from conllu file, also from stdin to stdout. Optionally, it can accept an CMD argument denoting the mode, which can be: `tok`: UD tokenized, `detok`: detokenize by UD's SpaceAfter hint, `orig`: read UD's headline comments' text or ToDoOrigText.
