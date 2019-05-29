# 29 May 2019
# By: Aldrian Obaja Muis
# Run analysis.py

for cl in en; do
    for vs in 10000 30000 60000 90000; do
        f="outputs/ud2/${cl}_ud2.bpe_${vs}.txt"
        echo $cl $vs
        python3 scripts/analysis.py \
            --f1 $f \
            --f2 outputs/ud2/${cl}_ud2.tok.txt \
            --group_by_ppl outputs/ud2/en_ud2.tok.score \
            --n_groups 10 \
            |& grep -E "(Overall|Max score)"
    done
done
