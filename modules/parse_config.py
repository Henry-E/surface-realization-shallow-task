import argparse
import os
import json
import subprocess

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
    args = parser.parse_args()

    required_experiment_info = [
        'exp_type',
        'run_name',
        'root_dir',
        'create_src_tgt_sub_dir',
        'preprocess_sub_dir',
        'train_sub_dir',
    ]
    experiment_info = dict.fromkeys(required_experiment_info)
    experiment_info['root_dir'] = args.root_dir_name

    # with open(os.path.join(args.root_dir_name, 'configs/saved.json'), 'w') as out_file:
    #     json.dump([['heheh', 'heheh'], ['e','eeh']], out_file, indent=4)
    with open(args.input_file_name) as in_file:
        commands = json.load(in_file)
    # Get the default dir names
    experiment_info.update(commands['experiment_info'])

    ACTIONS = ['create_source_and_target', 'preprocess']
    print('performing actions:\n', ACTIONS)
    for action in ACTIONS:
        if action not in commands:
            print('skipping action: {}'.format(action))
            continue
        # TODO there has to be a better way to do this boiler plate stuff.
        # possibly just put it in a function? In a function that returns the
        # updated experiment_info dict seems for the best 
        if action == 'create_source_and_target':
            # TODO make the subdir if it doesn't already exist
            sub_dir = 'this'
            experiment_info['create_src_tgt_sub_dir'] = sub_dir
        elif action == 'preprocess':
            # TODO make if not exist
            sub_dir = 'this'
            experiment_info['preprocess_sub_dir'] = sub_dir
        elif action == 'train':
            # TODO make if not exist
            sub_dir = 'this'
            experiment_info['train_sub_dir'] = sub_dir
        # TODO save commands with substitions before executing them
        command = commands[action]
        command = [this.format(**experiment_info) for this in command]
        subprocess.run(command)


if __name__ == '__main__':
    main()
