"""Set up for analysing the correlation between deprels and bleu score

It gets a count of dependency relation type per sentence and stores that in a
convenient format to run through compare-mt.

It will work when comparing any two dev set prediction files
"""
import argparse
import os

from collections import Counter

import pyconll
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_name', help='en dev set conll')
    args = parser.parse_args()

    COMMAND_TEMPLATE = 'bucket_type=label,out_labels={output_file_name};{output_file_name},label_set={label_set},statistic_type=score,score_measure=bleu,title={dep_rel}'
    NUM_SENTS=1978 # assuming dev set
    sents = pyconll.load.iter_from_file(args.input_file_name)
    dep_rels = set()
    sent_counters = []
    for sent in tqdm(sents, total=NUM_SENTS):
        these_dep_rels = []
        for token in sent:
            # if any of the key pieces are missing skip the token
            if not all([token.form, token.deprel]):
                continue
            these_dep_rels.append(token.deprel)
            dep_rels.add(token.deprel)
        sent_counters.append(Counter(these_dep_rels))

    comparemt_command = []
    for dep_rel in tqdm(dep_rels):
        this_out = []
        for sent in sent_counters:
            this_out.append(sent[dep_rel])
        output_file_name = os.path.join(args.output_dir_name,
                '{}.txt'.format(dep_rel))
        largest_freq = max(this_out)
        label_set = '+'.join([str(i) for i in range(largest_freq + 1)])
        this_command = COMMAND_TEMPLATE.format(
            output_file_name=output_file_name,
            label_set=label_set,
            dep_rel=dep_rel)
        comparemt_command.append(this_command)
        with open(output_file_name, 'w') as out_file:
            out_file.write('\n'.join(str(i) for i in this_out))
    output_file_name = os.path.join(args.output_dir_name, 'comparemt.txt')
    with open(output_file_name, 'w') as out_file:
        out_file.write("'" + "' '".join(comparemt_command) + "'")



if __name__ == '__main__':
    main()
