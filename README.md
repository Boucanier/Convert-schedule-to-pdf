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

Run _main.py_, then enter the element you want your schedule based on (1 : group, 2 : staff, 3 : room), refresh the list of schedule (4 : refresh), create or reset the SQL database (5 : DB creation), update the SQL database (6 : DB update) or exit the program (7 : quit).

If you chose to get a schedule based on room or staff (option 3 or 4), the program will get the schedule of every group and then you will have to specify a room/professor. The program will filter every schedule with your choice and merge everything together. Once you have created a schedule based on a room/professor, the program will not refresh every schedule unless you refresh it with option 4 in the menu.

If you choose to create the SQL database, then it will create a file called ___schedule.db___ in the _data_ directory. This DB contain tables for staff, modules, rooms, groups and courses. When you create/reset the DB, every table is dropped. Then the tables for staff, modules, rooms and groups are filled with data.

If you choose to update the DB, it will add all missing staff, rooms, modules and groups to the corresponding tables. Then it will delete every course for the current week and the next 3 weeks. After that, it will insert the missing courses in the table.

Then the program will create a xlsx file and a pdf file from it. It will open the pdf file automatically.
