#!/usr/bin/env bash

echo archlinux-desktop-vm > /etc/hostname
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB --removable
grub-mkconfig -o /boot/grub/grub.cfg
useradd --home-dir /home/vmuser --groups wheel --create-home --shell /bin/bash vmuser
chfn --full-name "VM User" vmuser
passwd vmuser
