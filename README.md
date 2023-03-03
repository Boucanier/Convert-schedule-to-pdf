# Convert-schedule-to-pdf

This project is a schedule scrapper that will convert it into a .pdf file.

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
 
 Run _main.py_, then enter the group you want.
 
 On __Linux__, the program will create a pdf file and open it.
 
 On __Windows__, it will only create a xlsx file that will be open at the end of the program
