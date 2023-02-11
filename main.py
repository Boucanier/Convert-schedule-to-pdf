import toXLSX
import scrapper


if __name__ == "__main__" :

    url, title, weekChoice = scrapper.getLink()
    response = scrapper.getSchedule(url)

    courseList = scrapper.parseSchedule(response)

    courseList, overCourse, overIndex = scrapper.sortCourse(courseList)

    toXLSX.transformToXls(courseList[weekChoice], title)
