import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.Customer.Thanhtoan_EX import ThanhToan_EX

# Kết nối SQL Server bằng Windows Authentication
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"          # hoặc tên instance của mày, vd: localhost\SQLEXPRESS
    "DATABASE=Metro_Customer;"
    "Trusted_Connection=yes;"
)

app = QApplication([])
gui = ThanhToan_EX()
my_window = QMainWindow()
gui.setupUi(my_window, conn=conn, user_id=1)   # user_id=1 test với user_1 có sẵn trong data
my_window.show()
app.exec()

conn.close()