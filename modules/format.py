import argparse
import os

import nltk.translate.bleu_score as bs
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_name', help='')
    parser.add_argument('-n',
                        '--n_best',
                        type=int,
                        help='n_best option chosen in opennmt')
    parser.add_argument('--best_bleu',
                        action='store_true',
                        help='choose hyp with best bleu')
    parser.add_argument(
        '--refs_file_name',
        default=
        '/home/henrye/projects/surface_realization_shallow_task/experiments/tokenization_tests_18th_april/reference_texts/dev_ref.txt.tok'
    )
    args = parser.parse_args()

    chencherry = bs.SmoothingFunction()

    with open(args.input_file_name) as in_file:
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
        del(all_lines[-1])
    num_biger_bleu = 0
    if args.best_bleu:
        with open(args.refs_file_name) as in_file:
            refs = [line.strip() for line in in_file]
        best_hyps = []
        best_bleu_scores = []
        for i, hyps in enumerate(tqdm(all_lines, smoothing=0.1)):
            bleu_scores = []
            for hyp in hyps:
                this_bleu = bs.sentence_bleu(
                    [refs[i]], hyp, smoothing_function=chencherry.method2)
                bleu_scores.append(this_bleu)
            best_hyp = [
                hyp for _, hyp in sorted(zip(bleu_scores, hyps), reverse=True)
            ][0]
            # counting how many sentences have a better bleu scoring choice
            if best_hyp != hyps[0]:
                num_biger_bleu += 1
            best_bleu_scores.append(str(max(bleu_scores)))
            best_hyps.append(best_hyp)
    else:
        num_empty_hyps = 0
        best_hyps = []
        for hyps in all_lines:
            if hyps:
                best_hyp = hyps[0]
            else:
                best_hyp = ''
                num_empty_hyps += 1
            best_hyps.append(best_hyp)
        print(len(best_hyps))
        print('failed hyps: {}'.format(num_empty_hyps))
    print('num with a better bleu score than first option {}'.format(num_biger_bleu))

    input_file_root = os.path.basename(
        os.path.splitext(args.input_file_name)[0])
    output_file_name = os.path.join(args.output_dir_name,
                                    input_file_root + '.best_hyps.txt')
    print('output_file_name: \n{}'.format(output_file_name))
    with open(output_file_name, 'w') as out_file:
        out_file.write('\n'.join(best_hyps))
    if args.best_bleu:
        output_file_name = os.path.join(args.output_dir_name,
                                        input_file_root + '.top_bleu_scores.txt')
        print('bleu_scores_file_name: \n{}'.format(output_file_name))
        with open(output_file_name, 'w') as out_file:
            out_file.write('\n'.join(best_bleu_scores))


if __name__ == '__main__':
    main()
