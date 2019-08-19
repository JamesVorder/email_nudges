#import sqlalchemy
from sqlalchemy import Column, String, Boolean, Float, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ..common.base import Base

class Report(Base): 

    __tablename__ = "reports"

    report_id = Column(Integer, index=True, primary_key=True)
    grade = Column(Integer)
    days_enrolled = Column(Float)
    days_present = Column(Float)
    days_excused = Column(Float)
    days_not_excused = Column(Float) 

    report_student_id = Column(Integer, ForeignKey('student.student_id')) 

    student = relationship("Student", back_populates="reports")
    
    def as_dict(self):
        return {'report_id': self.id, \
                'grade': self.grade, \
                'days_enrolled': float(self.days_enrolled), \
                'days_present': float(self.days_present), \
                'days_excused': float(self.days_excused), \
                'days_not_excused': float(self.days_excused)}

