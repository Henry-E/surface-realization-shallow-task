import argparse
import os
import json
import re

from random import shuffle

import pyconll
from pyconll.tree import SentenceTree
from tqdm import tqdm


def linearize_tree(node, scopes_to_close=0):
    linearization = []
    # I don't think it matters whether this is checking form for synthetic or
    # srst data
    if node.data.form:
        linearization.append(str(node.data.id))
    child_nodes = [child for child in node.children if child.data.form]
    # We're always shuffling nodes these days, even though sentence order is
    # very helpful
    shuffle(child_nodes)
    # We're opening a scope if there is any amount of child nodes
    if child_nodes:
        linearization.append('_(')
    else:
        # no more children so close whatever scopes are open
        linearization.extend([')_'] * scopes_to_close)
    for k, child in enumerate(child_nodes):
        # if it's the last child
        if k == len(child_nodes) - 1:
            scopes_to_close += 1
            linearization.extend(linearize_tree(child, scopes_to_close))
        else:
            linearization.extend(linearize_tree(child))
    return linearization


def get_mapping(linearized_ids):
    new_id = 1
    id_mapping = {'0': '0'}
    for tok_id in linearized_ids:
        if tok_id in ['_(', ')_']:
            continue
        id_mapping[tok_id] = str(new_id)
        new_id += 1
    return id_mapping


def get_tokens_with_feats(sent, data_type, form_suggestions=None):
    # feats = ['xpos', 'id', 'head', 'deprel', 'feats']
    feats = ['xpos', 'id', 'head', 'deprel',]
    num_feats = len(feats)
    this_tree = SentenceTree(sent).tree
    linearized_ids = linearize_tree(this_tree)
    id_mapping = get_mapping(linearized_ids)
    toks_with_feats = []
    these_form_suggestions = []
    for tok_id in linearized_ids:
        this_tok_with_feats = []
        if tok_id in ['_(', ')_']:
            this_tok_with_feats.append(tok_id)
            this_tok_with_feats.extend(['_'] * num_feats)
            toks_with_feats.append('￨'.join(this_tok_with_feats))
            continue
        if data_type in ['train', 'dev', 'test']:
            # the srst data has the lemma in the form column
            this_lemma = sent[tok_id].form
        else:
            this_lemma = sent[tok_id].lemma
        if not this_lemma:
            continue
        this_lemma = this_lemma.lower()
        # We have to get rid of non-breaking white spaces
        this_lemma = re.sub(r'\s', '', this_lemma)
        this_tok_with_feats.append(this_lemma)
        for feat in feats:
            feat_value = getattr(sent[tok_id], feat)
            # Sometimes feats are None type
            if feat_value:
                if feat in ['id', 'head']:
                    out_feat = id_mapping[feat_value]
                elif feat in ['feats']:
                    if 'lin' in feat_value:
                        out_feat = feat_value['lin'].pop()
                    else:
                        out_feat = '_'
                else:
                    out_feat = feat_value
            else:
                out_feat = '_'
            this_tok_with_feats.append(out_feat)
        toks_with_feats.append('￨'.join(this_tok_with_feats))
        if not form_suggestions:
            continue
        this_xpos = sent[tok_id].xpos
        if not this_xpos:
            continue
        lemma_xpos = '_'.join([this_xpos, this_lemma])
        if not lemma_xpos in form_suggestions:
            continue
        # If there's only one suggestion we're going to directly substitute it
        # following what we think appeared in the ims paper. It makes sense
        if len(form_suggestions[lemma_xpos]) == 1:
            this_form = form_suggestions[lemma_xpos][0]
            this_form = re.sub(r'\s', '', this_form)
            toks_with_feats[-1] = toks_with_feats[-1].replace(this_lemma, this_form)
            continue
        for this_form in form_suggestions[lemma_xpos]:
            # We're not adding the original lemma as a suggestion, this is
            # because we feel like it would add to much weight to it. But we're
            # not entirely sure how this might confuse the network, since it
            # doesn't always have to use the suggestion
            if this_form in [this_lemma]:
                continue
            this_form = re.sub(r'\s', '', this_form)
            this_form_with_feats = [this_form]
            this_form_with_feats.append(this_xpos)
            this_form_with_feats.append(id_mapping[tok_id])
            this_form_with_feats.extend(['_'] * (num_feats - 2))
            these_form_suggestions.append('￨'.join(this_form_with_feats))
    out_string = ' '.join(toks_with_feats)
    if these_form_suggestions:
        delimiter = ['_form_suggestions_']
        delimiter.extend(['_'] * num_feats)
        these_form_suggestions.insert(0, '￨'.join(delimiter))
        out_string += ' ' + ' '.join(these_form_suggestions)
    return out_string


def get_tokenized_sent(sent):
    """Constructs string of sentence tokens."""
    sent_tokens = []
    for token in sent:
        if any([token.form]):
            this_form = token.form.lower()
            this_form = re.sub(r'\s', '', this_form)
            sent_tokens.append(this_form)
    return ' '.join(sent_tokens)


def create_source_and_target(args, dataset_split, input_file_names):
    form_suggestions = {}
    if args.form_suggestions_file_name:
        with open(args.form_suggestions_file_name) as in_file:
            form_suggestions = json.load(in_file)
    source_file_name = os.path.join(args.output_dir_name,
                                    dataset_split + '.src')
    open(source_file_name, 'w').close()
    if dataset_split not in ['test']:
        target_file_name = os.path.join(args.output_dir_name,
                                        dataset_split + '.tgt')
        open(target_file_name, 'w').close()

    for data_type, input_file_name in tqdm(input_file_names, smoothing=0):
        if data_type in ['synthetic']:
            input_file_match = re.match(r'.*/(.*)_filtered.conllu',
                                        input_file_name)
            input_file_root = input_file_match.group(1)
            # if synthetic data we just keep everything the same
            source_conllu_file_name = input_file_name
            target_conllu_file_name = input_file_name
        elif data_type in ['test']:
            input_file_root = data_type
            source_conllu_file_name = os.path.join(args.test_conllu_dir_name,
                                                   input_file_name)
            target_conllu_file_name = os.path.join(args.test_conllu_dir_name,
                                                   input_file_name)
        else:
            input_file_root = data_type
            source_conllu_file_name = os.path.join(args.source_conllu_dir_name,
                                                   input_file_name)
            target_conllu_file_name = os.path.join(args.target_conllu_dir_name,
                                                   input_file_name)
        with open(source_conllu_file_name) as in_file:
            num_sents = sum(1 for line in in_file if len(line.strip()) == 0)
        source_sents = pyconll.load.iter_from_file(source_conllu_file_name)
        target_sents = pyconll.load.iter_from_file(target_conllu_file_name)
        sources = []
        targets = []
        num_sents_so_far = 0
        for source_sent, target_sent in tqdm(zip(source_sents, target_sents),
                                             total=num_sents,
                                             smoothing=0.01,
                                             desc=input_file_root):
            try:
                # # TODO very messy temporary code to test out adding a domain
                # # token to the src sequence. To see if it will improve training
                # # with ukwac
                # if input_file_root == 'dev':
                #     base_source = get_tokens_with_feats(source_sent, data_type, form_suggestions)
                #     this_source = '__train__' + '￨_￨_￨_￨_ ' + base_source
                # else:
                #     base_source = get_tokens_with_feats(source_sent, data_type, form_suggestions)
                #     this_source = '__' + input_file_root + '__' + '￨_￨_￨_￨_ ' + base_source
                # sources.append(this_source)
                sources.append(
                    get_tokens_with_feats(source_sent, data_type, form_suggestions))
                if dataset_split not in ['test']:
                    targets.append(get_tokenized_sent(target_sent))
                # It slows down if the list gets too large
                num_sents_so_far += 1
                if num_sents_so_far > 100000:
                    with open(source_file_name, 'a') as out_file:
                        out_file.write('\n'.join(sources) + '\n')
                    if dataset_split not in ['test']:
                        with open(target_file_name, 'a') as out_file:
                            out_file.write('\n'.join(targets) + '\n')
                    sources = []
                    targets = []
                    num_sents_so_far = 0
            except:
                print('Ran into one of those random _ underscore errors')
        with open(source_file_name, 'a') as out_file:
            out_file.write('\n'.join(sources) + '\n')
        if dataset_split not in ['test']:
            with open(target_file_name, 'a') as out_file:
                out_file.write('\n'.join(targets) + '\n')


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument(
        '-i',
        '--input_file_names',
        nargs='*',
        help='all of the synthetic, train, dev and test files')
    parser.add_argument('--form_suggestions_file_name',
                        type=str,
                        default='',
                        help='form suggestions dictionary in json format')
    parser.add_argument('--source_conllu_dir_name',
                        default='/home/henrye/projects/surface-realization-shallow-task/data/srst/en_source',
                        help='folder with source conllu, hardcodedish')
    parser.add_argument('--target_conllu_dir_name',
                        default='/home/henrye/projects/surface-realization-shallow-task/data/srst/en_target',
                        help='folder with target conllu, hardcodedish')
    parser.add_argument('--test_conllu_dir_name',
                        default='/home/henrye/data/msr_2019/T1-test_en')
    parser.add_argument('--eval_set_repeats',
                        type=int,
                        default=1,
                        help='num repeats of dev or test set')
    parser.add_argument('--train_set_repeats',
                        type=int,
                        default=1,
                        help='repeat srst train set')
    parser.add_argument('--synthetic_data_repeats',
                        type=int,
                        default=0,
                        help='repeat synthetic datasets')
    args = parser.parse_args()

    dataset_split_file_names = {'train':[], 'dev':[], 'test':[]}
    for input_file_name in args.input_file_names:
        # Have to remember to use a trailing comma after tuple to be able to
        # repeat it https://stackoverflow.com/a/19753291/4507677
        if re.match(r'.*test.conll', input_file_name):
            dataset_split_file_names['test'].extend(
                (('test', input_file_name), ) * args.eval_set_repeats)
        elif re.match(r'.*dev.conll', input_file_name):
            dataset_split_file_names['dev'].extend(
                (('dev', input_file_name), ) * args.eval_set_repeats)
        elif re.match(r'.*train.conll', input_file_name):
            dataset_split_file_names['train'].extend(
                (('train', input_file_name), ) * args.train_set_repeats)
        elif re.match(r'.*filtered.conllu', input_file_name):
            dataset_split_file_names['train'].extend(
                (('synthetic', input_file_name), ) * args.synthetic_data_repeats)

    for dataset_split, input_file_names in dataset_split_file_names.items():
        if not input_file_names:
            continue
        # We mostly shuffle for the benefit of the training data files
        shuffle(input_file_names)
        create_source_and_target(args, dataset_split, input_file_names)


if __name__ == '__main__':
    main()
