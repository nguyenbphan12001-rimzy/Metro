from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.Customer.Thanhtoan_EX import ThanhToan_EX

app=QApplication([])
gui=ThanhToan_EX()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec()