# ......
# :.  .:
# .'  '.
# |    |
# |    |
# `----'
# https://www.cyberciti.biz/faq/vim-text-editor-find-and-replace-all-text/
# https://docs.python.org/3.7/howto/regex.html
# https://wiki.python.org/moin/Templating
# https://github.com/defunkt/pystache
# https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
# https://www.tutorialspoint.com/python_pandas/python_pandas_comparison_with_sql.htm
# https://pandas.pydata.org/pandas-docs/stable/
# https://pandas.pydata.org/pandas-docs/stable/user_guide/cookbook.html#new-columns
# https://stackoverflow.com/questions/35439613/python-pandas-dividing-column-by-another-column
# https://www.pythonforbeginners.com/basics/list-comprehensions-in-python
# https://vim.fandom.com/wiki/Replace_a_word_with_yanked_text
# https://vim.fandom.com/wiki/Go_to_definition_using_g
# http://zetcode.com/python/jinja/
# http://jinja.pocoo.org/docs/2.10/templates/
import csv
import re
import jinja2 as jinja
#import pybars3
#import pystache
import pandas as pd
import numpy as np
import sqlite3

class Student:
    # the distance from this student's attendance rate to the average attendance rate
    def __init__(self, grade, ID, name, days_enrolled, days_not_enrolled, days_present, days_excused, days_not_excused, attendance_rate=1):
        self.grade = grade
        self.ID = ID
        self.name = name
        self.days_enrolled = days_enrolled
        self.days_not_enrolled = days_not_enrolled
        self.days_present = days_present
        self.days_excused = days_excused
        self.days_not_excused = days_not_excused
        #DERIVATIVE VALUES
        self.total_days_absent = int(days_excused) + int(days_not_excused)
        self.attendance_distance = 0.0
        self.attendance_rate = 1.0

    def __str__(self):
        return self.name

    def render(self, _template):
        tm = jinja.Template(_template)
        return tm.render(student=self)

    def get_class_average_attendance(self):
        return abs(self.attendance_distance - self.attendance_rate)

    def add_to_db(self, connection):
        connection.execute("CREATE TABLE if not exists students (ID integer, name text, grade integer)")
        connection.execute("INSERT INTO students VALUES(?, ?, ?)", (int(self.ID), self.name, int(self.grade)))
        connection.commit()

class AttendanceReport:
    def __init__(self, filename, db, target_grade="09"):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.students = {}
        self.filename = filename
        self.target_grade = target_grade

    def extract_students(self, _in):
        #print(f"Extracting students from {self.filename}")
        rows = csv.reader(_in)
        curr_grade = ""
        for row in rows:
            #print(row)
            if re.search("Grade Level:.*$", row[0]):
                curr_grade = re.search("(\d+)", row[0]).groups()[0]
            elif re.search("\d{6}.*$", row[0]):
                #print("doing the thing")
                new_student = Student(curr_grade, row[0], row[2], row[6], row[7], row[8], row[9], row[10])
                new_student.add_to_db(self.connection)
                self.students[int(new_student.ID)] = new_student
                print(f"Added {new_student.name} to the DB...")

    def get_attendance_rates(self):
        # "comprehend" the list of students as a dataframe
        students_list = self.students.values()
        df = pd.DataFrame([student.__dict__.values() for student_id, student in self.students.items()],
                          columns=Student("", "", "", "", "", "", "0", "0").__dict__.keys())
        # Specify type where appropriate (for maths later on)
        df[['days_present', 'days_enrolled']] = df[['days_present', 'days_enrolled']].apply(pd.to_numeric)
        # filter down to the specified grade
        df = df[df['grade'] == self.target_grade]
        print(df)
        # compute the attendance rate
        df['attendance_rate'] = df['days_present']/df['days_enrolled']
        #print(df) 
        return df

    def get_average_attendance_rate(self, _students_dataFrame):
        df = _students_dataFrame
        return df[['attendance_rate']].mean(axis=0)

    def read(self):
        with open(self.filename, 'r') as incoming:

            # read the students out of the csv into an array of Student objects
            self.extract_students(incoming)
            print(self.students)
            
            #print(self.cursor.fetchone())
            #self.connection.commit()
            self.connection.close()

            # parsing the students into a dataframe lets us do computations on them more easily
            students_dataframe = self.get_attendance_rates()

            print(students_dataframe)
            
            self.average_attendance_rate = self.get_average_attendance_rate(students_dataframe)

            def update_attendance(row):
                #print(f"{row} was the row.")
                curr_student = self.students[int(row['ID'])]
                curr_student.attendance_rate = row['attendance_rate']
                curr_student.attendance_distance = float(curr_student.attendance_rate - self.average_attendance_rate)
            
            #df = students_dataframe[students_dataframe['grade'] == self.target_grade]
            #print(df)
            students_dataframe.apply(update_attendance, axis=1)
            #print(f"{students[319752].attendance_rate} ({students[319752].attendance_distance})")

            for student_id, student in self.students.items():
                if student.grade == self.target_grade:
                    with open(f'_templates/attendance.html', 'r') as template:
                        with open(f'test_data/{student_id}_attendanceReport.html', 'w') as out:
                            out.write(student.render(template.read()))
