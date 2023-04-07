import toXLSX
import toPDF
import scraper
import elementSchedule


if __name__ == "__main__" :
    
    print("1 Emploi du temps de groupe")
    print("2 Emploi du temps par prof")
    print("3 Emploi du temps par salle")

    choice = 0

    while choice not in (1, 2, 3) :
        choice = int(input("Sélectionner une option : "))

    if choice == 1 :

        url, title = scraper.getLink()
        response = scraper.getSchedule(url)

        courseList, weekDesc = scraper.parseSchedule(response)

        courseList, overCourse = scraper.sortCourse(courseList)

        toXLSX.createXlsx(courseList, overCourse, weekDesc, title)

        toPDF.convertToPdf("schedule.xlsx")
    
    else :

        courseFullList = scraper.getLink(True)

        if choice == 2 :
            elementList, courseList, weekDesc = elementSchedule.getFullList(courseFullList, "staff")

        else :
            elementList, courseList, weekDesc = elementSchedule.getFullList(courseFullList, "room")

        elementChoice = elementSchedule.elementChoice(elementList)

        if choice == 2 :
            courseList = elementSchedule.getCourseElement(elementChoice, courseList, "staff")

        else :
            courseList = elementSchedule.getCourseElement(elementChoice, courseList, "room")

        courseList = elementSchedule.checkEquals(courseList)

        courseList, overCourse = scraper.sortCourse(courseList)

        toXLSX.createXlsx(courseList, overCourse, weekDesc, elementChoice)

        toPDF.convertToPdf("schedule.xlsx")