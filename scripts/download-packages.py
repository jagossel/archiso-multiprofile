import json
import os
import subprocess

CANNOT_FIND_PATH_TEMPLATE = 'Cannot find the path, %s.'

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

config_path = os.path.join(root_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, config_path))

with open(config_path) as reader:
    config = json.load(reader)

pacman_cmd = [ 'sudo', 'pacman', '--sync', '--refresh', '--downloadonly', '--noconfirm' ]

packages = config['packages']
for package in packages:
    package_name = package['name']
    pacman_cmd.append(package_name)

subprocess.run(pacman_cmd, check=True)
