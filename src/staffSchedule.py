import scraper

def getFullList(linkTitleList : list[list[str]]):
    """
        Get every schedule available, then extract the staff list of every different professor using function clearStaff()

        - Args :
            - linkTitleList (list[list[str]]) : list containing list of schedule link and ist of schedule title
        
        - Returns :
            - staffList (list[str])
            - courseFullList (list[list[Course]])
            - weekDesc (list[str])
    """
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
    """
        Check if many professors are assigned to a same course and add them to the main staff list if they are not already in

        - Args :
            - profList (list[str])
        
        - Returns :
            - profList (list[str])
    """
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
    """
        Display the list of every professor and ask the user to chose a professor

        - Args :
            - staffList (list[str])
        
        - Returns :
            - (str)
    """
    choice = -1
    staffList.sort()
    for i in range(len(staffList)) :
        print(i, staffList[i])

    while not (0 <= choice <= len(staffList)) :
        choice = int(input("\nProf : "))
    
    print(staffList[choice] + '\n')

    return staffList[choice]


def getCourseProf(profChoice : str, courseList) :
    """
        Add every course of a specified professor from every schedule to a single schedule

        - Args :
            - profChoice (str)
            - courseList (list[Course])

        - Returns :
            - courseFullList (list[Course])
    """
    courseFullList = []
    for e in courseList :
        for k in e :
            if k.profContent == profChoice :
                courseFullList.append(k)
            elif profChoice in (k.profContent).split(", "):
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
