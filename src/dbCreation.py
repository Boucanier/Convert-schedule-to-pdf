import sqlite3
import os
import scraper
import elementSchedule

FILE_PATH = "data/schedule.db"

def resetDB():
    new_db = os.path.exists(FILE_PATH)
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()
    if new_db :
        cur.execute("DROP TABLE staff")
        cur.execute("DROP TABLE module")
        cur.execute("DROP TABLE groups")
        cur.execute("DROP TABLE room")
        cur.execute("DROP TABLE course")

    cur.execute("CREATE TABLE staff (staff_id INTEGER PRIMARY KEY, staff_name TEXT)")
    cur.execute("CREATE TABLE module (module_id INTEGER PRIMARY KEY, module_name TEXT)")
    cur.execute("CREATE TABLE groups (group_id INTEGER PRIMARY KEY, group_name VARCHAR(20))")
    cur.execute("CREATE TABLE room (room_id INTEGER PRIMARY KEY, room_name VARCHAR(10))")
    cur.execute("CREATE TABLE course (first_day_week DATE, date_cours DATE, t_start VARCHAR(5), t_end VARCHAR(5),\
                 group_id INTEGER REFERENCES groups(group_id),\
                 module_id INTEGER REFERENCES module(module_id),\
                 staff_id INTEGER REFERENCES staff(staff_id),\
                 room_id INTEGER REFERENCES room(room_id))")
    
    elements = ("staff", "room", "module")

    urlList, titleList = scraper.getLink(True)
    allCourse, weekDesc = elementSchedule.getFullSchedule(urlList, titleList)

    for e in elements :
        elementList, courseList = elementSchedule.getFullList(allCourse, e)
        for i in range(len(elementList)) :
            cur.execute("INSERT INTO " + e + " VALUES (" + str(i) + ", '" + elementList[i] + "')")

    conn.commit()
    cur.close()
    conn.close()

resetDB()