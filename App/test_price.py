from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.admin.price_EX import price_EX

app=QApplication([])
gui=price_EX()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec()