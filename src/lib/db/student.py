import jinja2 as jinja
#import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ..common.base import Base

class Student(Base):

    __tablename__ = "student"

    student_id = Column(Integer, index=True, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    contact_by_phone = Column(Boolean)

    reports = relationship("Report", back_populates="student")

    def as_dict(self):
        return {'student_id': self.student_id, \
                'name': self.name, \
                'email': self.email, \
                'phone': self.phone, \
                'contact_by_phone': self.contact_by_phone}
