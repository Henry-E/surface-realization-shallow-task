import argparse
import os
import json

from collections import Counter

import pyconll
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument(
        '-i',
        '--input_file_names',
        nargs='*',
        help='the additional data and training data conllu files')
    args = parser.parse_args()

    print('loop over all the input files')
    all_mappings = {}
    for input_file_name in tqdm(args.input_file_names):
        with open(input_file_name) as in_file:
            num_sents = sum(1 for line in in_file if len(line.strip()) == 0)
        sents = pyconll.load.iter_from_file(input_file_name)

        for sent in tqdm(sents, total=num_sents):
            for token in sent:
                # if any of the three key pieces are missing skip the token
                if not all([token.lemma, token.xpos, token.form]):
                    continue
                xpos_lemma = '_'.join([token.xpos, token.lemma.lower()])
                if xpos_lemma in all_mappings:
                    all_mappings[xpos_lemma].update([token.form.lower()])
                else:
                    all_mappings[xpos_lemma] = Counter()
                    all_mappings[xpos_lemma].update([token.form.lower()])

    print('moving onto filtering the mapping dict')
    out_mappings = {}
    single_mapping = {}
    multiple_mappings = {}
    multiple_mappings_incl_lemma = {}
    for mapping, freqs in tqdm(all_mappings.items()):
        # on the off change there's an underscore in the lemma but
        # hopefully there's none in the xpos ever?
        lemma = '_'.join(mapping.split('_')[1:])
        # we want a min of (used to be 10) 2 occurences, in order to be included in vocab
        # And for it not to be to uncommon relative to the most common
        for form in list(freqs):
            if freqs[form] < 2:
                del freqs[form]
            # TODO decide if there's a better way to filter multiple options
            # We lowered this to 0.01 from 0.05 because of the increased
            # dataset size
            elif freqs[form] / freqs.most_common(1)[0][1] < 0.01:
                del freqs[form]
        if not freqs:
            continue
        # If there's more than one possibility we probably need to use
        # suggestions
        if len(freqs) > 1:
            out_mappings[mapping] = [form for form, _ in freqs.most_common()]
            # We're making a special output file for now so we can decide on
            # rules regarding filtering less common form suggestions
            if lemma in list(freqs):
                multiple_mappings_incl_lemma[mapping] = freqs
            else:
                multiple_mappings[mapping] = freqs
        # even if there's only 1 mapping but it's different from the lemma
        # then we also need to use this as a suggestion. We haven't decided if
        # capitalised lemmas are something we need to think about
        elif lemma not in list(freqs):
            out_mappings[mapping] = [form for form, _ in freqs.most_common()]
            single_mapping[mapping] = freqs

    output_file_name = os.path.join(args.output_dir_name,
                                    'lemma_form_dict_sorted.json')
    with open(output_file_name, 'w') as out_file:
        json.dump(out_mappings, out_file, sort_keys=True, indent=4)

    # Analysing the output forms and lemmas
    print("Single mapping: {}".format(len(single_mapping)))
    output_file_name = os.path.join(args.output_dir_name,
                                    'single_mapping.json')
    with open(output_file_name, 'w') as out_file:
        json.dump(single_mapping, out_file, sort_keys=True, indent=4)
    print("multiple_mappings_incl_lemma: {}".format(
        len(multiple_mappings_incl_lemma)))
    output_file_name = os.path.join(args.output_dir_name,
                                    'multiple_mappings_incl_lemma.json')
    with open(output_file_name, 'w') as out_file:
        json.dump(multiple_mappings_incl_lemma, out_file, sort_keys=True, indent=4)
    print("multiple_mappings: {}".format(len(multiple_mappings)))
    output_file_name = os.path.join(args.output_dir_name,
                                    'multiple_mappings.json')
    with open(output_file_name, 'w') as out_file:
        json.dump(multiple_mappings, out_file, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
