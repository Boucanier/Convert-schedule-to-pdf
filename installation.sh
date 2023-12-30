#!/bin/sh

packages_install () {
    sed -i -e 's/^/python3-/' requirements.txt
    xargs -a requirements.txt sudo apt install -y
    cat requirements.txt | cut -c9- > temp.txt
    cat temp.txt > requirements.txt
    rm temp.txt
}

sudo apt update
sudo apt install python3 libreoffice-calc xdg-utils
pip install -r requirements.txt || packages_install
echo -e "\nInstallation completed !"
exit 0