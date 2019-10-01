#import sqlalchemy
from sqlalchemy import Column, String, Boolean, Float, Integer, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ..common.base import Base

class GradesReport(Base):

    __tablename__ = "grades"

    report_id = Column(Integer, index=True, primary_key=True)
    current_avg = Column(Float)
    course = Column(String)
    date_added = Column(Date)

    report_student_id = Column(Integer, ForeignKey('student.student_id'))

    student = relationship("Student", back_populates="grades_reports")

    def as_dict(self):
        return {'report_id': self.report_id, \
                'current_avg': self.avg_grade, \
                'course': str(self.department), \
                'date_added': self.date_added)}
