from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.Customer.Dangnhap_EX import Dangnhap_EX

app=QApplication([])
gui=Dangnhap_EX()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec()
#user_1
#hashed_pw
