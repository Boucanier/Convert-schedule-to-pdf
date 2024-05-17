"""
    This module will convert the data scrapped with the scrapper into a xlsx file
"""
import xlsxwriter
from datetime import date, datetime
from models.course import *


ROW = 27
COL = 133 #EC

ROW_SHORT = 7


def set_format_ws(workbook : xlsxwriter.Workbook) -> tuple[xlsxwriter.workbook.Format, xlsxwriter.workbook.Format, xlsxwriter.workbook.Format, xlsxwriter.workbook.Format]:
    '''
        Create formats used to set the sheet of the schedule in the xlsx document

        - Args :
            - workbook (xlsxwriter workbook) : workbook containing the schedule
        
        - Returns :
            - day_format (xlsxwriter format) : format for the days cells and more
            - under_format (xlsxwriter format) : format used to create the bottom border of the schedule
            - right_format (xlsxwriter format) : format used to create the right border of the schedule
            - corner_format (xlsxwriter format) : format used to create corner border of the schedule
    '''
    day_format = workbook.add_format()
    day_format.set_align('center')
    day_format.set_align('vcenter')
    day_format.set_font_name('Arial')
    day_format.set_font_size(13)
    day_format.set_text_wrap()
    day_format.set_border()
    day_format.set_bg_color('#DCDCDC')

    under_format = workbook.add_format()
    under_format.set_bottom()

    right_format = workbook.add_format()
    right_format.set_right()

    corner_format = workbook.add_format()
    corner_format.set_bottom()
    corner_format.set_right()

    return day_format, under_format, right_format, corner_format


