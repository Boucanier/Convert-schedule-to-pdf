"""
    This code will scrap the schedule data with requests\n
    It will parse it using beauriful soup in objects of a "Course" class
"""
import requests
from bs4 import BeautifulSoup
from course import *


def clearText(txt : str) -> str :
    """
        Clean a text : Remove all unnecessary blank and new line characters
        
        - Args :
            - txt (str)
            
        - Returns :
            - txt (str)
    """
    txtLetters = list(txt)
    if '\n' in txt or "'" in txt:
        txtLetters = list(txt)
        for i in range(len(txtLetters)) :
            if txtLetters[i] == '\n':
                if i == 0 :
                    txtLetters[i] = ''
                else :
                    txtLetters[i] = ', '
            if txtLetters[i] == "'" :
                txtLetters[i] = "`"
    if txtLetters[0] == ' ':
        txtLetters[0] = ''
    if txtLetters[-1] == ' ':
        txtLetters[-1] = ''
    txt = ''.join(txtLetters)
    return txt


def getContent(dayContent : list[str], weekContent : list[int], resourceList : list) -> list :
    """
        Collect all the content of a type for every resource in the xml file and create every Course with it
        
        - Args :
            - dayContent (list[str])
            - weekContent (list[int])
            - resourceList (list)
        
        - Returns :
            - courseList (list[Course])
    """

    courseList = []
    elementList = ["starttime", "endtime", "module", "room", "staff", "group", "notes"]
    
    cpt = 0
    for resource in resourceList :
        paramList = []
        for element in elementList :
            if not resource.find(element):
                paramList.append("- - -")
            else :
                paramList.append(clearText((resource.find(element)).text))
        paramList.append(resource['colour'])
        courseList.append(Course(dayContent[cpt], [paramList[0], paramList[1]], paramList[2], paramList[3], paramList[4], paramList[5], weekContent[cpt], paramList[6], paramList[7]))
        cpt += 1
    
    return courseList


def menu(groupList : list, linkList : list[str], groupChoice = -1) -> tuple[str, str]:
    """
        Display the list of all group and ask the user the one he wants if groupChoice == -1, if not, do not display the menu
        
        - Args :
            - groupList (list)
            - linkList (list)
            - groupChoice (int) : Default value = -1
            
        - Returns :
            - (tuple[str, str])
    """
    if groupChoice == -1 :
        for i in range(len(groupList)):
            print(i, groupList[i])

        groupChoice = input('\nGroupe : ')

        if groupChoice.isdigit() and (int(groupChoice) in (range(len(groupList)))) :
            groupChoice = int(groupChoice)
        else :
            print("Selectionner un groupe VALIDE\n")
            groupChoice = len(groupList) + 1

        while groupChoice not in (range(len(groupList))) :
            groupChoice = input("Groupe : ")
            if groupChoice.isdigit() and (int(groupChoice) in (range(len(groupList)))) :
                groupChoice = int(groupChoice)
            else :
                print("Selectionner une option VALIDE\n")
                groupChoice = len(groupList) + 1

        print(groupList[groupChoice])
        
    return ("http://chronos.iut-velizy.uvsq.fr/EDT/" + linkList[groupChoice]), groupList[groupChoice]


def getLink(fullList : bool = False, chosenGroupName : str = None):
    """
        Get the url for the requested schedule and title of it after calling menu

        - Args :
            - fullList (boolean) : Default value = False, if True, get every available course in a list with titles using a loop and function menu()
        
        - Returns :
            - link (str) : if not fullList
            - title (str) : if not fullList

            - fullLinkTitle (list[str]) : if fullList, list containing list of schedule link and ist of schedule title
    """
    url = "http://chronos.iut-velizy.uvsq.fr/EDT/finder.xml"

    response = requests.get(url)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    soup = BeautifulSoup(response.content, "lxml")

    groupList = soup.findAll('name')
    groupList = [e.text for e in groupList]

    linkList = soup.findAll('link',  {"class": "xml"})
    linkList = [e['href'] for e in linkList]

    # If the user has chosen a group name, return the link and the title of the schedule
    if chosenGroupName != None :
        for i in range(len(groupList)) :
            if clearText(groupList[i]) == chosenGroupName :
                return ("http://chronos.iut-velizy.uvsq.fr/EDT/" + linkList[i]), groupList[i]
    
    if not fullList :
        link, group = menu(groupList, linkList)

        title = 'Emploi du temps - ' + group
        
        return link, title
    
    else :
        linkFullList = []
        for i in range(len(linkList)) :
            link = menu(groupList, linkList, i)[0]
            linkFullList.append(link)

        return linkFullList, groupList


def getSchedule(url : str):
    """
        Get response of the requested schedule
        
        - Args :
            - url (str)
        
        - Returns :
            - response (response)
    """
    response = requests.get(url)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    return response


