from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.Customer.KhachHang_EX import KhachHang_EX

app=QApplication([])
gui=KhachHang_EX()
my_window = QMainWindow()
gui.setupUi(my_window, user_id=1)
my_window.show()

app.exec()