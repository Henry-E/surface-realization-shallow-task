import argparse
import os

from tqdm import tqdm
import pyconll
from nltk.tokenize.treebank import TreebankWordDetokenizer
from sacremoses import MosesDetokenizer


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('--gen_sents_file_name', help='')
    parser.add_argument('--conll_sents_file_name', help='')
    parser.add_argument(
        '--n_best', type=int, help='n_best option chosen in opennmt')
    parser.add_argument('--leave_tokenized', action='store_true')
    args = parser.parse_args()

    with open(args.gen_sents_file_name) as in_file:
        # A quick reminder that opennmt over generates hyps because sometimes
        # the top hyps are filtered out by the restricted decoding
        all_lines = [[]]
        num_lines = 0
        for line in in_file:
            line = line.strip()
            if line:
                all_lines[-1].append(line)
            num_lines += 1
            if args.n_best <= num_lines:
                num_lines = 0
                all_lines.append([])
        # it adds an extra list at the end even though it's finished
        del all_lines[-1]

        gen_sents = []
        for hyps in all_lines:
            gen_sent = hyps[0]
            gen_sents.append(gen_sent)
    conll_sents = pyconll.load.iter_from_file(args.conll_sents_file_name)

    ptb_detok = TreebankWordDetokenizer()
    moses_detok = MosesDetokenizer(lang='en')
    formatted_sents = []
    sent_id = 1
    for gen_sent, conll_sent in zip(gen_sents, conll_sents):
        sent_toks = gen_sent.split()
        # in dev and test sets they have lemma in the form column
        sent_lemmas = [tok.form for tok in conll_sent if tok.form]
        upper_case_lemmas = [
            lemma for lemma in sent_lemmas if any(x.isupper() for x in lemma)
        ]
        # We filter ambiguous cases where there are both upper and lower case
        # versions of words in a sentence but we won't catch them all this way
        upper_case_lemmas = [
            lemma for lemma in upper_case_lemmas
            if lemma.lower() not in sent_lemmas
        ]
        lemma_mapping = {lemma.lower(): lemma for lemma in upper_case_lemmas}
        true_case_toks = [
            lemma_mapping[tok] if tok in lemma_mapping else tok
            for tok in sent_toks
        ]
        # detokenizing makes a huge difference to scoring

        # Tested out doing ptb first but it's not as good
        # sent_tc_detok = ptb_detok.detokenize(true_case_toks)
        # sent_tc_detok = ' '.join(
        #     [tok.replace('-', '@-@') for tok in sent_tc_detok.split()])
        # sent_tc_detok = moses_detok.detokenize(sent_tc_detok.split())
        # sent_tc_detok = ' '.join(
        #     [tok.replace('@-@', '-') for tok in sent_tc_detok.split()])

        if args.leave_tokenized:
            sent_tc_tok = ' '.join(true_case_toks)
            this_sent = '# sent_id = {}\n# text = {}'.format(
                sent_id, sent_tc_tok)
        else:
            true_case_toks = [tok.replace('-', '@-@') for tok in true_case_toks]
            sent_tc_detok = moses_detok.detokenize(true_case_toks)
            sent_tc_detok = ptb_detok.detokenize(sent_tc_detok.split())
            sent_tc_detok = ' '.join(
                [tok.replace('@-@', '-') for tok in sent_tc_detok.split()])

            sent_tc_detok = sent_tc_detok[0].upper() + sent_tc_detok[1:]
            this_sent = '# sent_id = {}\n# text = {}'.format(
                sent_id, sent_tc_detok)
        formatted_sents.append(this_sent)
        sent_id += 1

    output_file_name = os.path.join(args.output_dir_name, 'en_out.txt')
    with open(output_file_name, 'w') as out_file:
        out_file.write('\n\n'.join(formatted_sents))
# TODO probably output a file without the formatting or detok for separate
# evaluation


if __name__ == '__main__':
    main()
