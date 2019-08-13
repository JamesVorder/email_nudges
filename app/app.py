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

class App:
    def __init__(self, master):

        master.title("Attendance Nudge-er")

        self.lbl_students_file=ttk.Label(master, text="Students List")
        self.lbl_students_file.grid(row=0, column=0, sticky=tk.W)
        self.txt_students_file = ttk.Label(master, relief=tk.SUNKEN, width=30)
        self.txt_students_file.grid(row=1, column=0)
        self.btn_students_file = ttk.Button(master, text="...", width=3, command=self.set_students_file)
        self.btn_students_file.grid(row=1, column=1)

        self.lbl_report_file = ttk.Label(master, text="Latest Attendance Report")
        self.lbl_report_file.grid(row=2, column=0, sticky=tk.W)
        self.txt_report_file = ttk.Label(master, relief=tk.SUNKEN, width=30)
        self.txt_report_file.grid(row=3, column=0)
        self.btn_report_file = ttk.Button(master, text="...", width=3, command=self.set_report_file)
        self.btn_report_file.grid(row=3, column=1)

        self.btn_run_report = ttk.Button(master, text="Run Report", width=10, command=self.run_report)
        self.btn_run_report.grid(row=4)

        with open("config.yml", 'r') as ymlfile:
                self.conf = yaml.load(ymlfile)

    def set_report_file(self):
        self.report_file = askopenfilename()
        self.txt_report_file.config(text=self.report_file)

    def set_students_file(self):
        self.students_file = askopenfilename()
        self.txt_students_file.config(text=self.students_file)

    def import_report(self):
        filename = self.report_file
        #self.lbl_out.config(text=f'Reading {filename}')
        report = AttendanceReport(filename, target_grade="09")
        self.students_with_reports, self.average_attendance_rate = report.read() 
        #self.lbl_out.config(text="Report imported! Go ahead and send texts/emails.")

    def import_students(self):
        filename = self.students_file
        #self.lbl_out.config(text=f'Reading students from {filename}')
        report = StudentListReport(filename)
        report.read()
        #self.lbl_out.config(text="Students list imported! Go ahead and import a report.")

    def send_sms(self):
        nudger = Nudger(self.conf)
        [nudger.send_text(swr, self.average_attendance_rate) for swr in self.students_with_reports if swr['contact_by_phone']]

    def send_emails(self):
        server = smtplib.SMTP('smtp.gmail.com:587') 
        server.ehlo()
        server.starttls()
        server.ehlo()
        #The nudger will authenticate us, then send the emails
        nudger = Nudger(self.conf, server)
        [nudger.send_email(swr, self.average_attendance_rate) for swr in self.students_with_reports if not swr['contact_by_phone']]

    def run_report(self):
        self.import_students()
        self.import_report()
        self.send_sms()
        self.send_emails()

def main(): 
    pass

root = Tk()
app = App(root)
root.mainloop()
root.destroy()
