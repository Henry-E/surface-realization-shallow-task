import argparse
import os
from collections import Counter, defaultdict

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-o', '--output_dir_name', help='output directory')
    parser.add_argument('-i', '--input_file_names', nargs='*', help='')
    args = parser.parse_args()

    all_sents = defaultdict(Counter)
    for input_file_name in args.input_file_names:
        with open(input_file_name) as in_file:
            for line in in_file:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('# sent_id'):
                    sent_id = int(line.split('# sent_id = ')[1])
                    continue
                if line.startswith('# text'):
                    sent = line.split('# text = ')[1]
                    all_sents[sent_id].update([sent])

    formatted_sents = []
    for sent_id in range(1, len(all_sents)+1):
        sent = all_sents[sent_id].most_common(1)[0][0]
        this_sent = '# sent_id = {}\n# text = {}'.format(
            sent_id, sent)
        formatted_sents.append(this_sent)

    output_file_name = os.path.join(args.output_dir_name, 'en_out.txt')
    with open(output_file_name, 'w') as out_file:
        out_file.write('\n\n'.join(formatted_sents))

if __name__ == '__main__':
    main()
