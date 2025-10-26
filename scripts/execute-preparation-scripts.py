import json
import os
import subprocess

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

config_path = os.path.join(root_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(f'Cannot find the path, {config_path}.')

scripts_path = os.path.join(base_dir, 'preparation')
if not os.path.isdir(scripts_path):
    exit()

config = dict()
with open(config_path) as reader:
    config = json.load(reader)

preparation_script_configs = config['preparationScripts']
preparation_script_configs = sorted(preparation_script_configs, key=lambda config: config['order'])
for preparation_script_config in preparation_script_configs:
    script_relative_path = preparation_script_config['path']
    script_path = os.path.join(scripts_path, script_relative_path)
    if os.path.isfile(script_path):
        python_cmd = [ 'python3', script_path ]
        subprocess.run(python_cmd, check=True)
