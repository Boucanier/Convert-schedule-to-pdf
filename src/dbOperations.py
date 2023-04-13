import sqlite3
import os
import elementSchedule


FILE_PATH = "data/schedule.db"
ELEMENTS = ("staff", "room", "module", "groups")

def createDB(allCourse) -> None:
    """
        Create new database with every tables and fill tables STAFF, ROOM, MODULE, GROUPS

        If database already exists, it drops every table before insertion

        - Args :
            - allCourse (list[list[Course]])
    """
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

    cur.execute("CREATE TABLE staff (staff_id NUMBER(3) PRIMARY KEY, staff_name TEXT)")
    cur.execute("CREATE TABLE module (module_id NUMBER(3) PRIMARY KEY, module_name TEXT)")
    cur.execute("CREATE TABLE groups (groups_id NUMBER(3) PRIMARY KEY, group_name VARCHAR(20))")
    cur.execute("CREATE TABLE room (room_id NUMBER(3) PRIMARY KEY, room_name VARCHAR(10))")
    cur.execute("CREATE TABLE course (first_day_week VARCHAR(10), week_day NUMBER(1), t_start VARCHAR(5) NOT NULL, t_end VARCHAR(5) NOT NULL,\
                 man_set BOOLEAN NOT NULL,\
                 groups_id INTEGER REFERENCES groups(groups_id),\
                 module_id INTEGER REFERENCES module(module_id),\
                 staff_id INTEGER REFERENCES staff(staff_id),\
                 room_id INTEGER REFERENCES room(room_id),\
                 note TEXT,\
                 PRIMARY KEY(first_day_week, week_day, t_start, t_end, groups_id, module_id))")

    for e in ELEMENTS :
        elementList = elementSchedule.getFullList(allCourse, e)
        for i in range(len(elementList)) :
            cur.execute("INSERT INTO " + e + " VALUES (" + str(i) + ", '" + elementList[i] + "')")

    conn.commit()
    cur.close()
    conn.close()
    print("DataBase created\n")


def updateDB(allCourse) -> None:
    """
        Update database by adding missing elements of tables

        If database does not exist, it calls createDB() to create it

        - Args :
            - allCourse (list[list[Course]])
    """
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


def getElements(tableName):
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()
    data = cur.execute("SELECT * FROM " + tableName).fetchall()
    elementDic = {e[1] : e[0] for e in data}

    cur.close()
    conn.close()
    return elementDic