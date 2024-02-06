"""
    This file contains functions to create an image representing a one day schedule
"""
from PIL import Image, ImageDraw, ImageFont
from models.course import *
from datetime import date, datetime

HEIGHT = 1000
WIDTH = 400


def createHeader(scheduleDraw : ImageDraw, scheduleDate : date = date.today()) -> None :
    myFont = ImageFont.truetype('src/lib/fonts/Arial/arial.ttf', 30)

    scheduleDraw.rectangle((0, 0, WIDTH, 100), fill=(220, 220, 220))

    scheduleDraw.text((WIDTH/2, 50), scheduleDate.strftime("%d/%m/%Y"), font=myFont, fill= "black", anchor="ms")


def createScheduleImage(courseList : list[list[Course]], weekDesc : list[str], title : str, name : str, toDate : date = date.today()) -> None:
    """
        Create a xlsx file with only one day schedule from course list
    """
    scheduleImg = Image.new("RGB", (WIDTH, HEIGHT), "white")
    scheduleDraw = ImageDraw.Draw(scheduleImg)

    createHeader(scheduleDraw)

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
