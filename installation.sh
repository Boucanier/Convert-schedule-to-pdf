#!/bin/sh

sudo apt update
sudo apt install python3 libreoffice-calc xdg-utils
pip install requests bs4 lxml xlsxwriter discord || sudo apt install python3-requests python3-bs4 python3-lxml python3-xlsxwriter python3-discord
echo -e "\nInstallation completed !"
exit 0