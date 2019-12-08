"""A module to convert the output of translate for use with compare-mt

Translate includes the n best hyps, so all but the top 1 need to be discarded
"""
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', '--input_file_names', nargs='*', help='')
    args = parser.parse_args()

    NUM_DEV_SENTS = 1978
    for input_file_name in args.input_file_names:
        print(input_file_name)
        with open(input_file_name) as in_file:
            lines = [line for line in in_file]
        n_best = len(lines) / NUM_DEV_SENTS
        all_lines = [[]]
        num_lines = 0
        for line in lines:
            line = line.strip()
            if line:
                all_lines[-1].append(line)
            num_lines += 1
            if n_best <= num_lines:
                num_lines = 0
                all_lines.append([])
        # it adds an extra list at the end even though it's finished
        del all_lines[-1]

        out_lines = []
        for hyps in all_lines:
            out_lines.append(hyps[0])

        output_dir_name = os.path.dirname(input_file_name)
        output_file_name = os.path.join(output_dir_name, 'sr.pred.top1.txt')
        print(output_file_name)
        with open(output_file_name, 'w') as out_file:
            out_file.write('\n'.join(out_lines))


if __name__ == '__main__':
    main()
