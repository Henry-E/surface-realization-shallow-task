import argparse
import os
import json
import subprocess
import pathlib
import csv
from datetime import datetime
from subprocess import PIPE



def datetime_stamp():
    now = datetime.now()
    return now.strftime("%d-%b_%H-%M")


def get_run_name(args):
    """Returns a run name and moves that name to end of the file

    """
    run_names_file_name = os.path.join(args.root_dir_name,
                                       args.run_names_file_name)
    with open(run_names_file_name, 'r') as in_file:
        names = [line.strip() for line in in_file]
    out_name = names[0]
    with open(run_names_file_name, 'w') as out_file:
        out_file.write('\n'.join(names[1:] + names[0:1]))
    return out_name


def save_updated_config(commands, experiment_info, action, command):
    """Take all the updated info and save the config

    """
    # Not sure about this since it will update commands var everywhere
    commands['experiment_info'].update(experiment_info)
    if command[0] in ['python']:
        debug_command = command[0:1] + ['-m', 'ipdb'] + command[1:]
        commands[action + '_debug'] = ' '.join(debug_command)
    with open(experiment_info['this_run_config_file'], 'w') as out_file:
        json.dump(commands, out_file, indent=4)


def initialize_experiment(args):
    """Load config and init any required variables

    """
    # Information that is either passed in via a config or created during the run
    EXPERIMENT_INFO = [
        'exp_type',
        'available_actions',
        'actions_to_take',
        'run_name',
        'last_run_datetime',
        'this_run_config_file',
        'root_dir',
        'opennmt_dir',
        'src_and_tgt_sub_dir',
        'preprocess_sub_dir',
        'train_sub_dir',
        'best_model_file',
        'tensorboard_sub_dir',
        'translate_sub_dir',
        'format_sub_dir',
        'eval_sub_dir',
    ]
    experiment_info = dict.fromkeys(EXPERIMENT_INFO)
    experiment_info['root_dir'] = args.root_dir_name
    experiment_info['opennmt_dir'] = args.opennmt_dir_name


    with open(args.input_file_name) as in_file:
        commands = json.load(in_file)
    # Import the default values
    experiment_info.update(commands['experiment_info'])
    experiment_info['last_run_datetime'] = datetime_stamp()
    if not experiment_info['run_name']:
        experiment_info['run_name'] = get_run_name(args)
    if not experiment_info['this_run_config_file']:
        file_name = '{root_dir}/configs/{exp_type}/{run_name}_{last_run_datetime}.json'.format(
            **experiment_info)
        experiment_info['this_run_config_file'] = file_name
        dir_name = os.path.dirname(file_name)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)
    return commands, experiment_info


def mk_missing_dirs(experiment_info, action):
    """Create the dir if none exists

    """
    # TODO figure out a way to make the path creation cleaner & clearer
    sub_dir = experiment_info['run_name'] + '_' + datetime_stamp()
    this_path = ''
    if action == 'src_and_tgt' and not experiment_info['src_and_tgt_sub_dir']:
        experiment_info['src_and_tgt_sub_dir'] = sub_dir
        this_path = '{root_dir}/experiments/src_and_tgt/{exp_type}/{src_and_tgt_sub_dir}'.format(
            **experiment_info)
        pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
    elif action == 'preprocess' and not experiment_info['preprocess_sub_dir']:
        experiment_info['preprocess_sub_dir'] = sub_dir
        this_path = '{root_dir}/experiments/preprocess/{exp_type}/{preprocess_sub_dir}'.format(
            **experiment_info)
        pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
    elif action == 'train' and not experiment_info['train_sub_dir']:
        experiment_info['train_sub_dir'] = sub_dir
        this_path = '{root_dir}/experiments/train/{exp_type}/{train_sub_dir}'.format(
            **experiment_info)
        pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
        # Also make a tensorboard directory
        experiment_info['tensorboard_sub_dir'] = sub_dir
        this_path = '{root_dir}/experiments/tensorboard/{exp_type}/{tensorboard_sub_dir}'.format(
            **experiment_info)
        pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
    # Translate is special, even if subdir already exists we make a new one
    elif action == 'translate':
        experiment_info['translate_sub_dir'] = sub_dir
        this_path = '{root_dir}/experiments/translate/{exp_type}/{translate_sub_dir}'.format(
            **experiment_info)
        pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
        # Specify best model file manually or take file with the top accuracy
        if not experiment_info['best_model_file']:
            model_files = os.listdir(
                '{root_dir}/experiments/train/{exp_type}/{train_sub_dir}'.
                format(**experiment_info))
            best_model_file = sorted(model_files)[-1]
            experiment_info['best_model_file'] = best_model_file
    elif action == 'format':
        experiment_info['format_sub_dir'] = sub_dir
        this_path = '{root_dir}/experiments/format/{exp_type}/{format_sub_dir}'.format(
            **experiment_info)
        pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
    elif action == 'eval':
        this_path = '{root_dir}/experiments/eval/{exp_type}'.format(
            **experiment_info)
        pathlib.Path(this_path).mkdir(parents=True, exist_ok=True)
    if this_path:
        print(this_path)
    return experiment_info


def save_eval_to_csv(command, experiment_info):
    """Update an eval file across the experiment type

    We do this special stuff instead of editing the eval python module directly
    """
    results = subprocess.run(command, stdout=PIPE)
    print(results.stdout.decode())
    results = results.stdout.decode()
    results = [this.split() for this in results.splitlines() if this]
    results = {k: v for k, v in results}
    results.update(experiment_info)
    results_file_name = '{root_dir}/experiments/eval/{exp_type}/results.csv'.format(
        **experiment_info)
    fieldnames = ['BLEU', 'DIST', 'NIST', 'run_name', 'last_run_datetime']
    these_values = {this: results[this] for this in fieldnames}
    results_csv = []
    try:
        with open(results_file_name, 'r') as csv_in:
            csv_reader = csv.DictReader(csv_in)
            for line in csv_reader:
                results_csv.append(line)
    except:
        pass

    with open(results_file_name, 'w') as csv_out:
        results_csv.append(these_values)
        csv_writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        csv_writer.writeheader()
        for line in results_csv:
            csv_writer.writerow(line)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-o', '--output_dir_name', help='Where to save updated configs')
    parser.add_argument('-i', '--input_file_name', help='JSON config file')
    parser.add_argument(
        '-r',
        '--root_dir_name',
        help='',
        default='/home/henrye/projects/surface-realization-shallow-task')
    parser.add_argument(
        '--opennmt_dir_name',
        help='location of custom opennmt-py fork',
        default='/home/henrye/downloads/henrye_OpenNMT-py')
    parser.add_argument('--run_names_file_name', default='configs/run_names.txt')
    args = parser.parse_args()

    commands, experiment_info = initialize_experiment(args)

    print('performing actions:\n', experiment_info['actions_to_take'])
    for action in experiment_info['actions_to_take']:
        if action not in commands:
            print('skipping unavailable action: {}'.format(action))
            continue
        print('Doing action: {}'.format(action))
        experiment_info = mk_missing_dirs(experiment_info, action)
        command = commands[action]
        command = [this.format(**experiment_info) for this in command]
        save_updated_config(commands, experiment_info, action, command)
        if action in ['eval']:
            save_eval_to_csv(command, experiment_info)
        elif action in ['shuffle']:
            subprocess.run(command[0], shell=True)
        else:
            subprocess.run(command)


if __name__ == '__main__':
    main()
