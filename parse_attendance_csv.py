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
import csv
import re
import pystache
import pandas as pd
import numpy as np

class Grade:
    average_attendance_rate = 0
    def __init__(self, _students):
        self.students = _students

class Student: 
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
    def __str__(self):
        return self.name
    def render(self, _template):
        return pystache.render(_template, self.__dict__)

# outputs a list of Student objects.
def extract_students(_in):
    rows = csv.reader(_in)
    curr_grade = "" 
    output = []
    for row in rows:
        if re.search("Grade Level:.*$", row[0]):
            curr_grade = re.search("(\d+)", row[0]).groups()[0]
        elif re.search("\d{6}.*$", row[0]):
            output.append(Student(curr_grade, row[0], row[2], row[6], row[7], row[8], row[9], row[10]))  
    return output

def compute_averages(_students, grade): 
    df = pd.DataFrame([student.__dict__.values() for student in _students], columns=_students[0].__dict__.keys())
    df[['days_present', 'days_enrolled']] = df[['days_present', 'days_enrolled']].apply(pd.to_numeric)
    df = df[df['grade'] == grade]
    df['attendance_rate'] = df['days_present']/df['days_enrolled'] 
    print(df)
    return df

#def aggregate_averages(_students):


with open('test_data/test.csv', 'r') as test_input:
   students = extract_students(test_input) 
   compute_averages(students, '09')
#with open('_templates/attendance.html', 'r') as attendance_template: 
#    email_content = students[0].render(attendance_template.read())
#with open('test_data/out.html', 'w') as test_output:
#    test_output.write(email_content)
