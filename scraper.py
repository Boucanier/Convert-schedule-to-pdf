"""
    This code will scrap the schedule data with requests
    It will parse it using beauriful soup in objects of a "Course" class
"""
import requests
from bs4 import BeautifulSoup


class Course :
    """
        Class of a course containing day, time, "content", room, staff, group, week, duration parameters
    """
    def __init__(self, parDay, parTime, parModule, parRoom, parProf, parGroup, parWeek):
        self.dayContent = parDay
        self.timeContent = parTime
        self.moduleContent = parModule
        self.roomContent = parRoom
        self.profContent = parProf
        self.groupContent = parGroup
        self.weekContent = parWeek

        self.duration = self.dTime()
        self.startMinutes = self.toMinutes()
        self.endMinutes = self.startMinutes + self.duration

        self.sameTime = []

    def __str__(self) -> str:
        st = ''
        for e in self.sameTime :
            st += ' ' + str(e)
        display = str(self.weekContent) + ' ' + str(self.dayContent) + ' [' + self.timeContent[0] + ':' + self.timeContent[1] + '] - [' + str(self.startMinutes) + ':' + str(self.endMinutes) + '] - ' + str(self.duration) + ', ' \
            + self.moduleContent + ' ' + self.roomContent + ' ' + self.profContent + ' ' + self.groupContent + ', incompatible with :' + st
        return display

    def dTime(self) -> int :
        """
            Calculate the duration of the course
            
            Returns :
                - dt (int)
        """
        d1 = (int((self.timeContent[1].split(':'))[0]) - int((self.timeContent[0].split(':'))[0]))
        d2 = ((int((self.timeContent[1].split(':'))[1]) - int((self.timeContent[0].split(':'))[1])))
        d1 *= 60
        dt = d1 + d2
        return dt

    def toMinutes(self) -> int:
        """
            Convert time content in minutes
            
            Returns :
                - (int)
        """
        hr = (self.timeContent[0]).split(':')
        return (int(hr[0])*60) + int(hr[-1])
    
    def isCompatible(self, hr2):
        """
            Check if the parameter course overlap or is overlapped by the current course
            
            Args :
                - hr2 (Course)
            
            Returns :
                - (boolean)
        """
        if (self.weekContent == hr2.weekContent) and (self.dayContent == hr2.dayContent) :
            if ((self.startMinutes <= hr2.startMinutes < self.endMinutes) or (self.startMinutes < hr2.endMinutes <= self.endMinutes)):
                return False
            if ((hr2.startMinutes <= self.startMinutes < hr2.endMinutes) or (hr2.startMinutes < self.endMinutes <= hr2.endMinutes)):
                return False
            if (hr2.startMinutes == self.startMinutes) and (hr2.endMinutes == self.endMinutes):
                return False
        return True


def clearText(txt : str) -> str :
    """
        Clean a text : Remove all unnecessary blank and new line characters
        
        Args :
            - txt (str)
            
        Returns :
            - txt (str)
    """
    txtLetters = list(txt)
    if '\n' in txt :
        for i in range(len(txtLetters)) :
            if txtLetters[i] == '\n':
                if i == 0 :
                    txtLetters[i] = ''
                else :
                    txtLetters[i] = ', '
    if txtLetters[0] == ' ':
        txtLetters[0] = ''
    if txtLetters[-1] == ' ':
        txtLetters[-1] = ''
    txt = ''.join(txtLetters)
    return txt


def getContent(element : str, resourceList : list) -> list :
    """
        Get all the content of a type for every resource in the xml file
        
        Args :
            - element (str)
            - resourceList (list)
        
        Returns :
            - content (list)
    """
    content = []
    for e in resourceList :
        if not e.find(element):
            content.append("- - -")
        else :
            content.append(clearText((e.find(element)).text))
    return content


def getTime(element : str, soup) -> list :
    """
        Get time content on the xml file
        
        Args :
            - element (str)
            - soup (BeautifulSoup soup)
            
        Returns :
            - content (list)
    """
    content = soup.findAll(element)
    content = [clearText(e.text) for e in content]
    return content


