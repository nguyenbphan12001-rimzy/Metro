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
    station_name NVARCHAR(100) NOT NULL
);

CREATE TABLE ROUTE (
    route_id   INT PRIMARY KEY,
    route_name NVARCHAR(100) NOT NULL
);

CREATE TABLE PAYMENT_METHOD (
    method_id   INT PRIMARY KEY,
    method_name NVARCHAR(100) NOT NULL
);

CREATE TABLE TICKET_TYPE (
    type_id       INT PRIMARY KEY,
    type_name     NVARCHAR(100) NOT NULL,
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

-- SỬA: balance mặc định đổi về 0 (đúng nghiệp vụ: ví được cấp ngay khi
-- tạo tài khoản với số dư = 0, khách phải tự nạp tiền vào mới mua vé được)
CREATE TABLE WALLET (
    wallet_id    INT PRIMARY KEY,
    user_id      INT UNIQUE,
    balance      DECIMAL(15,2) DEFAULT 0.00 CHECK (balance >= 0),
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

-- SỬA:
--  1) status: thêm CANCELLED (vé bị hủy/hoàn tiền) để phân biệt với EXPIRED
--     (vé hết hạn tự nhiên) — tránh 1 vé đã hoàn tiền còn bị hiểu nhầm là
--     "hết hạn", đồng thời trigger quét QR sẽ dựa vào CANCELLED để chặn
--     khách quét vé đã hoàn.
--  2) train_id: cho phép NULL. Vé lượt (type_id = 1) mới bắt buộc gắn với
--     1 chuyến tàu cụ thể; vé ngày/vé tháng (type_id 2,3,4) là vé "mở",
--     khách được đi nhiều chuyến/nhiều tàu trong thời hạn hiệu lực nên
--     không hợp lý khi khóa cứng vào 1 train_id (thực tế trước đây là bug).
--     CHK_Ticket_TrainByType ép đúng quy tắc này ở tầng CSDL.
CREATE TABLE TICKET (
    ticket_id       INT PRIMARY KEY,
    user_id         INT,
    train_id        INT NULL,
    type_id         INT,
    from_station_id INT NULL,
    to_station_id   INT NULL,
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    qr_code         VARCHAR(100) NOT NULL UNIQUE,
    status          VARCHAR(50) DEFAULT 'UNUSED' CHECK (status IN ('UNUSED', 'USED', 'EXPIRED', 'CANCELLED')),
    issued_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)         REFERENCES [USER](user_id), -- Gọi đến [USER]
    FOREIGN KEY (train_id)        REFERENCES TRAIN(train_id),
    FOREIGN KEY (type_id)         REFERENCES TICKET_TYPE(type_id),
    FOREIGN KEY (from_station_id) REFERENCES STATION(station_id),
    FOREIGN KEY (to_station_id)   REFERENCES STATION(station_id),
    CONSTRAINT CHK_Tickets_DistinctStations CHECK (from_station_id IS NULL OR to_station_id IS NULL OR from_station_id <> to_station_id),
    -- SỬA: type_id = 1 là 'Vé lượt' (cố định theo dữ liệu TICKET_TYPE ở Nhom1.sql)
    CONSTRAINT CHK_Ticket_TrainByType CHECK (
        (type_id = 1 AND train_id IS NOT NULL) OR
        (type_id <> 1 AND train_id IS NULL)
    )
);
CREATE TABLE DEPOSIT_HISTORY (
    deposit_id INT PRIMARY KEY,
    wallet_id  INT,
    user_id    INT,
    method_id  INT,
    amount     DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES WALLET(wallet_id),
    FOREIGN KEY (user_id)   REFERENCES [USER](user_id),
    FOREIGN KEY (method_id) REFERENCES PAYMENT_METHOD(method_id)
);

-- ====================================================================
-- NHÓM 4: CÁC BẢNG NGHIỆP VỤ
-- ====================================================================

