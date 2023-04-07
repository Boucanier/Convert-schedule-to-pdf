"""
    This code contains functions that will be used to fetch a specific schedule based on a room/professor
"""
import scraper

def getFullList(linkTitleList : list[list[str]], element : str):
    """
        Get every schedule available, then extract the list of every different element using function clearElement()

        - Args :
            - linkTitleList (list[list[str]]) : list containing list of schedule link and ist of schedule title
        
        - Returns :
            - elementList (list[str])
            - courseFullList (list[list[Course]])
            - weekDesc (list[str])
    """
    courseFullList = []

    for i in range(len(linkTitleList[0])):
        response = scraper.getSchedule(linkTitleList[0][i])

        courseList, weekDesc = scraper.parseSchedule(response)
        courseFullList.append(courseList)
        print(i, linkTitleList[1][i])

    elementList = []


    if element == "staff" :
        for e in courseFullList :
            for k in e :
                if k.profContent not in elementList :
                    elementList.append(k.profContent)

    elif element == "room" :
        for e in courseFullList :
            for k in e :
                if k.roomContent not in elementList :
                    elementList.append(k.roomContent)

    elementList = clearElement(elementList)
        
    return elementList, courseFullList, weekDesc


def clearElement(elementList : list[str]) -> list[str] :
    """
        Check if many elements are assigned to a same course and add them to the main element list if they are not already in it

        - Args :
            - elementList (list[str])
        
        - Returns :
            - elementList (list[str])
    """
    toRemove = []
    toAdd = []
    for i in range(len(elementList)):
        if ',' in elementList[i] :
            toRemove.append(elementList[i])
            tempElementList = elementList[i].split(', ')
            [toAdd.append(e) for e in tempElementList]
    for e in toAdd :
        if e not in elementList :
            elementList.append(e)
    for e in toRemove :
        elementList.remove(e)

    return elementList


def elementChoice(elementList : list[str]) -> str:
    """
        Display the list of every element and ask the user to choose an element

        - Args :
            - elementList (list[str])
        
        - Returns :
            - (str)
    """
    choice = -1
    elementList.sort()
    for i in range(len(elementList)) :
        print(i, elementList[i])

    while not (0 <= choice <= len(elementList)) :
        choice = int(input("\nChoix : "))
    
    print(elementList[choice] + '\n')

    return elementList[choice]


def getCourseElement(elementChoice : str, courseList, element : str) :
    """
        Merge every course of a specified element from every schedule in a single schedule

        - Args :
            - elementChoice (str)
            - courseList (list[Course])

        - Returns :
            - courseFullList (list[Course])
    """
    courseFullList = []

    if element == "staff" :
        for e in courseList :
            for k in e :
                if k.profContent == elementChoice :
                    courseFullList.append(k)
                elif elementChoice in (k.profContent).split(", "):
                    courseFullList.append(k)

    elif element == "room" :
        for e in courseList :
            for k in e :
                if k.roomContent == elementChoice :
                    courseFullList.append(k)
                elif elementChoice in (k.roomContent).split(", "):
                    courseFullList.append(k)

    return courseFullList


def checkEquals(courseList) :
    """
        Check if many courses are similar and keep only one in the list

        Then sort the list of course regarding the days

        - Args :
            - courseList (list[Course])

        - Returns :
            - courseList (list[Course])
    """
    toRemove = []
    intToRemove = []

    for i in range(len(courseList)):
        for j in range(len(courseList)):
            if i != j and i not in intToRemove :
                if courseList[i] == courseList[j] :
                    toRemove.append(courseList[j])
                    intToRemove.append(j)

    for e in toRemove :
        courseList.remove(e)

    n = len(courseList)

    for i in range(n):
        for j in range(0, n-i-1):
            if courseList[j].dayContent > courseList[j+1].dayContent :
                courseList[j], courseList[j+1] = courseList[j+1], courseList[j]

    return courseList
