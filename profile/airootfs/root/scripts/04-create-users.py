import json
import os
import subprocess
import sys
PROFILE_NAME_REQUIRED = 'Profile name is required.'
CANNOT_FIND_PATH = 'Cannot find the path, {0}.'
CHROOT_PATH = '/mnt'
DIALOG_CMD_NAME = 'dialog'
BACK_TITLE_SWITCH = '--backtitle'
BACK_TITLE = 'Custom Arch Linux Installer by jagossel'
CLEAR_SWITCH = '--clear'
NOCANCEL_SWITCH = '--nocancel'
DIALOG_TITLE_SWITCH = '--title'
DIALOG_TITLE = 'Set password for {1} ({0}).'
INSECURE_SWITCH = '--insecure'
PASSWORD_BOX_SWITCH = '--passwordbox'
PASSWORD_BOX_WIDTH = '0'
PASSWORD_BOX_HEIGHT = '0'
CHROOT_CMD_NAME = 'arch-chroot'
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
config = dict()
with open(config_path, 'r') as reader:
    config = json.load(reader)
users_config = config['users']
for user_config in users_config:
    profiles = user_config['profiles']
    if '*' not in profiles and profile_name not in profiles: continue
    user_name = user_config['name']
    user_full_name = user_config['fullName']
    user_groups = user_config['groups']
    set_password = False
    new_password_result = ''
    while not set_password:
        dialog_cmd = [
            DIALOG_CMD_NAME,
            BACK_TITLE_SWITCH,
            BACK_TITLE,
            CLEAR_SWITCH,
            NOCANCEL_SWITCH,
            DIALOG_TITLE_SWITCH,
            str.format(DIALOG_TITLE, user_name, user_full_name),
            INSECURE_SWITCH,
            PASSWORD_BOX_SWITCH,
            'Enter password:',
            PASSWORD_BOX_HEIGHT,
            PASSWORD_BOX_WIDTH
        ]
        new_password_result = subprocess.run(dialog_cmd, stderr=subprocess.PIPE, text=True)
        new_password_value = new_password_result.stderr.strip()
        dialog_cmd = [
            DIALOG_CMD_NAME,
            BACK_TITLE_SWITCH,
            BACK_TITLE,
            CLEAR_SWITCH,
            NOCANCEL_SWITCH,
            DIALOG_TITLE_SWITCH,
            str.format(DIALOG_TITLE, user_name, user_full_name),
            INSECURE_SWITCH,
            PASSWORD_BOX_SWITCH,
            'Confirm password:',
            PASSWORD_BOX_HEIGHT,
            PASSWORD_BOX_WIDTH
        ]
        confirm_password_result = subprocess.run(dialog_cmd, stderr=subprocess.PIPE, text=True)
        confirm_password_value = confirm_password_result.stderr.strip()
        if new_password_value != confirm_password_value:
            dialog_cmd = [
                DIALOG_CMD_NAME,
                BACK_TITLE_SWITCH,
                BACK_TITLE,
                '--msgbox',
                f'The passwords do not match for {user_full_name} ({user_name}).',
                '0',
                '0'
            ]
            subprocess.run(dialog_cmd, check=True, stderr=subprocess.PIPE, text=True)
        else:
            set_password = True
    chroot_useradd_cmd = [ CHROOT_CMD_NAME, CHROOT_PATH, 'useradd', '--home-dir', f'/home/{user_name}', '--create-home', '--shell', '/bin/bash' ]
    if len(user_groups) > 0:
        chroot_useradd_cmd.append('--groups')
        for user_group in user_groups:
            chroot_useradd_cmd.append(user_group)
    chroot_useradd_cmd.append(user_name)
    subprocess.run(chroot_useradd_cmd, check=True)
    chroot_chfn_cmd = [ CHROOT_CMD_NAME, CHROOT_PATH, 'chfn', '--full-name', user_full_name, user_name ]
    subprocess.run(chroot_chfn_cmd, check=True)
    chpasswd_parameter = f'{user_name}:{new_password_value}'
    chroot_chpasswd_cmd = [ CHROOT_CMD_NAME, CHROOT_PATH, 'chpasswd' ]
    subprocess.run(chroot_chpasswd_cmd, input=chpasswd_parameter, text=True, capture_output=True, check=True)
