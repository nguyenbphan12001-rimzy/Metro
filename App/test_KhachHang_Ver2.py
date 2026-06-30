import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.Customer.KhachHang_Ver2_EX import  KhachHang_Ver2_EX
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Metro_Customer;"
    "Trusted_Connection=yes;"
)


app=QApplication([])
gui=KhachHang_Ver2_EX()
my_window = QMainWindow()
gui.setupUi(my_window, user_id=1,conn=conn)
my_window.show()

app.exec()