for json in configs/ablation_analysis/sr*
do
    echo "$json"
    python modules/parse_config.py -i "$json"
done
