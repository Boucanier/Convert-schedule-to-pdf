import toXLSX
import toPDF
import scraper


if __name__ == "__main__" :

    url, title = scraper.getLink()
    response = scraper.getSchedule(url)

    courseList, weekDesc = scraper.parseSchedule(response)

    courseList, overCourse = scraper.sortCourse(courseList)

    toXLSX.createXlsx(courseList, overCourse, weekDesc, title)

    toPDF.convertToPdf("schedule.xlsx")
