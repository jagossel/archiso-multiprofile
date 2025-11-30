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
DIALOG_TITLE = 'Set password for root.'
INSECURE_SWITCH = '--insecure'
PASSWORD_BOX_SWITCH = '--passwordbox'
PASSWORD_BOX_WIDTH = '0'
PASSWORD_BOX_HEIGHT = '0'
CHROOT_CMD_NAME = 'arch-chroot'
ROOT_USER_NAME = 'root'

if len(sys.argv) < 2:
    raise Exception(PROFILE_NAME_REQUIRED)

profile_name = sys.argv[1]
if not profile_name:
    raise Exception(PROFILE_NAME_REQUIRED)

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

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
        DIALOG_TITLE,
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
        DIALOG_TITLE,
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
            f'The passwords do not match for root.',
            '0',
            '0'
        ]
        subprocess.run(dialog_cmd, check=True, stderr=subprocess.PIPE, text=True)
    else:
        set_password = True

os.system('clear')
chpasswd_parameter = f'root:{new_password_value}'
chroot_chpasswd_cmd = [ CHROOT_CMD_NAME, CHROOT_PATH, 'chpasswd' ]
subprocess.run(chroot_chpasswd_cmd, input=chpasswd_parameter, text=True, capture_output=True, check=True)
