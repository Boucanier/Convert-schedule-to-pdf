"""
    Module containing utility functions for the scrapers
"""
from datetime import date, timedelta
from models.course import Course


def clear_text(txt : str) -> str :
    """
        Clean a text : Remove all unnecessary blank and new line characters
        
        - Args :
            - txt (str) : text to clean
            
        - Returns :
            - txt (str) : cleaned text
    """
    txt_letters = list(txt)

    if txt :
        if '\n' in txt or "'" in txt:
            txt_letters = list(txt)
            for (i, item) in enumerate(txt_letters) :
                if item == '\n':
                    if i == 0 :
                        txt_letters[i] = ''
                    else :
                        txt_letters[i] = ', '
                if item == "'" :
                    txt_letters[i] = "`"
        if txt_letters[0] == ' ':
            txt_letters[0] = ''
        if txt_letters[-1] == ' ':
            txt_letters[-1] = ''
        txt = ''.join(txt_letters)
    return txt


def sort_courses(course_list : list[Course]) -> tuple[list[list[Course]], list[list[Course]]]:
    """
        Check overlapping courses and divide all courses into 4 lists (2 per week)
            of normal courses and overlapping courses
        
        - Args :
            - courseList (list[Course]) : list of courses
        
        - Returns :
            - tcourseList (list) : list of normal courses
            - overCourse (list[Course]) : list of overlapping courses
    """
    course_w = [[] for _ in range(len(course_list))]

    for e in course_list :
        course_w[e.week_content].append(e)

    for e in course_w :
        e = check_multiple(e)

    over_course = [[] for i in range(len(course_list))]

    for i in range(len(course_list)):
        res = multiple_sort(course_w[i])
        course_w[i] = res[0]
        over_course[i] = res[1]

    return course_w, over_course


def multiple_sort(course_list : list[Course]) -> tuple[list[Course], list[Course]] :
    """
        Check which courses are overlapping and parse split into multiple lists
        
        - Args :
            - courseList (list[Course]) : list of courses
        
        - Returns :
            - gComp (list[Course]) : Courses that are not overlapping
            - nComp (list[Course]) : Courses that are overlapping
    """
    tempindex = []
    temp2index = []
    replace_course = []
    n_comp = []
    g_comp = []
    for e in course_list :
        if len(e.same_time) > 0 :
            tempindex.append(e.same_time)

    for e in tempindex:
        e.sort()
        for l in e :
            if e.count(l) > 1 :
                e.remove(l)

    tempindex_copy = tempindex.copy()
    for e in tempindex_copy:
        if tempindex.count(e) > 1:
            tempindex.remove(e)

    if len(tempindex) > 1 :
        for (i, item) in enumerate(tempindex):
            for (j, jtem) in enumerate(tempindex):
                if (i != j) and all(e in item for e in jtem) and item != jtem:
                    temp2index.append(jtem)

        tempindex = [e for e in tempindex if e not in temp2index]
        for (i, item) in enumerate(tempindex):
            for (j, jtem) in enumerate(item):
                for (k, ktem) in enumerate(tempindex):
                    if (i!=k) and jtem in ktem:
                        _tk = [tempindex[k].append(e) for e in item if e not in ktem]

        for e in tempindex :
            for k in e :
                if e.count(k) != 1:
                    e.remove(k)

        for e in tempindex :
            e.sort()

        for e in tempindex :
            if tempindex.count(e) != 1 :
                tempindex.remove(e)

    for e in tempindex :
        tempstart = 1140
        tempend = 0
        hstart = ''
        hend = ''
        for k in e :
            if course_list[k].start_minutes < tempstart :
                tempstart = course_list[k].start_minutes
                hstart = course_list[k].time_content[0]
            if course_list[k].end_minutes > tempend :
                tempend = course_list[k].end_minutes
                hend = course_list[k].time_content[1]

        replace_course.append(Course(course_list[e[0]].day_content,
                                     [hstart,hend],
                                     "COURS",
                                     "- - -",
                                     "MULTIPLES",
                                     "- - -",
                                     course_list[e[0]].week_content,
                                     "- - -",
                                     '7BEBFF'))

    for e in course_list:
        if len(e.same_time) != 0 :
            n_comp.append(e)

    g_comp = [e for e in course_list if e not in n_comp]
    _ge = [g_comp.append(e) for e in replace_course]

    return g_comp, n_comp


def check_multiple(course_list : list[Course]) -> list[Course]:
    """
        Check if several courses overlap themselves and add them to the sameTime list of each course
        
        - Args :
            - courseList (list[Course])
        
        - Returns :
            - courseList (list[Course])
    """
    for (i, item) in enumerate(course_list):
        for (j, jtem) in enumerate(course_list):
            if i != j :
                if not item.is_compatible(jtem):
                    if j not in list(item.same_time) :
                        item.same_time.append(j)
                    if i not in list(item.same_time) :
                        item.same_time.append(i)
    return course_list


def add_missing_weeks(week_desc : list[str]) -> list[str]:
    """
        Add missing weeks in the list of week description
        
        - Args :
            - weekDesc (list[str])
        
        - Returns :
            - weekDesc (list[str])
    """
    for i in range(len(week_desc)-1):
        curr_date = date(int(week_desc[i][-4:]),
                         int(week_desc[i][3:5]),
                         int(week_desc[i][:2]))

        next_date = date(int(week_desc[i+1][-4:]),
                         int(week_desc[i+1][3:5]),
                         int(week_desc[i+1][:2]))

        if (next_date - curr_date).days > 7 :
            for j in range(1, (next_date - curr_date).days // 7):
                week_desc.insert(i+j, (curr_date + timedelta(days = 7*j)).strftime("%d_%m_%Y"))

    return week_desc