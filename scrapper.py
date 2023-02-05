import requests
from bs4 import BeautifulSoup


class Course :
    def __init__(self, parDay, parTime, parModule, parRoom, parProf, parGroup, parWeek):
        self.dayContent = parDay
        self.timeContent = parTime
        self.moduleContent = parModule
        self.roomContent = parRoom
        self.profContent = parProf
        self.groupContent = parGroup
        self.weekContent = parWeek

        self.duration = self.cTime()
    
    def display(self) -> None:
        print(self.dayContent, self.timeContent, self.moduleContent, self.roomContent, self.profContent, self.groupContent)

    def cTime(self) -> str :
        dt = (int((self.timeContent[1].split(':'))[0]) - int((self.timeContent[0].split(':'))[0])) + ((int((self.timeContent[1].split(':'))[1]) - int((self.timeContent[0].split(':'))[1])) / 60)
        d1 = round(dt // 1)
        d2 = str(round((dt - d1) * 60))
        d1 = str(d1)
        dt = ':'.join([d1,d2])
        return dt


def clearText(txt : str) -> str :
    if '\n' in txt :
        txtLetters = list(txt)
        for i in range(len(txtLetters)) :
            if txtLetters[i] == '\n':
                txtLetters[i] = ' '
        txt = ''.join(txtLetters)
    return txt


def getContent(element : str, soup) -> list :
    content = soup.findAll(element)
    content = [clearText(e.text) for e in content]
    return content


def menu(groupList : list, linkList : list):
    weekChoice = -1
    for i in range(len(groupList)):
        print(i, groupList[i])
    groupChoice = int(input('Group : '))
    while weekChoice not in [0,1,2,3]:
        weekChoice = int(input("Semaine 0, 1, 2 ou 3 : "))
    return ("http://chronos.iut-velizy.uvsq.fr/EDT/" + linkList[groupChoice]), groupList[groupChoice], weekChoice


def getLink():
    url = "http://chronos.iut-velizy.uvsq.fr/EDT/finder.xml"

    response = requests.get(url)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    soup = BeautifulSoup(response.content, "lxml")

    groupList = soup.findAll('name')
    groupList = [e.text for e in groupList]

    linkList = soup.findAll('link',  {"class": "xml"}, href = True)
    linkList = [e['href'] for e in linkList]
    
    link, group, weekChoice = menu(groupList, linkList)

    title = 'Emploi du temps - ' + group
    
    return link, title, weekChoice


def getSchedule(url : str):
    response = requests.get(url)
    response.encoding = 'utf-8'

    assert (response.ok), url + " can not be reached"

    return response


def sortCourse(courseList : list):
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
        
    return courseW0, courseW1, courseW2, courseW3

def getWeek(soup):
    wContent = []
    
    rs = soup.findAll('rawweeks')
    rs = [clearText(e.text) for e in rs]

    min = len(rs[0])
    max = 0

    for e in rs :
        y = 0
        while e[y] != 'Y':
            y += 1
        tempval = y
        if tempval < min :
            min = tempval
        if tempval > max :
            max = tempval
    
    for e in rs :
        y = 0
        while e[y] != 'Y':
            y += 1
        tempval = y
        if tempval == min :
            wContent.append(0)
        elif tempval == (min+1) :
            wContent.append(1)
        elif tempval == (min+2) :
            wContent.append(2)
        elif tempval == max :
            wContent.append(3)
    return wContent


def notCourse(moduleContent : list, profContent : list, soup):
    tp = [(clearText(e.text)) for e in soup.find_all('resources')]

    for i in range(len(tp)):
        if len(tp[i].split()) == 2 :
            moduleContent.insert(i,' Apprentissage')
            profContent.insert(i,' CFA')
    
    return moduleContent, profContent


def parseSchedule(response):
    courseList = []
    soup = BeautifulSoup(response.content, "lxml")

    moduleContent = soup.findAll('module')
    dayCt = len(moduleContent)
    moduleContent = [clearText(e.text) for e in moduleContent]

    profContent = soup.findAll('staff')
    
    profContent = [clearText(e.text) for e in profContent]

    roomContent = getContent('room', soup)

    groupContent = getContent('group', soup)

    startContent = getContent('starttime', soup)
    endContent = getContent('endtime', soup)

    weekContent = getWeek(soup)
    
    timeContent = []
    for i in range(len(startContent)):
        timeContent.append([startContent[i], endContent[i]])

    for i in range(len(moduleContent)):
        if "Travail d'équipe" in moduleContent[i]:
            profContent.insert(i,'SAÉ')

    moduleContent, profContent = notCourse(moduleContent, profContent, soup)

    dayCt = len(moduleContent)

    dayTemp = soup.findAll('day')
    dayContent = []
    for i in range(1, dayCt + 1):
        dayContent += dayTemp[-i]
    dayContent.reverse()

    for i in range(len(moduleContent)):
        courseList.append(Course(dayContent[i], timeContent[i], moduleContent[i], roomContent[i], profContent[i], groupContent[i], weekContent[i]))
    
    dayContent.clear()
    timeContent.clear()
    moduleContent.clear()
    roomContent.clear()
    profContent.clear()
    groupContent.clear()
    
    return courseList