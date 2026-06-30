import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.Customer.Hoanve_EX import Hoanve_EX

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=Metro_Customer;"
    "Trusted_Connection=yes;"
)

app = QApplication([])
gui = Hoanve_EX()
my_window = QMainWindow()
gui.setupUi(my_window, conn=conn, user_id=1)
my_window.show()
app.exec()

conn.close()