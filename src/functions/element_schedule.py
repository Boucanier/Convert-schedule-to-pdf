"""
    This code contains functions that will be used
    to fetch a specific schedule based on a room/professor
"""
from functions import scraper
from models.course import Course


def get_full_schedule(url_list :list[str],
                      title_list : list[str]) -> tuple[list[list[Course]], list[str]]:
    """
        Get every available schedule from a list of url and title,
        parse them and return a list with every schedule

        - Args :
            - urlList (list[str]) : list of schedules' urls
            - titleList (list[str]) : list of schedules' titles

        - Returns :
            - courseFullList (list[list[Course]]) : list containing list of every schedule
            - weekDesc (list[str]) : list of weeks' first days
    """
    course_full_list = []
    week_desc = []

    # If the url is a string, convert url and title to a list for the further loop
    if isinstance(url_list, str) :
        url_list = [url_list]

    if isinstance(title_list, str) :
        title_list = [title_list]

    for (i, item) in enumerate(url_list):
        response = scraper.get_schedule(item)

        course_list, week_desc = scraper.parse_schedule(response)
        course_full_list.append(course_list)
        print(title_list[i] + " : " + str(len(course_list)) + " cours\n")

    return course_full_list, week_desc


def get_full_list(course_full_list : list[list[Course]], element : str) -> list[str]:
    """
        Get every schedule available,
            then extract the list of every different element using function clearElement()

        - Args :
            - courseFullList (list[list[Course]]) : list containing list of schedule link and list of schedule title

        - Returns :
            - elementList (list[str]) : list of every different element
    """

    element_list = []

    if element == "staff" :
        for e in course_full_list :
            for k in e :
                if k.prof_content not in element_list :
                    element_list.append(k.prof_content)

    elif element == "room" :
        for e in course_full_list :
            for k in e :
                if k.room_content not in element_list :
                    element_list.append(k.room_content)

    elif element == "module" :
        for e in course_full_list :
            for k in e :
                if k.module_content not in element_list :
                    element_list.append(k.module_content)

    elif element == "groups" :
        for e in course_full_list :
            for k in e :
                if k.group_content not in element_list :
                    element_list.append(k.group_content)

    if element != "module" :
        element_list = clear_element(element_list)

    return element_list


def clear_element(element_list : list[str]) -> list[str]:
    """
        Check if many elements are assigned to a single course
        and add them to the main element list if they are not already in it

        - Args :
            - elementList (list[str])
        
        - Returns :
            - elementList (list[str])
    """
    to_remove = []
    to_add = []
    for (i, item) in enumerate(element_list):
        if ',' in element_list[i] :
            to_remove.append(item)
            temp_element_list = item.split(', ')
            _ta = [to_add.append(e) for e in temp_element_list]

    for e in to_add :
        if e not in element_list :
            element_list.append(e)

    for e in to_remove :
        element_list.remove(e)

    return element_list


def choose_element(element_list : list[str]) -> str :
    """
        Display the list of every element and ask the user to choose an element

        - Args :
            - elementList (list[str])
        
        - Returns :
            - (str)
    """
    element_list.sort()
    for (i, item) in enumerate(element_list) :
        print(i, item)

    choice = -1

    while not 0 <= int(choice) <= len(element_list) - 1 :
        choice = input("\nChoix : ")
        if choice.isdigit() and (0 <= int(choice) <= len(element_list) - 1) :
            choice = int(choice)
        else :
            print("Selectionner une option VALIDE")
            choice = -1

    print(element_list[choice] + '\n')

    return element_list[choice]


def get_course_element(element_choice : str, course_list : list[list[Course]], element : str) :
    """
        Merge every course of a specified element from every schedule in a single schedule

        - Args :
            - elementChoice (str)
            - courseList (list[list[Course]])

        - Returns :
            - courseFullList (list[Course])
    """
    course_full_list = []

    if element == "staff" :
        for e in course_list :
            for k in e :
                if k.prof_content == element_choice :
                    course_full_list.append(k)
                elif element_choice in (k.prof_content).split(", "):
                    course_full_list.append(k)

    elif element == "room" :
        for e in course_list :
            for k in e :
                if k.room_content == element_choice :
                    course_full_list.append(k)
                elif element_choice in (k.room_content).split(", "):
                    course_full_list.append(k)

    return course_full_list


def check_equals(course_list : list[Course]) -> list[Course]:
    """
        Check if many courses are similar and keep only one in the list

        Then sort the list of course regarding the days

        - Args :
            - courseList (list[Course])

        - Returns :
            - courseList (list[Course])
    """
    to_remove = []
    int_to_remove = []

    for (i, item) in enumerate(course_list):
        for (j, jtem) in enumerate(course_list):
            if i != j and i not in int_to_remove :
                if item == jtem :
                    to_remove.append(jtem)
                    int_to_remove.append(j)

    for e in to_remove :
        course_list.remove(e)

    n = len(course_list)

    for i in range(n):
        for j in range(0, n-i-1):
            if course_list[j].day_content > course_list[j+1].day_content :
                course_list[j], course_list[j+1] = course_list[j+1], course_list[j]

    return course_list


def get_full_detailed_list(course_list : list[list[Course]]) -> list[list[Course]] :
    """
        Get every course of a schedule and split them if they are assigned to many elements
        except for modules (maybe there are commas in module names)

        - Args :
            - courseList (list[list[Course]])

        - Returns :
            - courseList (list[list[Course]]) : updated list of courses
    """
    to_remove = []

    for e in course_list :
        for k in e :
            if ", " in k.prof_content :
                to_remove.append(k)
                for i in range(len(k.prof_content.split(', '))):
                    e.append(Course(str(k.day_content),
                                    k.time_content,
                                    k.module_content,
                                    k.room_content,
                                    (k.prof_content.split(", "))[i],
                                    k.group_content,
                                    k.week_content,
                                    k.note_content,
                                    k.color_content))

        _rmk = [e.remove(k) for k in to_remove]
        to_remove.clear()
        e = check_equals(e)
        for k in e :
            if ", " in k.room_content :
                to_remove.append(k)
                for i in range(len(k.room_content.split(', '))):
                    e.append(Course(str(k.day_content),
                                    k.time_content,
                                    k.module_content,
                                    (k.room_content.split(", "))[i],
                                    k.prof_content,
                                    k.group_content,
                                    k.week_content,
                                    k.note_content,
                                    k.color_content))

        _rmk = [e.remove(k) for k in to_remove]
        to_remove.clear()
        e = check_equals(e)
        for k in e :
            if ", " in k.group_content :
                to_remove.append(k)
                for i in range(len(k.group_content.split(', '))):
                    e.append(Course(str(k.day_content),
                                    k.time_content,
                                    k.module_content,
                                    k.room_content,
                                    k.prof_content,
                                    (k.group_content.split(", "))[i],
                                    k.week_content,
                                    k.note_content,
                                    k.color_content))

        _rmk = [e.remove(k) for k in to_remove]
        to_remove.clear()
        e = check_equals(e)
        n = len(e)
        for i in range(n):
            for j in range(0, n-i-1):
                if e[j].day_content > e[j+1].day_content :
                    e[j], e[j+1] = e[j+1], e[j]
        for i in range(n):
            for j in range(0, n-i-1):
                if e[j].week_content > e[j+1].week_content :
                    e[j], e[j+1] = e[j+1], e[j]

    return course_list


def merge_course(course_list : list[Course]) -> list[Course]:
    """
        Merge course with same module and time content into one course

        - Args :
            - courseList (list[Course])

        - Returns :
            - courseList (list[Course]) : list of courses with merged courses
    """
    merged_course = []
    multiple_id = []
    first_id = []
    for i in range(len(course_list) - 1) :
        cpt = 0
        temp_id = []
        stop = False
        for (j, jtem) in enumerate(multiple_id) :
            if i in jtem :
                stop = True

        if not stop :
            while (i + cpt + 1 < len(course_list))\
                and (course_list[i].module_content == course_list[i + cpt + 1].module_content)\
                and (course_list[i].time_content == course_list[i + cpt + 1].time_content)\
                and (course_list[i].day_content == course_list[i + cpt + 1].day_content) :

                temp_id.append(i + cpt + 1)
                cpt += 1

            if cpt > 0 :
                first_id.append(i)
                multiple_id.append(temp_id)
                merged_course.append(course_list[i])

    for (i, item) in enumerate(first_id) :
        for j in range(len(multiple_id[i])) :
            merged_course[i].merge(course_list[multiple_id[i][j]])

        course_list[item] = merged_course[i]

    cpt = 0
    for (i, item) in enumerate(multiple_id) :
        for (j, jtem) in enumerate(item) :
            course_list.pop(jtem - cpt)
            cpt += 1

    return course_list
