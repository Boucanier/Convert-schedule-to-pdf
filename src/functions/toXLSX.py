"""
    This module will convert the data scrapped with the scrapper into a xlsx file
"""
import xlsxwriter
from datetime import date, datetime, timedelta
from models.course import *


ROW = 27
COL = 133 #EC

ROW_SHORT = 7


def setFormatWS(workbook : xlsxwriter.Workbook) -> tuple[xlsxwriter.workbook.Format, xlsxwriter.workbook.Format, xlsxwriter.workbook.Format, xlsxwriter.workbook.Format]:
    '''
        Create formats used to set the sheet of the schedule in the xlsx document

        - Args :
            - workbook (xlsxwriter workbook) : workbook containing the schedule
        
        - Returns :
            - dayFormat (xlsxwriter format) : format for the days cells and more
            - underFormat (xlsxwriter format) : format used to create the bottom border of the schedule
            - rightFormat (xlsxwriter format) : format used to create the right border of the schedule
            - cornerFormat (xlsxwriter format) : format used to create corner border of the schedule
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


def initWS(worksheet, row : int, col : int, short : bool = False) -> tuple:
    """
        Initialize the worksheet by setting the size of the cells and the columns

        - Args :
            - worksheet (xlsx worksheet) : worksheet to initialize
            - row (int) : number of rows
            - col (int) : number of columns
            - short (bool) : default = False, if True : only format first day, else : format every day

        - Returns :
            - totalLetters (tuple[str]) : tuple containing the letters of the columns (A, B, C, ..., AA, AB, ..., BA, BB, ...)
    """
    worksheet.set_landscape()
    worksheet.set_margins(left = 0.15, right = 0.15, top = 0.15, bottom = 0.15)
    worksheet.center_horizontally()
    letters = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')
    totalLetters = list()
    for i in range(COL):
        if i < 26 :
            totalLetters.append(letters[i%26])
        else :
            totalLetters.append(totalLetters[(i//26)-1] + letters[i%26])

    worksheet.set_column('B:' + str(totalLetters[-1]), 0.8)
    worksheet.set_column('A:A', 12)
    for i in range(ROW):
        worksheet.set_row((i+1),19)

    if short :
        worksheet.set_row(5, 25)
        worksheet.set_row(4, 25)

    else :
        for i in range(5):
            worksheet.set_row(5 + 5*i, 25)
            worksheet.set_row(4 + 5*i, 25)

    worksheet.set_row(1,20)
    worksheet.print_area('A1:' + str(totalLetters[-1]) + str(ROW))
    worksheet.set_paper(9)
    worksheet.fit_to_pages(1, 0)
    totalLetters = tuple(totalLetters)
    return totalLetters
    

def formatWS(worksheet, dayFormat : xlsxwriter.workbook.Format, totalLetters : tuple, underFormat : xlsxwriter.workbook.Format, rightFormat : xlsxwriter.workbook.Format, cornerFormat : xlsxwriter.workbook.Format, title : str, week : str, row : int, col : int, dayInd : int = 5) -> None:
    """
        Set the frame for the schedule with days and times

        - Args :
            - worksheet (xlsx worksheet) : worksheet in which the formats will be applied
            - dayFormat (xlsxwriter format) : format for the days cells
            - totalLetters (tuple[str])
            - underFormat (xlsxwriter format) : format used to create the bottom border of the schedule
            - rightFormat (xlsxwriter format) : format used to create the right border of the schedule
            - cornerFormat (xlsxwriter format) : format used to create corner border of the schedule
            - title (str) : title of the schedule
            - row (int) : Number of rows
            - col (int) : Number of columns
            - dayInd (int) : Day of week index, default = 5, dayInd > 5 means all week is requested

        - Returns :
            - None
    """
    weekDays = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi')

    if dayInd < 5 :
        weekDays = [weekDays[dayInd]]

    for i in range(0, row - 2, 5):
        worksheet.merge_range('A' + str(i+3) + ':A' + str(i+7), weekDays[i//5], dayFormat)
    listWeek = list(week)
    for i in range(len(listWeek)):
        if listWeek[i] == '_':
            listWeek[i] = '/'
    week = ''.join(listWeek)
    worksheet.merge_range('B1:' + str(totalLetters[-1]) + '1', title + ', semaine du ' + week, dayFormat)
    worksheet.set_row(0,25)
    for i in range(1, col-10, 12):
        worksheet.merge_range(str(totalLetters[i]) + '2:' + str(totalLetters[i+11]) + '2', str(round(i/12)+8) + ':00 - ' + str(round(i/12)+9) + ':00', dayFormat)
    for i in range(3, row + 1) :
        worksheet.write_blank(str(totalLetters[-1]) + str(i), None, rightFormat)
    for i in range(1, col):
        worksheet.write_blank(str(totalLetters[i]) + str(row), None, underFormat)
    worksheet.write_blank(str(totalLetters[-1]) + str(row), None, cornerFormat)


def setToColumn(courseList : list[Course], totalLetters : tuple) -> list[list[list[str]]] :
    """
        Get the range of column at the xlsx format for every course

        - Args :
            - courseList (list[Course])
            - totalLetters (tuple[str])
        
        - Returns :
            - timeColumn (list[list[list[str]]])
    """
    timeColumn = []
    for j in range(len(courseList)):
        tempList = []
        for i in range(2):
            tempTime = 0
            tempTime += (int(((courseList[j].timeContent)[i].split(':'))[0])-8) * 12 + 1 + int(((courseList[j].timeContent)[i].split(':'))[1])//5 - i
            tempList.append(totalLetters[tempTime])
        timeColumn.append(tempList)
    return timeColumn


def addCourse(worksheet, columnTime : list, courseList : list, workbook : xlsxwriter.Workbook, short : bool = False) -> None:
    """
        Create formats used to add course\n
        Add a course to the xlsx file
        
        - Args :
            - worksheet (xlsx worksheet)
            - columntime (list)
            - courseList (list[Course])
            - workbook (xlsx workbook)
            - short (bool) : default False, if True : add course to first row only
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
        if short :
            rowNbr = 3
        else :
            rowNbr = int(courseList[i].dayContent)*5+3

        worksheet.merge_range(columnTime[i][0] + str(rowNbr) + ':' + columnTime[i][1] + str(rowNbr), courseList[i].timeContent[0] + ' - ' + courseList[i].timeContent[1], fmtList[0][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 1) + ':' + columnTime[i][1] + str(rowNbr + 1), courseList[i].groupContent, fmtList[1][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 2) + ':' + columnTime[i][1] + str(rowNbr + 2), courseList[i].moduleContent, fmtList[1][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 3) + ':' + columnTime[i][1] + str(rowNbr + 3), courseList[i].profContent, fmtList[1][i])
        worksheet.merge_range(columnTime[i][0] + str(rowNbr + 4) + ':' + columnTime[i][1] + str(rowNbr + 4), courseList[i].roomContent, fmtList[2][i])


def writeToList(workbook : xlsxwriter.Workbook, worksheet, overCourse : list, courseList : list, week : str, totalLetters : tuple) -> tuple[list[Course], xlsxwriter.workbook.Format, xlsxwriter.workbook.Format]:
    """
        Write a list of every courses

        - Args :
            - workbook (xlsx workbook) : workbook containing the schedule
            - worksheet (xlsx worksheet) : worksheet to write on
            - overCourse (list[Course]) : list of overlapping courses
            - week (str) : week of the schedule
            - totalLetters (tuple[str])

        - Returns :
            - totalCourse (list[Course])
            - bigfmt (xlsxwriter format)
            - fmt (xlsxwriter format)
    """
    weekDays = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi')

    bigfmt = workbook.add_format()
    bigfmt.set_align('center')
    bigfmt.set_align('vcenter')
    bigfmt.set_font_name('Arial')
    bigfmt.set_font_size(15)
    bigfmt.set_bold()
    bigfmt.set_text_wrap()
    bigfmt.set_shrink()
    bigfmt.set_border()

    fmt = workbook.add_format()
    fmt.set_align('vcenter')
    fmt.set_font_name('Arial')
    fmt.set_font_size(13)
    fmt.set_text_wrap()
    fmt.set_shrink()
    fmt.set_border()

    worksheet.set_row(0, 25)
    worksheet.merge_range('A1:' + totalLetters[-1] + '1', 'Liste des cours - semaine du ' + week[:2] + '/' + week[3:5] + '/' + week[-4:], bigfmt)

    overCpt = 0
    courseCpt = 0
    totalCourse = []

    while overCpt < len(overCourse) or courseCpt < len(courseList):
        if (overCpt < len(overCourse) and courseCpt < len(courseList) and overCourse[overCpt].startBefore(courseList[courseCpt])) or courseCpt == len(courseList):
            totalCourse.append(overCourse[overCpt])
            overCpt += 1
        else :
            if courseList[courseCpt].profContent != 'MULTIPLES' :
                totalCourse.append(courseList[courseCpt])
            courseCpt += 1

    newLine = 3

    for i in range(len(totalCourse)):

        if i == 0 or (totalCourse[i-1].dayContent != totalCourse[i].dayContent) :
            newLine += 1
            worksheet.set_row(newLine - 1, 22)
            worksheet.merge_range('A' + str(newLine) + ':' + totalLetters[-1] + str(newLine), weekDays[totalCourse[i].dayContent], bigfmt)
            newLine += 1

        msg = ' ' + totalCourse[i].groupContent + ', ' + totalCourse[i].moduleContent + ', ' + totalCourse[i].profContent + ' : ' + totalCourse[i].roomContent
        worksheet.merge_range('A' + str(newLine) + ':D' + str(newLine), totalCourse[i].timeContent[0] + '-' + totalCourse[i].timeContent[1], bigfmt)

        if len(msg) > 115 :
            worksheet.set_row(newLine - 1, 32)

        else :
            worksheet.set_row(newLine - 1, 18)
        
        worksheet.merge_range('E' + str(newLine) + ':' + totalLetters[-1] + str(newLine), msg, fmt)
        newLine += 1

        if totalCourse[i].noteContent != '- - -':
            if len(totalCourse[i].noteContent) > 115 :
                worksheet.set_row(newLine - 1, 32)
            else :
                worksheet.set_row(newLine - 1, 20)
            worksheet.merge_range('A' + str(newLine) + ':D' + str(newLine), 'Remarques', bigfmt)
            worksheet.merge_range('E' + str(newLine) + ':' + totalLetters[-1] + str(newLine), ' ' + totalCourse[i].noteContent, fmt)
            newLine += 1
    
    worksheet.print_area('A1:' + str(totalLetters[-1]) + str(newLine))

    return totalCourse, bigfmt, fmt


def avgTimeToStr(timeList : list[int]) -> str :
    """
        Get the average time from a list of times in minutes and return a str

        - Args :
            - timeList (list[int]) : list of times in minutes
        
        - Returns :
            - (str) : average time
    """
    rTime = sum(timeList) / len(timeList)
    hTime = 0
    mTime = 0
    hTime += int(rTime//60)
    mTime += round((rTime/60 - rTime//60) * 60)
    if mTime == 60 :
        mTime = 0
        hTime += 1
    hTime = str(hTime)
    mTime = str(mTime)
    if len(mTime) == 1:
        mTime = '0' + mTime
    return hTime + ':' + mTime


def statList(totalCourse : list[Course], worksheet, bigfmt : xlsxwriter.workbook.Format, fmt : xlsxwriter.workbook.Format, totalLetters : tuple, week : str) -> None :
    """
        Create and display some statistical data from a list of courses in a new page

        - Args :
            - totalCourse (list[Course]) : list of courses
            - worksheet (xlsx worksheet) : worksheet to write on
            - bigfmt (xlsxwriter format) : format for the big cells
            - fmt (xlsxwriter format) : format for the normal cells
            - totalLetters (tuple[str]) 
            - week (str) : week of the schedule

        - Returns :
            - None
    """
    moduleDic = {}
    for e in totalCourse :
        moduleDic[e.moduleContent] = 0
    for e in totalCourse :
        moduleDic[e.moduleContent] += e.duration

    moduleTime = list(moduleDic.values())

    sumTime = sum(moduleTime)

    fullTime = avgTimeToStr([sumTime])
    avgDailyTime = avgTimeToStr([sumTime//5])

    moduleTime.sort()
    moduleTime.reverse()
    for i in range(len(moduleDic)):
        moduleTime[i] = avgTimeToStr([moduleTime[i]])
    
    moduleName = list(moduleDic.keys())

    moduleName = [x for _, x in sorted(zip(list(moduleDic.values()), list(moduleDic.keys())))]
    moduleName.reverse()
    
    startList = []
    endList = []

    for i in range(len(totalCourse)):
        if i == 0 or (totalCourse[i-1].dayContent != totalCourse[i].dayContent) :
            startList.append(totalCourse[i].startMinutes)
        if i == len(totalCourse) - 1:
            endList.append(totalCourse[i].endMinutes)
        elif i != 0 and totalCourse[i-1].dayContent != totalCourse[i].dayContent :
            endList.append(totalCourse[i - 1].endMinutes)

    startTime = avgTimeToStr(startList)
    
    endTime = avgTimeToStr(endList)

    worksheet.set_row(0, 25)
    worksheet.merge_range('A1:' + totalLetters[-1] + '1', 'Statistiques des cours - semaine du ' + week[:2] + '/' + week[3:5] + '/' + week[-4:], bigfmt)
    newLine = 3

    worksheet.set_row(newLine - 1, 20)
    worksheet.merge_range('A' + str(newLine) + ':' + totalLetters[-1] + str(newLine), 'Horaires moyennes : ' + startTime + ' - ' + endTime, bigfmt)
    newLine += 1

    worksheet.set_row(newLine - 1, 20)
    worksheet.merge_range('A' + str(newLine) + ':' + str(totalLetters[-1]) + str(newLine), 'Temps de cours journalier moyen : ' + avgDailyTime, bigfmt)
    newLine += 1

    worksheet.set_row(newLine - 1, 20)
    worksheet.merge_range('A' + str(newLine) + ':' + str(totalLetters[-1]) + str(newLine), 'Total des heures de cours : ' + fullTime + ' - ' + str(len(totalCourse)) + ' cours', bigfmt)
    newLine += 2

    worksheet.set_row(newLine - 1, 20)
    worksheet.merge_range('A' + str(newLine) + ':' + str(totalLetters[-1]) + str(newLine), 'Durées cumulées pour chaque module', bigfmt)
    newLine += 1

    for i in range(len(moduleDic)):
        worksheet.set_row(newLine - 1, 25)
        worksheet.merge_range('A' + str(newLine) + ':' + str(totalLetters[len(totalLetters) - 10]) + str(newLine), ' ' + moduleName[i], fmt)
        worksheet.merge_range(str(totalLetters[len(totalLetters) - 9]) + str(newLine) + ':' + totalLetters[-1] + str(newLine), moduleTime[i], bigfmt)
        newLine += 1

    worksheet.print_area('A1:' + str(totalLetters[-1]) + str(newLine))


def createXlsx(courseList : list[list[Course]], overCourse : list[list[Course]], weekDesc : list[str], title : str, name : str) -> None:
    """
        Create a xlsx file from course list
        
        - Args :
            - courseList (tuple[list[Course]]) : list of courses
            - overCourse (list[list[Course]]) : list of overlapping courses
            - weekDesc (list[str]) : list of weeks' first days
            - title (str) : title of the schedule
            - name (str) : name of the output file

        - Returns :
            - None
    """
    workbook = xlsxwriter.Workbook(name + '.xlsx')

    cpt = 1
    for i in range (len(weekDesc)):
        worksheet = workbook.add_worksheet(str(weekDesc[i]))
        worksheet.center_vertically()
        dayFormat, underFormat, rightFormat, cornerFormat = setFormatWS(workbook)
        totalLetters = initWS(worksheet, ROW, COL)
        formatWS(worksheet, dayFormat, totalLetters, underFormat, rightFormat, cornerFormat, title, str(weekDesc[i]), ROW, COL)
        columnTime = setToColumn(courseList[i], totalLetters)
        addCourse(worksheet, columnTime, courseList[i], workbook)

        if len(overCourse[i]) > 0 or len(courseList[i]) > 0:
            worksheet = workbook.add_worksheet('Liste des cours ' + str(cpt))
            totalLetters = initWS(worksheet, ROW, COL)
            totalCourse, bigfmt, fmt = writeToList(workbook, worksheet, overCourse[i], courseList[i], weekDesc[i], totalLetters)
            worksheet = workbook.add_worksheet('Statistiques ' + str(cpt))
            totalLetters = initWS(worksheet, ROW, COL)
            statList(totalCourse, worksheet, bigfmt, fmt, totalLetters, weekDesc[i])
            cpt += 1
        
    workbook.close()


def createShortXlsx(courseList : list[list[Course]], overCourse : list[list[Course]], weekDesc : list[str], title : str, name : str, toDate : date = date.today()) -> None:
    """
        Create a xlsx file with only one day schedule from course list
    """
    workbook = xlsxwriter.Workbook(name + '.xlsx')

    wIndex, i = -1, 0
    while wIndex < 0 or i < len(weekDesc):
        compDate = datetime.strptime(weekDesc[i], "%d_%m_%Y").date()
        if ((compDate - toDate).days) <= 5 :
            wIndex = i
        i += 1
    
    chosenDay = list()
    for e in courseList[wIndex] :
        if e.dayContent == toDate.weekday() :
            chosenDay.append(e)
    
    worksheet = workbook.add_worksheet(str(weekDesc[wIndex]))
    worksheet.center_vertically()
    dayFormat, underFormat, rightFormat, cornerFormat = setFormatWS(workbook)
    totalLetters = initWS(worksheet, ROW_SHORT, COL, short = True)
    formatWS(worksheet, dayFormat, totalLetters, underFormat, rightFormat, cornerFormat, title, str(weekDesc[wIndex]), ROW_SHORT, COL, toDate.weekday())
    columnTime = setToColumn(chosenDay, totalLetters)
    addCourse(worksheet, columnTime, chosenDay, workbook, short = True)

    workbook.close()
