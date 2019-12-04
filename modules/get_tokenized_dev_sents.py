"""A module to convert a conll file into a set of tokenized sents

This is mainly for use with the dev set, make sure to use the target conll
file
"""
import argparse
import os

import pyconll

def main():
    """Loop over conll file and get form tokens, then write to file!

    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_name', help='')
    args = parser.parse_args()

    output_file_name = os.path.join(args.output_dir_name, 'sr.ref.txt')
    sents = pyconll.load.iter_from_file(args.input_file_name)

    sents_out = []
    for sent in sents:
        this_sent_out = []
        for token in sent:
            if token.form:
                this_sent_out.append(token.form)
        sents_out.append(' '.join(this_sent_out))

    with open(output_file_name, 'w') as out_file:
        out_file.write('\n'.join(sents_out))

if __name__ == '__main__':
    main()
