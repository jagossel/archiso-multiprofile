import glob
import json
import os
import subprocess

CANNOT_FIND_PATH = 'Cannot find the path, {0}.'
DIALOG_CMD_NAME = 'dialog'
BACK_TITLE_SWITCH = '--backtitle'
BACK_TITLE = 'Custom Arch Linux Installer by jagossel'

base_path = os.path.dirname(os.path.realpath(__file__))
scripts_path = os.path.join(base_path, 'scripts')
if not os.path.isdir(scripts_path):
    raise Exceptin(str.format(CANNOT_FIND_PATH, scripts_path))

config_path = os.path.join(base_path, 'config.json')
if not os.path.isfile(config_path):
    raise Exception(str.format(CANNOT_FIND_PATH, config_path))

config = dict()
with open(config_path, 'r') as reader:
    config = json.load(reader)

profiles = dict()
partitioning_configs = config['partitioning']
profile_option_tag = 0
for partitioning_config in partitioning_configs:
    profile_name = partitioning_config['profile']
    if not profile_name in profiles:
        profile_option_tag = profile_option_tag + 1
        profiles[profile_option_tag] = profile_name

confirm_dialog_cmd = [ DIALOG_CMD_NAME ]
confirm_dialog_cmd.append(BACK_TITLE_SWITCH)
confirm_dialog_cmd.append(BACK_TITLE)
confirm_dialog_cmd.append('--yesno')
confirm_dialog_cmd.append('This operation will wipe the selected drive and remove all existing data.\n\nDo you wish to continue?')
confirm_dialog_cmd.append('0')
confirm_dialog_cmd.append('0')
confirm_dialog_result = subprocess.run(confirm_dialog_cmd)
if confirm_dialog_result.returncode == 1:
    exit()

profile_dialog_cmd = [ DIALOG_CMD_NAME ]
profile_dialog_cmd.append(BACK_TITLE_SWITCH)
profile_dialog_cmd.append(BACK_TITLE)
profile_dialog_cmd.append('--menu')
profile_dialog_cmd.append('Select the profile:')
profile_dialog_cmd.append('0')
profile_dialog_cmd.append('0')
profile_dialog_cmd.append('0')
for profile_tag in profiles:
    profile_name = profiles[profile_tag]
    profile_dialog_cmd.append(str(profile_tag))
    profile_dialog_cmd.append(profile_name)

profile_dialog_result = subprocess.run(profile_dialog_cmd, stderr=subprocess.PIPE, text=True)
os.system('clear')

selected_profile_tag_value = profile_dialog_result.stderr.strip()
if profile_dialog_result.returncode == 1 or selected_profile_tag_value == '':
    exit()

selected_profile_tag = int(selected_profile_tag_value)
selected_profile_name = profiles[selected_profile_tag]
python_scripts_glob = os.path.join(scripts_path, '*.py')
python_script_paths = sorted(glob.glob(python_scripts_glob))
for python_script_path in python_script_paths:
    if not os.path.isfile(python_script_path):
        continue
    python_cmd = [ 'python', python_script_path, selected_profile_name ]
    subprocess.run(python_cmd, check=True)

unmount_cmd = [ 'umount', '-Rfv', '/mnt' ]
subprocess.run(unmount_cmd, check=True)

poweroff_cmd = [ 'poweroff' ]
subprocess.run(poweroff_cmd, check=True)
