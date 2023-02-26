# Convert-schedule-to-pdf

This project is a schedule scrapper that will convert it into a .pdf file.

## Requirements

To run the code, you need to have :

 - __Python 3.10__ or above (_sudo apt install python3_)
 - __requests__ module (_pip install requests_)
 - __BeautifulSoup__ (_pip install bs4_)
 - __xlsxwriter__ (_pip install xlsxwriter_)
 - __lxml parser__ (_pip install lxml_)
 - __LibreOffice 7.3__ or above (_sudo apt install libreoffice_)
 - __xdg-utils__ (_sudo apt install xdg-utils_) : _only for __Linux__ distribution_
 
 To install all these requirements on a Linux distribution, you can run the script _installation.sh_
 
 ## Description
 
 Run _main.py_, then enter the group you want.
 
 On __Linux__, the program will create a pdf file and open it.
 
 On __Windows__, it will only create a xlsx file that will be open at the end of the program
