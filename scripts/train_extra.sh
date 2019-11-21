# TODO set up for command line control of certain variables
sub_dir=extra_data_6_repeats_ewt_60_repeats
date_dir=20th_oct_tests
time_stamp=$(date +"%Hh%Mm%Ss")
preprocess_dir_name=preprocess/"$date_dir"/"$sub_dir"
new_date_dir=5th_nov_tests
train_dir_name=train/"$new_date_dir"/"$sub_dir"_"$time_stamp"
tensorboard_log_dir=tensorboard_runs/"$new_date_dir"/"$sub_dir"_"$time_stamp"
world_size=2
mkdir -p "$train_dir_name"
mkdir -p "$tensorboard_log_dir"
python /home/henrye/downloads/Henry_OpenNMT-py/train.py \
    -data "$preprocess_dir_name"/msr \
    -save_model "$train_dir_name"/msr \
    --log_file "$train_dir_name"/msr.log.txt \
    --optim adam \
    --learning_rate 0.001 \
    --encoder_type brnn \
    --layers 2 \
    --batch_size 32 \
    --word_vec_size 300 \
    --rnn_size 900 \
    --share_embeddings \
    --copy_attn \
    --copy_attn_force \
    --report_every $((1000/$world_size)) \
    --valid_steps $((1000/$world_size)) \
    --save_checkpoint $((10000/$world_size))  \
    --train_steps $((850000/$world_size)) \
    --start_decay_steps $((600000/$world_size)) \
    --decay_steps $((50000/$world_size)) \
    --gpu_ranks 0 1 \
    --world_size "$world_size" \
    --tensorboard \
    --tensorboard_log_dir "$tensorboard_log_dir"
    # --gpu_ranks 0 1 \
