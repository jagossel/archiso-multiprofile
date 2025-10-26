#!/usr/bin/env bash

bail() {
    echo "$1" >&2
    exit 1
}

[ -z "$1" ] && bail "The profile name is required."

base_dir=$( dirname "$( readlink -f $0 )" )

scripts_dir="$base_dir/scripts"
[ -d "$scripts_dir" ] || bail "Cannot find the path, $scripts_dir."

for script_path in "$scripts_dir"/*; do
    if [ -f "$script_path" ]; then
        python3 $script_path $1
    fi
done

umount -Rfv /mnt
poweroff