def menu(groupList : list, linkList : list):
    """
        Display the list of all group and ask the user the one he wants
        
        Args :
            - groupList (list)
            - linkList (list)
            
        Returns :
            - (str)
            - (str)
    """
    weekChoice = -1
    groupChoice = -1
    while not (0 <= groupChoice <= len(groupList)):
        for i in range(len(groupList)):
            print(i, groupList[i])
        groupChoice = int(input('Group : '))
    print(groupList[groupChoice])
    return ("http://chronos.iut-velizy.uvsq.fr/EDT/" + linkList[groupChoice]), groupList[groupChoice]


def getLink():
    """
        Get the url for the requested schedule and title of it after calling menu
        
        Returns :
            - link (str)
            - title (str)
    """
    url = "http://chronos.iut-velizy.uvsq.fr/EDT/finder.xml"

    response = requests.get(url)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    soup = BeautifulSoup(response.content, "lxml")

    groupList = soup.findAll('name')
    groupList = [e.text for e in groupList]

    linkList = soup.findAll('link',  {"class": "xml"}, href = True)
    linkList = [e['href'] for e in linkList]
    
    link, group = menu(groupList, linkList)

    title = 'Emploi du temps - ' + group
    
    return link, title


def getSchedule(url : str):
    """
        Get response of the requested schedule
        
        Args :
            - url (str)
        
        Returns :
            - response (response)
    """
    response = requests.get(url)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    return response


def sortCourse(courseList : list):
    """
        Check overlapping courses and divide all courses into 4 lists (2 per week) of normal courses and overlapping courses
        
        Args :
            - courseList (list)
        
        Returns :
            - courseList (list)
            - overCourse (list)
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

    return tCourseList


def multipleSort(courseList : list) :
    """
        Check which courses are overlapping and parse split into multiple list
        
        Args :
            - courseList (list)
        
        Returns :
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
        replaceCourse.append(Course(courseList[e[0]].dayContent, [hstart,hend], "COURS", "- - -", "MULTIPLES", "- - -", courseList[e[0]].weekContent))

    for e in courseList:
        if len(e.sameTime) != 0 :
            nComp.append(e)
    gComp = [e for e in courseList if e not in nComp]
    [gComp.append(e) for e in replaceCourse]
    return gComp, nComp


def getWeek(soup) -> list:
    """
        Get in which week is a course in the next 4 weeks
        
        Args :
            - soup (BeautifulSoup soup)
        
        Returns :
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
        
        Args :
            - courseList (list)
        
        Returns :
            - courseList (list)
    """
    for i in range(len(courseList)):
        for j in range(len(courseList)):
            if (i != j):
                if not courseList[i].isCompatible(courseList[j]):
                    courseList[i].sameTime.append(j)
                    courseList[i].sameTime.append(i)
    return courseList


def parseSchedule(response):
    """
        Main function of the scrapper module
        
        Args :
            - response (xml request response)
            
        Returns :
            - courseList (list)
            - weekDesc (list)
    """
    courseList = []
    soup = BeautifulSoup(response.content, "lxml")

    resourceList = soup.find_all("resources")

    tWeek = soup.find_all("description")
    tWeek = [(e.text)[-10:] for e in tWeek]
    weekDesc = []
    for e in tWeek:
        temp = ''
        for i in range(len(e)):
            if e[i] == "/":
                temp += "_"
            else :
                temp += e[i]
        weekDesc.append(temp)

    moduleContent = getContent("module", resourceList)
    profContent = getContent("staff", resourceList)
    roomContent = getContent("room", resourceList)
    groupContent = getContent("group", resourceList)

    startContent = getTime("starttime", soup)
    endContent = getTime("endtime", soup)

    weekContent = getWeek(soup)

    timeContent = []
    for i in range(len(startContent)):
        timeContent.append([startContent[i], endContent[i]])

    dayCt = len(moduleContent)

    dayTemp = soup.findAll("day")
    dayContent = []
    for i in range(1, dayCt + 1):
        dayContent += dayTemp[-i]
    dayContent.reverse()

    for i in range(dayCt):
        courseList.append(Course(dayContent[i], timeContent[i], moduleContent[i], roomContent[i], profContent[i], groupContent[i], weekContent[i]))
    
    dayContent.clear()
    timeContent.clear()
    moduleContent.clear()
    roomContent.clear()
    profContent.clear()
    groupContent.clear()
    
    return courseList, weekDesc
