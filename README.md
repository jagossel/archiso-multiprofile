# archiso-multiprofile
A collection of scripts that builds a fully offline Arch Linux installer ISO
with multiple selectable profiles, all driven by a single config.json.

## Table of Contents
- [About](#about)
- [Dependencies](#dependencies)
- [config.json](#configjson)
  - [Profile Names](#profile-names)
  - [packages](#packages-section)
  - [aur](#aur-section)
  - [preparationScripts](#preparationscripts-section)
  - [partitioning](#partitioning-section)
  - [chrootScripts](#chrootscripts-section)
  - [users](#users-section)
  - [postInstallScripts](#postinstallscripts-section)
- [Additional Notes](#additional-notes)
  - [File System Types](#file-system-types)
  - [Partition Size](#partition-size)
- [Build Process](#build-process)
- [Installation Process](#installation-process)

## About
This is an archiso profile that will build an ISO image for offline
installation, and define multiple profiles for installation.

## Dependencies
The following packages will need to be installed in order to build the ISO
image:
- `archiso`
- `pacman-contrib`

## `config.json`
The configuration file, `config.json`, is used to define the installation
parameters, including drive partitioning, package installation, and scripts to
execute as part of the installation process.

### Profile Names
There are no defined profile names to use, the profile names are completely
arbitrary.  The profiles names used in the original `config.json` file use
`pc` and `vm`.  This is not required, any profile name can be used.

### `packages` Section
An array of objects that define what packages to install for a particular
profile.

```json
"packages": [{
  "name": "package-name",
  "profiles": [ "profile-name", ... ]
}, ... ]
```

- `name`: The name of the package.
- `profiles`: An array of strings for the profile; `*` denotes any profile.

### `aur` Section
An array of objects that define what AUR packages to build and install for a
particular profile.

```json
"aur": [{
  "url": "url-to-aur-git-repo",
  "name": "package-name",
  "profiles": [ "profile-name", ... ],
  "isDependency": false,
  "order": 0
}, ... ]
```

- `url`: The URL to the AUR git repository
  (e.g. https://aur.archlinux.org/yay.git)
- `name`: The name of the package to install.  Under some circumstances,
  the AUR could build multiple packages, the `name` property defines
  which of those packages to install.
- `profiles`: An array of strings for the profile; `*` denotes any
  profile.
- `isDependency`: A Boolean property indicating that this package is a
  required package for other AUR packages.  `true` to build and install
  the package during the preparation process, otherwise, `false` to just
  build the package.  Regardless of the value, the package will be copied
  over to the offline repository.
- `order`: The order of which to build or install packages.  This is used
  to help handle AUR package dependencies.

### `preparationScripts` Section
An array of objects that define what Python scripts to run as part of the
preparation process (the process that builds the ISO image).  The preparation
scripts must be located in the `scripts/preparation` folder.

```json
"preparationScripts": [{
  "path": "script-path",
  "order": 0
}, ... ]
```

- `path`: The path of the script, relative to `scripts/preparation`.
- `order`: The order of which to execute the script.

### `partitioning` Section
An array of objects that maps out the drives and partitions.

```json
"partitioning": [{
  "profile": "profile-name",
  "drives": [{
    "name": "drive-name",
    "layout": [{
      "partition": "partition-name",
      "filesystemType": "filesystem-type",
      "size": "partition-size",
      "mount": "partition-mount-path",
      "mountOrder": 0,
      "label": "partition-label"
    }, ... ]
  }, ... ]
}, ... ]
```

- `profile`: The name of the profile; `*` is not allowed in this case
  because hardware will be different between the machine or VM the installer
  is running in.
- `drives`: The JSON object defining the drive and layout of that drive.
- `name`: The name of the drive, according to the output of the `lsblk`
  command.  `/dev/` will be prefixed to each drive name (e.g. `vda` becomes
  `/dev/vda` during execution).
- `layout`: The JSON object defining the layout of the drive.
- `partition`: The name of the partition, which will be concatenated
  string providing the full path (e.g. `1` becomes `/dev/vda1` during
  execution).
- `filesystemType`: The name of the file system type of the drive, this
  will be used to format the drive with the given file system type. See
  `File System Types` section of this file for more information.
- `size`: The size of the partition; see `Partition Size` section of this
  file for more information.
- `mount`: The directory to mount the newly created partition in.
- `mountOrder`: The order to mount the partition; under some
  circumstances, some partitions that will be mounted in sub-folders of
  other partitions will have to be mount _after_ other mount points.
- `label`: The label of the partition.

### `chrootScripts` Section
An array of objects defining what BASH scripts to run after the packages have
been installed.  These scripts define the configuration commands needed as part
of the installation process.

```json
"chrootScripts": [{
  "path": "script-path",
  "profiles": [ "profile-name", ... ],
  "order": 0
}, ... ]
```

- `path`: The path, relative to `/root/chroot-scripts` of the live system.
- `profiles`: An array of string for the profile that the script is for; `*`
  denotes any profile will run the script.
- `order`: The order the script will run; some scripts cannot be executed
unless another script has already been executed.

### `users` Section
An array of objects defining what users to create after the packages have
been installed, and the system has been configured.

```json
"users": [{
  "name": "username",
  "fullName": "User Full Name",
  "groups": [ "group" ],
  "profiles": [ "profile-name", ... ]
}, ... ]
```

- `name`: The user name, e.g. `john`
- `fullName`: The full name of the user, e.g. `John Smith`
- `groups`: An array of strings defining what groups the user will be
  assigned to.
- `profiles`: An array of strings for the profile that the user is for; `*`
  denotes any profile will have that user.


### `postInstallScripts` Section
An array of objects defining what Python scripts to run after the
installation.  The scripts will be executed outside of the installed system;
in other words, these scripts will be executed in the live system.  The path
will be relative to `/root/scripts/post-install` of the live system.

```json
"postInstallScripts": [{
  "path": "script-path",
  "profiles": [ "profile-name", ... ],
  "order": 1
}, ... ]
```

- `path`: The path, relative to `/root/scripts/post-install` of the live
  system.
- `profiles`: An array of strings of the profile to run the script; `*`
  denotes any profile can run the script.
- `order`: The order the script will run; some scripts cannot be executed
  unless another script has already been executed.

### `preparationScripts` vs. `chrootScripts` vs. `postInstallScripts`
Here is a table to summarize when each group of scripts are executed between
the `preparationScripts`, `chrootScripts`, and `postInstallScripts`:

|      Section       |        Runs On       |             When             |      Path Root (relative to)       |
|:-------------------|:---------------------|:-----------------------------|:-----------------------------------|
| preparationScripts | Build host           | Before ISO is built          | `scripts/preparation/`             |
| chrootScripts      | Live system (chroot) | After package install        | `/root/chroot-scripts/` (in ISO)   |
| postInstallScripts | Live system          | After installation completes | `/root/scripts/post-install` (ISO) |

### Example `config.json`

```json
{
  "packages": [
    { "name": "base",       "profiles": ["*"] },
    { "name": "linux",      "profiles": ["*"] },
    { "name": "grub",       "profiles": ["*"] },
    { "name": "efibootmgr", "profiles": ["*"] }
  ],
  "aur": [
    { "url": "https://aur.archlinux.org/doas.git", "name": "doas", "profiles": ["*"], "isDependency": true,  "order": 1 },
    { "url": "https://aur.archlinux.org/yay.git",  "name": "yay",  "profiles": ["*"], "isDependency": false, "order": 2 }
  ],
  "preparationScripts": [],
  "partitioning": [{
    "profile": "vm",
    "drives": [{
      "name": "vda",
      "layout": [
        { "partition": "1", "filesystemType": "fat32", "size": "1G",  "mount": "/boot/efi", "mountOrder": 2, "label": "Boot" },
        { "partition": "2", "filesystemType": "ext4",  "size": "*",   "mount": "/",         "mountOrder": 1, "label": "Arch Linux OS" },
        { "partition": "3", "filesystemType": "swap",  "size": "2xRAM","mount": "swap",     "mountOrder": 3 }
      ]
    }]
  }],
  "chrootScripts": [
    { "path": "common-setup.sh",  "profiles": ["*"],       "order": 1 },
    { "path": "desktop-setup.sh", "profiles": ["pc","vm"], "order": 2 }
  ],
  "users": [
    { "name": "john", "fullName": "John Smith", "groups": [ "wheel" ], "profiles": [ "*" ] }
  ],
  "postInstallScripts": []
}
```

## Additional Notes

### File System Types
Currently, the following values are supported for the file system types
in the `partitioning[].drives[].layout[].filesystemType` property:
- `ext4`
- `fat32`
- `swap`
 
Because of the inconsistencies in file system names between each command,
there must be some translation for each file system type.  For example,
`fat32` works as is with `parted`, but the command to format it is
`mkfs.vfat`.

Other file system types _might_ work, but there it has not been tested
and there is no support for it.

### Partition Size
The property, `partitioning[].drives[].layout[].size`, is a string. This
allows flexibility in defining the sizes.  The following size values are
supported:
- `xRAM`: The size of RAM on the machine.  For example, `1xRAM` on a system
  with 4GB of RAM will translate to `4GB`, or `2xRAM` could translate to
  `8GB` on a system 4GB of RAM.  This is more useful for defining the size of
  the swap partition.
- `T`, `G`, `M`, `K`: Unit of size of the drive: terabytes (T),
  gigabytes (G), megabytes (M), and kilobytes (K).  For example, `100G` will
  translate to 100GB or 107,374,182,400 bytes (or 100 * (1024 ^ 3)).
- `*`: Will fill in the remaining space available.  The Python script that
  partitions the drives will calculate the sizes of the other partitions and
  whatever remains will be the space that partition will use.

### Partitioning Assumptions

The provided examples target UEFI systems using GPT. Ensure an EFI System
Partition (FAT32) is created and mounted at `/boot/efi` for GRUB +
`efibootmgr` to work as shown. Legacy BIOS installs may require different steps.

## Build Process
The process to make an ISO image is defined in `Makefile`.  To start the
process of building an image, run `make` with no additional targets.

There are other targets available:
- `iso`: The main build process
- `distclean`: Cleans up everything and attempts to put the folder back to a
  pristine state.
- `rebuild`: The same as calling `make distclean` and `make`, forces a
  complete rebuild of the packages, offline repository, and ISO image.
- `install`: Invokes the Python script that will prompt which drive to burn
  the image to, and executes the `dd` command to burn the ISO onto a USB drive.

## Installation Process
After the ISO file has been created (and burned onto USB drive for real
hardware), boot up the VM or the computer with the newly created ISO image.
Invoke the following command:

```bash
bash install.sh profile-name
```

Where `profile-name` is the name of the profile to run the installation
process for.

After installation is finished, it will be powered off, giving
an opportunity to remove the USB drive or to clear out the ISO setting on the
VM before booting to the newly installed system.

Networking connection is not required during the installation process since
the packages are stored in the live system image.
