# /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/ewt_lines_test_set_14-Oct_09-51
# /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/augmented_and_ewt_test_set_13-Oct_11-23
# /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/augmented_lines_test_set_14-Oct_09-52
# /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/ewt_only_test_set_13-Oct_11-19

# /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_only_test_set_13-Oct_11-27_tokenized
# /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_and_ewt_test_set_13-Oct_12-07_tokenized
# /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_lines_test_set_14-Oct_10-03_tokenized
# /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_lines_test_set_14-Oct_10-44_tokenized


# EWT only Test set

mkdir /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_only_test_set_13-Oct_11-27_tokenized
python /home/henrye/projects/surface-realization-shallow-task/modules/format.py --conll_sents_file_name /home/henrye/projects/surface-realization-shallow-task/data/srst_2020/ewt_source/en_ewt-ud-test.conllu --gen_sents_file_name /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/ewt_only_test_set_13-Oct_11-19/sr.pred.txt -o /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_only_test_set_13-Oct_11-27_tokenized --n_best 50 --leave_tokenized

# Augmented Test set

mkdir /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_and_ewt_test_set_13-Oct_12-07_tokenized
python /home/henrye/projects/surface-realization-shallow-task/modules/format.py --conll_sents_file_name /home/henrye/projects/surface-realization-shallow-task/data/srst_2020/ewt_source/en_ewt-ud-test.conllu --gen_sents_file_name /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/augmented_and_ewt_test_set_13-Oct_11-23/sr.pred.txt -o /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_and_ewt_test_set_13-Oct_12-07_tokenized --n_best 50 --leave_tokenized

# EWT Lines test set

mkdir /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_lines_test_set_14-Oct_10-03_tokenized
python /home/henrye/projects/surface-realization-shallow-task/modules/format.py --conll_sents_file_name /home/henrye/projects/surface-realization-shallow-task/data/srst_2020/lines_test_set/en_filtered_lines-fix.conllu --gen_sents_file_name /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/ewt_lines_test_set_14-Oct_09-51/sr.pred.txt -o /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_lines_test_set_14-Oct_10-03_tokenized --n_best 50 --leave_tokenized


# Augment Lines test set

mkdir /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_lines_test_set_14-Oct_10-44_tokenized
python /home/henrye/projects/surface-realization-shallow-task/modules/format.py --conll_sents_file_name /home/henrye/projects/surface-realization-shallow-task/data/srst_2020/lines_test_set/en_filtered_lines-fix.conllu --gen_sents_file_name /home/henrye/projects/surface-realization-shallow-task/experiments/translate/srst_2020/augmented_lines_test_set_14-Oct_09-52/sr.pred.txt -o /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_lines_test_set_14-Oct_10-44_tokenized --n_best 50 --leave_tokenized


echo /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_only_test_set_13-Oct_11-27_tokenized/en_out.txt
echo /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_and_ewt_test_set_13-Oct_12-07_tokenized/en_out.txt
echo /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/ewt_lines_test_set_14-Oct_10-03_tokenized/en_out.txt
echo /home/henrye/projects/surface-realization-shallow-task/experiments/format/srst_2020/augmented_lines_test_set_14-Oct_10-44_tokenized/en_out.txt
