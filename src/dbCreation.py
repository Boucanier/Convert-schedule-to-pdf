import sqlite3
import os

FILE_PATH = "data/schedule.db"

def resetDB():
    new_db = os.path.exists(FILE_PATH)
    conn = sqlite3.connect(FILE_PATH)
    cur = conn.cursor()
    if new_db :
        cur.execute("DROP TABLE staff")
        cur.execute("DROP TABLE modules")
        cur.execute("DROP TABLE groups")
        cur.execute("DROP TABLE rooms")
        cur.execute("DROP TABLE courses")

    cur.execute("CREATE TABLE staff (staff_id INTEGER PRIMARY KEY, staff_name TEXT)")
    cur.execute("CREATE TABLE modules (module_id INTEGER PRIMARY KEY, module_name TEXT)")
    cur.execute("CREATE TABLE groups (group_id INTEGER PRIMARY KEY, group_name VARCHAR(20))")
    cur.execute("CREATE TABLE rooms (room_id INTEGER PRIMARY KEY, room_name VARCHAR(10))")
    cur.execute("CREATE TABLE courses (first_day_week DATE, date_cours DATE, t_start VARCHAR(5), t_end VARCHAR(5),\
                  group_id INTEGER REFERENCES groups(group_id),\
                  module_id INTEGER REFERENCES modules(module_id),\
                  staff_id INTEGER REFERENCES staff(staff_id),\
                  room_id INTEGER REFERENCES rooms(room_id))")
    
    conn.commit()
    cur.close()
    conn.close()

resetDB()