from DB_Connection import get_connection


def get_wallet(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT wallet_id, balance, last_updated FROM WALLET WHERE user_id = ?",
        (user_id,)
    )
    wallet = cursor.fetchone()
    conn.close()

    if wallet:
        return {
            "wallet_id": wallet[0],
            "balance": wallet[1],
            "last_updated": wallet[2]
        }
    else:
        return None