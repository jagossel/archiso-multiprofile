#!/usr/bin/env bash

echo archlinux-desktop-pc > /etc/hostname
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
useradd --home-dir /home/pcuser --groups wheel --create-home --shell /bin/bash pcuser
chfn --full-name "PC User" pcuser
passwd pcuser
