import csv
import re

def locate_subtotals(csv_path):
    with open(csv_path, 'r') as csv_file:
        csv_lines = csv_file.readlines()
        curr_line = 0
        sections = dict()
        sections_indices = []
        for line in csv_lines:
            if re.search("Subtotals.*$", line):
                print("Found some subtotals!")
                sections_indices.append((curr_line - 5, curr_line + 15))
            curr_line += 1 
        print(sections_indices)
        return sections_indices

# _in: string This is the path to the file to read from.
# _out: string This is the path to the file to write to. This will be the processed file we use later on.
def extract_ninth_grade_stats(_in, _out, subtotals_indices):
    csv_file_in = open(_in)
    with open(_out, 'w') as csv_file:
        writing = False
        lines = csv_file_in.readlines()
        cursor = 0
        for tup in subtotals_indices:
            for y in range(cursor, tup[0]):
                csv_file.write(lines[y])
            cursor = tup[1]
            #for y in range(tup[0], tup[1]):
            #    csv_file.write(lines[y])  
    return

extract_ninth_grade_stats('test_data/test.csv', 'test_data/out.csv', locate_subtotals('test_data/test.csv'))

