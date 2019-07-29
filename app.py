# ......
# :.  .:
# .'  '.
# |    |
# |    |
# `----'
# https://effbot.org/tkinterbook/tkinter-hello-again.htm
# https://effbot.org/tkinterbook/tkinter-classes.htm
# https://stackoverflow.com/questions/3579568/choosing-a-file-in-python-with-simple-dialog

from tkinter import *
from tkinter.filedialog import askopenfilename
import parse_attendance_csv

class App:
    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.button = Button(
                frame, text="QUIT", fg="red", command=frame.quit
                )
        self.button.pack(side=LEFT)

        self.pick_file = Button(
                frame, text="Import Report", fg="green", command=self.import_report
                )
        self.pick_file.pack(side=LEFT)

    def import_report(self):
        filename = askopenfilename()
        print(filename)
        parse_attendance_csv.import_attendance_from_csv(filename)
                
root = Tk()

app = App(root)

root.mainloop()
root.destroy()
