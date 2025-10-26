import json
import os
import subprocess
import sys

if len(sys.argv) < 2:
    raise Exception('Profile name is required.')

profile_name = sys.argv[1]
if not profile_name:
    raise Exception('Profile name is required.')

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

post_install_scripts_dir = os.path.join(base_dir, 'post-install')
if not os.path.isdir(post_install_scripts_dir):
    exit()

config_path = os.path.join(root_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(f'Cannot find the path, {config_path}.')

config = dict()
with open(config_path) as reader:
    config = json.load(reader)

post_isntall_script_configs = config['postInstallScripts']
post_isntall_script_configs = sorted(post_isntall_script_configs, key=lambda element: element['order'])
for post_install_script_config in post_isntall_script_configs:
    profiles = post_install_script_config['profiles']
    script_relative_path = post_install_script_config['path']
    if '*' in profiles or profile_name in profiles:
        script_path = os.path.join(post_install_scripts_dir, script_relative_path)
        if not os.path.isfile(script_path): continue
        python_cmd = [ 'python3', script_path ]
        subprocess.run(python_cmd, check=True)
