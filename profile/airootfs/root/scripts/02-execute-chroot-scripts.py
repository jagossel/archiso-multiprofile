import json
import os
import shutil
import subprocess
import sys

if len(sys.argv) < 2:
    raise Exception('Profile name is required.')

profile_name = sys.argv[1]
if not profile_name:
    raise Exception('Profile name is required.')

CHROOT_PATH = '/mnt'
HOME_PATH = '/root'

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

chroot_scripts_dir = os.path.join(root_dir, 'chroot-scripts')
if not os.path.isdir(chroot_scripts_dir):
    raise Exception(f'Cannot find the path, {chroot_scripts_dir}.')

config_path = os.path.join(root_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(f'Cannot find the path, {config_path}.')

if not os.path.isdir(CHROOT_PATH):
    raise Exception(f'Cannot find the path, {CHROOT_PATH}.')

chroot_home_dir = os.path.join(CHROOT_PATH, HOME_PATH[1:])
if not os.path.isdir(chroot_home_dir):
    raise Exception(f'Cannot find the path, {chroot_home_dir}.')

config = dict()
with open(config_path) as reader:
    config = json.load(reader)

chroot_scripts_config = config['chrootScripts']
chroot_scripts_config = sorted(chroot_scripts_config, key=lambda config: config['order'])
for chroot_script_config in chroot_scripts_config:
    profiles = chroot_script_config['profiles']
    if '*' in profiles or profile_name in profiles:
        script_relative_path = chroot_script_config['path']
        source_script_path = os.path.join(chroot_scripts_dir, script_relative_path)
        destination_script_path = os.path.join(chroot_home_dir, script_relative_path)
        shutil.copy(source_script_path, destination_script_path)
        script_path = os.path.join(HOME_PATH, script_relative_path)
        if os.path.isfile(destination_script_path):
            chroot_cmd = [ 'arch-chroot', CHROOT_PATH, '/bin/bash', script_path ]
            subprocess.run(chroot_cmd, check=True)
