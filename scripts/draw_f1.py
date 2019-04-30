#

import re
from collections import defaultdict
import matplotlib.pyplot as plt

#
plt.rcParams['font.family'] = "Times New Roman"
plt.rcParams.update({'font.size': 16})

# draw the f1 results for BPE compared with UD-gold-segmentation

UD_RESULTS_ON_UD = """en 6221
Overall, prec1=0.4251, prec2=0.5186, f1=0.4672
en 12442
Overall, prec1=0.4775, prec2=0.5035, f1=0.4902
en 24884
Overall, prec1=0.5083, prec2=0.4641, f1=0.4852
en 49768
Overall, prec1=0.4887, prec2=0.3841, f1=0.4301
id 5980
Overall, prec1=0.4004, prec2=0.5537, f1=0.4647
id 11961
Overall, prec1=0.4792, prec2=0.5657, f1=0.5189
id 23923
Overall, prec1=0.5402, prec2=0.5378, f1=0.5390
id 47846
Overall, prec1=0.5660, prec2=0.4681, f1=0.5124
ja 6615
Overall, prec1=0.3971, prec2=0.4324, f1=0.4140
ja 13230
Overall, prec1=0.4333, prec2=0.4048, f1=0.4186
ja 26460
Overall, prec1=0.4508, prec2=0.3603, f1=0.4005
ja 52920
Overall, prec1=0.4401, prec2=0.2965, f1=0.3543
zh 5599
Overall, prec1=0.5045, prec2=0.6224, f1=0.5573
zh 11198
Overall, prec1=0.5875, prec2=0.6186, f1=0.6027
zh 22396
Overall, prec1=0.5880, prec2=0.5338, f1=0.5596
zh 44792
Overall, prec1=0.5375, prec2=0.4057, f1=0.4624"""

UD_RESULTS_ON_WIKI = """en 10000
Overall, prec1=0.4347, prec2=0.5558, f1=0.4879
en 30000
Overall, prec1=0.5049, prec2=0.5470, f1=0.5251
en 60000
Overall, prec1=0.5300, prec2=0.5227, f1=0.5263
en 90000
Overall, prec1=0.5337, prec2=0.5032, f1=0.5180
id 10000
Overall, prec1=0.4342, prec2=0.5611, f1=0.4895
id 30000
Overall, prec1=0.5378, prec2=0.5736, f1=0.5551
id 60000
Overall, prec1=0.5734, prec2=0.5573, f1=0.5652
id 90000
Overall, prec1=0.5863, prec2=0.5436, f1=0.5641
ja 10000
Overall, prec1=0.4141, prec2=0.4446, f1=0.4288
ja 30000
Overall, prec1=0.4644, prec2=0.4110, f1=0.4361
ja 60000
Overall, prec1=0.4838, prec2=0.3905, f1=0.4322
ja 90000
Overall, prec1=0.4914, prec2=0.3778, f1=0.4272
zh 10000
Overall, prec1=0.5362, prec2=0.6379, f1=0.5826
zh 30000
Overall, prec1=0.6163, prec2=0.6010, f1=0.6086
zh 60000
Overall, prec1=0.6288, prec2=0.5653, f1=0.5954
zh 90000
Overall, prec1=0.6283, prec2=0.5414, f1=0.5817"""

# str to dict for the results
def res_s2d(ss):
    ret = defaultdict(dict)
    lines = ss.split("\n")
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        idx += 1
        cl, vsize = line.split()
        vsize = int(vsize)
        line = lines[idx]
        idx += 1
        m = re.fullmatch(r"Overall, prec1=([0-9.]+), prec2=([0-9.]+), f1=([0-9.]+)", line)
        precision, recall, f1 = m.group(1), m.group(2), m.group(3)
        ret[cl][vsize] = (precision, recall, f1)
    return ret

def draw_one(one_res, title):
    vocab_sizes = sorted(one_res.keys())
    precisions, recalls, f1s = [[float(one_res[v][i]) for v in vocab_sizes] for i in range(3)]
    #
    plt.clf()
    fig, ax1 = plt.subplots(figsize=(10,6))
    ax1.set_xticks(vocab_sizes)
    ax1.set_title(title, fontsize=24)
    ax1.plot(vocab_sizes, precisions, "b-o", label="Precision")
    ax1.plot(vocab_sizes, recalls, "g-o", label="Recall")
    ax1.plot(vocab_sizes, f1s, "r-o", label="F1")
    ax1.grid(linestyle='--')
    ax1.set_ylabel("Score", fontsize=24)
    ax1.set_xlabel("Vocab Size", fontsize=24)
    ax1.legend(loc='upper right', fontsize=20)
    fig.tight_layout()
    plt.savefig(title + ".pdf", format="pdf")
    # plt.show()

#
def main():
    for res_str, train_data in zip([UD_RESULTS_ON_UD, UD_RESULTS_ON_WIKI], ["UD", "WIKI"]):
        res = res_s2d(res_str)
        for cl in ["en", "id", "ja", "zh"]:
            draw_one(res[cl], f"Lang={cl},TrainingData={train_data}")

if __name__ == '__main__':
    main()


# how to get results
"""
# with models trained on UD
declare -A vsizes=( ["en"]=24884 ["id"]=23923 ["ja"]=26460 ["zh"]=22396 )
for cl in en id ja zh; do
curvs=${vsizes[$cl]}
for vs in $(($curvs/4)) $(($curvs/2)) $curvs $(($curvs*2)); do
f="outputs/${cl}_ud2.bpe_${vs}.txt"
echo $cl $vs
python3 ../analysis.py --f1 $f --f2 ${cl}_ud2.tok.txt |& grep "Overall"
done
done
# with models trained on WIKI-CUT
for cl in en id ja zh; do
for vs in 10000 30000 60000 90000; do
f="outputs/${cl}_ud2.bpe_${vs}.txt"
echo $cl $vs
python3 ../analysis.py --f1 $f --f2 ../data_ud2/${cl}_ud2.tok.txt |& grep "Overall"
done
done
"""