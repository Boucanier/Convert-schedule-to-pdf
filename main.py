import toXLSX
import scraper


if __name__ == "__main__" :

    url, title = scraper.getLink()
    response = scraper.getSchedule(url)

    courseList, weekDesc = scraper.parseSchedule(response)

    courseList = scraper.sortCourse(courseList)

    toXLSX.transformToXls(courseList, weekDesc, title)