def sortCourse(courseList : list) -> tuple :
    """
        Check overlapping courses and divide all courses into 4 lists (2 per week) of normal courses and overlapping courses
        
        - Args :
            - courseList (list)
        
        - Returns :
            - tcourseList (list)
    """
    courseW0 = []
    courseW1 = []
    courseW2 = []
    courseW3 = []

    for e in courseList :
        if e.weekContent == 0 :
            courseW0.append(e)
        elif e.weekContent == 1 :
            courseW1.append(e)
        elif e.weekContent == 2 :
            courseW2.append(e)
        elif e.weekContent == 3 :
            courseW3.append(e)
    
    courseList = [courseW0, courseW1, courseW2, courseW3]
    
    for e in courseList :
        e = checkMultiple(e)
    
    overCourse = [[],[],[],[]]

    for i in range(len(courseList)):
        res = multipleSort(courseList[i])
        courseList[i] = res[0]
        overCourse[i] = res[1]

    tCourseList = tuple(courseList)

    return tCourseList, overCourse


def multipleSort(courseList : list) :
    """
        Check which courses are overlapping and parse split into multiple list
        
        - Args :
            - courseList (list)
        
        - Returns :
            - gComp (list) : Courses that are not overlapping
            - nComp (list) : Coures that are overlapping
    """
    tempindex = []
    temp2index = []
    replaceCourse = []
    nComp = []
    gComp = []
    for e in courseList :
        if len(e.sameTime) > 0 :
            tempindex.append(e.sameTime)
    for e in tempindex:
        e.sort()
        for l in e :
            if e.count(l) > 1 :
                e.remove(l)
    for e in tempindex :
        if tempindex.count(e) > 1 :
            tempindex.remove(e)
    if (len(tempindex) > 1) :
        for i in range(len(tempindex)):
            for j in range(len(tempindex)):
                if (i != j) and all(e in tempindex[i] for e in tempindex[j]) and tempindex[i]!=tempindex[j]:
                    temp2index.append(tempindex[j])
        tempindex = [e for e in tempindex if e not in temp2index]
        for i in range(len(tempindex)):
            for j in range(len(tempindex[i])):
                for k in range(len(tempindex)):
                    if (i!=k) and tempindex[i][j] in tempindex[k]:
                        [tempindex[k].append(e) for e in tempindex[i] if e not in tempindex[k]]
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
            if courseList[k].startMinutes < tempstart :
                tempstart = courseList[k].startMinutes
                hstart = courseList[k].timeContent[0]
            if courseList[k].endMinutes > tempend :
                tempend = courseList[k].endMinutes
                hend = courseList[k].timeContent[1]
        replaceCourse.append(Course(courseList[e[0]].dayContent, [hstart,hend], "COURS", "- - -", "MULTIPLES", "- - -", courseList[e[0]].weekContent, "- - -", '#7BEBFF'))

    for e in courseList:
        if len(e.sameTime) != 0 :
            nComp.append(e)
    gComp = [e for e in courseList if e not in nComp]
    [gComp.append(e) for e in replaceCourse]
    return gComp, nComp


def getWeek(soup) -> list[int]:
    """
        Get in which week is a course in the next 4 weeks
        
        - Args :
            - soup (BeautifulSoup soup)
        
        - Returns :
            - wcontent (list)
    """
    wContent = []

    rs = soup.findAll('rawweeks')
    rs = [clearText(e.text) for e in rs]

    min = len(rs[0])
    max = 0

    for e in rs :
        y = 0
        while e[y] != 'Y':
            y += 1
        if y < min :
            min = y
        if y > max :
            max = y

    for e in rs :
        y = 0
        while e[y] != 'Y':
            y += 1
        if y == min :
            wContent.append(0)
        elif y == (min+1) :
            wContent.append(1)
        elif y == (min+2) :
            wContent.append(2)
        elif y == max :
            wContent.append(3)

    return wContent


def checkMultiple(courseList : list) -> list:
    """
        Check if several courses overlap themselves
        
        - Args :
            - courseList (list)
        
        - Returns :
            - courseList (list)
    """
    for i in range(len(courseList)):
        for j in range(len(courseList)):
            if (i != j):
                if not courseList[i].isCompatible(courseList[j]):
                    if j not in list(courseList[i].sameTime) :
                        courseList[i].sameTime.append(j)
                    if i not in list(courseList[i].sameTime) :
                        courseList[i].sameTime.append(i)
    return courseList


def parseSchedule(response):
    """
        Main function of the scrapper module
        
        - Args :
            - response (xml request response)
            
        - Returns :
            - courseList (list[Course])
            - weekDesc (list[str])
    """
    courseList = []
    soup = BeautifulSoup(response.content, "lxml")

    resourceList = soup.find_all("event")

    weekFull = soup.find_all("description")
    tWeek = [(e.text)[-10:] for e in weekFull]
    weekDesc = []
    for e in tWeek:
        temp = ''
        for i in range(len(e)):
            if e[i] == "/":
                temp += "_"
            else :
                temp += e[i]
        weekDesc.append(temp)

    weekContent = getWeek(soup)

    dayTemp = soup.findAll("day")
    dayContent = []
    for i in range(1, len(resourceList) + 1):
        dayContent += dayTemp[-i]
    dayContent.reverse()

    courseList = getContent(dayContent, weekContent, resourceList)

    offList = []
    for i in range(len(weekFull)) :
        if "congé" in clearText(weekFull[i]) :
            offList.append(i)
            weekDesc[i] += " - VACANCES"

    for e in offList :
        for k in courseList :
            if k.weekContent >= e :
                k.weekContent += 1
    
    return courseList, weekDesc
