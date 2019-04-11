# 11 Apr 2019
# By: Aldrian Obaja Muis
# Calculate type count from PUD

mkdir -p "vocab"
for lang in "en" "id" "ja" "zh"; do
    filename="PUD/${lang}_pud-ud-test.conllu.txt"
    vocab_file="vocab/${lang}_pud_vocab.txt"
    cat ${filename} \
        | grep -Ev "(^#|^$)" \
        | cut -d$'\t' -f2 \
        | tr [A-Z] [a-z] \
        | sort \
        | uniq -c \
        | sort -nr \
        > ${vocab_file}
    n_lines=$(wc -l ${vocab_file})
    echo "Number of lines: ${n_lines}"
done
