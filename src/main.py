"""
    Main file to run the CLI version of the project
"""
from functions import element_schedule, to_pdf, to_xlsx, scraper
import functions.db_operations as db_op

OUTPUT_DIR = "output/"

if __name__ == "__main__" :

    CHOICE = 0

    # Get every course from the schedule
    # If the general school schedule is not found, get every schedule
    IUTurl, IUTtitle = scraper.get_link(True, "IUT")

    if IUTtitle and IUTurl :
        allCourse, weekDesc = element_schedule.get_full_schedule(IUTurl, IUTtitle)
        db_op.overwrite_db(allCourse, weekDesc)

    while CHOICE != 5 :

        print("1 Emploi du temps de groupe")
        print("2 Emploi du temps par prof")
        print("3 Emploi du temps par salle")
        print("4 Mise à jour de la base de données")
        print("5 Quitter\n")

        while CHOICE not in (1, 2, 3, 4, 5) :
            CHOICE = input("Sélectionner une option : ")
            if CHOICE.isdigit() and (int(CHOICE) in (1, 2, 3, 4, 5)) :
                CHOICE = int(CHOICE)
            else :
                print("Selectionner une option VALIDE\n")
                CHOICE = 0

        if CHOICE == 1 :

            url, title = scraper.get_link()
            response = scraper.get_schedule(url)

            courseList, weekDesc = scraper.parse_schedule(response)

            courseList, overCourse = scraper.sort_courses(courseList)

            to_pdf.clear_files('xlsx', 'pdf', path = OUTPUT_DIR)
            to_xlsx.create_xlsx(courseList,
                                overCourse,
                                weekDesc,
                                title,
                                OUTPUT_DIR + title.replace(' ', '_'))
            to_pdf.convert_to_pdf(OUTPUT_DIR + title.replace(' ', '_') + ".xlsx")

            CHOICE = 0

        elif CHOICE in (2, 3, 4) :
            if CHOICE in (2, 3) :
                options = ("staff", "room")

                # Get the list of all elements from the selected option
                elementList = element_schedule.get_full_list(allCourse, options[CHOICE - 2])

                # Ask the user to select an element from the list
                elementChoice = element_schedule.choose_element(elementList)

                # Get the list of all courses of the selected element
                courseList = element_schedule.get_course_element(elementChoice,
                                                                 allCourse,
                                                                 options[CHOICE - 2])

                courseList = element_schedule.check_equals(courseList)
                courseList = element_schedule.merge_course(courseList)
                courseList, overCourse = scraper.sort_courses(courseList)

                to_pdf.clear_files('xlsx', 'pdf', path = OUTPUT_DIR)
                to_xlsx.create_xlsx(courseList,
                                    overCourse,
                                    weekDesc,
                                    elementChoice,
                                    OUTPUT_DIR + elementChoice.replace(' ', '_'))
                to_pdf.convert_to_pdf(OUTPUT_DIR + elementChoice.replace(' ', '_') + ".xlsx")

            else :
                IUTurl, IUTtitle = scraper.get_link(True, "IUT")
                allCourse, weekDesc = element_schedule.get_full_schedule(IUTurl, IUTtitle)
                db_op.overwrite_db(allCourse, weekDesc)

            CHOICE = 0
