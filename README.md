# Convert-schedule-to-pdf

This project is a schedule scrapper that will convert it into a pdf file.

## Requirements

To run the code, you need to have :

- __Python 3.10__ or above (_```sudo apt install python3```_)
- __requests__ module (_```pip install requests```_)
- __BeautifulSoup__ (_```pip install bs4```_)
- __xlsxwriter__ (_```pip install xlsxwriter```_)
- __lxml parser__ (_```pip install lxml```_)
- __LibreOffice 7.3__ or above (_```sudo apt install libreoffice```_)
- __xdg-utils__ (_```sudo apt install xdg-utils```_) : _only for __Linux__ distribution_

To install all these requirements on a Linux distribution, you can run the script _installation.sh_

## Description

Run _main.py_, then enter the element you want your schedule based on (1 : group, 2 : staff, 3 : room).

If you chose to get a schedule based on room or staff, the program will get the schedule for every group and then you will have to specify a room/professor. The program will filter every schedule with your choice and merge everything together.

Then the program will create a xlsx file and a pdf file from it. It will open the pdf file automatically.
