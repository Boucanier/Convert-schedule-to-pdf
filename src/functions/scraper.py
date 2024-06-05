"""
    This code will scrap the schedule data with requests\n
    It will parse it using beauriful soup in objects of a "Course" class
"""
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup
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


def get_content(day_content : list[str],
                week_content : list[int],
                resource_list : list) -> list[Course]:
    """
        Collect all the _content of a type for every resource in the xml file
        and create every Course with it
        
        - Args :
            - day_content (list[str])
            - week_content (list[int])
            - resourceList (list)
        
        - Returns :
            - courseList (list[Course])
    """

    course_list = []
    element_list = ["starttime", "endtime", "module", "room", "staff", "group", "notes"]

    cpt = 0
    for resource in resource_list :
        param_list = []
        for element in element_list :
            if not resource.find(element):
                param_list.append("- - -")
            else :
                param_list.append(clear_text((resource.find(element)).text))
        param_list.append(resource['colour'])
        course_list.append(Course(day_content[cpt],
                                  [param_list[0],
                                   param_list[1]],
                                   param_list[2],
                                   param_list[3],
                                   param_list[4],
                                   param_list[5],
                                   week_content[cpt],
                                   param_list[6],
                                   param_list[7]))
        cpt += 1

    return course_list


def menu(group_list : list[str], link_list : list[str], group_choice = -1) -> tuple[str, str]:
    """
        Display the list of all group and ask the user the one he wants
        if groupChoice == -1, if not, do not display the menu
        
        - Args :
            - groupList (list)
            - linkList (list)
            - groupChoice (int) : Default value = -1
            
        - Returns :
            - (tuple[str, str])
    """
    if group_choice == -1 :
        for (i, item) in enumerate(group_list):
            print(i, item)

        group_choice = input('\nGroupe : ')

        if group_choice.isdigit() and (int(group_choice) in (range(len(group_list)))) :
            group_choice = int(group_choice)
        else :
            print("Selectionner un groupe VALIDE\n")
            group_choice = len(group_list) + 1

        while group_choice not in (range(len(group_list))) :
            group_choice = input("Groupe : ")
            if group_choice.isdigit() and (int(group_choice) in (range(len(group_list)))) :
                group_choice = int(group_choice)
            else :
                print("Selectionner une option VALIDE\n")
                group_choice = len(group_list) + 1

        print(group_list[group_choice])

    full_url = "http://chronos.iut-velizy.uvsq.fr/EDT/" + link_list[group_choice]

    return full_url, group_list[group_choice]


def get_link(full_list : bool = False, chosen_group_name = None) -> tuple :
    """
        Get the url for the requested schedule and its name after calling menu

        - Args :
            - fullList (boolean) : Default value = False,
                if True, get every available course in a list with group name
                using a loop and function menu()

            - chosenGroupName (str) : Default value = None,
                if not None, get the url and the group name of the schedule with the specified name
        
        - Returns :
            - link (str) : (if not fullList) schedule url
            - group (str) : (if not fullList) group name
            - linkFullList (list[str]) : (if fullList) list _containing schedule links
            - groupList (list[str]) : (if fullList) list _containing group names
    """
    url = "http://chronos.iut-velizy.uvsq.fr/EDT/finder.xml"

    response = requests.get(url, timeout=5)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    soup = BeautifulSoup(response.content, "lxml")

    group_list = soup.findAll('name')
    group_list = [e.text for e in group_list]

    link_list = soup.findAll('link',  {"class": "xml"})
    link_list = [e['href'] for e in link_list]

    # If the user has chosen a group name, return the link and the group name of the schedule
    if chosen_group_name :
        for (i, item) in enumerate(group_list) :
            if clear_text(item) == chosen_group_name :
                return ("http://chronos.iut-velizy.uvsq.fr/EDT/" + link_list[i]), item

        # If the group name is not found, return None
        return None, None

    if not full_list :
        link, group = menu(group_list, link_list)

        return link, group

    else :
        link_full_list = []
        for i in range(len(link_list)) :
            link = menu(group_list, link_list, i)[0]
            link_full_list.append(link)

        return link_full_list, group_list


def get_schedule(url : str) -> requests.models.Response :
    """
        Get response of the requested schedule
        
        - Args :
            - url (str)
        
        - Returns :
            - response (response)
    """
    response = requests.get(url, timeout=5)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    return response


def sort_sourse(course_list : list[Course]) -> tuple[list[list[Course]], list[list[Course]]]:
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


def get_week(soup : BeautifulSoup) -> list[int]:
    """
        Get in which week is a course in the next 4 weeks
        
        - Args :
            - soup (BeautifulSoup soup)
        
        - Returns :
            - w_content (list)
    """
    w_content = []

    rs = soup.findAll('rawweeks')
    rs = [clear_text(e.text) for e in rs]

    _min = len(rs[0])
    max_week = 0

    for e in rs :
        y = 0
        while e[y] != 'Y':
            y += 1
        if y < _min :
            _min = y
        if y > max_week :
            max_week = y

    for e in rs :
        y = 0
        while e[y] != 'Y':
            y += 1

        w_content.append(y-_min)

    return w_content


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


def parse_schedule(response : requests.models.Response) -> tuple[list[Course], list[str]]:
    """
        Main function of the scrapper module
        
        - Args :
            - response (xml request response)
            
        - Returns :
            - courseList (list[Course])
            - weekDesc (list[str])
    """
    course_list = []
    soup = BeautifulSoup(response.content, "lxml")

    resource_list = soup.find_all("event")

    week_full = soup.find_all("description")
    t_week = [(e.text)[-10:] for e in week_full]
    week_desc = []

    for e in t_week:
        temp = ''
        for ei in e :
            if ei == "/":
                temp += "_"
            else :
                temp += ei
        week_desc.append(temp)

    week_desc = add_missing_weeks(week_desc)

    week_content = get_week(soup)

    day_temp = soup.findAll("day")
    day_content = []
    for i in range(1, len(resource_list) + 1):
        day_content += day_temp[-i]
    day_content.reverse()

    course_list = get_content(day_content, week_content, resource_list)

    return course_list, week_desc
