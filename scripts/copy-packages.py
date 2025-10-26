import glob
import logging
import os
import shutil
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)

CANNOT_FIND_PATH_TEMPLATE = 'Cannot find the path, %s.'
COPY_MESSAGE_TEMPLATE = 'Copying %s to %s.'

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

cached_pkg_dir = '/var/cache/pacman/pkg'
if not os.path.isdir(cached_pkg_dir):
    raise Exception(str.format(CANNOT_FIND_PATH_TEMPLATE, cached_pkg_dir))

package_glob = os.path.join(cached_pkg_dir, '*.pkg.tar.*')
for package_path in glob.glob(package_glob):
    logger.info(COPY_MESSAGE_TEMPLATE, package_path, repo_dir)
    shutil.copy(package_path, repo_dir)
