import toXLSX
import toPDF
import scraper
import elementSchedule
import dbOperations


if __name__ == "__main__" :

    firstReq = True
    choice = 0

    while choice != 7 :

        print("1 Emploi du temps de groupe")
        print("2 Emploi du temps par prof")
        print("3 Emploi du temps par salle")
        print("4 Mise à jour des emplois du temps")
        print("5 Création de la base de données")
        print("6 Mise à jour de la base de données")
        print("7 Quitter\n")

        choice = input("Sélectionner une option : ")
        if choice.isdigit() and (int(choice) in (1, 2, 3, 4, 5, 6, 7)) :
            choice = int(choice)
        else :
            print("Selectionner une option VALIDE\n")
            choice = 0

        while choice not in (1, 2, 3, 4, 5, 6, 7) :
            choice = input("Sélectionner une option : ")
            if choice.isdigit() and (int(choice) in (1, 2, 3, 4, 5, 6, 7)) :
                choice = int(choice)
            else :
                print("Selectionner une option VALIDE\n")
                choice = 0

        if choice == 1 :

            url, title = scraper.getLink()
            response = scraper.getSchedule(url)

            courseList, weekDesc = scraper.parseSchedule(response)

            courseList, overCourse = scraper.sortCourse(courseList)

            toXLSX.createXlsx(courseList, overCourse, weekDesc, title)

            toPDF.convertToPdf("schedule.xlsx")

            choice = 0
        
        elif choice in (2, 3, 5, 6) :

            if firstReq :
                urlList, titleList = scraper.getLink(True)
                allCourse, weekDesc = elementSchedule.getFullSchedule(urlList, titleList)
                firstReq = False

            if choice in (2, 3) :
                options = ("staff", "room")

                elementList = elementSchedule.getFullList(allCourse, options[choice - 2])

                elementChoice = elementSchedule.elementChoice(elementList)

                courseList = elementSchedule.getCourseElement(elementChoice, allCourse, options[choice - 2])

                courseList = elementSchedule.checkEquals(courseList)

                courseList, overCourse = scraper.sortCourse(courseList)

                toXLSX.createXlsx(courseList, overCourse, weekDesc, elementChoice)

                toPDF.convertToPdf("schedule.xlsx")

            elif choice == 5 :
                dbOperations.createDB(allCourse)
            
            else :
                dbOperations.updateDB(allCourse)
                dbOperations.deleteByWeek(weekDesc)
                detailedCourse = elementSchedule.getFullDetailedList(allCourse)
                dbOperations.insertCourse(detailedCourse, weekDesc)
        
            choice = 0
        
        elif choice == 4 :

            urlList, titleList = scraper.getLink(True)
            allCourse, weekDesc = elementSchedule.getFullSchedule(urlList, titleList)

            firstReq = False
            choice = 0