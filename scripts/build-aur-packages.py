import glob
import json
import logging
import os
import subprocess
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

prebuild_dir = os.path.join(base_dir, 'prebuild')
if os.path.isdir(prebuild_dir):
    prebuild_script_glob = os.path.join(prebuild_dir, '*.sh')
    for prebuild_script_path in glob.glob(prebuild_script_glob):
        if not os.path.isfile(prebuild_script_path):
            raise Exception(f'Cannot find the path, {prebuild_script_path}')
        bash_cmd = [ 'bash', prebuild_script_path ]
        subprocess.run(bash_cmd, check=True, cwd=prebuild_dir)

builds_dir = os.path.join(root_dir, 'builds')
if not os.path.isdir(builds_dir):
    raise Exception(f'Cannot find the path, {builds_dir}.')

profile_dir = os.path.join(root_dir, 'profile')
if not os.path.isdir(profile_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, profile_dir))

airootfs_dir = os.path.join(profile_dir, 'airootfs')
if not os.path.isdir(airootfs_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, airootfs_dir))

repo_dir = os.path.join(airootfs_dir, 'repo')
if not os.path.isdir(repo_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, repo_dir))

config_path = os.path.join(root_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(f'Cannot find the path, {config_path}.')

with open(config_path) as reader:
    config = json.load(reader)

aur_packages = config['aur']
aur_packages = sorted(aur_packages, key=lambda config: config['order'])
for aur_package in aur_packages:
    aur_package_url = aur_package['url']
    aur_package_dir_name = os.path.basename(aur_package_url)
    aur_package_name = aur_package_dir_name.replace('.git', '')
    aur_package_dir = os.path.join(builds_dir, aur_package_name)
    if os.path.isdir(aur_package_dir):
        logger.info(f'Skipping {aur_package_name}...')
    else:
        git_cmd = [ 'git', 'clone', aur_package_url ]
        subprocess.run(git_cmd, check=True, cwd=builds_dir)
        if not os.path.isdir(aur_package_dir):
            raise Exception(f'Cannot find the path, {aur_package_dir}.')
        makepkg_cmd = [ 'makepkg', '--syncdeps', '--noconfirm', '--noprogressbar' ]
        if aur_package['isDependency']:
            makepkg_cmd.append('--install')
        subprocess.run(makepkg_cmd, cwd=aur_package_dir)
    aur_package_glob = os.path.join(aur_package_dir, '*.pkg.tar.zst')
    for package_path in glob.glob(aur_package_glob):
        cp_cmd = [ 'sudo', 'cp', '-fv', package_path, repo_dir ]
        subprocess.run(cp_cmd, cwd=aur_package_dir)
