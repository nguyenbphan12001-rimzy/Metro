import sys
import os

# Thêm project root vào sys.path để import được UI.*
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.Customer.NapTien_EX import NapTien_EX

app = QApplication([])
gui = NapTien_EX()
my_window = QMainWindow()
gui.setupUi(my_window, user_id=1)
my_window.show()
app.exec()