def init_ws(worksheet, row : int, col : int, short : bool = False) -> tuple:
    """
        Initialize the worksheet by setting the size of the cells and the columns

        - Args :
            - worksheet (xlsx worksheet) : worksheet to initialize
            - row (int) : number of rows
            - col (int) : number of columns
            - short (bool) : default = False, if True : only format first day, else : format every day

        - Returns :
            - total_letters (tuple[str]) : tuple containing the letters of the columns (A, B, C, ..., AA, AB, ..., BA, BB, ...)
    """
    worksheet.set_landscape()
    worksheet.set_margins(left = 0.15, right = 0.15, top = 0.15, bottom = 0.15)
    worksheet.center_horizontally()
    letters = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')
    total_letters = list()
    for i in range(col):
        if i < 26 :
            total_letters.append(letters[i%26])
        else :
            total_letters.append(total_letters[(i//26)-1] + letters[i%26])

    worksheet.set_column('B:' + str(total_letters[-1]), 0.8)
    worksheet.set_column('A:A', 12)
    for i in range(row):
        worksheet.set_row((i+1),19)

    if short :
        worksheet.set_row(5, 25)
        worksheet.set_row(4, 25)

    else :
        for i in range(5):
            worksheet.set_row(5 + 5*i, 25)
            worksheet.set_row(4 + 5*i, 25)

    worksheet.set_row(1,20)

    worksheet.print_area('A1:' + str(total_letters[-1]) + str(row))

    if short :
        worksheet.set_paper(8)
    else :
        worksheet.set_paper(9)

    worksheet.fit_to_pages(1, 0)
    total_letters = tuple(total_letters)

    return total_letters


def format_ws(worksheet, day_format : xlsxwriter.workbook.Format, total_letters : tuple, under_format : xlsxwriter.workbook.Format, right_format : xlsxwriter.workbook.Format, corner_format : xlsxwriter.workbook.Format, title : str, week : str, row : int, col : int, day_ind : int = 5) -> None:
    """
        Set the frame for the schedule with days and times

        - Args :
            - worksheet (xlsx worksheet) : worksheet in which the formats will be applied
            - day_format (xlsxwriter format) : format for the days cells
            - total_letters (tuple[str])
            - under_format (xlsxwriter format) : format used to create the bottom border of the schedule
            - right_format (xlsxwriter format) : format used to create the right border of the schedule
            - corner_format (xlsxwriter format) : format used to create corner border of the schedule
            - title (str) : title of the schedule
            - row (int) : Number of rows
            - col (int) : Number of columns
            - day_ind (int) : Day of week index, default = 5, day_ind > 5 means all week is requested

        - Returns :
            - None
    """
    week_days = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi')

    if day_ind < 5 :
        week_days = [week_days[day_ind]]

    for i in range(0, row - 2, 5):
        worksheet.merge_range('A' + str(i+3) + ':A' + str(i+7), week_days[i//5], day_format)
    list_week = list(week)
    for i in range(len(list_week)):
        if list_week[i] == '_':
            list_week[i] = '/'
    week = ''.join(list_week)
    worksheet.merge_range('B1:' + str(total_letters[-1]) + '1', title + ', semaine du ' + week, day_format)
    worksheet.set_row(0,25)
    for i in range(1, col-10, 12):
        worksheet.merge_range(str(total_letters[i]) + '2:' + str(total_letters[i+11]) + '2', str(round(i/12)+8) + ':00 - ' + str(round(i/12)+9) + ':00', day_format)
    for i in range(3, row + 1) :
        worksheet.write_blank(str(total_letters[-1]) + str(i), None, right_format)
    for i in range(1, col):
        worksheet.write_blank(str(total_letters[i]) + str(row), None, under_format)
    worksheet.write_blank(str(total_letters[-1]) + str(row), None, corner_format)


def set_to_column(course_list : list[Course], total_letters : tuple) -> list[list[list[str]]] :
    """
        Get the range of column at the xlsx format for every course

        - Args :
            - course_list (list[Course])
            - total_letters (tuple[str])
        
        - Returns :
            - time_column (list[list[list[str]]])
    """
    time_column = []
    for j in range(len(course_list)):
        temp_list = []
        for i in range(2):
            temp_time = 0
            temp_time += (int(((course_list[j].time_content)[i].split(':'))[0])-8) * 12 + 1 + int(((course_list[j].time_content)[i].split(':'))[1])//5 - i
            temp_list.append(total_letters[temp_time])
        time_column.append(temp_list)
    return time_column


def add_course(worksheet, column_time : list, course_list : list, workbook : xlsxwriter.Workbook, short : bool = False) -> None:
    """
        Create formats used to add course\n
        Add a course to the xlsx file
        
        - Args :
            - worksheet (xlsx worksheet)
            - columntime (list)
            - course_list (list[Course])
            - workbook (xlsx workbook)
            - short (bool) : default False, if True : add course to first row only
    """
    fmt_list = [[],[],[]]
    for e in course_list :
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
        topfmt.set_bg_color(e.color_content)
        fmt_list[0].append(topfmt)

        fmt = workbook.add_format()
        fmt.set_align('center')
        fmt.set_align('vcenter')
        fmt.set_font_name('Arial')
        fmt.set_font_size(11)
        fmt.set_text_wrap()
        fmt.set_right()
        fmt.set_left()
        fmt.set_shrink()
        fmt.set_bg_color(e.color_content)
        fmt_list[1].append(fmt)

        botfmt = workbook.add_format()
        botfmt.set_align('center')
        botfmt.set_align('vcenter')
        botfmt.set_font_name('Arial')
        botfmt.set_font_size(13)
        botfmt.set_text_wrap()
        botfmt.set_right()
        botfmt.set_left()
        botfmt.set_bottom()
        botfmt.set_bg_color(e.color_content)
        fmt_list[2].append(botfmt)

    for i in range(len(course_list)):
        if short :
            row_nbr = 3
        else :
            row_nbr = int(course_list[i].day_content)*5+3

        worksheet.merge_range(column_time[i][0] + str(row_nbr) + ':' + column_time[i][1] + str(row_nbr), course_list[i].time_content[0] + ' - ' + course_list[i].time_content[1], fmt_list[0][i])
        worksheet.merge_range(column_time[i][0] + str(row_nbr + 1) + ':' + column_time[i][1] + str(row_nbr + 1), course_list[i].group_content, fmt_list[1][i])
        worksheet.merge_range(column_time[i][0] + str(row_nbr + 2) + ':' + column_time[i][1] + str(row_nbr + 2), course_list[i].module_content, fmt_list[1][i])
        worksheet.merge_range(column_time[i][0] + str(row_nbr + 3) + ':' + column_time[i][1] + str(row_nbr + 3), course_list[i].prof_content, fmt_list[1][i])
        worksheet.merge_range(column_time[i][0] + str(row_nbr + 4) + ':' + column_time[i][1] + str(row_nbr + 4), course_list[i].room_content, fmt_list[2][i])


def write_to_list(workbook : xlsxwriter.Workbook, worksheet, over_course : list, course_list : list, week : str, total_letters : tuple) -> tuple[list[Course], xlsxwriter.workbook.Format, xlsxwriter.workbook.Format]:
    """
        Write a list of every courses

        - Args :
            - workbook (xlsx workbook) : workbook containing the schedule
            - worksheet (xlsx worksheet) : worksheet to write on
            - over_course (list[Course]) : list of overlapping courses
            - week (str) : week of the schedule
            - total_letters (tuple[str])

        - Returns :
            - total_course (list[Course])
            - bigfmt (xlsxwriter format)
            - fmt (xlsxwriter format)
    """
    week_days = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi')

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
    worksheet.merge_range('A1:' + total_letters[-1] + '1', 'Liste des cours - semaine du ' + week[:2] + '/' + week[3:5] + '/' + week[-4:], bigfmt)

    over_cpt = 0
    course_cpt = 0
    total_course = []

    while over_cpt < len(over_course) or course_cpt < len(course_list):
        if (over_cpt < len(over_course) and course_cpt < len(course_list) and over_course[over_cpt].start_before(course_list[course_cpt])) or course_cpt == len(course_list):
            total_course.append(over_course[over_cpt])
            over_cpt += 1
        else :
            if course_list[course_cpt].prof_content != 'MULTIPLES' :
                total_course.append(course_list[course_cpt])
            course_cpt += 1

    new_line = 3

    for i in range(len(total_course)):

        if i == 0 or (total_course[i-1].day_content != total_course[i].day_content) :
            new_line += 1
            worksheet.set_row(new_line - 1, 22)
            worksheet.merge_range('A' + str(new_line) + ':' + total_letters[-1] + str(new_line), week_days[total_course[i].day_content], bigfmt)
            new_line += 1

        msg = ' ' + total_course[i].group_content + ', ' + total_course[i].module_content + ', ' + total_course[i].prof_content + ' : ' + total_course[i].room_content
        worksheet.merge_range('A' + str(new_line) + ':D' + str(new_line), total_course[i].time_content[0] + '-' + total_course[i].time_content[1], bigfmt)

        if len(msg) > 115 :
            worksheet.set_row(new_line - 1, 32)

        else :
            worksheet.set_row(new_line - 1, 18)

        worksheet.merge_range('E' + str(new_line) + ':' + total_letters[-1] + str(new_line), msg, fmt)
        new_line += 1

        if total_course[i].note_content != '- - -':
            if len(total_course[i].note_content) > 115 :
                worksheet.set_row(new_line - 1, 32)
            else :
                worksheet.set_row(new_line - 1, 20)
            worksheet.merge_range('A' + str(new_line) + ':D' + str(new_line), 'Remarques', bigfmt)
            worksheet.merge_range('E' + str(new_line) + ':' + total_letters[-1] + str(new_line), ' ' + total_course[i].note_content, fmt)
            new_line += 1

    worksheet.print_area('A1:' + str(total_letters[-1]) + str(new_line))

    return total_course, bigfmt, fmt


def avg_time_to_str(time_list : list[int]) -> str :
    """
        Get the average time from a list of times in minutes and return a str

        - Args :
            - time_list (list[int]) : list of times in minutes
        
        - Returns :
            - (str) : average time
    """
    r_time = sum(time_list) / len(time_list)
    h_time = 0
    m_time = 0
    h_time += int(r_time//60)
    m_time += round((r_time/60 - r_time//60) * 60)
    if m_time == 60 :
        m_time = 0
        h_time += 1
    h_time = str(h_time)
    m_time = str(m_time)
    if len(m_time) == 1:
        m_time = '0' + m_time
    return h_time + ':' + m_time


def stat_list(total_course : list[Course], worksheet, bigfmt : xlsxwriter.workbook.Format, fmt : xlsxwriter.workbook.Format, total_letters : tuple, week : str) -> None :
    """
        Create and display some statistical data from a list of courses in a new page

        - Args :
            - total_course (list[Course]) : list of courses
            - worksheet (xlsx worksheet) : worksheet to write on
            - bigfmt (xlsxwriter format) : format for the big cells
            - fmt (xlsxwriter format) : format for the normal cells
            - total_letters (tuple[str]) 
            - week (str) : week of the schedule

        - Returns :
            - None
    """
    module_dic = {}
    for e in total_course :
        module_dic[e.module_content] = 0
    for e in total_course :
        module_dic[e.module_content] += e.duration

    module_time = list(module_dic.values())

    sum_time = sum(module_time)

    full_time = avg_time_to_str([sum_time])
    avg_daily_time = avg_time_to_str([sum_time//5])

    module_time.sort()
    module_time.reverse()
    for i in range(len(module_dic)):
        module_time[i] = avg_time_to_str([module_time[i]])

    module_name = list(module_dic.keys())

    module_name = [x for _, x in sorted(zip(list(module_dic.values()), list(module_dic.keys())))]
    module_name.reverse()

    start_list = []
    end_list = []

    for i in range(len(total_course)):
        if i == 0 or (total_course[i-1].day_content != total_course[i].day_content) :
            start_list.append(total_course[i].start_minutes)
        if i == len(total_course) - 1:
            end_list.append(total_course[i].end_minutes)
        elif i != 0 and total_course[i-1].day_content != total_course[i].day_content :
            end_list.append(total_course[i - 1].end_minutes)

    start_time = avg_time_to_str(start_list)
    end_time = avg_time_to_str(end_list)

    worksheet.set_row(0, 25)
    worksheet.merge_range('A1:' + total_letters[-1] + '1', 'Statistiques des cours - semaine du ' + week[:2] + '/' + week[3:5] + '/' + week[-4:], bigfmt)
    new_line = 3

    worksheet.set_row(new_line - 1, 20)
    worksheet.merge_range('A' + str(new_line) + ':' + total_letters[-1] + str(new_line), 'Horaires moyennes : ' + start_time + ' - ' + end_time, bigfmt)
    new_line += 1

    worksheet.set_row(new_line - 1, 20)
    worksheet.merge_range('A' + str(new_line) + ':' + str(total_letters[-1]) + str(new_line), 'Temps de cours journalier moyen : ' + avg_daily_time, bigfmt)
    new_line += 1

    worksheet.set_row(new_line - 1, 20)
    worksheet.merge_range('A' + str(new_line) + ':' + str(total_letters[-1]) + str(new_line), 'Total des heures de cours : ' + full_time + ' - ' + str(len(total_course)) + ' cours', bigfmt)
    new_line += 2

    worksheet.set_row(new_line - 1, 20)
    worksheet.merge_range('A' + str(new_line) + ':' + str(total_letters[-1]) + str(new_line), 'Durées cumulées pour chaque module', bigfmt)
    new_line += 1

    for i in range(len(module_dic)):
        worksheet.set_row(new_line - 1, 25)
        worksheet.merge_range('A' + str(new_line) + ':' + str(total_letters[len(total_letters) - 10]) + str(new_line), ' ' + module_name[i], fmt)
        worksheet.merge_range(str(total_letters[len(total_letters) - 9]) + str(new_line) + ':' + total_letters[-1] + str(new_line), module_time[i], bigfmt)
        new_line += 1

    worksheet.print_area('A1:' + str(total_letters[-1]) + str(new_line))


def create_xlsx(course_list : list[list[Course]], over_course : list[list[Course]], week_desc : list[str], title : str, name : str) -> None:
    """
        Create a xlsx file from course list
        
        - Args :
            - course_list (tuple[list[Course]]) : list of courses
            - over_course (list[list[Course]]) : list of overlapping courses
            - weekDesc (list[str]) : list of weeks' first days
            - title (str) : title of the schedule
            - name (str) : name of the output file

        - Returns :
            - None
    """
    workbook = xlsxwriter.Workbook(name + '.xlsx')

    cpt = 1
    for i in range (len(week_desc)):
        worksheet = workbook.add_worksheet(str(week_desc[i]))
        worksheet.center_vertically()
        day_format, under_format, right_format, corner_format = set_format_ws(workbook)
        total_letters = init_ws(worksheet, ROW, COL)
        format_ws(worksheet, day_format, total_letters, under_format, right_format, corner_format, title, str(week_desc[i]), ROW, COL)
        column_time = set_to_column(course_list[i], total_letters)
        add_course(worksheet, column_time, course_list[i], workbook)

        if len(over_course[i]) > 0 or len(course_list[i]) > 0:
            worksheet = workbook.add_worksheet('Liste des cours ' + str(cpt))
            total_letters = init_ws(worksheet, ROW, COL)
            total_course, bigfmt, fmt = write_to_list(workbook, worksheet, over_course[i], course_list[i], week_desc[i], total_letters)
            worksheet = workbook.add_worksheet('Statistiques ' + str(cpt))
            total_letters = init_ws(worksheet, ROW, COL)
            stat_list(total_course, worksheet, bigfmt, fmt, total_letters, week_desc[i])
            cpt += 1

    workbook.close()


def create_short_xlsx(course_list : list[list[Course]], week_desc : list[str], title : str, name : str, to_date : date = date.today()) -> None:
    """
        Create a xlsx file with only one day schedule from course list
    """
    workbook = xlsxwriter.Workbook(name + '.xlsx')

    w_index, i = -1, 0
    while w_index < 0 or i < len(week_desc):
        comp_date = datetime.strptime(week_desc[i], "%d_%m_%Y").date()
        if ((comp_date - to_date).days) <= 5 :
            w_index = i
        i += 1

    chosen_day = list()
    for e in course_list[w_index] :
        if e.day_content == to_date.weekday() :
            chosen_day.append(e)

    worksheet = workbook.add_worksheet(str(week_desc[w_index]))
    worksheet.center_vertically()
    day_format, under_format, right_format, corner_format = set_format_ws(workbook)
    total_letters = init_ws(worksheet, ROW_SHORT, COL, short = True)
    format_ws(worksheet, day_format, total_letters, under_format, right_format, corner_format, title, str(week_desc[w_index]), ROW_SHORT, COL, to_date.weekday())
    column_time = set_to_column(chosen_day, total_letters)
    add_course(worksheet, column_time, chosen_day, workbook, short = True)

    workbook.close()
