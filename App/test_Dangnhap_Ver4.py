import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow

from UI.Customer.Dangnhap_Ver4_EX import Dangnhap_Ver4_EX

from App.DB_Connection import get_connection
conn=get_connection()


app=QApplication([])
gui=Dangnhap_Ver4_EX()
my_window = QMainWindow()
gui.setupUi(my_window,conn)
my_window.show()

app.exec()
#user_1
#hashed_pw
