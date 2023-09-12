#!/bin/sh

sudo apt update
sudo apt install python3 libreoffice-calc xdg-utils
pip install requests bs4 lxml xlsxwriter || sudo apt install python3-requests python3-bs4 python3-lxml python3-xlsxwriter
clear
echo "Everything is installed"
sleep 1
echo ...
sleep 1
echo "The program is ready to run"
sleep 2
clear
