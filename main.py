import toXLSX
import scrapper


if __name__ == "__main__":

    url, title, weekChoice = scrapper.getLink()
    response = scrapper.getSchedule(url)

    courseList = scrapper.parseSchedule(response)

    courseW0, courseW1, courseW2, courseW3 = scrapper.sortCourse(courseList)

    courseList = [courseW0, courseW1, courseW2, courseW3]

    toXLSX.transformToXls(courseList[weekChoice], title)