from PyQt6.QtWidgets import QApplication,QMainWindow

from ui.login.loginEx import LoginEx

app=QApplication([])
gui=LoginEx()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec()