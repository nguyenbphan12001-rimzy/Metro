from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.Customer.Dangky_EX import Dangky_EX
app=QApplication([])
gui=Dangky_EX()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec()

