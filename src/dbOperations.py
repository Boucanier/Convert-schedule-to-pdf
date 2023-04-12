import sqlite3
import os
import elementSchedule


FILE_PATH = "data/schedule.db"
ELEMENTS = ("staff", "room", "module", "groups")

def createDB(allCourse):
    new_db = os.path.exists(FILE_PATH)
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()

    print("DataBase creation")
    if new_db :
        cur.execute("DROP TABLE staff")
        cur.execute("DROP TABLE module")
        cur.execute("DROP TABLE groups")
        cur.execute("DROP TABLE room")
        cur.execute("DROP TABLE course")

    cur.execute("CREATE TABLE staff (staff_id INTEGER PRIMARY KEY, staff_name TEXT)")
    cur.execute("CREATE TABLE module (module_id INTEGER PRIMARY KEY, module_name TEXT)")
    cur.execute("CREATE TABLE groups (groups_id INTEGER PRIMARY KEY, group_name VARCHAR(20))")
    cur.execute("CREATE TABLE room (room_id INTEGER PRIMARY KEY, room_name VARCHAR(10))")
    cur.execute("CREATE TABLE course (first_day_week DATE, date_cours DATE, t_start VARCHAR(5), t_end VARCHAR(5),\
                 groups_id INTEGER REFERENCES groups(groups_id),\
                 module_id INTEGER REFERENCES module(module_id),\
                 staff_id INTEGER REFERENCES staff(staff_id),\
                 room_id INTEGER REFERENCES room(room_id))")

    for e in ELEMENTS :
        elementList = elementSchedule.getFullList(allCourse, e)
        for i in range(len(elementList)) :
            cur.execute("INSERT INTO " + e + " VALUES (" + str(i) + ", '" + elementList[i] + "')")

    conn.commit()
    cur.close()
    conn.close()
    print("DataBase created\n")


def updateDB(allCourse):
    new_db = os.path.exists(FILE_PATH)
    if not new_db :
        print("DataBase does not exist")
        createDB(allCourse)
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()

    for e in ELEMENTS :
        elementList = elementSchedule.getFullList(allCourse, e)
        elementData = (cur.execute("SELECT * FROM " + e + " ORDER BY " + e + "_id")).fetchall()
        for l in elementList :
            if not any(l in sub for sub in elementData):
                elementData.append((elementData[-1][0] + 1, l))
                cur.execute("INSERT INTO " + e + " VALUES (" + str(elementData[-1][0]) + ", '" + l + "')")
    
    conn.commit()
    cur.close()
    conn.close()
    print("DataBase updated\n")