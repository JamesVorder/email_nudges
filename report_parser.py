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
from student import Student
#import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class StudentListReport:
    def __init__(self, filename, db):
        #self.connection = sqlite3.connect(db)
        #self.cursor = self.connection.cursor()
        self.filename = filename 
        engine = create_engine(f'sqlite:///{db}')
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def read(self):
        with open(self.filename, 'r') as file_in:
            rows = csv.reader(file_in)
            # Read all the students in from the
            curr_grade = ""
            for row in rows: 
                if re.search("Grade Level:.*$", row[0]):
                    curr_grade = re.search("(\d+)", row[0]).groups()[0]
                elif re.search("\d{6}.*$", row[0]):
                    new_student = Student(id=row[0], name=row[2], email=row[3], phone=row[4], contact_by_phone=row[5])
                    # Only add new students that are unique
                    try:
                        if self.session.query(Student).filter(Student.id.in_([new_student.id])).all().__len__() == 0:
                            self.session.add(new_student)
                        #Else, update all the values
                        else:
                            our_student = self.session.query(Student).filter_by(id=new_student.id).first()
                            our_student.email = new_student.email
                            our_student.phone = new_student.phone
                            our_student.contact_by_phone = new_student.contact_by_phone 
                    except:
                        pass
        self.session.commit()

class AttendanceReport:
    def __init__(self, filename, db, target_grade="09"):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.students = {}
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
        with open(self.filename, 'r') as incoming:

            # TODO: Read reports into the DB appropriately

            # parsing the students into a dataframe lets us do computations on them more easily
            students_dataframe = self.get_attendance_rates()
            self.average_attendance_rate = self.get_average_attendance_rate(students_dataframe)

            def update_attendance(row): 
                curr_student = self.students[int(row['ID'])]
                curr_student.attendance_rate = row['attendance_rate']
                curr_student.attendance_distance = float(curr_student.attendance_rate - self.average_attendance_rate)
            
            students_dataframe.apply(update_attendance, axis=1) 
            return {k: v for k, v in self.students.items() if v.grade == self.target_grade}
