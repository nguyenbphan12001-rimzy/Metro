

CREATE DATABASE MetroDB;
GO

USE MetroDB;
GO

-- ====================================================================
-- NHÓM 1: CÁC BẢNG GỐC
-- ====================================================================

CREATE TABLE USER (
    user_id    INT PRIMARY KEY,
    user_name  VARCHAR(100) NOT NULL,
    password   VARCHAR(200) NOT NULL,
    role       VARCHAR(100) DEFAULT 'customer' CHECK (role IN ('customer')),
    phone      VARCHAR(20),
    DoB        DATE
);

CREATE TABLE STATION (
    station_id   INT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL
);

CREATE TABLE ROUTE (
    route_id   INT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL
);

CREATE TABLE PAYMENT_METHOD (
    method_id   INT PRIMARY KEY,
    method_name VARCHAR(100) NOT NULL
);

CREATE TABLE TICKET_TYPE (
    type_id       INT PRIMARY KEY,
    type_name     VARCHAR(100) NOT NULL,
    price         DECIMAL(10,2) NULL CHECK (price IS NULL OR price > 0),
    validity_days INT NULL CHECK (validity_days IS NULL OR validity_days > 0)
);

-- ====================================================================
-- NHÓM 2: CÁC BẢNG PHỤ THUỘC LỚP 1
-- ====================================================================

CREATE TABLE ROUTESTATION (
    route_station_id INT PRIMARY KEY,
    route_id         INT,
    station_id       INT,
    method_id      INT,
    position         INT NOT NULL CHECK (position > 0),
    FOREIGN KEY (route_id)   REFERENCES ROUTES(route_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);

CREATE TABLE TRAIN (
    train_id       INT PRIMARY KEY,
    route_id       INT,
    departure_time TIME NOT NULL,
    arrival_time   TIME NOT NULL,
    capacity       INT NOT NULL CHECK (capacity > 0),
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id)
);

CREATE TABLE WALLET (
    wallet_id    INT PRIMARY KEY,
    user_id      INT UNIQUE,
    balance      DECIMAL(15,2) DEFAULT 500000.00 CHECK (balance >= 0), -- Mặc định sẵn 500k như nhóm chốt, ví động trừ dần khi mua vé
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE PRICE_TABLE (
    price_id        INT PRIMARY KEY,
    route_id        INT,
    from_station_id INT,
    to_station_id   INT,
    price           DECIMAL(10,2) NOT NULL CHECK (price > 0),
    FOREIGN KEY (route_id)        REFERENCES ROUTES(route_id),
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id)   REFERENCES STATIONS(station_id)
);

-- ====================================================================
-- NHÓM 3: CÁC BẢNG LIÊN QUAN ĐẾN VÉ
-- ====================================================================

CREATE TABLE TICKET (
    ticket_id       INT PRIMARY KEY,
    user_id         INT,
    type_id         INT,
    from_station_id INT NULL,
    to_station_id   INT NULL,
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    qr_code         VARCHAR(100) NOT NULL UNIQUE,
    status          VARCHAR(50) DEFAULT 'UNUSED' CHECK (status IN ('UNUSED', 'USED', 'EXPIRED')),
    issued_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)         REFERENCES USERS(user_id),
    FOREIGN KEY (type_id)         REFERENCES TICKET_TYPES(type_id),
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id)   REFERENCES STATIONS(station_id),
    CONSTRAINT CHK_Tickets_DistinctStations CHECK (from_station_id IS NULL OR to_station_id IS NULL OR from_station_id <> to_station_id)
);

-- ====================================================================
-- NHÓM 4: CÁC BẢNG NGHIỆP VỤ
-- ====================================================================

CREATE TABLE TRANSACTION (
    transaction_id INT PRIMARY KEY,
    user_id        INT,
    wallet_id      INT,
    ticket_id      INT,
    amount         DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)   REFERENCES USERS(user_id),
    FOREIGN KEY (wallet_id) REFERENCES WALLETS(wallet_id),
    FOREIGN KEY (ticket_id) REFERENCES TICKETS(ticket_id)
);

CREATE TABLE SCANNING_HISTORY (
    scan_id    INT PRIMARY KEY,
    ticket_id  INT,
    station_id INT,
    scan_type  VARCHAR(10) NOT NULL CHECK (scan_type IN ('IN','OUT')), -- Hệ thống tự động ghi nhận khi khách tự quét mã tại cổng
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id)  REFERENCES TICKETS(ticket_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);
GO

-- ====================================================================
-- TRIGGER TỰ ĐỘNG HÓA (Đảm bảo tính nhất quán dữ liệu ví điện tử)
-- ====================================================================

-- Kích hoạt sau khi INSERT vào TRANSACTIONS, tự động trừ số tiền (amount) khỏi số dư (balance) của ví hành khách
CREATE TRIGGER trg_after_transaction
ON TRANSACTIONS
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE WALLETS
    SET balance = balance - i.amount,
        last_updated = CURRENT_TIMESTAMP
    FROM WALLETS w
    JOIN inserted i ON w.wallet_id = i.wallet_id;
END;
GO

-- ====================================================================
-- CHỈ MỤC (INDEX) TỐI ƯU TỐC ĐỘ TRUY VẤN CHO HÀNH KHÁCH
-- ====================================================================

CREATE NONCLUSTERED INDEX IX_Tickets_UserStatus ON TICKETS(user_id, status);
CREATE NONCLUSTERED INDEX IX_Tickets_QRCode ON TICKETS(qr_code);
CREATE NONCLUSTERED INDEX IX_Scanning_TicketTime ON SCANNING_HISTORY(ticket_id, scanned_at);
CREATE NONCLUSTERED INDEX IX_Transactions_UserTime ON TRANSACTIONS(user_id, created_at);
CREATE NONCLUSTERED INDEX IX_PriceTable_Stations ON PRICE_TABLE(from_station_id, to_station_id);
GO