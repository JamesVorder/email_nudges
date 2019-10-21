import tkinter as tk
from tkinter import ttk
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from .lib.common.report_parser import StudentListReport, AttendanceReport, GradesReport
from .lib.common.nudger import Nudger
import yaml
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import smtplib
import sys
import importlib.resources as pkg_resources
from . import config
from .lib.common.base import setup_logging
import logging

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
        self.logger = logging.getLogger(__name__)

    def write(self, _str):
        try:
            self.widget.configure(state="normal")
            self.widget.insert("end", _str, (self.tag,))
            self.widget.configure(state="disabled")
        except:
            pass

class App:
    def __init__(self, master):

        with pkg_resources.open_text(config, "config.yml") as ymlfile:
                self.conf = yaml.load(ymlfile, Loader=yaml.SafeLoader)

        self.report_file = None
        self.grade_file = None

        try:
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

            self.lbl_grade_file = ttk.Label(master, text="Latest Grades Report")
            self.lbl_grade_file.grid(row=4, column=0, stick=tk.W)
            self.txt_grade_file = ttk.Label(master, relief=tk.SUNKEN, width=output_width)
            self.txt_grade_file.grid(row=5, column=0)
            self.btn_grade_file = ttk.Button(master, text="...", width=3, command=self.set_grade_file)
            self.btn_grade_file.grid(row=5, column=1)

            self.txt_out = tk.Text(master, width=output_width, height=output_height, wrap=tk.WORD)
            self.txt_out.grid(row=6, column=0)

            self.btn_run_report = ttk.Button(master, text="Run Report", width=10, command=self.run_report)
            self.btn_run_report.grid(row=6, column=1)

            self.btn_send_logs = ttk.Button(master, text="Send Logs", width=10, command=self.send_logs)
            self.btn_send_logs.grid(row=7, column=0)


            #OUTPUT WINDOW TEXT REDIRECT
            #https://stackoverflow.com/questions/12351786/how-to-redirect-print-statements-to-tkinter-text-widget
            sys.stdout = TextRedirector(self.txt_out, "sys.stdout")
            sys.stderr = TextRedirector(self.txt_out, "sys.stderr")

            setup_logging()
            self.logger = logging.getLogger(__name__)

        except:
            self.logger.exception("There was a problem initializing the UI.")

    def set_report_file(self):
        try:
            self.report_file = askopenfilename()
            self.txt_report_file.config(text=self.report_file)
            self.logger.info("Most recent attendance file selected...")
        except:
            self.logger.exception("There was a problem selecting the attendance file.")

    def set_grade_file(self):
        try:
            self.grade_file = askopenfilename()
            self.txt_grade_file.config(text=self.grade_file)
            self.logger.info("Most recent grade file selected...")
        except:
            self.logger.exception("There was a problem selecting the grade file.")

    def set_students_file(self):
        try:
            self.students_file = askopenfilename()
            self.txt_students_file.config(text=self.students_file)
            self.logger.info("Students file selected...")
        except:
            self.logger.exception("There was a problem selecting the students file.")

    def import_report(self):
        try:
            filename = self.report_file
            self.logger.info(f'Reading {filename}')
            report = AttendanceReport(filename, target_grade="09")
            self.students_with_reports, self.average_attendance_rate, self.weekly_average_attendance_rate = report.read()
            self.logger.info(f"Added {len(self.students_with_reports)} reports...\nAverage reported attendance was {self.average_attendance_rate}...")
        except:
            self.logger.exception("There was a problem importing the attendance report.")

    def import_grades(self):
        try:
            filename = self.grade_file
            self.logger.info(f'Reading {filename}')
            report = GradesReport(filename)
        except:
            self.logger.exception("There was a problem importing the grades report.")

    def import_students(self):
        try:
            filename = self.students_file
            report = StudentListReport(filename)
            new_students = report.read()
            self.logger.info(f"Added {len(new_students)} students...")
        except:
            self.logger.exception("There was a problem importing the students list.")

    def send_sms(self):
        try:
            nudger = Nudger(self.conf)
            sent = []
            [sent.append(nudger.send_text(swr, self.average_attendance_rate, self.weekly_average_attendance_rate)) for swr in self.students_with_reports if swr['contact_by_phone']]
            self.logger.info(f"Sent {len(sent)} text messages...")
        except:
            self.logger.exception("There was a problem sending the text messages.")

    def send_emails(self):
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.ehlo()
            #The nudger will authenticate us, then send the emails
            nudger = Nudger(self.conf, server)
            sent = []
            [sent.append(nudger.send_email(swr, self.average_attendance_rate, self.weekly_average_attendance_rate)) for swr in self.students_with_reports if not swr['contact_by_phone']]
            self.logger.info(f"Sent {len(sent)} emails...")
            server.quit()
            self.logger.debug(f"Connection to server ({repr(server)}) closed.")
        except:
            self.logger.exception("There was a problem sending the emails.")

    def send_logs(self):
        with open("debug.log", "rb") as debug_log:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.ehlo()
            nudger = Nudger(self.conf, server)
            nudger.send_logs(debug_log.read())

    def run_report(self):
        self.import_students()
        if self.report_file is not None:
            self.import_report()
        if self.grade_file is not None:
            self.import_grades()
        self.send_sms()
        self.send_emails()
        self.logger.info(f"Done!")

def main():
    self.logger.debug("attendancenudger.app.main touched.")
    pass

root = Tk()
app = App(root)
root.mainloop()
root.destroy()
