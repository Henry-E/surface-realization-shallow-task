import argparse
import os

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
    parser.add_argument('-m', '--min_freq', type=int, default=8)
    parser.add_argument(
        '--max_vocab_size',
        type=int,
        default=100000,
        help='setting max vocab generally to be 100,000')
    args = parser.parse_args()

    print('loop over all the input files')
    vocab = Counter()
    for input_file_name in tqdm(args.input_file_names):
        with open(input_file_name) as in_file:
            num_sents = sum(1 for line in in_file if len(line.strip()) == 0)
        sents = pyconll.load.iter_from_file(input_file_name)

        for sent in tqdm(sents, total=num_sents):
            for token in sent:
                # if any of the three key pieces are missing skip the token
                if not all([token.lemma, token.xpos, token.form]):
                    continue
                vocab.update([token.form.lower()])
                # This is a new feature, where we will try to add common
                # lemmas to the vocab
                if token.lemma.lower() != token.form.lower():
                    vocab.update([token.lemma.lower()])

    # min freq
    out_vocab = [
            token for token, freq in vocab.most_common()
            if freq > args.min_freq
        ]
    # special tokens for trees 
    out_vocab = ['_(', ')_'] + out_vocab
    # limit the size 
    out_vocab = out_vocab[:args.max_vocab_size]
    output_file_name = os.path.join(args.output_dir_name,
                                    'vocab_min_{}.txt'.format(str(args.min_freq)))
    with open(output_file_name, 'w') as out_file:
        out_file.write('\n'.join(out_vocab))
    print(output_file_name, '\nvocab size {}'.format(len(out_vocab)))


if __name__ == '__main__':
    main()
