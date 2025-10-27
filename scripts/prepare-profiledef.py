import os
import shutil

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

CANNOT_FIND_PATH_TEMPLATE = 'Cannot find the path, %s.'
PROFILEDEF_FILENAME = 'profiledef.sh'

base_profiledef_path = os.path.join('/usr/share/archiso/configs/baseline', PROFILEDEF_FILENAME)
if not os.path.isfile(base_profiledef_path):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, base_profiledef_path))

profile_dir = os.path.join(root_dir, 'profile')
if not os.path.isdir(profile_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, profile_dir))

profiledef_path = os.path.join(profile_dir, PROFILEDEF_FILENAME)
if os.path.isfile(profiledef_path):
    os.remove(profiledef_path)

shutil.copyfile(base_profiledef_path, profiledef_path)

profiledef_content = [ ]
with open(profiledef_path, 'r') as profiledef:
    for profiledef_line in profiledef:
        if (str.startswith(profiledef_line, 'iso_name=')):
            profiledef_content.append('iso_name="archlinux-jagossel"\n')
        elif (str.startswith(profiledef_line, 'iso_application')):
            profiledef_content.append('iso_application="Arch Linux Jagossel Remix"\n')
        else:
            profiledef_content.append(profiledef_line)

with open(profiledef_path, 'w') as profiledef:
    for profiledef_line in profiledef_content:
        profiledef.write(f'{profiledef_line}')
