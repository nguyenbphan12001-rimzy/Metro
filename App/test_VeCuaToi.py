import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow
from UI.Customer.VeCuaToi_EX import VeCuaToi_EX

conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Metro_Customer;Trusted_Connection=yes;")

app = QApplication([])
gui = VeCuaToi_EX()
my_window = QMainWindow()
gui.setupUi(my_window, conn=conn, user_id=4)

screen = app.primaryScreen().availableGeometry()
my_window.resize(440, min(780, screen.height() - 40))
my_window.move(screen.x() + (screen.width() - 440) // 2, screen.y() + 20)
my_window.show()
app.exec()