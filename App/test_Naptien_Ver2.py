import sys
import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.Customer.Naptien_Ver2_EX import Naptien_Ver2_EX

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Metro_Customer;"
    "Trusted_Connection=yes;"
)

app = QApplication(sys.argv)
my_window = QMainWindow()
gui = Naptien_Ver2_EX()
gui.setupUi(my_window, conn=conn, user_id=1)  # user_id=1 để test với data mẫu
my_window.show()
sys.exit(app.exec())