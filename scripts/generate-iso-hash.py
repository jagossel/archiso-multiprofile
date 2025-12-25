import glob
import hashlib
import logging
import os
import sys

CANNOT_FIND_PATH = 'Cannot find the path, {0}.'
BUFFER_SIZE = 65536

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setLevel(logging.INFO)
logger.addHandler(logHandler)

base_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(base_path)

output_path = os.path.join(root_path, 'output')
if not os.path.isdir(output_path):
    raise Exception(str.format(CANNOT_FIND_PATH, output_path))

hash_path = os.path.join(output_path, 'sha256sums.txt')
if os.path.isfile(hash_path):
    os.remove(hash_path)

iso_glob = os.path.join(output_path, '*.iso')
with open(hash_path, 'w') as hash_writer:
    for iso_path in glob.glob(iso_glob):
        if not os.path.isfile(iso_path): continue
        sha256 = hashlib.sha256()
        logger.info(f'Generating SHA256 hash for {iso_path}...')
        with open(iso_path, 'rb') as file_reader:
            while True:
                data = file_reader.read(BUFFER_SIZE)
                if not data: break
                sha256.update(data)
        hash_result = sha256.hexdigest()
        hashed_filename = os.path.basename(iso_path)
        hash_writer.write(f'{hash_result}  {hashed_filename}\n')

