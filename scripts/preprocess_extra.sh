# TODO set up for command line control of certain variables
sub_dir=extra_data_6_repeats_ewt_60_repeats
# sub_dir=ewt_30_repeats
date_dir=25th_oct_tests
data_dir_name=data/"$sub_dir"
preprocess_dir_name=preprocess/"$date_dir"/"$sub_dir"
# mkdir -p "$data_dir_name"
mkdir -p "$preprocess_dir_name"
python ~/downloads/Henry_OpenNMT-py/preprocess.py \
    -train_src "$data_dir_name"/train.src \
    -train_tgt "$data_dir_name"/train.tgt \
    -valid_src "$data_dir_name"/dev.src \
    -valid_tgt "$data_dir_name"/dev.tgt \
    -save_data "$preprocess_dir_name"/msr \
    -dynamic_dict \
    -share_vocab \
    -shard_size 125000 \
    -src_vocab ../data_processing/form_suggestions/25th_october_tests/vocab_top_95k.txt \
    -tgt_vocab ../data_processing/form_suggestions/25th_october_tests/vocab_top_95k.txt \
    -src_vocab_size 95002 \
    -tgt_vocab_size 95002 \
    -src_seq_length 150 \
    -tgt_seq_length 100

    # -src_vocab ../data_processing/form_suggestions/7th_october_tests/vocab_top_30k.txt \
    # -tgt_vocab ../data_processing/form_suggestions/7th_october_tests/vocab_top_30k.txt \
    # -src_words_min_frequency $((10*$num_repeats)) \
    # -tgt_words_min_frequency $((10*$num_repeats)) \
# for non unk it's 10 * num_repeats

# to make unks for all four msr datasets combined
# -src_words_min_frequency 35000 * num_repeats
# -tgt_words_min_frequency 35000
# The vocab size should be only 6
# '<unk>': 0, '<blank>': 1, '<s>': 2, '</s>': 3, ')_': 4, '_(': 5
