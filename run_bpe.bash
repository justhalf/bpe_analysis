# 11 Apr 2019
# By: Aldrian Obaja Muis
# Run BPE

OPT=$1

mkdir -p "models"
mkdir -p "outputs"
for lang in "en" "id" "ja" "zh"; do
    echo "Doing ${lang}..."
    pud_vocab_size=$(wc -l vocab/${lang}_pud_vocab.txt | cut -d' ' -f1)
    vocab_sizes=()
    vocab_sizes+=($(python3 -c "print(int(2.0 * ${pud_vocab_size}))"))
    vocab_sizes+=($(python3 -c "print(int(1.0 * ${pud_vocab_size}))"))
    vocab_sizes+=($(python3 -c "print(int(0.5 * ${pud_vocab_size}))"))
    vocab_sizes+=($(python3 -c "print(int(0.1 * ${pud_vocab_size}))"))
    vocab_sizes+=($(python3 -c "print(int(0.05 * ${pud_vocab_size}))"))
    for vocab_size in ${vocab_sizes[@]}; do
        echo "Vocab size: ${vocab_size}"
        echo "Training..."
        model_prefix="models/${lang}_bpe_${vocab_size}_vocab"
        input_files="PUD/${lang}_pud-ud-test.conllu.txt"
        output_file="${model_prefix}.txt"
        python3 run_bpe.py \
            --mode train \
            --input_files "${input_files}" \
            --output_files "${output_file}" \
            --model_prefix "${model_prefix}" \
            --vocab_size ${vocab_size} $* \
            2> ${model_prefix}.log
        echo "Testing..."
        segmented_file="outputs/${lang}_pud-ud-test.conllu.bpe_${vocab_size}_vocab.txt"
        echo -n "" > ${segmented_file}
        python3 run_bpe.py \
            --mode test \
            --input_files "${output_file}" \
            --output_files "${segmented_file}" \
            --model_prefix "${model_prefix}" $*
    done
done
