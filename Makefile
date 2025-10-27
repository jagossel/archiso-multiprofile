.PHONY: all prepare clean pacman repo iso distclean rebuild install

all: iso

prepare:
	mkdir -pv builds
	python3 scripts/prepare-profiledef.py
	sudo mkdir -pv output
	sudo mkdir -pv profile/airootfs/repo
	sudo mkdir -pv profile/airootfs/root
	sudo paccache --remove --keep 1

clean:
	sudo rm -fv profile/airootfs/root/config.json
	sudo rm -Rfv profile/airootfs/repo
	sudo rm -Rfv work

pacman: clean prepare
	sudo python3 scripts/download-packages.py

aur: clean prepare
	python3 scripts/build-aur-packages.py

repo: pacman aur
	sudo python3 scripts/copy-packages.py
	sudo python3 scripts/build-repo-db.py

preparation:
	mkdir -pv profile/airootfs/files
	python3 scripts/execute-preparation-scripts.py

iso: repo preparation
	sudo cp config.json profile/airootfs/root/config.json
	sudo mkarchiso -v -w work -o output profile

distclean: clean
	sudo rm -Rfv profile/airootfs/files
	sudo rm -Rfv output
	sudo rm -Rfv builds

rebuild: distclean iso

install:
	sudo python3 scripts/burn-iso-mage.py
