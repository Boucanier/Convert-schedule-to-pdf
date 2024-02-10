"""
    This file contains functions to create an image representing a one day schedule
"""
from PIL import Image, ImageDraw, ImageFont, ImageColor
from models.course import *
from datetime import date, datetime

HEIGHT = 1000
WIDTH = 400


def createHeader(scheduleDraw : ImageDraw.ImageDraw, scheduleDate : date) -> None :
    """
        Create the header of the schedule image

        - Args :
            - scheduleDraw (ImageDraw.ImageDraw) : the draw object of the image
            - scheduleDate (date) : the date of the schedule

        - Returns :
            - None
    """
    weekDays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    tFont = ImageFont.truetype('src/lib/fonts/Arial/arial.ttf', 30)

    scheduleDraw.rectangle((0, 0, WIDTH, 100), fill=(220, 220, 220))

    scheduleDraw.text((WIDTH/2, 40), weekDays[scheduleDate.weekday()], font=tFont, fill= "black", anchor="ms")
    scheduleDraw.text((WIDTH/2, 80), scheduleDate.strftime("%d/%m/%Y"), font=tFont, fill= "black", anchor="ms")

    scheduleDraw.line((0, 100, WIDTH, 100), fill="black", width=2)


def createSideBar(scheduleDraw : ImageDraw.ImageDraw) -> None :
    """
        Create the side bar of the schedule image

        - Args :
            - scheduleDraw (ImageDraw.ImageDraw) : the draw object of the image

        - Returns :
            - None
    """
    timeList = ["8h", "9h", "10h", "11h", "12h", "13h", "14h", "15h", "16h", "17h", "18h", "19h"]
    tFont = ImageFont.truetype('src/lib/fonts/Arial/arial.ttf', 20)

    scheduleDraw.rectangle((0, 100, 60, HEIGHT), fill=(220, 220, 220))

    for i in range(len(timeList)) :
        scheduleDraw.text((60, 120 + i * 78), timeList[i] + " -", font=tFont, fill= "black", anchor="rm")

    scheduleDraw.line((60, 100, 60, HEIGHT), fill="black", width=2)


def addCourses(scheduleDraw : ImageDraw.ImageDraw, courseList : list[Course]) -> None :
    """
        Add the courses to the schedule image
        TODO : Improve spacing between elements of course depending on its duration

        - Args :
            - scheduleDraw (ImageDraw.ImageDraw) : the draw object of the image
            - courseList (list[Course]) : the list of courses

        - Returns :
            - None
    """
    bFont = ImageFont.truetype('src/lib/fonts/Arial/arial_bold.ttf', 18)
    tFont = ImageFont.truetype('src/lib/fonts/Arial/arial.ttf', 18)

    for course in courseList :
        startOffset = 121 + ((course.startMinutes) / 60 - 8) * 78
        endOffset = 121 + ((course.endMinutes) / 60 - 8) * 78

        scheduleDraw.rectangle((65, startOffset, WIDTH - 4, endOffset), fill=ImageColor.getrgb('#' + course.colorContent), outline="black", width=2)

        fLine = course.timeContent[0] + " - " + course.timeContent[1] + " : " + course.roomContent
        scheduleDraw.text(((61 + WIDTH)/2, startOffset + 15), fLine, font=tFont, fill= "black", anchor="mm")
        scheduleDraw.text(((61 + WIDTH)/2, startOffset + 40), course.moduleContent, font=tFont, fill= "black", anchor="mm")
        scheduleDraw.text(((61 + WIDTH)/2, startOffset + 62), course.profContent, font=tFont, fill= "black", anchor="mm")



def createScheduleImage(courseList : list[list[Course]], weekDesc : list[str], name : str, toDate : date = date.today()) -> None:
    """
        Create a xlsx file with only one day schedule from course list

        - Args :
            - courseList (list[list[Course]]) : the list of courses
            - weekDesc (list[str]) : the list of week description
            - title (str) : the title of the schedule
            - name (str) : the name of the file
            - toDate (date) : the date of the schedule to create

        - Returns :
            - None
    """
    scheduleImg = Image.new("RGB", (WIDTH, HEIGHT), "white")
    scheduleDraw = ImageDraw.Draw(scheduleImg)

    createHeader(scheduleDraw, toDate)
    createSideBar(scheduleDraw)

    wIndex, i = -1, 0
    while wIndex < 0 and i < len(weekDesc):
        compDate = datetime.strptime(weekDesc[i], "%d_%m_%Y").date()
        if ((compDate - toDate).days) <= 6 :
            wIndex = i
        i += 1
    
    chosenDay = list()
    for e in courseList[wIndex] :
        if e.dayContent == toDate.weekday() :
            chosenDay.append(e)

    addCourses(scheduleDraw, chosenDay)

    scheduleImg.save(name + '.png')
