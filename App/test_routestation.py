from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.admin.routestation_EX import routestation_Ex

app=QApplication([])
gui=routestation_Ex()
my_window = QMainWindow()
gui.setupUi(my_window)
my_window.show()

app.exec()