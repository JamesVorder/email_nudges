# ......
# :.  .:
# .'  '.
# |    |
# |    |
# `----'
import csv
import re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from lib.common.base import session_factory
from lib.db.schemas import Report, Student

class StudentListReport:
     
    def __init__(self, filename, db):
        self.filename = filename 

    def read(self):
        session = session_factory()
        with open(self.filename, 'r') as file_in:
            rows = csv.reader(file_in)
            # Read all the students in from the
            curr_grade = ""
            for row in rows: 
                if re.search("Grade Level:.*$", row[0]):
                    curr_grade = re.search("(\d+)", row[0]).groups()[0]
                elif re.search("\d{6}.*$", row[0]):
                    new_student = Student(id=int(row[0]), name=row[2], email=row[3], phone=row[4], contact_by_phone=bool(row[5]))
                    # Only add new students that are unique 
                    try:
                        if session.query(Student).filter(Student.id == new_student.id).all().__len__() == 0:
                            session.add(new_student) 
                        else:
                            our_student = session.query(Student).filter_by(id=new_student.id).first()
                            our_student.email = new_student.email
                            our_student.phone = new_student.phone
                            our_student.contact_by_phone = new_student.contact_by_phone 
                    except:
                        session.add(new_student)
        session.commit()
        session.close()

class AttendanceReport:
    def __init__(self, filename, db, target_grade="09"):
        self.filename = filename
        self.target_grade = target_grade

    def get_attendance_rates(self):
        # "comprehend" the list of students as a dataframe
        students_list = self.students.values()
        df = pd.DataFrame([student.__dict__.values() for student_id, student in self.students.items()],
                          columns=Student("", "", "", "", "", "", "0", "0").__dict__.keys())
        # Specify type where appropriate (for maths later on)
        df[['days_present', 'days_enrolled']] = df[['days_present', 'days_enrolled']].apply(pd.to_numeric)
        # filter down to the specified grade
        df = df[df['grade'] == self.target_grade] 
        # compute the attendance rate
        df['attendance_rate'] = df['days_present']/df['days_enrolled'] 
        return df

    def get_average_attendance_rate(self, _students_dataFrame):
        df = _students_dataFrame
        return df[['attendance_rate']].mean(axis=0)

    def read(self):
        session = session_factory()
        with open(self.filename, 'r') as incoming:
            rows = csv.reader(incoming) 
            for row in rows:
                if re.search("Grade Level:.*$", row[0]):
                    curr_grade = re.search("(\d+)", row[0]).groups()[0]
                elif re.search("\d{6}.*$", row[0]) and curr_grade == "09":
                    new_report = Report(student_id = row[0], grade = curr_grade, days_enrolled = row[6], days_present = row[8], days_excused=row[9], days_not_excused = row[10])  
                    if session.query(Report).filter(and_(Report.student_id == new_report.student_id, Report.days_enrolled == new_report.days_enrolled)).all().__len__() == 0:
                        student = session.query(Student).filter(Student.id == new_report.student_id).first()
                        student.reports.append(new_report)
                        print(student.reports)
                    else:
                        pass 

            session.commit()
            session.close()

            # parsing the students into a dataframe lets us do computations on them more easily
            students_dataframe = self.get_attendance_rates()
            self.average_attendance_rate = self.get_average_attendance_rate(students_dataframe)

            def update_attendance(row): 
                curr_student = self.students[int(row['ID'])]
                curr_student.attendance_rate = row['attendance_rate']
                curr_student.attendance_distance = float(curr_student.attendance_rate - self.average_attendance_rate)
            
            students_dataframe.apply(update_attendance, axis=1) 
            return {k: v for k, v in self.students.items() if v.grade == self.target_grade}
