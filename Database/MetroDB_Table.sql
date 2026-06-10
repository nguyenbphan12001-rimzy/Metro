-- ====================================================================
-- NHÓM 1: CÁC BẢNG GỐC
-- ====================================================================

CREATE TABLE USERS (
    user_id INT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(100) DEFAULT 'customer' CHECK (role IN ('customer', 'admin', 'staff')), -- Bổ sung 'staff'
    phone VARCHAR(20)
);

CREATE TABLE STATIONS (
    station_id INT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL
);

CREATE TABLE ROUTES (
    route_id INT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL
);

CREATE TABLE PAYMENT_METHODS (
    method_id INT PRIMARY KEY,
    method_name VARCHAR(100) NOT NULL
);

CREATE TABLE TICKET_TYPES (
    type_id INT PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NULL CHECK (price IS NULL OR price > 0),
    validity_days INT NULL CHECK (validity_days IS NULL OR validity_days > 0)         -- Ràng buộc số 5
);

-- ====================================================================
-- NHÓM 2: CÁC BẢNG PHỤ THUỘC LỚP 1
-- ====================================================================

CREATE TABLE ROUTESTATIONS (
    route_station_id INT PRIMARY KEY,
    route_id INT,
    station_id INT,
    position INT NOT NULL CHECK (position > 0),                   -- Ràng buộc số 11
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id),
    CONSTRAINT UQ_Route_Position UNIQUE (route_id, position),     -- Ràng buộc số 11 (Bổ sung)
    CONSTRAINT UQ_Route_Station UNIQUE (route_id, station_id)     -- Ràng buộc số 11 (Bổ sung)
);

CREATE TABLE TRAINS (
    train_id INT PRIMARY KEY,
    route_id INT,
    departure_time TIME,
    arrival_time TIME,
    capacity INT NOT NULL CHECK (capacity > 0),
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id)
);



CREATE TABLE ADMIN_HISTORY (
    ad_log_id INT PRIMARY KEY,
    admin_id INT,
    action VARCHAR(50) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_id INT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES USERS(user_id)
);

CREATE TABLE WALLETS (
    wallet_id INT PRIMARY KEY,
    user_id INT UNIQUE,
    balance DECIMAL(15, 2) DEFAULT 0.00 CHECK (balance >= 0),  -- Ràng buộc số 1
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE PRICE_TABLE (
    price_id INT PRIMARY KEY,
    route_id INT,
    from_station_id INT,
    to_station_id INT,
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),             -- Ràng buộc số 9
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id),
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id) REFERENCES STATIONS(station_id),
    CONSTRAINT CHK_PriceTable_DistinctStations CHECK (from_station_id <> to_station_id) -- Ràng buộc số 10
);

CREATE TABLE STAFFS (
    staff_id INT PRIMARY KEY,
    user_id INT,
    station_id INT,
    full_name VARCHAR(100) NOT NULL,
    employee_code VARCHAR(50) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);

-- ====================================================================
-- NHÓM 3: CÁC BẢNG PHỤ THUỘC LỚP 2
-- ====================================================================

CREATE TABLE PRICE_HISTORY (
    price_history_id INT PRIMARY KEY,
    price_id INT,
    old_price DECIMAL(10, 2) NOT NULL CHECK (old_price > 0),     -- Ràng buộc số 8
    new_price DECIMAL(10, 2) NOT NULL CHECK (new_price > 0),     -- Ràng buộc số 8
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by INT,
    FOREIGN KEY (price_id) REFERENCES PRICE_TABLE(price_id),
    FOREIGN KEY (changed_by) REFERENCES USERS(user_id)
);

CREATE TABLE DEPOSIT_HISTORY (
    deposit_id INT PRIMARY KEY,
    wallet_id INT,
    user_id INT,
    method_id INT,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),           -- Ràng buộc số 2
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES WALLETS(wallet_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (method_id) REFERENCES PAYMENT_METHODS(method_id)
);

CREATE TABLE TICKETS (
    ticket_id INT PRIMARY KEY,
    user_id INT,
    trip_id INT,                                                 -- Đổi từ train_id sang trip_id
    type_id INT,
    from_station_id INT NULL,                                    -- Cho phép NULL nếu là vé trọn gói ngày/tháng
    to_station_id INT NULL,                                      -- Cho phép NULL nếu là vé trọn gói ngày/tháng
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),             -- Ràng buộc số 6
    qr_code VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'UNUSED' CHECK (status IN ('UNUSED', 'USED', 'EXPIRED', 'CANCELLED')),
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (trip_id) REFERENCES TRIPS(trip_id),             -- Khóa ngoại hướng về TRIPS
    FOREIGN KEY (type_id) REFERENCES TICKET_TYPES(type_id),
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id) REFERENCES STATIONS(station_id),
    CONSTRAINT CHK_Tickets_Duration CHECK (expires_at IS NULL OR expires_at >= issued_at), -- Ràng buộc số 7
    CONSTRAINT CHK_Tickets_DistinctStations CHECK (from_station_id IS NULL OR to_station_id IS NULL OR from_station_id <> to_station_id) -- Ràng buộc trùng ga
);

-- ====================================================================
-- NHÓM 4: CÁC BẢNG NGHIỆP VỤ (Giao dịch, quét vé, hoàn tiền)
-- ====================================================================

CREATE TABLE TRANSACTIONS (
    transaction_id INT PRIMARY KEY,
    user_id INT,
    wallet_id INT,
    ticket_id INT,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),           -- Ràng buộc số 3
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (wallet_id) REFERENCES WALLETS(wallet_id),
    FOREIGN KEY (ticket_id) REFERENCES TICKETS(ticket_id)
);

CREATE TABLE SCANNING_HISTORY (
    scan_id INT PRIMARY KEY,
    ticket_id INT,
    staff_id INT NULL,
    station_id INT,
    scan_type VARCHAR(10) NOT NULL CHECK (scan_type IN ('IN', 'OUT')), -- Thêm Check-in / Check-out
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES TICKETS(ticket_id),
    FOREIGN KEY (staff_id) REFERENCES STAFFS(staff_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);

CREATE TABLE REFUNDS (
    refund_id INT PRIMARY KEY,
    ticket_id INT,
    wallet_id INT,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),           -- Ràng buộc số 4
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES TICKETS(ticket_id),
    FOREIGN KEY (wallet_id) REFERENCES WALLETS(wallet_id)
    -- LƯU Ý: Ràng buộc "Số tiền hoàn <= Số tiền đã trả trên vé" sẽ được xử lý bằng Trigger riêng.
);