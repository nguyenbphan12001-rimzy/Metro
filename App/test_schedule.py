from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.admin.schedule_EX import schedule_EX

app=QApplication([])
gui=schedule_EX()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec() 