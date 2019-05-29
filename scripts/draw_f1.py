#

import re
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
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
Overall, prec1=0.5375, prec2=0.4057, f1=0.4624
id 2000
Overall, prec1=0.2674, prec2=0.4776, f1=0.3428
id 4000
Overall, prec1=0.3527, prec2=0.5353, f1=0.4252
id 6000
Overall, prec1=0.4007, prec2=0.5536, f1=0.4649
id 8000
Overall, prec1=0.4322, prec2=0.5592, f1=0.4876
id 10000
Overall, prec1=0.4602, prec2=0.5662, f1=0.5077
id 12000
Overall, prec1=0.4796, prec2=0.5657, f1=0.5191
id 14000
Overall, prec1=0.5089, prec2=0.5788, f1=0.5416
id 16000
Overall, prec1=0.5092, prec2=0.5617, f1=0.5342
id 18000
Overall, prec1=0.5309, prec2=0.5708, f1=0.5501
id 20000
Overall, prec1=0.5543, prec2=0.5803, f1=0.5670
id 22000
Overall, prec1=0.5528, prec2=0.5631, f1=0.5579
id 24000
Overall, prec1=0.5406, prec2=0.5379, f1=0.5393
id 26000
Overall, prec1=0.5504, prec2=0.5399, f1=0.5451
id 28000
Overall, prec1=0.5574, prec2=0.5389, f1=0.5480
id 30000
Overall, prec1=0.5616, prec2=0.5351, f1=0.5480
id 32000
Overall, prec1=0.5639, prec2=0.5294, f1=0.5461
id 34000
Overall, prec1=0.5651, prec2=0.5225, f1=0.5429
id 36000
Overall, prec1=0.5653, prec2=0.5147, f1=0.5388
id 38000
Overall, prec1=0.5658, prec2=0.5072, f1=0.5349
id 40000
Overall, prec1=0.5662, prec2=0.4996, f1=0.5308
id 42000
Overall, prec1=0.5648, prec2=0.4904, f1=0.5249
id 44000
Overall, prec1=0.5632, prec2=0.4811, f1=0.5189
id 46000
Overall, prec1=0.5646, prec2=0.4743, f1=0.5155
id 48000
Overall, prec1=0.5658, prec2=0.4673, f1=0.5119
id 50000
Overall, prec1=0.5659, prec2=0.4595, f1=0.5072
id 52000
Overall, prec1=0.5659, prec2=0.4516, f1=0.5023
id 54000
Overall, prec1=0.5655, prec2=0.4432, f1=0.4969
id 56000
Overall, prec1=0.5641, prec2=0.4342, f1=0.4907
id 58000
Overall, prec1=0.5607, prec2=0.4237, f1=0.4826
id 60000
Overall, prec1=0.5548, prec2=0.4115, f1=0.4725
ja 2000
Overall, prec1=0.2573, prec2=0.0356, f1=0.0626
ja 4000
Overall, prec1=0.3537, prec2=0.4460, f1=0.3945
ja 6000
Overall, prec1=0.3889, prec2=0.4341, f1=0.4102
ja 8000
Overall, prec1=0.4085, prec2=0.4252, f1=0.4167
ja 10000
Overall, prec1=0.4217, prec2=0.4179, f1=0.4198
ja 12000
Overall, prec1=0.4300, prec2=0.4099, f1=0.4197
ja 14000
Overall, prec1=0.4412, prec2=0.4075, f1=0.4237
ja 16000
Overall, prec1=0.4398, prec2=0.3942, f1=0.4157
ja 18000
Overall, prec1=0.4439, prec2=0.3890, f1=0.4147
ja 20000
Overall, prec1=0.4519, prec2=0.3883, f1=0.4177
ja 22000
Overall, prec1=0.4497, prec2=0.3779, f1=0.4107
ja 24000
Overall, prec1=0.4502, prec2=0.3700, f1=0.4062
ja 26000
Overall, prec1=0.4506, prec2=0.3620, f1=0.4015
ja 28000
Overall, prec1=0.4497, prec2=0.3554, f1=0.3971
ja 30000
Overall, prec1=0.4469, prec2=0.3491, f1=0.3920
ja 32000
Overall, prec1=0.4461, prec2=0.3443, f1=0.3886
ja 34000
Overall, prec1=0.4456, prec2=0.3397, f1=0.3855
ja 36000
Overall, prec1=0.4455, prec2=0.3354, f1=0.3827
ja 38000
Overall, prec1=0.4446, prec2=0.3305, f1=0.3792
ja 40000
Overall, prec1=0.4434, prec2=0.3255, f1=0.3754
ja 42000
Overall, prec1=0.4423, prec2=0.3206, f1=0.3717
ja 44000
Overall, prec1=0.4419, prec2=0.3161, f1=0.3686
ja 46000
Overall, prec1=0.4410, prec2=0.3113, f1=0.3649
ja 48000
Overall, prec1=0.4405, prec2=0.3069, f1=0.3618
ja 50000
Overall, prec1=0.4405, prec2=0.3027, f1=0.3588
ja 52000
Overall, prec1=0.4403, prec2=0.2985, f1=0.3558
ja 54000
Overall, prec1=0.4402, prec2=0.2943, f1=0.3527
ja 56000
Overall, prec1=0.4399, prec2=0.2899, f1=0.3495
ja 58000
Overall, prec1=0.4394, prec2=0.2855, f1=0.3461
ja 60000
Overall, prec1=0.4392, prec2=0.2813, f1=0.3429
zh 2000
Overall, prec1=0.4444, prec2=0.5858, f1=0.5054
zh 4000
Overall, prec1=0.4121, prec2=0.5807, f1=0.4821
zh 6000
Overall, prec1=0.5119, prec2=0.6197, f1=0.5606
zh 8000
Overall, prec1=0.5547, prec2=0.6266, f1=0.5885
zh 10000
Overall, prec1=0.5666, prec2=0.6106, f1=0.5878
zh 12000
Overall, prec1=0.5871, prec2=0.6089, f1=0.5978
zh 14000
Overall, prec1=0.5911, prec2=0.5951, f1=0.5931
zh 16000
Overall, prec1=0.6158, prec2=0.6029, f1=0.6093
zh 18000
Overall, prec1=0.6050, prec2=0.5765, f1=0.5904
zh 20000
Overall, prec1=0.5925, prec2=0.5484, f1=0.5696
zh 22000
Overall, prec1=0.5887, prec2=0.5359, f1=0.5611
zh 24000
Overall, prec1=0.5833, prec2=0.5230, f1=0.5515
zh 26000
Overall, prec1=0.5764, prec2=0.5089, f1=0.5406
zh 28000
Overall, prec1=0.5714, prec2=0.4967, f1=0.5315
zh 30000
Overall, prec1=0.5684, prec2=0.4864, f1=0.5242
zh 32000
Overall, prec1=0.5630, prec2=0.4741, f1=0.5148
zh 34000
Overall, prec1=0.5587, prec2=0.4628, f1=0.5063
zh 36000
Overall, prec1=0.5550, prec2=0.4522, f1=0.4984
zh 38000
Overall, prec1=0.5513, prec2=0.4416, f1=0.4904
zh 40000
Overall, prec1=0.5482, prec2=0.4318, f1=0.4831
zh 42000
Overall, prec1=0.5428, prec2=0.4201, f1=0.4736
zh 44000
Overall, prec1=0.5395, prec2=0.4102, f1=0.4660
zh 46000
Overall, prec1=0.5351, prec2=0.3994, f1=0.4574
zh 48000
Overall, prec1=0.5306, prec2=0.3888, f1=0.4488
zh 50000
Overall, prec1=0.5271, prec2=0.3790, f1=0.4410
zh 52000
Overall, prec1=0.5237, prec2=0.3696, f1=0.4333
zh 54000
Overall, prec1=0.5200, prec2=0.3599, f1=0.4254
zh 56000
Overall, prec1=0.5159, prec2=0.3500, f1=0.4170
zh 58000
Overall, prec1=0.5119, prec2=0.3402, f1=0.4088
zh 60000
Overall, prec1=0.5066, prec2=0.3298, f1=0.3995
en 2000
Overall, prec1=0.3193, prec2=0.5027, f1=0.3905
en 4000
Overall, prec1=0.3864, prec2=0.5192, f1=0.4430
en 6000
Overall, prec1=0.4209, prec2=0.5176, f1=0.4643
en 8000
Overall, prec1=0.4433, prec2=0.5125, f1=0.4754
en 10000
Overall, prec1=0.4583, prec2=0.5056, f1=0.4808
en 12000
Overall, prec1=0.4730, prec2=0.5025, f1=0.4873
en 14000
Overall, prec1=0.4804, prec2=0.4942, f1=0.4872
en 16000
Overall, prec1=0.4885, prec2=0.4884, f1=0.4884
en 18000
Overall, prec1=0.4969, prec2=0.4853, f1=0.4911
en 20000
Overall, prec1=0.5011, prec2=0.4785, f1=0.4896
en 22000
Overall, prec1=0.4939, prec2=0.4613, f1=0.4770
en 24000
Overall, prec1=0.5037, prec2=0.4631, f1=0.4825
en 26000
Overall, prec1=0.5131, prec2=0.4643, f1=0.4875
en 28000
Overall, prec1=0.5156, prec2=0.4592, f1=0.4858
en 30000
Overall, prec1=0.5115, prec2=0.4481, f1=0.4777
en 32000
Overall, prec1=0.5043, prec2=0.4345, f1=0.4668
en 34000
Overall, prec1=0.4957, prec2=0.4199, f1=0.4546
en 36000
Overall, prec1=0.4931, prec2=0.4121, f1=0.4489
en 38000
Overall, prec1=0.4960, prec2=0.4110, f1=0.4495
en 40000
Overall, prec1=0.4958, prec2=0.4072, f1=0.4472
en 42000
Overall, prec1=0.4958, prec2=0.4036, f1=0.4450
en 44000
Overall, prec1=0.4939, prec2=0.3985, f1=0.4411
en 46000
Overall, prec1=0.4921, prec2=0.3935, f1=0.4373
en 48000
Overall, prec1=0.4897, prec2=0.3880, f1=0.4329
en 50000
Overall, prec1=0.4885, prec2=0.3835, f1=0.4297
en 52000
Overall, prec1=0.4855, prec2=0.3776, f1=0.4248
en 54000
Overall, prec1=0.4832, prec2=0.3723, f1=0.4206
en 56000
Overall, prec1=0.4798, prec2=0.3662, f1=0.4154
en 58000
Overall, prec1=0.4766, prec2=0.3604, f1=0.4104
en 60000
Overall, prec1=0.4750, prec2=0.3557, f1=0.4068"""

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

UD_RESULTS_ON_WIKI_GROUP_PPL = """en 10000
Overall, prec1=0.5269, prec2=0.5727, f1=0.5488
Overall, prec1=0.5019, prec2=0.5695, f1=0.5336
Overall, prec1=0.4699, prec2=0.5635, f1=0.5125
Overall, prec1=0.4305, prec2=0.5581, f1=0.4861
Overall, prec1=0.1999, prec2=0.4552, f1=0.2778
en 30000
Overall, prec1=0.5794, prec2=0.5339, f1=0.5558
Overall, prec1=0.5691, prec2=0.5451, f1=0.5568
Overall, prec1=0.5466, prec2=0.5546, f1=0.5506
Overall, prec1=0.5184, prec2=0.5712, f1=0.5435
Overall, prec1=0.2629, prec2=0.5087, f1=0.3467
en 60000
Overall, prec1=0.5825, prec2=0.4886, f1=0.5314
Overall, prec1=0.5819, prec2=0.5080, f1=0.5425
Overall, prec1=0.5714, prec2=0.5297, f1=0.5498
Overall, prec1=0.5564, prec2=0.5601, f1=0.5582
Overall, prec1=0.3097, prec2=0.5391, f1=0.3934
en 90000
Overall, prec1=0.5736, prec2=0.4604, f1=0.5108
Overall, prec1=0.5777, prec2=0.4827, f1=0.5260
Overall, prec1=0.5749, prec2=0.5096, f1=0.5403
Overall, prec1=0.5660, prec2=0.5458, f1=0.5557
Overall, prec1=0.3294, prec2=0.5455, f1=0.4107"""

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
        scores = []
        while idx < len(lines):
            line = lines[idx]
            if not line.startswith('Overall'):
                break
            idx += 1
            m = re.fullmatch(r"Overall, prec1=([0-9.]+), prec2=([0-9.]+), f1=([0-9.]+)", line)
            precision, recall, f1 = m.group(1), m.group(2), m.group(3)
            scores.append((precision, recall, f1))
        ret[cl][vsize] = scores
    return ret

def draw_one(one_res, title):
    vocab_sizes = sorted([v for v in one_res.keys() if ("WIKI" in title or 4000<=v<=50000)])
    for group_idx in range(len(one_res[vocab_sizes[0]])):
        precisions, recalls, f1s = [[float(one_res[v][group_idx][i]) for v in vocab_sizes] for i in range(3)]
        #
        plt.clf()
        fig, ax1 = plt.subplots(figsize=(10,6))
        if len(vocab_sizes) <= 5:
            ax1.set_xticks(vocab_sizes)
        ax1.set_title(title, fontsize=24)
        ax1.plot(vocab_sizes, precisions, "b-o", label="Precision")
        ax1.plot(vocab_sizes, recalls, "g-o", label="Recall")
        ax1.plot(vocab_sizes, f1s, "r-o", label="F1")
        ax1.grid(linestyle='--')
        ax1.set_ylabel("Score", fontsize=24)
        ax1.set_xlabel("Vocab Size", fontsize=24)
        if "UD" in title and ("Lang=ja" in title or "Lang=zh" in title):
            ax1.legend(loc='upper right', fontsize=20)
        else:
            ax1.legend(loc='lower right', fontsize=20)
        if "Lang=en" in title:
            ax1.set_ylim([0.15, 0.6])
        elif "Lang=id" in title:
            ax1.set_ylim([0.15, 0.6])
        elif "Lang=ja" in title:
            ax1.set_ylim([0.15, 0.5])
        elif "Lang=zh" in title:
            ax1.set_ylim([0.15, 0.65])
        fig.tight_layout()
        full_title = '{}_{}.pdf'.format(title, group_idx)
        plt.savefig(full_title, format="pdf")
        # plt.show()

#
def main():
    # for res_str, train_data in zip([UD_RESULTS_ON_UD, UD_RESULTS_ON_WIKI], ["UD", "WIKI"]):
    #     res = res_s2d(res_str)
    #     for cl in ["en", "id", "ja", "zh"]:
    #         draw_one(res[cl], f"Lang={cl},TrainingData={train_data}")
    for res_str, train_data in zip([UD_RESULTS_ON_WIKI_GROUP_PPL], ["WIKI_PPL"]):
        res = res_s2d(res_str)
        for cl in ["en"]:
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
