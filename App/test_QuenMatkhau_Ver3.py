from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.Customer.QuenMatkhau_Ver3_EX import QuenMatKhau_Ver3_EX
from App.DB_Connection import get_connection   # ← thêm import này

app = QApplication([])

conn = get_connection()

gui = QuenMatKhau_Ver3_EX()
my_window = QMainWindow()
gui.setupUi(my_window, conn=conn)
my_window.show()

app.exec()