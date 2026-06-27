from PyQt6.QtWidgets import QApplication,QMainWindow

from UI.admin.admin_dashboard_EX import admin_dashboard_EX

app=QApplication([])
gui=admin_dashboard_EX()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec()