import jinja2 as jinja
#import sqlite3
#from report import Report
import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer

class Student:
    
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    contact_by_phone(Boolean)

    def render(self, _template):
        tm = jinja.Template(_template)
        return tm.render(student=self)

    #def get_class_average_attendance(self):
    #    return abs(self.attendance_distance - self.attendance_rate)

    #def add_to_db(self, connection):
    #    try:
    #        print(f"Adding {self.name} to the DB...")
    #        connection.execute("CREATE TABLE if not exists student \
    #                (ID integer PRIMARY KEY, name text, email text, phone text, contact_by_phone integer)")
    #        connection.execute("INSERT INTO student VALUES(?, ?, ?, ?, ?)", 
    #            (int(self.ID), 
    #            self.name, 
    #            self.email,
    #            self.phone,
    #            self.contact_by_phone))
    #        connection.commit()
    #    except sqlite3.IntegrityError:
    #        pass
    
    #def add_report(self, report):
    #    self.reports.add(report)

