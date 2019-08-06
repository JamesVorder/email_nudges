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
