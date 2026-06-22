from DB_Connection import get_connection


def login(user_name, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, user_name, role FROM [USER] WHERE user_name = ? AND password = ?",
        (user_name, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "user_id": user[0],
            "user_name": user[1],
            "role": user[2]
        }
    else:
        return None