# ......
# :.  .:
# .'  '.
# |    |
# |    |
# `----'
import tkinter as tk
from tkinter import ttk
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from lib.common.report_parser import StudentListReport, AttendanceReport
from lib.common.nudger import Nudger
import yaml
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import smtplib
import sys

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")

class App:
    def __init__(self, master):

        master.title("Attendance Nudge-er")

        output_width = 90
        output_height = 30

        self.lbl_students_file=ttk.Label(master, text="Students List")
        self.lbl_students_file.grid(row=0, column=0, sticky=tk.W)
        self.txt_students_file = ttk.Label(master, relief=tk.SUNKEN, width=output_width)
        self.txt_students_file.grid(row=1, column=0)
        self.btn_students_file = ttk.Button(master, text="...", width=3, command=self.set_students_file)
        self.btn_students_file.grid(row=1, column=1)

        self.lbl_report_file = ttk.Label(master, text="Latest Attendance Report")
        self.lbl_report_file.grid(row=2, column=0, sticky=tk.W)
        self.txt_report_file = ttk.Label(master, relief=tk.SUNKEN, width=output_width)
        self.txt_report_file.grid(row=3, column=0)
        self.btn_report_file = ttk.Button(master, text="...", width=3, command=self.set_report_file)
        self.btn_report_file.grid(row=3, column=1)

        self.txt_out = tk.Text(master, width=output_width, height=output_height, wrap=tk.WORD)
        self.txt_out.grid(row=4, column=0)
        #https://stackoverflow.com/questions/12351786/how-to-redirect-print-statements-to-tkinter-text-widget
        sys.stdout = TextRedirector(self.txt_out, "stdout")
        sys.stderr = TextRedirector(self.txt_out, "stderr")
        
        self.btn_run_report = ttk.Button(master, text="Run Report", width=10, command=self.run_report)
        self.btn_run_report.grid(row=4, column=1)

        with open("config.yml", 'r') as ymlfile:
                self.conf = yaml.load(ymlfile, Loader=yaml.SafeLoader)

    def set_report_file(self):
        self.report_file = askopenfilename()
        self.txt_report_file.config(text=self.report_file)
        print("Most recent report selected...")

    def set_students_file(self):
        self.students_file = askopenfilename()
        self.txt_students_file.config(text=self.students_file)
        print("Students file selected...")

    def import_report(self):
        filename = self.report_file
        print(f'Reading {filename}')
        report = AttendanceReport(filename, target_grade="09")
        self.students_with_reports, self.average_attendance_rate = report.read()
        print(f"Added {len(self.students_with_reports)} reports...\nAverage reported attendance was {self.average_attendance_rate}...")

    def import_students(self):
        filename = self.students_file 
        report = StudentListReport(filename)
        new_students = report.read()
        print(f"Added {len(new_students)} students...")

    def send_sms(self):
        nudger = Nudger(self.conf)
        sent = []
        [sent.append(nudger.send_text(swr, self.average_attendance_rate)) for swr in self.students_with_reports if swr['contact_by_phone']]
        print(f"Sent {len(sent)} text messages...")

    def send_emails(self):
        server = smtplib.SMTP('smtp.gmail.com:587') 
        server.ehlo()
        server.starttls()
        server.ehlo()
        #The nudger will authenticate us, then send the emails
        nudger = Nudger(self.conf, server)
        sent = []
        [sent.append(nudger.send_email(swr, self.average_attendance_rate)) for swr in self.students_with_reports if not swr['contact_by_phone']]
        server.quit()
        print(f"Sent {len(sent)} emails...")

    def run_report(self):
        self.import_students()
        self.import_report()
        self.send_sms()
        self.send_emails()
        print(f"Done!")

def main(): 
    pass

root = Tk()
app = App(root)
root.mainloop()
root.destroy()
