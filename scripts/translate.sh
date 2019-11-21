# Defaults
beam_size=50
n_best=50
data_dir_name=data/ewt_30_repeats/
model_file_name=train/15th_aug_tests/all_four_no_dev.trains_30_repeats_18h26m59s/msr_step_9000.pt

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -n|--n_best)
    n_best="$2"
    shift # past argument
    shift # past value
    ;;
    -b|--beam_size)
    beam_size="$2"
    shift # past argument
    shift # past value
    ;;
    -m|--model_file_name)
    model_file_name="$2"
    shift # past argument
    shift # past value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

model_root_name="$(basename "$model_file_name")"
train_dir_name="$(dirname "$model_file_name")"
train_dir="$(basename "$train_dir_name")"

translate_dir_name=translate/8th_oct_tests/"$train_dir"
mkdir -p "$translate_dir_name"

# options which are unlikely to change
time_stamp=$(date +"%Hh%Mm%Ss")
restrict_type=2

python /home/henrye/downloads/Henry_OpenNMT-py/translate.py \
    -model "$model_file_name" \
    -src "$data_dir_name"/dev.src \
    -tgt "$data_dir_name"/dev.tgt \
    -report_bleu \
    -dynamic_dict \
    -share_vocab \
    -replace_unk \
    --n_best "$n_best" \
    -batch_size 1 \
    -block_ngram_repeat "$restrict_type" \
    -beam_size "$beam_size" \
    -output "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best"."$time_stamp".pred.txt \
    -log_file "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best"."$time_stamp".log.txt \
    -gpu 0
# The beam search returns the n best so
# take only the top result from that
python /home/henrye/projects/surface_realization_shallow_task/modules/filter_hyps.py \
    -i "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best"."$time_stamp".pred.txt \
    -o "$translate_dir_name" \
    -n "$n_best" \

# Get bleu and add it to a log file
perl ~/downloads/Henry_OpenNMT-py/tools/multi-bleu.perl -lc \
"$data_dir_name"/dev.tgt \
< "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best"."$time_stamp".pred.best_hyps.txt \
>> "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best"."$time_stamp".bleu_score.txt
tail -n 1 "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best"."$time_stamp".bleu_score.txt
# Starting to gather aggregate data
echo "$model_root_name" >> "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best".aggregate.txt
cat "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best"."$time_stamp".bleu_score.txt >> "$translate_dir_name"/beam_"$beam_size".n_best_"$n_best".aggregate.txt

