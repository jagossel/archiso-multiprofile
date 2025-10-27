import json
import os
import subprocess
import sys

if len(sys.argv) < 2:
    raise Exception('Profile name is required.')

profile_name = sys.argv[1]
if not profile_name:
    raise Exception('Profile name is required.')

CHROOT_PATH = '/mnt'
PACMAN_CONF_PATH = '/etc/pacman.d/pacman.conf'
FSTAB_PATH = '/mnt/etc/fstab'

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

config_path = os.path.join(root_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(f'Cannot find the path, {config_path}.')

if not os.path.isdir(CHROOT_PATH):
    raise Exception(f'Cannot find the path, {CHROOT_PATH}.')

if not os.path.isfile(PACMAN_CONF_PATH):
    raise Exception(f'Cannot find the path, {PACMAN_CONF_PATH}.')

config = dict()
with open(config_path) as reader:
    config = json.load(reader)

packages_config = config['packages']
packages = [ ]
for package_config in packages_config:
    profiles = package_config['profiles']
    if '*' in profiles or profile_name in profiles:
        packages.append(package_config['name'])

aur_packages_configs = config['aur']
aur_packages_configs = sorted(aur_packages_configs, key=lambda config: config['order'])
for aur_package_config in aur_packages_configs:
    aur_package_url = aur_package_config['url']
    aur_package_dir_name = os.path.basename(aur_package_url)
    aur_package_name = aur_package_config['name']
    profiles = aur_package_config['profiles']
    if '*' in profiles or profile_name in profiles:
        packages.append(aur_package_name)

subprocess.run([ 'pacman-key', '--init' ], check=True)
subprocess.run([ 'pacman-key' , '--populate' ], check=True)

pacstrap_cmd = [ 'pacstrap', '-C', PACMAN_CONF_PATH, CHROOT_PATH ]
pacstrap_cmd.extend(packages)
subprocess.run(pacstrap_cmd, check=True)

genfstab_cmd = [ 'genfstab', '-U', CHROOT_PATH ]
with open(FSTAB_PATH, 'a') as writer:
    subprocess.run(genfstab_cmd, stdout=writer)
