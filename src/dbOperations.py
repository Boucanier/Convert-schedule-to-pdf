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
                 staff_id INTEGER REFERENCES staff(staff_id),\
                 room_id INTEGER REFERENCES room(room_id),\
                 module_id INTEGER REFERENCES module(module_id),\
                 groups_id INTEGER REFERENCES groups(groups_id),\
                 note TEXT)")

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


def getElements(tableName : str) -> dict[str, str]:
    """
        Get every element of a given table from database

        - Args :
            - tableName (str) : name of the table to get elements from
    """
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()
    data = cur.execute("SELECT * FROM " + tableName).fetchall()
    elementDic = {e[1] : str(e[0]) for e in data}

    cur.close()
    conn.close()
    return elementDic


def deleteByWeek(weekDesc : list[str]) -> None:
    """
        Delete every course of a given week from database

        - Args :
            - weekDesc (list[str]) : list of weeks' first days
    """
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()

    for e in weekDesc :
        cur.execute("DELETE FROM COURSE WHERE first_day_week LIKE '" + e + "'")
    
    conn.commit()
    cur.close()
    conn.close()


def insertCourse(courseList, weekDesc) -> None:
    """
        Insert every course from courseList into database
        Check if course is already in database before insertion and insert it only if it is not

        - Args :
            - courseList (list[list[Course]])
            - weekDesc (list[str]) : list of weeks' first days
    """
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()

    elementList = [getElements(e) for e in ELEMENTS]

    insertedList = []

    for k in courseList:
        for e in k :
            if e not in insertedList :
                cur.execute("INSERT INTO course VALUES('" + weekDesc[e.weekContent] + "', '" + str(e.dayContent) + "', '" + e.timeContent[0] + "', '" + e.timeContent[1] + "', FALSE, '" +\
                            elementList[0][e.profContent] + "', '" + elementList[1][e.roomContent] + "', '" + elementList[2][e.moduleContent] + "', '" + elementList[3][e.groupContent] + "', '" + e.noteContent + "')")
                insertedList.append(e)
    
    conn.commit()
    cur.close()
    conn.close()


def overwriteDB(allCourse, weekDesc : list[str]) -> None:
    """
        Update and overwrite database with new data for the 4 next weeks

        - Args :
            - allCourse (list[list[Course]])
            - weekDesc (list[str]) : list of weeks' first days
    """
    # Update rooms, staffs, modules and groups tables
    updateDB(allCourse)

    # Delete all courses of the 4 next weeks since it will be reinserted
    deleteByWeek(weekDesc)

    # Insert all courses of the 4 next weeks
    detailedCourse = elementSchedule.getFullDetailedList(allCourse)
    insertCourse(detailedCourse, weekDesc)
    print("DataBase overwritten\n")