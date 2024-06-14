"""
    This file contains functions to create an image representing a one day schedule
"""
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont, ImageColor
from models.course import Course

HEIGHT = 1000
WIDTH = 400


def create_header(schedule_draw : ImageDraw.ImageDraw, schedule_date : date) -> None :
    """
        Create the header of the schedule image

        - Args :
            - scheduleDraw (ImageDraw.ImageDraw) : the draw object of the image
            - scheduleDate (date) : the date of the schedule

        - Returns :
            - None
    """
    week_days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    t_font = ImageFont.truetype('src/lib/fonts/Arial/arial.ttf', 30)

    schedule_draw.rectangle((0, 0, WIDTH, 100), fill=(220, 220, 220))

    schedule_draw.text((WIDTH/2, 40),
                       week_days[schedule_date.weekday()],
                       font=t_font,
                       fill= "black",
                       anchor="ms")
    schedule_draw.text((WIDTH/2, 80),
                       schedule_date.strftime("%d/%m/%Y"),
                       font=t_font,
                       fill= "black",
                       anchor="ms")

    schedule_draw.line((0, 100, WIDTH, 100), fill="black", width=2)


def create_side_bar(schedule_draw : ImageDraw.ImageDraw) -> None :
    """
        Create the side bar of the schedule image

        - Args :
            - scheduleDraw (ImageDraw.ImageDraw) : the draw object of the image

        - Returns :
            - None
    """
    time_list = ["8h", "9h", "10h", "11h", "12h", "13h", "14h", "15h", "16h", "17h", "18h", "19h"]
    t_font = ImageFont.truetype('src/lib/fonts/Arial/arial.ttf', 20)

    schedule_draw.rectangle((0, 100, 60, HEIGHT), fill=(220, 220, 220))

    for (i, item) in enumerate(time_list) :
        schedule_draw.text((60, 120 + i * 78), item + " -", font=t_font, fill= "black", anchor="rm")

    schedule_draw.line((60, 100, 60, HEIGHT), fill="black", width=2)


def add_courses(schedule_draw : ImageDraw.ImageDraw, course_list : list[Course]) -> None :
    """
        Add the courses to the schedule image
        TODO : Improve spacing between elements of course depending on its duration

        - Args :
            - scheduleDraw (ImageDraw.ImageDraw) : the draw object of the image
            - courseList (list[Course]) : the list of courses

        - Returns :
            - None
    """
    # b_font = ImageFont.truetype('src/lib/fonts/Arial/arial_bold.ttf', 18)
    t_font = ImageFont.truetype('src/lib/fonts/Arial/arial.ttf', 18)

    for course in course_list :
        start_offset = 121 + ((course.start_minutes) / 60 - 8) * 78
        end_offset = 121 + ((course.end_minutes) / 60 - 8) * 78

        schedule_draw.rectangle((65, start_offset, WIDTH - 4, end_offset),
                                fill=ImageColor.getrgb('#' + course.color_content),
                                outline="black",
                                width=2)

        f_line = course.time_content[0] + " - " + course.time_content[1]\
                + " : " + course.room_content

        schedule_draw.text(((61 + WIDTH)/2, start_offset + 15),
                           f_line, font=t_font,
                           fill= "black",
                           anchor="mm")
        schedule_draw.text(((61 + WIDTH)/2, start_offset + 40),
                           course.module_content,
                           font=t_font,
                           fill= "black",
                           anchor="mm")
        schedule_draw.text(((61 + WIDTH)/2, start_offset + 62),
                           course.prof_content,
                           font=t_font,
                           fill= "black",
                           anchor="mm")



def create_schedule_image(course_list : list[list[Course]],
                          week_desc : list[str],
                          name : str,
                          to_date : date = date.today()) -> None:
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
    schedule_img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    scheduledraw = ImageDraw.Draw(schedule_img)

    create_header(scheduledraw, to_date)
    create_side_bar(scheduledraw)

    w_index, i = -1, 0
    while w_index < 0 and i < len(week_desc):
        comp_date = datetime.strptime(week_desc[i], "%d_%m_%Y").date()
        if -6 <= ((comp_date - to_date).days) :
            w_index = i
        i += 1

    chosen_day = []
    for e in course_list[w_index] :
        if e.day_content == to_date.weekday() :
            chosen_day.append(e)

    add_courses(scheduledraw, chosen_day)

    schedule_img.save(name + '.png')
