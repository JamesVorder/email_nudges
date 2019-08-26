import csv
import re
from functools import reduce
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import func 
from .base import session_factory
from ..db.report import Report
from ..db.student import Student
import logging

class StudentListReport:
     
    def __init__(self, filename):
        self.filename = filename 
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized StudentListReport with {self.filename}")

    def read(self):
        self.logger.debug(f"Entered {__name__}.read()")
        try:
            session = session_factory()
        except:
            self.logger.exception("There was a problem initializing the DB session.")

        new_students = []
        with open(self.filename, 'r') as file_in:
            rows = csv.reader(file_in)
            # Read all the students in from the
            curr_grade = ""
            #self.logger.info(f"Reading {sum(1 for row in rows)} students from file.")
            #rows.seek(0)
            i = 0
            for row in rows:
                i += 1
                if re.search("\d{6}.*$", row[0]):
                    new_student = Student(student_id=int(row[0]), name=row[2], email=row[3], phone=row[4], contact_by_phone=bool(row[5])) 
                    self.logger.debug(f"new_student = {str(new_student)}")
                    try:
                        if session.query(Student).filter(Student.student_id == new_student.student_id).all().__len__() == 0:
                            self.logger.debug(f"Didnt find any existing students with student_id = {new_student.student_id}")
                            session.add(new_student)
                            new_students.append(new_student)
                            self.logger.debug(f"Added {repr(new_student)} to session and new_students[{len(new_students) - 1}]")
                        else:
                            self.logger.debug(f"Found an existing student with student_id = {new_student.student_id}")
                            our_student = session.query(Student).filter_by(student_id=new_student.student_id).first()
                            our_student.email = new_student.email
                            our_student.phone = new_student.phone
                            our_student.contact_by_phone = new_student.contact_by_phone 
                            self.logger.debug(f"Updated fields for existing student {new_student.student_id}")
                    except:
                        self.logger.debug(f"This must have been the first student added to the DB...")
                        session.add(new_student)
                        new_students.append(new_student)
                        self.logger.debug(f"Added {repr(new_student)} to session and new_students[{len(new_students) - 1}]")
                else:
                    self.logger.debug(f"Found a line that was not a student in the students file... (Line #{i}")
        session.commit()
        session.close()
        self.logger.debug(f"Committed and closed the session ({repr(session)})")

        return new_students

class AttendanceReport:
    def __init__(self, filename, target_grade="09"):
        self.filename = filename
        self.target_grade = target_grade
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized {__name__} with filename = '{self.filename}' and target_grade = {self.target_grade}")

    def read(self):
        students = []
        reports = []
        students_with_reports = []
        session = session_factory()
        with open(self.filename, 'r') as incoming:
            rows = csv.reader(incoming) 
            curr_grade = ""
            #self.logger.info(f"Reading {sum(1 for row in rows)} attendance records from file.")
            #rows.seek(0)
            for row in rows:
                if re.search("Grade Level:.*$", row[0]):
                    curr_grade = re.search("(\d+)", row[0]).groups()[0]
                    self.logger.debug(f"curr_grad={curr_grade}")
                elif re.search("\d{6}.*$", row[0]) and curr_grade == "09":
                    new_report = Report(report_student_id = row[0], grade = curr_grade, days_enrolled = row[6], days_present = row[8], days_excused=row[9], days_not_excused = row[10])  
                    self.logger.debug(f"new_report = {str(new_report)}")
                    if session.query(Report).filter(and_(Report.report_student_id == new_report.report_student_id, Report.days_enrolled == new_report.days_enrolled)).all().__len__() == 0:
                        student = session.query(Student).filter(Student.student_id == new_report.report_student_id).first()
                        student.reports.append(new_report)
                        students.append(student)
                        reports.append(new_report)
                        merged = dict()
                        merged.update(student.as_dict())
                        merged.update(new_report.as_dict())
                        students_with_reports.append(merged)
                    else:
                        pass 
            self.logger.info(f"Imported reports for {len(students_with_reports)} students.")

            def compute_attendance_rate(report): 
                return float(report.days_present) / float(report.days_enrolled)
  
            attendance_rates = [compute_attendance_rate(report) for report in reports] 
            _sum = 0.0
            average_attendance_rate = None
            try:
                average_attendance_rate = reduce((lambda _sum, rate: _sum + rate), attendance_rates) 
                average_attendance_rate /= attendance_rates.__len__() 
            except TypeError:
                self.logger.debug("There probably weren't any new records in this report.", stack_info=True)
                self.logger.warning("There weren't any new records in that report. Have you run it already?")
                pass
             
            session.commit()
            session.close()
            self.logger.debug(f"Committed and closed the session ({repr(session)})")

            return students_with_reports, average_attendance_rate

