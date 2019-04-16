# 11 Apr 2019
# By: Aldrian Obaja Muis
# Run BPE

if [ -z "${split_by_whitespace+x}" ]; then
    split_by_whitespace=""
fi
if [ -z "${no_lowercase+x}" ]; then
    no_lowercase=""
fi

mkdir -p "models"
mkdir -p "outputs"
#for lang in "en" "id" "ja" "zh"; do
for lang in "id"; do
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
            --vocab_size ${vocab_size} \
            ${split_by_whitespace} \
            ${no_lowercase} \
            2> ${model_prefix}.log
        echo "Testing..."
        segmented_file="outputs/${lang}_pud-ud-test.conllu.bpe_${vocab_size}_vocab.txt"
        echo -n "" > ${segmented_file}
        python3 run_bpe.py \
            --mode test \
            --input_files "${output_file}" \
            --output_files "${segmented_file}" \
            --model_prefix "${model_prefix}"
        if [ "${lang}" == "id" ]; then
            echo "Training on morph-normalized text..."
            model_prefix="models/${lang}_bpe_${vocab_size}_vocab_morph_norm"
            input_files="morphind/id_pud-ud-test.conllu.morphind.morphnorm"
            output_file="${model_prefix}.txt"
            python3 run_bpe.py \
                --mode train \
                --input_files "${input_files}" \
                --output_files "${output_file}" \
                --model_prefix "${model_prefix}" \
                --vocab_size ${vocab_size} \
                ${split_by_whitespace} \
                ${no_lowercase} \
                --informat "text" \
                2> ${model_prefix}.log
            echo "Testing..."
            segmented_file="outputs/${lang}_pud-ud-test.conllu.morphind.bpe_${vocab_size}_vocab.txt"
            echo -n "" > ${segmented_file}
            python3 run_bpe.py \
                --mode test \
                --input_files "${output_file}" \
                --output_files "${segmented_file}" \
                --model_prefix "${model_prefix}"
        fi
    done
done
