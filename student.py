import jinja2 as jinja
#import sqlite3
#from report import Report
import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

#def __init__():
Base = declarative_base()

class Student(Base):
    
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    contact_by_phone = Column(Boolean)

    def render(self, _template):
        tm = jinja.Template(_template)
        return tm.render(student=self)

