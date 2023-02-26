"""
    This code will convert the data scrapped with the scrapper into a xlsx file (into a pdf file if on Linux distribution)
"""
import xlsxwriter
import os
import platform


ROW = 27
COL = 133 #EC


def setFormatWS(workbook):
    '''
        Create formats used to set the sheet of the schedule in the xlsx document

        - Args :
            - workbook (xlsxwriter workbook) : workbook containing the schedule
        
        - Returns :
            - dayFormat (xlsxwriter format) : format for the days cells and more
            - underFormat (xlsxwriter format) : format used to create the bottom border of the schedule
            - rightFormat (xlsxwriter format) : format used to create the right border of the schedule
            - cornerFormat (xlsxwriter format) : format used to create the right bottom hand corner border of the schedule
    '''
    dayFormat = workbook.add_format()
    dayFormat.set_align('center')
    dayFormat.set_align('vcenter')
    dayFormat.set_font_name('Arial')
    dayFormat.set_font_size(13)
    dayFormat.set_text_wrap()
    dayFormat.set_border()
    dayFormat.set_bg_color('#DCDCDC')

    underFormat = workbook.add_format()
    underFormat.set_bottom()

    rightFormat = workbook.add_format()
    rightFormat.set_right()

    cornerFormat = workbook.add_format()
    cornerFormat.set_bottom()
    cornerFormat.set_right()

    return dayFormat, underFormat, rightFormat, cornerFormat


