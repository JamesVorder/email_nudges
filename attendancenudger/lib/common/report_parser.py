import csv
import re
from functools import reduce
from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import func
from .base import session_factory
from ..db.report import Report
from ..db.student import Student
import logging
from datetime import datetime
from numpy import mean
import itertools

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

class Report(object):
    def __init__(self, filename):
        self.filename = filename
        self.logger = logging.getLogger(__name__)


class AttendanceReport(Report):
    def __init__(self, filename, target_grade="09"):
        super().__init__(filename)
        self.target_grade = target_grade
        self.logger.debug(f"Initialized {__name__} with filename = '{self.filename}' and target_grade = {self.target_grade}")

    def read(self):
        students = []
        reports = []
        students_with_reports = []
        session = session_factory()
        with open(self.filename, 'r') as incoming:
            rows = csv.reader(incoming)
            curr_grade = ""
            for row in rows:
                if re.search("Grade Level:.*$", row[0]):
                    curr_grade = re.search("(\d+)", row[0]).groups()[0]
                    self.logger.debug(f"curr_grad={curr_grade}")
                #If this is a student's attendance report, and they're a ninth grader...
                elif re.search("\d{6}.*$", row[0]) and curr_grade == "09":
                    #initialize the new report object
                    new_report = Report(report_student_id = row[0], grade = curr_grade, days_enrolled = row[6],
                            days_present = row[8], days_excused=row[9], days_not_excused = row[10], date_added = datetime.now().date())
                    self.logger.debug(f"new_report = {str(new_report)}")
                    #if there is NOT already a matching report... (based on num days enrolled)
                    #AND there's a student in our DB that this record belongs to...
                    if len(session.query(Report).filter(
                            and_(Report.report_student_id == new_report.report_student_id, Report.days_enrolled == new_report.days_enrolled)
                            ).all()) == 0 and len(session.query(Student).filter(Student.student_id == new_report.report_student_id).all()) > 0:
                        student = session.query(Student).filter(Student.student_id == new_report.report_student_id).first()
                        student.reports.append(new_report)
                        students.append(student)
                        reports.append(new_report)
                        merged = dict()
                        merged.update(student.as_dict())
                        merged.update(new_report.as_dict())
                        try:
                            last_week_report = session.query(Report).filter(Report.report_student_id == new_report.report_student_id)\
			        .order_by(desc(Report.days_enrolled))[1]
                            weekly_stats = {
                                'days_enrolled_weekly': float(new_report.days_enrolled) - float(last_week_report.days_enrolled),
                                'days_present_weekly': float(new_report.days_present) - float(last_week_report.days_present)
                            }
                            merged.update(weekly_stats)
                        except IndexError:
                            weekly_stats = {
                                'days_enrolled_weekly': None,
                                'days_present_weekly': None,
                            }
                            merged.update(weekly_stats)
                            self.logger.debug("No report found from last week. This must be the first run on a new DB.")
                            pass
                        students_with_reports.append(merged)
                        self.logger.debug(f"students_with_reports[{len(students_with_reports)}] = {students_with_reports[len(students_with_reports)-1]}")
                    else:
                        next
            self.logger.info(f"Imported reports for {len(students_with_reports)} students.")

            def compute_attendance_rate(report):
                return float(report.days_present) / float(report.days_enrolled)

            attendance_rates = [compute_attendance_rate(report) for report in reports]
            weekly_attendance_rates = [(x['days_present_weekly'] / x['days_enrolled_weekly']) for x in students_with_reports \
                    if x['days_present_weekly'] and x['days_enrolled_weekly']]
            self.logger.debug(f"Computed {len(weekly_attendance_rates)} weekly attendance rates.")
            _sum = 0.0
            average_attendance_rate = None
            weekly_average_attendance_rate = None
            try:
                self.logger.debug(f"Computing average attendance rate for {len(attendance_rates)} students.")
                average_attendance_rate = mean(attendance_rates)
                self.logger.debug(f"Computing average attendance (this week) for {len(weekly_attendance_rates)} students.")
                weekly_average_attendance_rate = mean(weekly_attendance_rates)
                self.logger.debug(f"Computed weekly_average_attendance_rate = {weekly_average_attendance_rate}")
            except TypeError:
                self.logger.debug("There probably weren't any new records in this report.", stack_info=True)
                self.logger.warning("There weren't any new records in that report. Have you run it already?")
                pass

            session.commit()
            session.close()
            self.logger.debug(f"Committed and closed the session ({repr(session)})")
            self.logger.debug(f"Returning students_with_reports: {students_with_reports}, average_attendance_rate: {average_attendance_rate}, weekly_average_attendance_rate: {weekly_average_attendance_rate}")

            return students_with_reports, average_attendance_rate, weekly_average_attendance_rate

class GradesReport(Report):
    def __init__(self, filename):
        super().__init__(filename)
        self.logger.debug(f"Initialized {__name__} with filename = '{self.filename}'")

    def read(self):
        self.logger.debug(f"Entered {__name__}.read()")
        try:
            session = session_factory()
        except:
            self.logger.exception("There was a problem initializing the DB session.")

        with open(self.filename, 'r') as incoming:
            rows = itertools.islice(csv.reader(incoming), 2, None)
            for row in rows:
                student = session.query(Student).\
                    filter_by(name=row[0]).first()
                if student is None:
                    pass
                else:
                    print(f"{student.name}, {student.student_id}")
                    r = GradesReport(
                        report_student_id = student.student_id,
                        course = row[1],
                        current_avg = row[4],
                        created_date = datetime.now().date()
                    )
                    print(r).to_dict()
