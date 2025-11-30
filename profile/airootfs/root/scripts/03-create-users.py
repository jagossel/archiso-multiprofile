import json
import os
import subprocess
import sys
PROFILE_NAME_REQUIRED = 'Profile name is required.'
CANNOT_FIND_PATH = 'Cannot find the path, {0}.'
CHROOT_PATH = '/mnt'
if len(sys.argv) < 2:
    raise Exception(PROFILE_NAME_REQUIRED)
profile_name = sys.argv[1]
if not profile_name:
    raise Exception(PROFILE_NAME_REQUIRED)
base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)
config_path = os.path.join(root_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(str.format(CANNOT_FIND_PATH, config_path))
if not os.path.isdir(CHROOT_PATH):
    raise Exception(str.format(CANNOT_FIND_PATH, CHROOT_PATH))
config = dict()
with open(config_path) as reader:
    config = json.load(reader)
users_config = config['users']
for user_config in users_config:
    profiles = user_config['profiles']
    if '*' not in profiles and profile_name not in profiles: continue
    user_name = user_config['name']
    user_full_name = user_config['fullName']
    user_groups = user_config['groups']
    chroot_useradd_cmd = [ 'arch-chroot', CHROOT_PATH, 'useradd', '--home-dir', f'/home/{user_name}', '--create-home', '--shell', '/bin/bash' ]
    if len(user_groups) > 0:
        chroot_useradd_cmd.append('--groups')
        for user_group in user_groups:
            chroot_useradd_cmd.append(user_group)
    chroot_useradd_cmd.append(user_name)
    subprocess.run(chroot_useradd_cmd, check=True)
    chroot_chfn_cmd = [ 'arch-chroot', CHROOT_PATH, 'chfn', '--full-name', user_full_name, user_name ]
    subprocess.run(chroot_chfn_cmd, check=True)
    chroot_passwd_cmd = ['arch-chroot', CHROOT_PATH, 'passwd', user_name ]
    subprocess.run(chroot_passwd_cmd, check=True)
