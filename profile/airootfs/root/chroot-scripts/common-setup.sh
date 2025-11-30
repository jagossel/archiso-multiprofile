#!/usr/bin/env bash

ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime
ln -sf /usr/bin/vim /usr/bin/vi
sed -i 's/#en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
sed -i 's/# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers
sed -i 's/GRUB_TIMEOUT=5/GRUB_TIMEOUT=1/' /etc/default/grub
locale-gen
echo LANG=en_US.UTF-8 > /etc/locale.conf
mkinitcpio -P

mkdir -pv /etc/xdg/reflector
cat > /etc/xdg/reflector/reflector.conf << EOF
--save /etc/pacman.d/mirrorlist
--country US
--protocol https
--latest 5
--sort rate
EOF

systemctl enable reflector.{service,timer}
