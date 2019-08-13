# ......
# :.  .:
# .'  '.
# |    |
# |    |
# `----'
from tkinter import ttk
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from .lib.common.report_parser import StudentListReport, AttendanceReport
from .lib.common.nudger import Nudger
import yaml
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import smtplib

class App:
    def __init__(self, master):

        master.title("Attendance Nudge-er")

        self.btn_quit = ttk.Button(master, text="QUIT", command=master.quit)
        self.btn_quit.grid(row=0, column=0)

        self.btn_pick = ttk.Button(master, text="Import Attendance Report", command=self.import_report)
        self.btn_pick.grid(row=0, column=1)

        self.btn_import_students = ttk.Button(master, text="Import Students Report", command=self.import_students)
        self.btn_import_students.grid(row=0, column=2)
        
        self.lbl_out = ttk.Label(master, text="No reports run...")
        self.lbl_out.grid(row=1, columnspan=2)
       
        self.btn_send_emails = ttk.Button(master, text="Send Emails", command=self.send_emails)
        self.btn_send_emails.grid(row=2, column=0)

        self.btn_send_sms = ttk.Button(master, text="Send Texts", command=self.send_sms)
        self.btn_send_sms.grid(row=2, column=1)

        with open("config.yml", 'r') as ymlfile:
                self.conf = yaml.load(ymlfile)

    def import_report(self):
        filename = askopenfilename()
        self.lbl_out.config(text=f'Reading {filename}')
        report = AttendanceReport(filename, target_grade="09")
        self.students_with_reports, self.average_attendance_rate = report.read() 
        self.lbl_out.config(text="Report imported! Go ahead and send texts/emails.")

    def import_students(self):
        filename = askopenfilename()
        self.lbl_out.config(text=f'Reading students from {filename}')
        report = StudentListReport(filename)
        report.read()
        self.lbl_out.config(text="Students list imported! Go ahead and import a report.")

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

def main(): 
    pass

root = Tk()
app = App(root)
root.mainloop()
root.destroy()
