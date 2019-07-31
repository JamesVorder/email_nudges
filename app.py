# ......
# :.  .:
# .'  '.
# |    |
# |    |
# `----'
# https://effbot.org/tkinterbook/tkinter-hello-again.htm
# https://effbot.org/tkinterbook/tkinter-classes.htm
# https://stackoverflow.com/questions/3579568/choosing-a-file-in-python-with-simple-dialog
# https://docs.python.org/3/library/tkinter.html
# https://www.effbot.org/tkinterbook/grid.htm

from tkinter import *
from tkinter.filedialog import askopenfilename
import report_parser as parser

class App:
    def __init__(self, master):

        master.title("Attendance Nudge-er")

        self.btn_quit = Button(master, text="QUIT", fg="red", command=master.quit)
        self.btn_quit.grid(row=0, column=0)

        self.btn_pick = Button(master, text="Import Report", fg="green", command=self.import_report)
        self.btn_pick.grid(row=0, column=1)

        self.lbl_out = Label(master, text="No reports run...")
        self.lbl_out.grid(row=1, columnspan=2)

    def import_report(self):
        filename = askopenfilename()
        self.lbl_out.config(text=f'Reading {filename}')
        report = parser.AttendanceReport(filename, target_grade="09", db="attendance_nudger_v1")
        report.read()
        self.lbl_out.config(text="Done!")

### MAIN ###
root = Tk()
app = App(root)
root.mainloop()
root.destroy()
