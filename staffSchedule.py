import scraper

def getFullList(linkTitleList):
    courseFullList = []

    for i in range(len(linkTitleList[0])):
        response = scraper.getSchedule(linkTitleList[0][i])

        courseList, weekDesc = scraper.parseSchedule(response)
        courseFullList.append(courseList)
        print(i, linkTitleList[1][i])

    staffList = []
    for e in courseFullList :
        for k in e :
            if k.profContent not in staffList :
                staffList.append(k.profContent)

    staffList = clearStaff(staffList)
        
    return staffList, courseFullList, weekDesc


def clearStaff(profList : list[str]) -> list[str] :
    toRemove = []
    toAdd = []
    for i in range(len(profList)):
        if ',' in profList[i] :
            toRemove.append(profList[i])
            tempProfList = profList[i].split(', ')
            [toAdd.append(e) for e in tempProfList]
    for e in toAdd :
        if e not in profList :
            profList.append(e)
    for e in toRemove :
        profList.remove(e)

    return profList


def staffChoice(staffList : list[str]) -> str:
    choice = -1
    for i in range(len(staffList)) :
        print(i, staffList[i])

    while not (0 <= choice <= len(staffList)) :
        choice = int(input("\nProf : "))
    
    print(staffList[choice] + '\n')

    return staffList[choice]


def getCourseProf(profChoice : str, courseList) :
    courseFullList = []
    for e in courseList :
        for k in e :
            if k.profContent == profChoice :
                courseFullList.append(k)
            elif profChoice in (k.profContent).split(", "):
                courseFullList.append(k)
    return courseFullList

def checkEquals(courseList) :
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