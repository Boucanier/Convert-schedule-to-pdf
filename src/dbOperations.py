from itertools import count
import sqlite3, os, elementSchedule
from course import *
from datetime import datetime, timedelta


FILE_PATH = "data/schedule.db"
ELEMENTS = ("staff", "room", "module", "groups")

def createDB(allCourse : list[list[Course]]) -> None:
    """
        Create new database with every tables and fill tables STAFF, ROOM, MODULE, GROUPS

        If database already exists, it drops every table before insertion

        - Args :
            - allCourse (list[list[Course]])

        - Returns :
            - None
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
    cur.execute("CREATE TABLE course (week_day NUMBER(1), t_start VARCHAR(5) NOT NULL, t_end VARCHAR(5) NOT NULL,\
                 man_set BOOLEAN NOT NULL,\
                 staff_id INTEGER REFERENCES staff(staff_id),\
                 room_id INTEGER REFERENCES room(room_id),\
                 module_id INTEGER REFERENCES module(module_id),\
                 groups_id INTEGER REFERENCES groups(groups_id),\
                 note TEXT,\
                 first_day_week VARCHAR(10) NOT NULL,\
                 color VARCHAR(10))")

    for e in ELEMENTS :
        elementList = elementSchedule.getFullList(allCourse, e)
        for i in range(len(elementList)) :
            cur.execute("INSERT INTO " + e + " VALUES (" + str(i) + ", '" + elementList[i] + "')")

    conn.commit()
    cur.close()
    conn.close()
    print("DataBase created\n")


def updateDB(allCourse : list[list[Course]]) -> None:
    """
        Update database by adding missing elements of tables

        If database does not exist, it calls createDB() to create it

        - Args :
            - allCourse (list[list[Course]])

        - Returns :
            - None
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

        - Returns :
            - elementDic (dict[str, str]) : dictionary of elements with their id as key
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
        cur.execute("DELETE FROM COURSE WHERE first_day_week LIKE '" + e[6:10] + "_" + e[3:5] + "_" + e[0:2] + "'")
    
    conn.commit()
    cur.close()
    conn.close()


def insertCourse(courseList : list[list[Course]], weekDesc : list[str]) -> None:
    """
        Insert every course from courseList into database
        Check if course is already in database before insertion and insert it only if it is not

        - Args :
            - courseList (list[list[Course]])
            - weekDesc (list[str]) : list of weeks' first days

        - Returns :
            - None
    """
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()

    elementList = [getElements(e) for e in ELEMENTS]

    insertedList = []

    for k in courseList:
        for e in k :
            if e not in insertedList :
                cur.execute("INSERT INTO course VALUES('" + str(e.dayContent) + "', '" + e.timeContent[0] + "', '" + e.timeContent[1] + "', FALSE, '" +\
                            elementList[0][e.profContent] + "', '" + elementList[1][e.roomContent] + "', '" + elementList[2][e.moduleContent] + "', '" +\
                            elementList[3][e.groupContent] + "', '" + e.noteContent + "', '" + weekDesc[e.weekContent][6:10] + "_" + weekDesc[e.weekContent][3:5] + "_" + weekDesc[e.weekContent][0:2] + "', '" + e.colorContent + "')")
                insertedList.append(e)
    
    conn.commit()
    cur.close()
    conn.close()


def overwriteDB(allCourse : list[list[Course]], weekDesc : list[str]) -> None:
    """
        Update and overwrite database with new data for the 4 next weeks

        - Args :
            - allCourse (list[list[Course]])
            - weekDesc (list[str]) : list of weeks' first days

        - Returns :
            - None
    """
    # Update rooms, staffs, modules and groups tables
    updateDB(allCourse)

    # Delete all courses of the 4 next weeks since it will be reinserted
    deleteByWeek(weekDesc)

    # Insert all courses of the 4 next weeks
    detailedCourse = elementSchedule.getFullDetailedList(allCourse)
    insertCourse(detailedCourse, weekDesc)
    print("DataBase overwritten\n")


def getCourseByElement(type : str, element : str) -> tuple[list[Course], list[str]]:
    """
        Get every course of a given element

        - Args :
            - type (str) : type of the element (staff, room, module or groups)
            - element (str) : name of the element

        - Returns :
            - courseList (list[list[Course]])
            - weekDesc (list[str]) : list of weeks' first days
    """
    type = type + "_name"
    courseList = list()
    weekDesc = list()
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()

    today = (datetime.today() - timedelta(days = 6)).strftime(r"%Y_%m_%d")
    request = str()

    if type == "staff_name" :
        request = "SELECT DISTINCT c1.week_day, c1.t_start, c1.t_end, module_name, room_name, s2.staff_name, group_name, c1.first_day_week, c1.note, c1.color\
                    FROM course c1, course c2, groups g, module m, room r, staff s1, staff s2\
                    WHERE c1.module_id = c2.module_id\
                    AND c1.first_day_week = c2.first_day_week\
                    AND c1.week_day = c2.week_day\
                    AND c1.t_start = c2.t_start\
                    AND c1.t_end = c2.t_end\
                    AND c1.module_id = m.module_id\
                    AND c1.groups_id = g.groups_id\
                    AND c1.room_id = r.room_id\
                    AND c1.staff_id = s1.staff_id\
                    AND c2.staff_id = s2.staff_id\
                    AND s1." + type + " LIKE '%" + element + "%'\
                    AND c1.first_day_week >= '" + today +"'\
                    ORDER BY c1.first_day_week;"
    
    elif type == "room_name" :
        request = "SELECT DISTINCT c1.week_day, c1.t_start, c1.t_end, module_name, r2.room_name, s.staff_name, group_name, c1.first_day_week, c1.note, c1.color\
                    FROM course c1, course c2, groups g, module m, room r1, room r2, staff s\
                    WHERE c1.module_id = c2.module_id\
                    AND c1.first_day_week = c2.first_day_week\
                    AND c1.week_day = c2.week_day\
                    AND c1.t_start = c2.t_start\
                    AND c1.t_end = c2.t_end\
                    AND c1.module_id = m.module_id\
                    AND c1.groups_id = g.groups_id\
                    AND c1.room_id = r1.room_id\
                    AND c2.room_id = r2.room_id\
                    AND c1.staff_id = s.staff_id\
                    AND r1." + type + " LIKE '%" + element + "%'\
                    AND c1.first_day_week >= '" + today +"'\
                    ORDER BY c1.first_day_week;"


    data = cur.execute(request).fetchall()

    for e in data :
        if (e[7][8:10] + '_' + e[7][5:7] + '_' + e[7][0:4]) not in weekDesc :
            weekDesc.append(e[7][8:10] + '_' + e[7][5:7] + '_' + e[7][0:4])

    for e in data :
        courseList.append(Course(e[0], [e[1], e[2]], e[3], e[4], e[5], e[6], weekDesc.index(e[7][8:10] + '_' + e[7][5:7] + '_' + e[7][0:4]), e[8], e[9]))

    cur.close()
    conn.close()

    courseList = elementSchedule.mergeCourse(courseList)
    
    return courseList, weekDesc


def countElement(type : str, element : str) -> int :
    """
        Count the number of row containing a given element in a given table

        - Args :
            - type (str) : type of the element (staff, room, module or groups)
            - element (str) : name of the element

        - Returns :
            - count (int) : number of row containing the element
    """
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()

    request = "SELECT COUNT(DISTINCT " + type + "_name) FROM " + type + " WHERE " + type + "_name LIKE '%" + element + "%';"
    count = cur.execute(request).fetchone()[0]

    cur.close()
    conn.close()
    return count