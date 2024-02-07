"""
    This file contains functions to create an image representing a one day schedule
"""
from calendar import week
from PIL import Image, ImageDraw, ImageFont
from models.course import *
from datetime import date, datetime

HEIGHT = 1000
WIDTH = 400


def createHeader(scheduleDraw : ImageDraw.ImageDraw, scheduleDate : date = date.today()) -> None :
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
        scheduleDraw.text((60, 120 + i * 78), timeList[i] + " -", font=tFont, fill= "black", anchor="rs")

    scheduleDraw.line((60, 100, 60, HEIGHT), fill="black", width=2)


def createScheduleImage(courseList : list[list[Course]], weekDesc : list[str], title : str, name : str, toDate : date = date.today()) -> None:
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

    createHeader(scheduleDraw)
    createSideBar(scheduleDraw)

    wIndex, i = -1, 0
    while wIndex < 0 or i < len(weekDesc):
        compDate = datetime.strptime(weekDesc[i], "%d_%m_%Y").date()
        if ((compDate - toDate).days) <= 5 :
            wIndex = i
        i += 1
    
    chosenDay = list()
    for e in courseList[wIndex] :
        if e.dayContent == toDate.weekday() :
            chosenDay.append(e)

    scheduleImg.show()
