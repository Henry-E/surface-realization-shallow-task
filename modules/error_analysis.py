"""

"""
import argparse
import os
import string
import csv
import json
import copy
from collections import Counter

import pyconll


def compare_and_label(refs, preds, labels, this_label):
    """Loop over and compare refs and preds, label any that match

    The intention behind this is that all the changes that may be made to refs
    or preds should be done before coming into this function. So the inflection
    substitution and the punctuation removal, all happen in their own functions

    Args:
        refs: A list of lists of tokens

    Returns:
    """
    for idx, (ref, pred, label) in enumerate(zip(refs, preds, labels)):
        if label:
            continue
        if ref == pred:
            labels[idx] = this_label

    return labels


def remove_punctuation(sents):
    out_sents = []
    for sent in sents:
        this_sent = []
        for tok in sent:
            if tok in string.punctuation:
                continue
            this_sent.append(tok)
        out_sents.append(this_sent)
    return out_sents


def remove_inflection_errors(args, preds, labels):
    """Find and replace inflection errors

    It's kind of a rough approach to this, there will be edge cases that slip
    through, for instance lemma_pos pairs that don't exist in the dictionary.
    """
    with open(args.inflection_dict_file_name) as in_file:
        inflection_dict = json.load(in_file)
    refs = pyconll.load.iter_from_file(args.dev_conll_file_name)

    preds_inflected = copy.deepcopy(preds)
    preds_errors = [None] * len(preds)
    refs_lookup = [[] for i in range(len(preds))]
    for sent_idx, (ref, pred, label) in enumerate(zip(refs, preds, labels)):
        if label:
            continue
        # be careful with copy errors
        preds_errors[sent_idx] = pred[:]
        # if sent_idx == 17:
        #     import ipdb; ipdb.set_trace()
        for token in ref:
            if not all([token.lemma, token.xpos, token.form]):
                continue
            # Loop over all pred tokens and if the form isn't found there then
            # add it to refs lookup for use later
            for tok_idx, p_tok in enumerate(preds_errors[sent_idx]):
                if p_tok == token.form.lower():
                    preds_errors[sent_idx][tok_idx] = ''
                    break
            else:
                refs_lookup[sent_idx].append(token)

    for sent_idx, (ref_lookup, pred_errors) in enumerate(
            zip(refs_lookup, preds_errors)):
        if not ref_lookup:
            continue
        for token in ref_lookup:
            xpos_lemma = '_'.join([token.xpos, token.lemma.lower()])
            these_inflections = inflection_dict.get(xpos_lemma)
            # There may not be a xpos_lemma key for everything
            if not these_inflections:
                continue
            for tok_idx, p_tok in enumerate(pred_errors):
                if not p_tok:
                    continue
                if p_tok in these_inflections:
                    preds_inflected[sent_idx][tok_idx] = token.form.lower()
                # TODO in future iterations we could track which missing
                # inflection don't get corrected during this loop
    return preds_inflected


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('--ref_file_name', help='')
    parser.add_argument('--pred_file_name', help='')
    parser.add_argument('--inflection_dict_file_name', help='inflection dict used')
    parser.add_argument('--dev_conll_file_name', help='target dev conll file, with forms')
    args = parser.parse_args()

    with open(args.ref_file_name) as in_file:
        refs = [line.strip().split() for line in in_file]
    with open(args.pred_file_name) as in_file:
        preds = [line.strip().split() for line in in_file]

    num_preds = len(preds)
    assert len(refs) == num_preds, "refs and preds need to be the same length"
    labels = [None] * num_preds

    labels = compare_and_label(refs, preds, labels, this_label="exact_match")
    preds_no_punct = remove_punctuation(preds)
    refs_no_punct = remove_punctuation(refs)
    labels = compare_and_label(
        refs_no_punct, preds_no_punct, labels, this_label="punct_only")
    preds_correct_inflection = remove_inflection_errors(args, preds, labels)
    labels = compare_and_label(
        refs, preds_correct_inflection, labels, this_label="inflection_only")
    preds_no_punct_correct_inflection = remove_punctuation(preds_correct_inflection)
    labels = compare_and_label(
        refs,
        preds_no_punct_correct_inflection,
        labels,
        this_label="punct_and_inflection_only")
    final_label_count = Counter(labels)
    print(final_label_count)

    output_file_name = os.path.join(args.output_dir_name,
                                    "ref_pred_labels.tsv")
    with open(output_file_name, 'w') as out_file:
        csv_writer = csv.writer(out_file, delimiter='\t')
        header = ['refs', 'preds', 'labels']
        csv_writer.writerow(header)
        for ref, pred, label in zip(refs, preds, labels):
            csv_writer.writerow([' '.join(ref), ' '.join(pred), label])


if __name__ == '__main__':
    main()
