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

from tkinter import *
from tkinter.filedialog import askopenfilename
import parse_attendance_csv

class App:
    def __init__(self, master):

        frame = Frame(master)
        frame.pack()
        master.title("Attendance Nudge-er")

        self.button = Button(
                frame, text="QUIT", fg="red", command=frame.quit
                )
        self.button.pack(side="left")

        self.pick_file = Button(
                frame, text="Import Report", fg="green", command=self.import_report
                )
        self.pick_file.pack(side="left")

        self.out = Label(
                frame, text="No reports run..."
                )
        self.out.pack(side="bottom")

    def import_report(self):
        filename = askopenfilename()
        print(filename)
        parse_attendance_csv.import_attendance_from_csv(filename)
        self.out.config(text="Ran a report!")
                
root = Tk()

app = App(root)

root.mainloop()
root.destroy()
