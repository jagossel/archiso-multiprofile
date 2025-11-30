import glob
import json
import os
import subprocess

UNIT_SIZE = 1024

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

output_dir = os.path.join(root_dir, 'output')
if not os.path.isdir(output_dir):
    raise Exception(f'Cannot fin the path, {output_dir}.')

iso_path = ''
for file_path in glob.glob(f'{output_dir}/*.iso'):
    iso_path = file_path
    break

if iso_path.strip() == '' or not os.path.isfile(file_path):
    raise Exception(f'Cannot find the ISO file in, {output_dir}.')

lsblk_cmd = [ 'lsblk', '--json', '--byte' ]
lsblk_json = subprocess.check_output(lsblk_cmd)
block_devices = json.loads(lsblk_json)['blockdevices']

device_options = dict()
size_units = [ 'B', 'KB', 'MB', 'GB', 'TB' ]
max_index = len(size_units) - 1
for block_device in block_devices:
    device_name = block_device['name']
    device_size = block_device['size']
    readable_value = device_size
    readable_unit = size_units[max_index]
    for size_unit_index in range(max_index - 1, -1, -1):
        minimum_size = UNIT_SIZE ** size_unit_index
        if device_size > minimum_size:
            readable_value = int(device_size / minimum_size)
            readable_unit = size_units[size_unit_index]
            break
    device_options[device_name] = f'{readable_value}{readable_unit}'

drive_dialog_cmd = [ 'dialog' ]
drive_dialog_cmd.append('--backtitle')
drive_dialog_cmd.append('Custom Arch Linux Installer by jagossel')
drive_dialog_cmd.append('--menu')
drive_dialog_cmd.append('Select the profile:')
drive_dialog_cmd.append('0')
drive_dialog_cmd.append('0')
drive_dialog_cmd.append('0')
for device_option in device_options:
    drive_dialog_cmd.append(device_option)
    drive_dialog_cmd.append(device_options[device_option])

drive_dialog_result = subprocess.run(drive_dialog_cmd, stderr=subprocess.PIPE, text=True)

selected_option = drive_dialog_result.stderr.strip()
if drive_dialog_result.returncode == 1 or selected_option == '':
    os.system('cls' if os.name == 'nt' else 'clear')
    exit()

device_path = f'/dev/{selected_option}'

os.system('cls' if os.name == 'nt' else 'clear')
print(f'Burning to {device_path}...')
dd_cmd = [ 'dd', f'if={iso_path}', f'of={device_path}', 'status=progress' ]
subprocess.run(dd_cmd, check=True)