-- SỬA: thêm UNIQUE trên ticket_id — đối soát tài chính 1:1, 1 vé chỉ được
-- sinh đúng 1 hóa đơn giao dịch mua vé.
-- Giữ nguyên TRANSACTION dạng số ít bằng cách bọc dấu [ ]
CREATE TABLE [TRANSACTION] (
    transaction_id INT PRIMARY KEY,
    user_id        INT,
    wallet_id      INT,
    ticket_id      INT UNIQUE,
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

-- SỬA: thêm UNIQUE trên ticket_id — 1 vé chỉ được hoàn tiền tối đa 1 lần,
-- chặn tình huống hoàn trùng nhiều lần trên cùng 1 vé.
CREATE TABLE REFUNDS (
    refund_id  INT PRIMARY KEY,
    ticket_id  INT UNIQUE,
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


CREATE TRIGGER trg_after_deposit
ON DEPOSIT_HISTORY
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE w
    SET w.balance = w.balance + agg.total_amount,
        w.last_updated = CURRENT_TIMESTAMP
    FROM WALLET w
    JOIN (
        SELECT wallet_id, SUM(amount) AS total_amount
        FROM inserted
        GROUP BY wallet_id
    ) agg ON w.wallet_id = agg.wallet_id;
END;
GO

-- SỬA: trigger REFUNDS giờ làm 2 việc trong 1 lần INSERT:
--   1) Cộng tiền hoàn lại vào ví (giữ nguyên như bản trước)
--   2) Tự động chuyển TICKET.status -> 'CANCELLED', tránh việc Python phải
--      tự set status (dễ quên / dễ set sai) và tránh khách vẫn mở QR của vé
--      đã hoàn để quét cổng.
CREATE TRIGGER trg_after_refund
ON REFUNDS
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE w
    SET w.balance = w.balance + agg.total_amount,
        w.last_updated = CURRENT_TIMESTAMP
    FROM WALLET w
    JOIN (
        SELECT wallet_id, SUM(amount) AS total_amount
        FROM inserted
        GROUP BY wallet_id
    ) agg ON w.wallet_id = agg.wallet_id;

    UPDATE t
    SET t.status = 'CANCELLED'
    FROM TICKET t
    JOIN inserted i ON t.ticket_id = i.ticket_id;
END;
GO

-- SỬA: trigger mới — sau khi quét cổng (SCAN IN), tự động chuyển vé lượt
-- sang 'USED'. Chỉ áp dụng cho type_id = 1 (Vé lượt) vì vé ngày/vé tháng
-- cần được quét nhiều lần trong thời hạn hiệu lực nên không được đổi
-- trạng thái ngay sau lượt quét đầu tiên. Chỉ đổi khi vé đang ở UNUSED để
-- không ghi đè lên vé đã CANCELLED/EXPIRED.
CREATE TRIGGER trg_after_scan_in
ON SCANNING_HISTORY
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE t
    SET t.status = 'USED'
    FROM TICKET t
    JOIN inserted i ON t.ticket_id = i.ticket_id
    WHERE i.scan_type = 'IN'
      AND t.type_id = 1
      AND t.status = 'UNUSED';
END;
GO

-- Lưu ý (chưa xử lý bằng trigger — nhóm quyết định để ở tầng QUERY):
-- Vé ngày/vé tháng (type_id 2,3,4) khi hết hạn (issued_at + validity_days
-- từ TICKET_TYPE < ngày hiện tại) không có trigger tự chuyển EXPIRED, vì
-- SQL Server trigger chỉ chạy khi có thao tác INSERT/UPDATE/DELETE, không
-- tự chạy theo thời gian. Việc này nên xử lý bằng 1 SELECT/UPDATE query
-- (hoặc SQL Agent Job định kỳ) — sẽ đưa vào bộ 30 query của đồ án.

-- ====================================================================
-- CHỈ MỤC (INDEX) TỐI ƯU TỐC ĐỘ TRUY VẤN
-- ====================================================================

CREATE NONCLUSTERED INDEX IX_Tickets_UserStatus ON TICKET(user_id, status);
CREATE NONCLUSTERED INDEX IX_Tickets_QRCode ON TICKET(qr_code);
CREATE NONCLUSTERED INDEX IX_Scanning_TicketTime ON SCANNING_HISTORY(ticket_id, scanned_at);
CREATE NONCLUSTERED INDEX IX_Transactions_UserTime ON [TRANSACTION](user_id, created_at); -- Đưa về bảng số ít có ngoặc vuông
CREATE NONCLUSTERED INDEX IX_PriceTable_Stations ON PRICE_TABLE(from_station_id, to_station_id);
CREATE NONCLUSTERED INDEX IX_Deposit_WalletTime ON DEPOSIT_HISTORY(wallet_id, created_at);
CREATE NONCLUSTERED INDEX IX_Train_RouteDeparture ON TRAIN(route_id, departure_time); -- SỬA: phục vụ query đề xuất chuyến gần giờ hiện tại nhất
GO