def initWS(worksheet) -> tuple[str]:
    """
        Initialize the worksheet

        - Returns :
            - totalLetters (tuple[str])
    """
    worksheet.set_landscape()
    worksheet.set_margins(left = 0.15, right = 0.15, top = 0, bottom = 0)
    worksheet.center_horizontally()
    worksheet.center_vertically()
    letters = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')
    totalLetters = []
    for i in range(COL):
        if i < 26 :
            totalLetters.append(letters[i%26])
        else :
            totalLetters.append(totalLetters[(i//26)-1] + letters[i%26])
    # worksheet.set_column('B:' + str(totalLetters[-1]), 0.8)
    worksheet.set_column('B:' + str(totalLetters[-1]), 0.7)
    # worksheet.set_column('A:A', 12)
    for i in range(27):
        worksheet.set_row((i+1),19)
    for i in range(5):
        worksheet.set_row(5 + 5*i, 25)
        worksheet.set_row(4 + 5*i, 25)
    worksheet.set_row(1,20)
    worksheet.print_area('A1:' + str(totalLetters[-1]) + '27')
    worksheet.set_paper(9)
    worksheet.fit_to_pages(1, 0)
    totalLetters = tuple(totalLetters)
    return totalLetters
    

def formatWS(worksheet, dayFormat, totalLetters : tuple[str], underFormat, rightFormat, cornerFormat, title : str) -> None:
    """
        Set the frame for the schedule with days and times

        - Args :
            - worksheet
            - dayFormat
            - totalLetters (tuple[str])
            - underFormat
            - rightFormat
            - cornerFormat
            - title (str)
    """
    weekDays = ('lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi')
    for i in range(0,ROW - 2,5):
        worksheet.merge_range('A' + str(i+3) + ':A' + str(i+7), weekDays[i//5], dayFormat)
    worksheet.merge_range('B1:' + str(totalLetters[-1]) + '1', title, dayFormat)
    worksheet.set_row(0,25)
    for i in range(1,COL-10,12):
        worksheet.merge_range(str(totalLetters[i]) + '2:' + str(totalLetters[i+11]) + '2', str(round(i/12)+8) + ':00 - ' + str(round(i/12)+9) + ':00', dayFormat)
    for i in range(3,ROW + 1) :
        worksheet.write_blank(str(totalLetters[-1]) + str(i), None, rightFormat)
    for i in range(1,COL):
        worksheet.write_blank(str(totalLetters[i]) + '27', None, underFormat)
    worksheet.write_blank(str(totalLetters[-1]) + '27', None, cornerFormat)


def setToColumn(courseList : tuple, totalLetters : tuple[str]) -> list :
    timeColumn = []
    for j in range(len(courseList)):
        tempList = []
        for i in range(2):
            tempTime = 0
            tempTime += (int(((courseList[j].timeContent)[i].split(':'))[0])-8) * 12 + 1 + int(((courseList[j].timeContent)[i].split(':'))[1])//5 - i
            tempList.append(totalLetters[tempTime])
        timeColumn.append(tempList)
    return timeColumn


def addCourse(worksheet, columnTime : list, courseList : tuple, workbook) -> None:
    """
        Add a course to the xlsx file\n
        Create formats used to add course
        
        - Args :
            - worksheet (xlsx worksheet)
            - columntime (list)
            - courseList (tuple[list[Course]])
    """
    fmtList = [[],[],[]]
    for e in courseList :
        topfmt = workbook.add_format()
        topfmt.set_align('center')
        topfmt.set_align('vcenter')
        topfmt.set_font_name('Arial')
        topfmt.set_font_size(11)
        topfmt.set_text_wrap()
        topfmt.set_right()
        topfmt.set_left()
        topfmt.set_top()
        topfmt.set_bold()
        topfmt.set_bg_color(e.colorContent)
        fmtList[0].append(topfmt)

        fmt = workbook.add_format()
        fmt.set_align('center')
        fmt.set_align('vcenter')
        fmt.set_font_name('Arial')
        fmt.set_font_size(11)
        fmt.set_text_wrap()
        fmt.set_right()
        fmt.set_left()
        fmt.set_shrink()
        fmt.set_bg_color(e.colorContent)
        fmtList[1].append(fmt)

        botfmt = workbook.add_format()
        botfmt.set_align('center')
        botfmt.set_align('vcenter')
        botfmt.set_font_name('Arial')
        botfmt.set_font_size(13)
        botfmt.set_text_wrap()
        botfmt.set_right()
        botfmt.set_left()
        botfmt.set_bottom()
        botfmt.set_bg_color(e.colorContent)
        fmtList[2].append(botfmt)

    for i in range(len(courseList)):
        rowNbr = int(courseList[i].dayContent)*5+3

        worksheet.merge_range(columnTime[i][0] + str(rowNbr) + ':' + columnTime[i][1] + str(rowNbr), courseList[i].timeContent[0] + ' - ' + courseList[i].timeContent[1], fmtList[0][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 1) + ':' + columnTime[i][1] + str(rowNbr + 1), courseList[i].groupContent, fmtList[1][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 2) + ':' + columnTime[i][1] + str(rowNbr + 2), courseList[i].moduleContent, fmtList[1][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 3) + ':' + columnTime[i][1] + str(rowNbr + 3), courseList[i].profContent, fmtList[1][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 4) + ':' + columnTime[i][1] + str(rowNbr + 4), courseList[i].roomContent, fmtList[2][i])


def convertToPdf() -> None:
    '''
        Convert the created xlsx file to pdf using a libreOffice command on Linux\n
        Then, remove the xlsx file since it is useless\n
        Clear the terminal\n
        Open the previously created pdf
    '''
    if platform.system() == "Linux" :
        os.system('libreoffice --convert-to pdf schedule.xlsx')
        os.system('rm schedule.xlsx')
        os.system('clear')
        os.system('xdg-open schedule.pdf')
        
    elif platform.system() == "Windows" :
        os.system('start /B schedule.xlsx')
        os.system('cls')


def transformToXls(courseList : tuple, weekDesc : list[str], title : str) -> None:
    """
        Create a xlsx file from course list of 4 weeks and then convert it to a pdf file
        
        - Args :
            - courseList (tuple[list[Course]])
            - weekDesc (list[str])
            - title (str)
    """
    workbook = xlsxwriter.Workbook('schedule.xlsx')

    for i in range (len(weekDesc)):
        worksheet = workbook.add_worksheet(str(weekDesc[i]))
        dayFormat, underFormat, rightFormat, cornerFormat = setFormatWS(workbook)
        totalLetters = initWS(worksheet)
        formatWS(worksheet, dayFormat, totalLetters, underFormat, rightFormat, cornerFormat, title)
        columnTime = setToColumn(courseList[i], totalLetters)
        addCourse(worksheet, columnTime, courseList[i], workbook)
        
    workbook.close()
    convertToPdf()
