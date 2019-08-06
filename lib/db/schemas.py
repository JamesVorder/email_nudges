import jinja2 as jinja
import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ..common.base import Base

class Student(Base):
    
    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    contact_by_phone = Column(Boolean)

    reports = relationship("Report", back_populates="student")

class Report(Base): 

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    grade = Column(Integer)
    days_enrolled = Column(Float)
    days_present = Column(Float)
    days_excused = Column(Float)
    days_not_excused = Column(Float) 

    student_id = Column(Integer, ForeignKey('student.id')) 

    student = relationship("Student", back_populates="reports")
    
    #def render(self, _template):
    #    tm = jinja.Template(_template)
    #    return tm.render(student=self)

