"""
    This code will scrap the schedule data with requests\n
    It will parse it using beauriful soup in objects of a "Course" class
"""
import requests, subprocess, platform
from bs4 import BeautifulSoup
from course import *
from datetime import date, timedelta


def clearText(txt : str) -> str :
    """
        Clean a text : Remove all unnecessary blank and new line characters
        
        - Args :
            - txt (str) : text to clean
            
        - Returns :
            - txt (str) : cleaned text
    """
    txtLetters = list(txt)

    if txt :
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


def getContent(dayContent : list[str], weekContent : list[int], resourceList : list) -> list[Course] :
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


def menu(groupList : list[str], linkList : list[str], groupChoice = -1) -> tuple[str, str]:
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


def getLink(fullList : bool = False, chosenGroupName = None) -> tuple :
    """
        Get the url for the requested schedule and its name after calling menu

        - Args :
            - fullList (boolean) : Default value = False, if True, get every available course in a list with group name using a loop and function menu()
            - chosenGroupName (str) : Default value = None, if not None, get the url and the group name of the schedule with the specified name
        
        - Returns :
            - link (str) : (if not fullList) schedule url
            - group (str) : (if not fullList) group name

            - linkFullList (list[str]) : (if fullList) list containing schedule links
            - groupList (list[str]) : (if fullList) list containing group names
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

    # If the user has chosen a group name, return the link and the group name of the schedule
    if chosenGroupName != None :
        for i in range(len(groupList)) :
            if clearText(groupList[i]) == chosenGroupName :
                return ("http://chronos.iut-velizy.uvsq.fr/EDT/" + linkList[i]), groupList[i]
        
        # If the group name is not found, return None
        return None, None
    
    if not fullList :
        link, group = menu(groupList, linkList)
        
        return link, group
    
    else :
        linkFullList = []
        for i in range(len(linkList)) :
            link = menu(groupList, linkList, i)[0]
            linkFullList.append(link)

        return linkFullList, groupList


def getSchedule(url : str) -> requests.models.Response :
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


def sortCourse(courseList : list[Course]) -> tuple[list[list[Course]], list[list[Course]]] :
    """
        Check overlapping courses and divide all courses into 4 lists (2 per week) of normal courses and overlapping courses
        
        - Args :
            - courseList (list[Course]) : list of courses
        
        - Returns :
            - tcourseList (list) : list of normal courses
            - overCourse (list[Course]) : list of overlapping courses
    """
    courseW = [[] for _ in range(len(courseList))]

    for e in courseList :
        courseW[e.weekContent].append(e)
    
    for e in courseW :
        e = checkMultiple(e)
    
    overCourse = [[] for i in range(len(courseList))]

    for i in range(len(courseList)):
        res = multipleSort(courseW[i])
        courseW[i] = res[0]
        overCourse[i] = res[1]

    return courseW, overCourse


def multipleSort(courseList : list[Course]) -> tuple[list[Course], list[Course]] :
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


def getWeek(soup : BeautifulSoup) -> list[int]:
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

        wContent.append(y-min)

    return wContent


def checkMultiple(courseList : list[Course]) -> list[Course]:
    """
        Check if several courses overlap themselves and add them to the sameTime list of each course
        
        - Args :
            - courseList (list[Course])
        
        - Returns :
            - courseList (list[Course])
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


def addMissingWeeks(weekDesc : list[str]) -> list[str]:
    """
        Add missing weeks in the list of week description
        
        - Args :
            - weekDesc (list[str])
        
        - Returns :
            - weekDesc (list[str])
    """
    for i in range(len(weekDesc)-1):
        currDate = date(int(weekDesc[i][-4:]), int(weekDesc[i][3:5]), int(weekDesc[i][:2]))
        nextDate = date(int(weekDesc[i+1][-4:]), int(weekDesc[i+1][3:5]), int(weekDesc[i+1][:2]))
        if (nextDate - currDate).days > 7 :
            for j in range(1, (nextDate - currDate).days // 7):
                weekDesc.insert(i+j, (currDate + timedelta(days = 7*j)).strftime("%d_%m_%Y"))
                
    return weekDesc


def parseSchedule(response : requests.models.Response) -> tuple[list[Course], list[str]]:
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
    
    weekDesc = addMissingWeeks(weekDesc)

    weekContent = getWeek(soup)

    dayTemp = soup.findAll("day")
    dayContent = []
    for i in range(1, len(resourceList) + 1):
        dayContent += dayTemp[-i]
    dayContent.reverse()

    courseList = getContent(dayContent, weekContent, resourceList)
    
    return courseList, weekDesc
