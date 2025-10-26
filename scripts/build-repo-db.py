import glob
import os
import subprocess

CANNOT_FIND_PATH_TEMPLATE = 'Cannot find the path, %s.'

base_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(base_dir)

profile_dir = os.path.join(root_dir, 'profile')
if not os.path.isdir(profile_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, profile_dir))

airootfs_dir = os.path.join(profile_dir, 'airootfs')
if not os.path.isdir(airootfs_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, airootfs_dir))

repo_dir = os.path.join(airootfs_dir, 'repo')
if not os.path.isdir(repo_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, repo_dir))

repo_db_path = os.path.join(repo_dir, 'custom.db.tar.zst')
package_path_glob = os.path.join(repo_dir, '*.pkg.tar.zst')

repo_add_cmd = [ 'sudo', 'repo-add', repo_db_path ]
for package_path in glob.glob(package_path_glob):
    repo_add_cmd.append(package_path)

subprocess.run(repo_add_cmd, check=True)
