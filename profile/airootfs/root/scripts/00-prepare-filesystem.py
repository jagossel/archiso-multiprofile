import json
import os
import psutil
import subprocess
import sys

if len(sys.argv) < 2:
    raise Exception('Profile name is required.')

profile_name = sys.argv[1]
if not profile_name:
    raise Exception('Profile name is required.')

base_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = os.path.dirname(base_dir)

config_path = os.path.join(home_dir, 'config.json')
if not os.path.isfile(config_path):
    raise Exception('Cannot find the path, ' + config_path + '.')

config = dict()
with open(config_path) as reader:
    config = json.load(reader)

ram_size = psutil.virtual_memory().total

lsblk_cmd = [ 'lsblk', '--json', '--bytes' ]
lsblk_json = subprocess.check_output(lsblk_cmd)
block_devices = json.loads(lsblk_json)['blockdevices']

partitioning_configs = config['partitioning']
partitioning_config = next((element for element in partitioning_configs if element['profile'] == profile_name), '')
if not partitioning_config:
    raise Exception('Profiles not defined, ' + profile_name)

drives_config = partitioning_config['drives']
for drive_config in drives_config:
    drive_name = drive_config['name']
    target_device = next((element for element in block_devices if element['name'] == drive_name), '')
    if not target_device:
        raise Exception('Device not found: ' + drive_name)
    drive_size = target_device['size'] - 4096
    layout_configs = drive_config['layout']
    require_calculation = None
    total_used = 0
    for layout_config in layout_configs:
        partition_size_config = layout_config['size']
        partition_size = 0
        if partition_size_config.endswith('xRAM'):
            size_factor = int(partition_size_config[:-4])
            partition_size = ram_size * size_factor
            total_used = total_used + partition_size
        elif partition_size_config == '*':
            require_calculation = layout_config
        elif partition_size_config.endswith('T'):
            partition_size = int(partition_size_config[:-1]) * (1024 ** 4)
            total_used = total_used + partition_size
        elif partition_size_config.endswith('G'):
            partition_size = int(partition_size_config[:-1]) * (1024 ** 3)
            total_used = total_used + partition_size
        elif partition_size_config.endswith('M'):
            partition_size = int(partition_size_config[:-1]) * (1024 ** 2)
            total_used = total_used + partition_size
        elif partition_size_config.endswith('K'):
            partition_size = int(partition_size_config[:-1]) * (1024 ** 1)
            total_used = total_used + partition_size
        else:
            partition_size = int(partition_size_config)
            total_used = total_used + partition_size
        if partition_size > 0:
            layout_config['size'] = partition_size
    if require_calculation:
        partition_size = drive_size - total_used
        if partition_size < 0:
            raise Exception('The total space used for partitions exceeded the size of the drive.')
        require_calculation['size'] = partition_size

SECTOR_SIZE = 512
SECTOR_OFFSET = 2048
for drive_config in drives_config:
    layout_configs = drive_config['layout']
    device_path = f'/dev/{drive_config['name']}'
    device_size = sum(element['size'] for element in layout_configs)
    sector_count = int((device_size / SECTOR_SIZE) - SECTOR_OFFSET)
    start_sector = SECTOR_OFFSET
    parted_cmd = [ 'parted', '--script', device_path, 'mklabel', 'GPT' ]
    for layout_config in layout_configs:
        partition_size = layout_config['size']
        sector_size = int(partition_size / SECTOR_SIZE)
        if start_sector % SECTOR_OFFSET != 0:
            start_sector += SECTOR_OFFSET - (start_sector % SECTOR_OFFSET)
        end_sector = start_sector + sector_size - 1
        end_sector = min([ end_sector, sector_count ])
        filesystem_type = layout_config['filesystemType']
        if filesystem_type == 'swap':
            filesystem_type = 'linux-swap'
        parted_cmd.extend([ 'mkpart', filesystem_type, f'{start_sector}s', f'{end_sector}s' ])
        start_sector = end_sector + 1
    subprocess.run(parted_cmd, check=True)

for drive_config in drives_config:
    layout_configs = drive_config['layout']
    device_path = f'/dev/{drive_config['name']}'
    for layout_config in layout_configs:
        partition_path = device_path + layout_config['partition']
        filesystem_type = layout_config['filesystemType']
        drive_label = ''
        if 'label' in layout_config:
            drive_label = layout_config['label']
        mkfs_cmd = [ ]
        if filesystem_type == 'fat32':
            mkfs_cmd.extend([ 'mkfs.vfat', partition_path ])
        elif filesystem_type == 'swap':
            mkfs_cmd.extend([ 'mkswap', partition_path ])
        else:
            mkfs_cmd.extend([ f'mkfs.{filesystem_type}', partition_path ])
        if len(mkfs_cmd) <= 0:
            raise Exception('Invalid command provided.')
        subprocess.run(mkfs_cmd, check=True)
        if not drive_label: continue
        label_cmd = [ ]
        if filesystem_type == 'fat32':
            label_cmd.extend([ 'dosfslabel', partition_path, drive_label ])
        elif filesystem_type == 'swap':
            continue
        else:
            label_cmd.extend([ 'e2label', partition_path, drive_label ])
        subprocess.run(label_cmd, check=True)

for drive_config in drives_config:
    device_path = f'/dev/{drive_config['name']}'
    layout_configs = drive_config['layout']
    layout_configs = sorted(layout_configs, key=lambda config: config['mountOrder'])
    for layout_config in layout_configs:
        partition_path = f'{device_path}{layout_config['partition']}'
        mount_point = layout_config['mount']
        full_mount_point = mount_point
        if mount_point.startswith('/'):
            full_mount_point = full_mount_point[1:]
        full_mount_point = os.path.join('/mnt', full_mount_point)
        if mount_point == 'swap':
            swapon_cmd = [ 'swapon', partition_path ]
            subprocess.run(swapon_cmd, check=True)
            continue
        if mount_point != '/' and not os.path.isdir(full_mount_point):
            os.makedirs(full_mount_point)
        mount_cmd = [ 'mount', '-v', partition_path, full_mount_point ]
        subprocess.run(mount_cmd, check=True)
