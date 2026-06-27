import pyodbc
from dotenv import load_dotenv


load_dotenv()

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=Metro_Customer;"
        "Trusted_Connection=yes;"
    )
    return conn
if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 5 * FROM [USER]")
    for row in cursor.fetchall():
        print(row)
    conn.close()