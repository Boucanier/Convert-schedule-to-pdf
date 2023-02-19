import toXLSX
import scraper


if __name__ == "__main__" :

    url, title = scrapper.getLink()
    response = scrapper.getSchedule(url)

    courseList, weekDesc = scrapper.parseSchedule(response)

    courseList, overCourse = scrapper.sortCourse(courseList)

    toXLSX.transformToXls(courseList, weekDesc, title)
