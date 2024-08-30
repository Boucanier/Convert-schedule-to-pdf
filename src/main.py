"""
    Main file to run the CLI version of the project
"""
from functions import element_schedule, to_pdf, to_xlsx, scraper
import functions.db_operations as db_op

OUTPUT_DIR = "output/"

def iut_schedule() :
    """
        Process to get the IUT schedule
    """
    choice = 0

    # Get every course from the schedule
    # If the general school schedule is not found, get every schedule
    iut_url, iut_title = scraper.get_link(True, "IUT")

    if iut_title and iut_url :
        all_course, week_desc = element_schedule.get_full_schedule(iut_url, iut_title)
        db_op.overwrite_db(all_course, week_desc)

    while choice != 5 :

        print("1 Emploi du temps de groupe")
        print("2 Emploi du temps par prof")
        print("3 Emploi du temps par salle")
        print("4 Mise à jour de la base de données")
        print("5 Quitter\n")

        while choice not in (1, 2, 3, 4, 5) :
            choice = input("Sélectionner une option : ")
            if choice.isdigit() and (int(choice) in (1, 2, 3, 4, 5)) :
                choice = int(choice)
            else :
                print("Selectionner une option VALIDE\n")
                choice = 0

        if choice == 1 :

            url, title = scraper.get_link()
            response = scraper.get_schedule(url)

            course_list, week_desc = scraper.parse_schedule(response)

            course_list, over_course = scraper.sort_courses(course_list)

            to_pdf.clear_files('xlsx', 'pdf', path = OUTPUT_DIR)
            to_xlsx.create_xlsx(course_list,
                                over_course,
                                week_desc,
                                title,
                                OUTPUT_DIR + title.replace(' ', '_'))
            to_pdf.convert_to_pdf(OUTPUT_DIR + title.replace(' ', '_') + ".xlsx")

            choice = 0

        elif choice in (2, 3, 4) :
            if choice in (2, 3) :
                options = ("staff", "room")

                # Get the list of all elements from the selected option
                element_list = element_schedule.get_full_list(all_course, options[choice - 2])

                # Ask the user to select an element from the list
                element_choice = element_schedule.choose_element(element_list)

                # Get the list of all courses of the selected element
                course_list = element_schedule.get_course_element(element_choice,
                                                                all_course,
                                                                options[choice - 2])

                course_list = element_schedule.check_equals(course_list)
                course_list = element_schedule.merge_course(course_list)
                course_list, over_course = scraper.sort_courses(course_list)

                to_pdf.clear_files('xlsx', 'pdf', path = OUTPUT_DIR)
                to_xlsx.create_xlsx(course_list,
                                    over_course,
                                    week_desc,
                                    element_choice,
                                    OUTPUT_DIR + element_choice.replace(' ', '_'))
                to_pdf.convert_to_pdf(OUTPUT_DIR + element_choice.replace(' ', '_') + ".xlsx")

            else :
                iut_url, iut_title = scraper.get_link(True, "IUT")
                all_course, week_desc = element_schedule.get_full_schedule(iut_url, iut_title)
                db_op.overwrite_db(all_course, week_desc)

            choice = 0


def uqac_schedule() :
    """
        Process to get the UQAC schedule
    """
    print(" Work in progress...")


if __name__ == "__main__" :

    EST = 0
    print("1 IUT\n2 UQAC\n")

    while EST not in (1, 2) :
        EST = input("Sélectionner une option : ")

        if EST.isdigit() and (int(EST) in (1, 2)) :
            EST = int(EST)
        else :
            print("Selectionner une option VALIDE\n")
            EST = 0

    print()

    if EST == 1 :
        iut_schedule()

    elif EST == 2 :
        uqac_schedule()
