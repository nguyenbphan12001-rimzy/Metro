-- ====================================================================
-- TỰ ĐỘNG DỌN DẸP: XÓA DATABASE CŨ NẾU ĐÃ TỒN TẠI ĐỂ TRÁNH LỖI TRÙNG ĐỐI TƯỢNG
-- ====================================================================
USE master;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'Metro_Customer')
BEGIN
    ALTER DATABASE Metro_Customer SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Metro_Customer;
END
GO

CREATE DATABASE Metro_Customer;
GO

USE Metro_Customer;
GO

-- ====================================================================
-- NHÓM 1: CÁC BẢNG GỐC
-- ====================================================================

-- Giữ nguyên USER dạng số ít bằng cách bọc dấu [ ]
CREATE TABLE [USER] (
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
    position         INT NOT NULL CHECK (position > 0),
    FOREIGN KEY (route_id)   REFERENCES ROUTE(route_id),
    FOREIGN KEY (station_id) REFERENCES STATION(station_id)
);

CREATE TABLE TRAIN (
    train_id       INT PRIMARY KEY,
    route_id       INT,
    departure_time TIME NOT NULL,
    arrival_time   TIME NOT NULL,
    capacity       INT NOT NULL CHECK (capacity > 0),
    FOREIGN KEY (route_id) REFERENCES ROUTE(route_id)
);

CREATE TABLE WALLET (
    wallet_id    INT PRIMARY KEY,
    user_id      INT UNIQUE,
    balance      DECIMAL(15,2) DEFAULT 500000.00 CHECK (balance >= 0),
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES [USER](user_id) -- Gọi đến [USER]
);

CREATE TABLE PRICE_TABLE (
    price_id        INT PRIMARY KEY,
    route_id        INT,
    from_station_id INT,
    to_station_id   INT,
    price           DECIMAL(10,2) NOT NULL CHECK (price > 0),
    FOREIGN KEY (route_id)        REFERENCES ROUTE(route_id),
    FOREIGN KEY (from_station_id) REFERENCES STATION(station_id),
    FOREIGN KEY (to_station_id)   REFERENCES STATION(station_id)
);

-- ====================================================================
-- NHÓM 3: CÁC BẢNG LIÊN QUAN ĐẾN VÉ
-- ====================================================================

CREATE TABLE TICKET (
    ticket_id       INT PRIMARY KEY,
    user_id         INT,
    train_id        INT,
    type_id         INT,
    from_station_id INT NULL,
    to_station_id   INT NULL,
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    qr_code         VARCHAR(100) NOT NULL UNIQUE,
    status          VARCHAR(50) DEFAULT 'UNUSED' CHECK (status IN ('UNUSED', 'USED', 'EXPIRED')),
    issued_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)         REFERENCES [USER](user_id), -- Gọi đến [USER]
    FOREIGN KEY (train_id)        REFERENCES TRAIN(train_id),
    FOREIGN KEY (type_id)         REFERENCES TICKET_TYPE(type_id),
    FOREIGN KEY (from_station_id) REFERENCES STATION(station_id),
    FOREIGN KEY (to_station_id)   REFERENCES STATION(station_id),
    CONSTRAINT CHK_Tickets_DistinctStations CHECK (from_station_id IS NULL OR to_station_id IS NULL OR from_station_id <> to_station_id)
);

-- ====================================================================
-- NHÓM 4: CÁC BẢNG NGHIỆP VỤ
-- ====================================================================

-- Giữ nguyên TRANSACTION dạng số ít bằng cách bọc dấu [ ]
CREATE TABLE [TRANSACTION] (
    transaction_id INT PRIMARY KEY,
    user_id        INT,
    wallet_id      INT,
    method_id      INT,
    ticket_id      INT,
    amount         DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)   REFERENCES [USER](user_id), -- Gọi đến [USER]
    FOREIGN KEY (wallet_id) REFERENCES WALLET(wallet_id),
    FOREIGN KEY (ticket_id) REFERENCES TICKET(ticket_id)
);

CREATE TABLE SCANNING_HISTORY (
    scan_id    INT PRIMARY KEY,
    ticket_id  INT,
    station_id INT,
    scan_type  VARCHAR(10) NOT NULL CHECK (scan_type IN ('IN','OUT')),
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id)  REFERENCES TICKET(ticket_id),
    FOREIGN KEY (station_id) REFERENCES STATION(station_id)
);

CREATE TABLE REFUNDS (
    refund_id  INT PRIMARY KEY,
    ticket_id  INT,
    wallet_id  INT,
    amount     DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES TICKET(ticket_id),
    FOREIGN KEY (wallet_id) REFERENCES WALLET(wallet_id)
);
GO

-- ====================================================================
-- TRIGGER TỰ ĐỘNG HÓA
-- ====================================================================

CREATE TRIGGER trg_after_transaction
ON [TRANSACTION]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE w
    SET w.balance = w.balance - agg.total_amount,
        w.last_updated = CURRENT_TIMESTAMP
    FROM WALLET w
    JOIN (
        SELECT wallet_id, SUM(amount) AS total_amount
        FROM inserted
        GROUP BY wallet_id
    ) agg ON w.wallet_id = agg.wallet_id;
END;
GO

-- ====================================================================
-- CHỈ MỤC (INDEX) TỐI ƯU TỐC ĐỘ TRUY VẤN
-- ====================================================================

CREATE NONCLUSTERED INDEX IX_Tickets_UserStatus ON TICKET(user_id, status);
CREATE NONCLUSTERED INDEX IX_Tickets_QRCode ON TICKET(qr_code);
CREATE NONCLUSTERED INDEX IX_Scanning_TicketTime ON SCANNING_HISTORY(ticket_id, scanned_at);
CREATE NONCLUSTERED INDEX IX_Transactions_UserTime ON [TRANSACTION](user_id, created_at); -- Đưa về bảng số ít có ngoặc vuông
CREATE NONCLUSTERED INDEX IX_PriceTable_Stations ON PRICE_TABLE(from_station_id, to_station_id);
GO