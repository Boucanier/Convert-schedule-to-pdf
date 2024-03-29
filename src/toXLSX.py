"""
    This module will convert the data scrapped with the scrapper into a xlsx file
"""
import xlsxwriter


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
    worksheet.set_margins(left = 0.15, right = 0.15, top = 0.15, bottom = 0.15)
    worksheet.center_horizontally()
    letters = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')
    totalLetters = []
    for i in range(COL):
        if i < 26 :
            totalLetters.append(letters[i%26])
        else :
            totalLetters.append(totalLetters[(i//26)-1] + letters[i%26])
    worksheet.set_column('B:' + str(totalLetters[-1]), 0.8)
    worksheet.set_column('A:A', 12)
    for i in range(ROW):
        worksheet.set_row((i+1),19)
    for i in range(5):
        worksheet.set_row(5 + 5*i, 25)
        worksheet.set_row(4 + 5*i, 25)
    worksheet.set_row(1,20)
    worksheet.print_area('A1:' + str(totalLetters[-1]) + str(ROW))
    worksheet.set_paper(9)
    worksheet.fit_to_pages(1, 0)
    totalLetters = tuple(totalLetters)
    return totalLetters
    

def formatWS(worksheet, dayFormat, totalLetters : tuple[str], underFormat, rightFormat, cornerFormat, title : str, week : str) -> None:
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
    weekDays = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi')
    for i in range(0,ROW - 2,5):
        worksheet.merge_range('A' + str(i+3) + ':A' + str(i+7), weekDays[i//5], dayFormat)
    listWeek = list(week)
    for i in range(len(listWeek)):
        if listWeek[i] == '_':
            listWeek[i] = '/'
    week = ''.join(listWeek)
    worksheet.merge_range('B1:' + str(totalLetters[-1]) + '1', title + ', semaine du ' + week, dayFormat)
    worksheet.set_row(0,25)
    for i in range(1,COL-10,12):
        worksheet.merge_range(str(totalLetters[i]) + '2:' + str(totalLetters[i+11]) + '2', str(round(i/12)+8) + ':00 - ' + str(round(i/12)+9) + ':00', dayFormat)
    for i in range(3,ROW + 1) :
        worksheet.write_blank(str(totalLetters[-1]) + str(i), None, rightFormat)
    for i in range(1,COL):
        worksheet.write_blank(str(totalLetters[i]) + str(ROW), None, underFormat)
    worksheet.write_blank(str(totalLetters[-1]) + str(ROW), None, cornerFormat)


def setToColumn(courseList : list, totalLetters : tuple[str]) -> list[list[list[str]]] :
    """
        Get the range of column at the xlsx format for every course

        Args :
            - courseList (list[Course])
            - totalLetters (tuple[str])
        
        Returns :
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


def addCourse(worksheet, columnTime : list, courseList : list, workbook) -> None:
    """
        Create formats used to add course\n
        Add a course to the xlsx file
        
        - Args :
            - worksheet (xlsx worksheet)
            - columntime (list)
            - courseList (list[Course])
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


def writeToList(workbook, worksheet, overCourse : list, courseList : list, week : str, totalLetters : tuple[str]):
    """
        Write a list of every courses

        Args :
            - workbook
            - worksheet
            - overCourse (list[Course])
            - week (str)
            - totalLetters (tuple[str])
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
            - timeList (list[int])
        
        - Returns :
            - (str)
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


def statList(totalCourse : list, worksheet, bigfmt, fmt, totalLetters : tuple[str], week : str) -> None :
    """
        Create and display some statistical data from a list of courses in a new page

        - Args :
            - totalCourse (list[Course])
            - worksheet
            - bigfmt
            - fmt
            - totalLetters (tuple[str])
            - week (str)
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


def createXlsx(courseList : tuple, overCourse : list, weekDesc : list[str], title : str) -> None:
    """
        Create a xlsx file from course list of 4 weeks and then convert it to a pdf file
        
        - Args :
            - courseList (tuple[list[Course]])
            - weekDesc (list[str])
            - title (str)
    """
    workbook = xlsxwriter.Workbook('schedule.xlsx')

    cpt = 1
    for i in range (len(weekDesc)):
        worksheet = workbook.add_worksheet(str(weekDesc[i]))
        worksheet.center_vertically()
        dayFormat, underFormat, rightFormat, cornerFormat = setFormatWS(workbook)
        totalLetters = initWS(worksheet)
        formatWS(worksheet, dayFormat, totalLetters, underFormat, rightFormat, cornerFormat, title, str(weekDesc[i]))
        columnTime = setToColumn(courseList[i], totalLetters)
        addCourse(worksheet, columnTime, courseList[i], workbook)

        if len(overCourse[i]) > 0 or len(courseList[i]) > 0:
            worksheet = workbook.add_worksheet('Liste des cours ' + str(cpt))
            totalLetters = initWS(worksheet)
            totalCourse, bigfmt, fmt = writeToList(workbook, worksheet, overCourse[i], courseList[i], weekDesc[i], totalLetters)
            worksheet = workbook.add_worksheet('Statistiques ' + str(cpt))
            totalLetters = initWS(worksheet)
            statList(totalCourse, worksheet, bigfmt, fmt, totalLetters, weekDesc[i])
            cpt += 1
        
    workbook.close()
