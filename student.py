import jinja2 as jinja
import sqlite3
from report import Report

class Student:
    
    reports = []

    def __init__(self, ID, name, email, phone, contact_by_phone): 
        self.ID = ID
        self.name = name
        self.email = email
        self.phone = phone
        self.contact_by_phone = 1

    def __str__(self):
        return self.name

    def render(self, _template):
        tm = jinja.Template(_template)
        return tm.render(student=self)

    def get_class_average_attendance(self):
        return abs(self.attendance_distance - self.attendance_rate)

    def add_to_db(self, connection):
        try:
            print(f"Adding {self.name} to the DB...")
            connection.execute("CREATE TABLE if not exists student \
                    (ID integer PRIMARY KEY, name text, email text, phone text, contact_by_phone integer)")
            connection.execute("INSERT INTO student VALUES(?, ?, ?, ?, ?)", 
                (int(self.ID), 
                self.name, 
                self.email,
                self.phone,
                self.contact_by_phone))
            connection.commit()
        except sqlite3.IntegrityError:
            pass
    
    def add_report(self, report):
        self.reports.add(report)

