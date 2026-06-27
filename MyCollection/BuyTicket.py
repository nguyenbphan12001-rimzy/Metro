import pyodbc
from datetime import datetime

def mua_ve(conn, user_id, type_id, quantity, from_station_id=None, to_station_id=None, route_id=None):
    cursor = conn.cursor()

    # 1. Lấy giá vé
    cursor.execute("SELECT type_name, price FROM TICKET_TYPE WHERE type_id = ?", type_id)
    type_name, fixed_price = cursor.fetchone()

    if type_name == 'Vé lượt':
        # Vé lượt -> tra PRICE_TABLE theo cặp ga
        cursor.execute("""
            SELECT price FROM PRICE_TABLE
            WHERE route_id = ? AND from_station_id = ? AND to_station_id = ?
        """, route_id, from_station_id, to_station_id)
        row = cursor.fetchone()
        if not row:
            raise ValueError("Chưa có giá cho cặp ga này trong PRICE_TABLE")
        unit_price = row[0]
        from_id, to_id = from_station_id, to_station_id
    else:
        # Vé ngày / vé tháng -> giá cố định, không cần ga
        unit_price = fixed_price
        from_id, to_id = None, None

    total_price = unit_price * quantity

    # 2. Lấy wallet_id + check số dư
    cursor.execute("SELECT wallet_id, balance FROM WALLET WHERE user_id = ?", user_id)
    wallet_id, balance = cursor.fetchone()
    if balance < total_price:
        raise ValueError("Số dư không đủ")

    # 3. Lấy ticket_id / transaction_id kế tiếp (vì không có IDENTITY)
    cursor.execute("SELECT ISNULL(MAX(ticket_id), 0) FROM TICKET")
    next_ticket_id = cursor.fetchone()[0] + 1
    cursor.execute("SELECT ISNULL(MAX(transaction_id), 0) FROM [TRANSACTION]")
    next_txn_id = cursor.fetchone()[0] + 1

    now = datetime.now()
    tickets = []
    transactions = []

    for i in range(quantity):
        ticket_id = next_ticket_id + i
        qr_code = f"QR_{ticket_id}_{int(now.timestamp())}"
        tickets.append((ticket_id, user_id, None, type_id, from_id, to_id,
                         unit_price, qr_code, 'UNUSED', now))
        transactions.append((next_txn_id + i, user_id, wallet_id, ticket_id, unit_price, now))

    # 4. Insert hàng loạt trong CÙNG 1 transaction SQL
    try:
        cursor.executemany("""
            INSERT INTO TICKET (ticket_id, user_id, train_id, type_id,
                from_station_id, to_station_id, price, qr_code, status, issued_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tickets)

        cursor.executemany("""
            INSERT INTO [TRANSACTION] (transaction_id, user_id, wallet_id, ticket_id, amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, transactions)
        # trigger trg_after_transaction sẽ tự GROUP BY wallet_id và trừ đúng 1 lần tổng amount

        conn.commit()
        return [t[0] for t in tickets]  # trả về list ticket_id vừa tạo
    except Exception as e:
        conn.rollback()
        raise e