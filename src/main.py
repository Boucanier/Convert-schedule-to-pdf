import toXLSX
import toPDF
import scraper
import elementSchedule


if __name__ == "__main__" :

    firstReq = True
    choice = 0

    while choice != 5 :

        print("\n")
        print("1 Emploi du temps de groupe")
        print("2 Emploi du temps par prof")
        print("3 Emploi du temps par salle")
        print("4 Mise à jour des emplois du temps")
        print("5 Quitter\n")

        while choice not in (1, 2, 3, 4, 5) :
            choice = input("Sélectionner une option : ")
            if choice.isdigit() :
                choice = int(choice)
            else :
                choice = 0

        if choice == 1 :

            url, title = scraper.getLink()
            response = scraper.getSchedule(url)

            courseList, weekDesc = scraper.parseSchedule(response)

            courseList, overCourse = scraper.sortCourse(courseList)

            toXLSX.createXlsx(courseList, overCourse, weekDesc, title)

            toPDF.convertToPdf("schedule.xlsx")

            choice = 0
        
        elif choice in (2, 3) :

            if firstReq :
                courseFullList = scraper.getLink(True)
                allCourse, weekDesc = elementSchedule.getFullSchedule(courseFullList)

            options = ("staff", "room")

            elementList, courseList = elementSchedule.getFullList(allCourse, options[choice - 2])

            elementChoice = elementSchedule.elementChoice(elementList)

            courseList = elementSchedule.getCourseElement(elementChoice, courseList, options[choice - 2])

            courseList = elementSchedule.checkEquals(courseList)

            courseList, overCourse = scraper.sortCourse(courseList)

            toXLSX.createXlsx(courseList, overCourse, weekDesc, elementChoice)

            toPDF.convertToPdf("schedule.xlsx")
        
            choice = 0
            firstReq = False
        
        elif choice == 4 :

            courseFullList = scraper.getLink(True)
            allCourse, weekDesc = elementSchedule.getFullSchedule(courseFullList)

            firstReq = False
            choice = 0