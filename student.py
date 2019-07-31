import jinja2 as jinja
import sqlite3

class Student:
    # the distance from this student's attendance rate to the average attendance rate
    def __init__(self, grade, ID, name, days_enrolled, days_not_enrolled, days_present, days_excused, days_not_excused, attendance_rate=1):
        self.grade = grade
        self.ID = ID
        self.name = name
        self.days_enrolled = days_enrolled
        self.days_not_enrolled = days_not_enrolled
        self.days_present = days_present
        self.days_excused = days_excused
        self.days_not_excused = days_not_excused
        #DERIVATIVE VALUES
        self.total_days_absent = int(days_excused) + int(days_not_excused)
        self.attendance_distance = 0.0
        self.attendance_rate = 1.0

    def __str__(self):
        return self.name

    def render(self, _template):
        tm = jinja.Template(_template)
        return tm.render(student=self)

    def get_class_average_attendance(self):
        return abs(self.attendance_distance - self.attendance_rate)

    def add_to_db(self, connection):
        try:
            connection.execute("CREATE TABLE if not exists students (ID integer primary key, name text, grade integer)")
            connection.execute("INSERT INTO students VALUES(?, ?, ?)", (int(self.ID), self.name, int(self.grade)))
            #connection.commit()
        except sqlite3.IntegrityError:
            pass
