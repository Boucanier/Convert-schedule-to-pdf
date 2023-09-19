import toXLSX
import toPDF
import scraper
import elementSchedule
import dbOperations


if __name__ == "__main__" :

    choice = 0

    # Get every course from the schedule
    urlList, titleList = scraper.getLink(True)
    allCourse, weekDesc = elementSchedule.getFullSchedule(urlList, titleList)

    while choice != 7 :

        print("1 Emploi du temps de groupe")
        print("2 Emploi du temps par prof")
        print("3 Emploi du temps par salle")
        print("4 Mise à jour de la base de données")
        print("5 Quitter\n")

        choice = input("Sélectionner une option : ")
        if choice.isdigit() and (int(choice) in (1, 2, 3, 4, 5)) :
            choice = int(choice)
        else :
            print("Selectionner une option VALIDE\n")
            choice = 0

        while choice not in (1, 2, 3, 4, 5) :
            choice = input("Sélectionner une option : ")
            if choice.isdigit() and (int(choice) in (1, 2, 3, 4, 5)) :
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
        
        elif choice in (2, 3, 4) :
            if choice in (2, 3) :
                options = ("staff", "room")

                # Get the list of all elements from the selected option
                elementList = elementSchedule.getFullList(allCourse, options[choice - 2])

                # Ask the user to select an element from the list
                elementChoice = elementSchedule.elementChoice(elementList)

                # Get the list of all courses of the selected element
                courseList = elementSchedule.getCourseElement(elementChoice, allCourse, options[choice - 2])

                courseList = elementSchedule.checkEquals(courseList)
                courseList, overCourse = scraper.sortCourse(courseList)

                toXLSX.createXlsx(courseList, overCourse, weekDesc, elementChoice)

                toPDF.convertToPdf("schedule.xlsx")
            
            else :
                # Update rooms, staffs, modules and groups tables
                dbOperations.updateDB(allCourse)

                # Delete all courses of the 4 next weeks since it will be reinserted
                dbOperations.deleteByWeek(weekDesc)

                # Insert all courses of the 4 next weeks
                detailedCourse = elementSchedule.getFullDetailedList(allCourse)
                dbOperations.insertCourse(detailedCourse, weekDesc)
        
            choice = 0