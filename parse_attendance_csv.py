# ......
# :.  .:
# .'  '.
# |    |
# |    |
# `----'
# https://www.cyberciti.biz/faq/vim-text-editor-find-and-replace-all-text/
# https://docs.python.org/3.7/howto/regex.html
import csv
import re

def locate_students(lines_in): 
    indices = []
    x = 0 
    for line in lines_in:
        if re.search("\d{6}.*$", line):#[\d,]+[0\.0]+$", line):
            #print(line)
            indices.append(x)
        #else:
            #print (f"OMITTED:{line}")
        x += 1
    #print(indices)
    return indices

def locate_subtotals(lines_in): 
    curr_line = 0
    sections = dict()
    ranges = []
    for line in lines_in:
        if re.search("Subtotals.*$", line):
            #print("Found some subtotals!")
            ranges.append((curr_line - 5, curr_line + 15))
        curr_line += 1 
    print(ranges)
    return ranges

def locate_grade(lines_in, grade):
    without_subtotals = filter_subtotals(lines_in, "test_data/out.csv", locate_subtotals(lines_in))
    cursor = 0
    output = []
    for line in without_subtotals:
        if(re.search(f"Grade Level: {grade}.*$", line)):
            #print(line)
            output.append(cursor)
        cursor += 1
    print(output)
    return output

def filter_subtotals(lines_in, _out, subtotals_ranges): 
    with open(_out, 'w') as csv_file:
        writing = False 
        cursor = 0
        output = []
        for tup in subtotals_ranges:
            for y in range(cursor, tup[0]):
                csv_file.write(lines_in[y])
                output.append(lines_in[y])
            cursor = tup[1]
    return output

class Student: 
    def __init__(self, grade, ID, name, days_enrolled, days_not_enrolled, days_present, days_excused, days_not_excused):
        self.name = name
        self.grade = grade
    def __str__(self):
        return self.name

def extract_students(_in):
    rows = csv.reader(_in)
    curr_grade = "" 
    output = []
    for row in rows:
        if re.search("Grade Level:.*$", row[0]):
            curr_grade = re.search("(\d+)", row[0]).groups()[0]
        elif re.search("\d{6}.*$", row[0]):
            output.append(Student(curr_grade, row[0], row[2], row[6], row[7], row[8], row[9], row[10])) 
    #print(output[0].grade)
    return output

with open('test_data/test.csv', 'r') as test_input:
   extract_students(test_input)

