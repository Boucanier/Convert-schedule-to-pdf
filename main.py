import toXLSX
import toPDF
import scraper
import staffSchedule


if __name__ == "__main__" :
    
    print("1 Emploi du temps de groupe")
    print("2 Emploi du temps de personnel")

    choice = 0

    while choice not in (1, 2) :
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

        staffList, courseList, weekDesc = staffSchedule.getFullList(courseFullList)

        profChoice = staffSchedule.staffChoice(staffList)

        courseList = staffSchedule.getCourseProf(profChoice, courseList)

        courseList = staffSchedule.checkEquals(courseList)

        courseList, overCourse = scraper.sortCourse(courseList)

        toXLSX.createXlsx(courseList, overCourse, weekDesc, profChoice)

        toPDF.convertToPdf("schedule.xlsx")