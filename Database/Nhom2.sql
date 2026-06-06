-- =========================================================
-- FILE: nhom2.sql (CHẠY FILE NÀY SAU KHI CHẠY FILE NHOM1)
-- Mô tả: Khởi tạo bảng chứa khóa ngoại và chèn dữ liệu giao dịch
-- =========================================================

-- TẠO CẤU TRÚC BẢNG (NHÓM 2)
CREATE TABLE ROUTESTATIONS (
    route_station_id INT PRIMARY KEY,
    route_id INT,
    station_id INT,
    station_order INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);

CREATE TABLE TRAINS (
    train_id INT PRIMARY KEY,
    train_name VARCHAR(50) NOT NULL,
    route_id INT,
    capacity INT DEFAULT 300,
    status VARCHAR(20) DEFAULT 'Operational',
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id)
);

CREATE TABLE WALLETS (
    wallet_id INT PRIMARY KEY,
    user_id INT UNIQUE,
    balance DECIMAL(10,2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'VND',
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE STAFFS (
    staff_id INT PRIMARY KEY,
    staff_name VARCHAR(100) NOT NULL,
    station_id INT,
    shift VARCHAR(20),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);

CREATE TABLE PRICE_TABLE (
    price_id INT PRIMARY KEY,
    from_station_id INT,
    to_station_id INT,
    route_id INT,
    base_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id)
);

CREATE TABLE ADMIN_HISTORY (
    log_id INT PRIMARY KEY,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE PRICE_HISTORY (
    history_id INT PRIMARY KEY,
    price_id INT,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    changed_by INT,
    FOREIGN KEY (price_id) REFERENCES PRICE_TABLE(price_id),
    FOREIGN KEY (changed_by) REFERENCES USERS(user_id)
);

CREATE TABLE DEPOSIT_HISTORY (
    deposit_id INT PRIMARY KEY,
    wallet_id INT,
    user_id INT,
    method_id INT,
    amount DECIMAL(10,2),
    FOREIGN KEY (wallet_id) REFERENCES WALLETS(wallet_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (method_id) REFERENCES PAYMENT_METHODS(method_id)
);

CREATE TABLE TICKETS (
    ticket_id INT PRIMARY KEY,
    user_id INT,
    train_id INT,
    type_id INT,
    from_station_id INT,
    to_station_id INT,
    price DECIMAL(10,2),
    qr_code VARCHAR(50) UNIQUE,
    status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (train_id) REFERENCES TRAINS(train_id),
    FOREIGN KEY (type_id) REFERENCES TICKET_TYPES(ticket_type_id),
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id) REFERENCES STATIONS(station_id)
);

-- CHÈN DỮ LIỆU MẪU (NHÓM 2)

-- 6. ROUTESTATIONS (26 dòng)
INSERT INTO ROUTESTATIONS (route_station_id, route_id, station_id, station_order) VALUES
(1, 101, 1, 1),   (2, 101, 2, 2),   (3, 101, 3, 3),   (4, 101, 4, 4),   (5, 101, 5, 5),
(6, 101, 6, 6),   (7, 101, 7, 7),   (8, 101, 8, 8),   (9, 101, 9, 9),   (10, 101, 10, 10),
(11, 101, 11, 11), (12, 101, 12, 12), (13, 101, 13, 13), (14, 101, 14, 14),
(15, 102, 1, 1),   (16, 102, 15, 2),  (17, 102, 16, 3),  (18, 102, 17, 4),  (19, 102, 18, 5),
(20, 102, 19, 6),  (21, 102, 20, 7),  (22, 102, 21, 8),  (23, 102, 22, 9),  (24, 102, 23, 10),
(25, 102, 24, 11), (26, 102, 25, 12);

-- 7. TRAINS (10 đoàn tàu)
INSERT INTO TRAINS (train_id, train_name, route_id, capacity, status) VALUES
(1, 'Đoàn tàu SE-01', 101, 300, 'Operational'),
(2, 'Đoàn tàu SE-02', 101, 300, 'Operational'),
(3, 'Đoàn tàu SE-03', 101, 300, 'Operational'),
(4, 'Đoàn tàu SE-04', 101, 300, 'Maintenance'),
(5, 'Đoàn tàu SE-05', 101, 300, 'Operational'),
(6, 'Đoàn tàu TL-01', 102, 300, 'Operational'),
(7, 'Đoàn tàu TL-02', 102, 300, 'Operational'),
(8, 'Đoàn tàu TL-03', 102, 300, 'Operational'),
(9, 'Đoàn tàu TL-04', 102, 300, 'Operational'),
(10, 'Đoàn tàu TL-05', 102, 300, 'Operational');

-- 8. WALLETS (50 ví)
INSERT INTO WALLETS (wallet_id, user_id, balance, currency) VALUES
(4, 4, 20000.00, 'VND'),   (5, 5, 150000.00, 'VND'),  (6, 6, 0.00, 'VND'),
(7, 7, 500000.00, 'VND'),  (8, 8, 230000.00, 'VND'),  (9, 9, 80000.00, 'VND'),
(10, 10, 110000.00, 'VND'),(11, 11, 420000.00, 'VND'),(12, 12, 310000.00, 'VND'),
(13, 13, 60000.00, 'VND'), (14, 14, 190000.00, 'VND'),(15, 15, 250000.00, 'VND'),
(16, 16, 130000.00, 'VND'),(17, 17, 480000.00, 'VND'),(18, 18, 90000.00, 'VND'),
(19, 19, 170000.00, 'VND'),(20, 20, 220000.00, 'VND'),(21, 21, 350000.00, 'VND'),
(22, 22, 40000.00, 'VND'), (23, 23, 120000.00, 'VND'),(24, 24, 500000.00, 'VND'),
(25, 25, 270000.00, 'VND'),(26, 26, 160000.00, 'VND'),(27, 27, 80000.00, 'VND'),
(28, 28, 330000.00, 'VND'),(29, 29, 210000.00, 'VND'),(30, 30, 140000.00, 'VND'),
(31, 31, 460000.00, 'VND'),(32, 32, 50000.00, 'VND'), (33, 33, 180000.00, 'VND'),
(34, 34, 290000.00, 'VND'),(35, 35, 380000.00, 'VND'),(36, 36, 70000.00, 'VND'),
(37, 37, 240000.00, 'VND'),(38, 38, 410000.00, 'VND'),(39, 39, 100000.00, 'VND'),
(40, 40, 150000.00, 'VND'),(41, 41, 260000.00, 'VND'),(42, 42, 320000.00, 'VND'),
(43, 43, 490000.00, 'VND'),(44, 44, 110000.00, 'VND'),(45, 45, 30000.00, 'VND'),
(46, 46, 200000.00, 'VND'),(47, 47, 430000.00, 'VND'),(48, 48, 360000.00, 'VND'),
(49, 49, 150000.00, 'VND'),(50, 50, 280000.00, 'VND'),
(1001, 1, 450000.00, 'VND'), (1002, 2, 120000.00, 'VND'), (1003, 3, 350000.00, 'VND');

-- 9. STAFFS (20 nhân viên)
INSERT INTO STAFFS (staff_id, staff_name, station_id, shift) VALUES
(501, 'Nguyễn Văn Hùng', 1, 'Sáng'), (502, 'Trần Thị Mai', 2, 'Chiều'),
(503, 'Lê Hoàng Long', 3, 'Sáng'),   (504, 'Phạm Thành Nam', 4, 'Chiều'),
(505, 'Đỗ Mỹ Linh', 5, 'Sáng'),     (506, 'Nguyễn Tiến Dũng', 6, 'Chiều'),
(507, 'Hoàng Hải Yến', 7, 'Sáng'),   (508, 'Bùi Minh Tuấn', 8, 'Chiều'),
(509, 'Vũ Phan Anh', 9, 'Sáng'),     (510, 'Ngô Quốc Bảo', 10, 'Chiều'),
(511, 'Đặng Thu Thảo', 15, 'Sáng'),  (512, 'Lý Gia Hân', 16, 'Chiều'),
(513, 'Trịnh Đình Quang', 17, 'Sáng'),(514, 'Võ Minh Trung', 18, 'Chiều'),
(515, 'Phan Văn Đức', 19, 'Sáng'),   (516, 'Lâm Thanh Hà', 20, 'Chiều'),
(517, 'Mai Tiến Đạt', 21, 'Sáng'),   (518, 'Đoàn Ngọc Hải', 22, 'Chiều'),
(519, 'Nguyễn Minh Triết', 23, 'Sáng'),(520, 'Hà Thị Ngọc', 25, 'Chiều');

-- 10. PRICE_TABLE (50 cặp ga)
INSERT INTO PRICE_TABLE (price_id, from_station_id, to_station_id, route_id, base_price) VALUES
(1, 1, 2, 101, 15000.00),  (2, 1, 3, 101, 17000.00),  (3, 1, 5, 101, 21000.00),
(4, 1, 7, 101, 25000.00),  (5, 1, 10, 101, 31000.00), (6, 1, 14, 101, 41000.00),
(7, 2, 3, 101, 15000.00),  (8, 2, 6, 101, 21000.00),  (9, 2, 11, 101, 31000.00),
(10, 3, 5, 101, 17000.00), (11, 3, 9, 101, 25000.00), (12, 4, 8, 101, 21000.00),
(13, 5, 6, 101, 15000.00), (14, 5, 10, 101, 23000.00), (15, 5, 14, 101, 31000.00),
(16, 6, 7, 101, 15000.00), (17, 6, 12, 101, 25000.00), (18, 7, 13, 101, 25000.00),
(19, 8, 14, 101, 25000.00), (20, 9, 11, 101, 17000.00), (21, 10, 14, 101, 21000.00),
(22, 11, 13, 101, 17000.00), (23, 12, 14, 101, 17000.00), (24, 13, 14, 101, 15000.00),
(25, 2, 14, 101, 39000.00),
(26, 1, 15, 102, 15000.00), (27, 1, 17, 102, 19000.00), (28, 1, 20, 102, 25000.00),
(29, 1, 22, 102, 29000.00), (30, 1, 25, 102, 35000.00), (31, 15, 16, 102, 15000.00),
(32, 15, 18, 102, 19000.00), (33, 15, 21, 102, 25000.00), (34, 16, 17, 102, 15000.00),
(35, 16, 20, 102, 21000.00), (36, 17, 19, 102, 17000.00), (37, 17, 23, 102, 25000.00),
(38, 18, 22, 102, 21000.00), (39, 18, 25, 102, 27000.00), (40, 19, 21, 102, 17000.00),
(41, 19, 24, 102, 23000.00), (42, 20, 22, 102, 17000.00), (43, 20, 25, 102, 23000.00),
(44, 21, 23, 102, 17000.00), (45, 22, 24, 102, 17000.00), (46, 23, 25, 102, 17000.00),
(47, 24, 25, 102, 15000.00), (48, 16, 25, 102, 31000.00), (49, 17, 25, 102, 29000.00),
(50, 15, 25, 102, 33000.00);

-- 11. ADMIN_HISTORY (10 dòng log)
INSERT INTO ADMIN_HISTORY (log_id, user_id, action, timestamp) VALUES
(801, 1, 'Thêm trạm mới vào Tuyến số 1', '2026-05-28 08:30:00'),
(802, 2, 'Cập nhật giá vé chặng Bến Thành - Suối Tiên', '2026-05-28 10:15:00'),
(803, 1, 'Bảo trì hệ thống định vị tàu TRAIN_04', '2026-05-29 14:00:00'),
(804, 3, 'Kích hoạt phương thức thanh toán VNPay', '2026-05-29 16:45:00'),
(805, 2, 'Điều chỉnh số thứ tự Ga Thảo Điền', '2026-05-30 09:10:00'),
(806, 1, 'Thêm nhân viên trực ca tại Ga Bến Thành', '2026-05-30 11:20:00'),
(807, 3, 'Cập nhật mở rộng Vé Tháng trong bảng TICKET_TYPES', '2026-05-31 13:05:00'),
(808, 2, 'Kiểm tra log hệ thống ví điện tử', '2026-06-01 15:40:00'),
(809, 1, 'Thay đổi trạng thái đoàn tàu TRAIN_01 thành Operational', '2026-06-02 08:00:00'),
(810, 3, 'Cập nhật bảng giá Tuyến số 2 chặng Ga Bến Thành - Ga Tham Lương', '2026-06-02 10:30:00');

-- 12. PRICE_HISTORY (Lịch sử giá)
INSERT INTO PRICE_HISTORY (history_id, price_id, old_price, new_price, changed_by) VALUES
(1, 1, 6000, 7000, 1), (2, 2, 8000, 9000, 2), (3, 5, 10000, 12000, 3),
(4, 8, 12000, 14000, 1), (5, 10, 15000, 16000, 2), (6, 15, 18000, 20000, 1),
(7, 20, 6000, 7000, 3), (8, 25, 9000, 10000, 2), (9, 30, 11000, 12000, 1),
(10, 32, 280000, 300000, 3), (11, 35, 120000, 150000, 2), (12, 40, 30000, 40000, 1),
(13, 42, 70000, 90000, 3), (14, 48, 10000, 11000, 1), (15, 50, 16000, 18000, 2);

-- 13. DEPOSIT_HISTORY (Lịch sử nạp tiền)
INSERT INTO DEPOSIT_HISTORY (deposit_id, wallet_id, user_id, method_id, amount) VALUES
(1, 4, 4, 3, 100000), (2, 4, 4, 4, 50000), (3, 5, 5, 2, 200000), (4, 5, 5, 3, 100000),
(5, 6, 6, 4, 500000), (6, 6, 6, 2, 100000), (7, 7, 7, 3, 50000), (8, 7, 7, 3, 200000),
(9, 8, 8, 2, 150000), (10, 8, 8, 4, 50000), (11, 9, 9, 3, 300000), (12, 9, 9, 2, 100000),
(13, 10, 10, 3, 250000), (14, 10, 10, 1, 50000), (15, 11, 11, 4, 100000), (16, 11, 11, 2, 200000),
(17, 12, 12, 3, 150000), (18, 12, 12, 3, 50000), (19, 13, 13, 2, 400000), (20, 13, 13, 1, 100000),
(21, 14, 14, 3, 50000), (22, 14, 14, 4, 200000), (23, 15, 15, 3, 100000), (24, 15, 15, 2, 300000),
(25, 16, 16, 3, 500000), (26, 16, 16, 1, 150000), (27, 17, 17, 4, 50000), (28, 17, 17, 2, 100000),
(29, 18, 18, 3, 200000), (30, 18, 18, 3, 100000), (31, 19, 19, 2, 300000), (32, 19, 19, 4, 50000),
(33, 20, 20, 3, 150000), (34, 20, 20, 2, 100000), (35, 21, 21, 3, 50000), (36, 21, 21, 1, 250000),
(37, 22, 22, 4, 400000), (38, 22, 22, 2, 100000), (39, 23, 23, 3, 100000), (40, 23, 23, 3, 200000),
(41, 24, 24, 2, 50000), (42, 24, 24, 4, 300000), (43, 25, 25, 3, 150000), (44, 25, 25, 2, 100000),
(45, 26, 26, 3, 500000), (46, 26, 26, 1, 50000), (47, 27, 27, 4, 200000), (48, 27, 27, 2, 150000),
(49, 28, 28, 3, 100000), (50, 28, 28, 3, 50000), (51, 29, 29, 2, 300000), (52, 29, 29, 1, 100000),
(53, 30, 30, 3, 250000), (54, 30, 30, 4, 50000), (55, 31, 31, 3, 100000), (56, 31, 31, 2, 200000),
(57, 32, 32, 3, 150000), (58, 32, 32, 1, 50000), (59, 33, 33, 4, 400000), (60, 33, 33, 2, 100000),
(61, 34, 34, 3, 50000), (62, 34, 34, 3, 300000), (63, 35, 35, 2, 200000), (64, 35, 35, 4, 100000),
(65, 36, 36, 3, 150000), (66, 36, 36, 2, 50000), (67, 37, 37, 3, 500000), (68, 37, 37, 1, 100000),
(69, 38, 38, 4, 250000), (70, 38, 38, 2, 50000), (71, 39, 39, 3, 100000), (72, 39, 39, 3, 200000),
(73, 40, 40, 2, 150000), (74, 40, 40, 4, 50000), (75, 41, 41, 3, 300000), (76, 41, 41, 2, 100000),
(77, 42, 42, 3, 50000), (78, 42, 42, 1, 250000), (79, 43, 43, 4, 400000), (80, 43, 43, 2, 100000),
(81, 44, 44, 3, 150000), (82, 44, 44, 3, 50000), (83, 45, 45, 2, 200000), (84, 45, 45, 4, 300000),
(85, 46, 46, 3, 100000), (86, 46, 46, 2, 50000), (87, 47, 47, 3, 500000), (88, 47, 47, 1, 150000),
(89, 48, 48, 4, 50000), (90, 48, 48, 2, 200000), (91, 49, 49, 3, 250000), (92, 49, 49, 3, 100000),
(93, 50, 50, 2, 150000), (94, 50, 50, 4, 50000), (95, 4, 4, 3, 100000), (96, 5, 5, 2, 200000),
(97, 6, 6, 3, 150000), (98, 7, 7, 4, 50000), (99, 8, 8, 3, 300000), (100, 9, 9, 2, 100000);

-- 14. TICKETS (Thông tin Vé tàu)
INSERT INTO TICKETS (ticket_id, user_id, train_id, type_id, from_station_id, to_station_id, price, qr_code, status) VALUES
(1, 4, 1, 1, 1, 14, 19000, 'QR_001', 'USED'),
(2, 5, 2, 1, 1, 8, 8000, 'QR_002', 'USED'),
(3, 6, 3, 1, 2, 14, 20000, 'QR_003', 'USED'),
(4, 7, 4, 1, 1, 4, 6000, 'QR_004', 'USED'),
(5, 8, 5, 1, 3, 10, 9000, 'QR_005', 'USED'),
(6, 9, 6, 2, 1, 14, 40000, 'QR_006', 'USED'),
(7, 10, 7, 4, 1, 14, 300000, 'QR_007', 'USED'),
(8, 11, 8, 3, 1, 14, 150000, 'QR_008', 'USED'),
(9, 12, 9, 1, 1, 12, 15000, 'QR_009', 'USED'),
(10, 13, 10, 1, 8, 12, 7000, 'QR_010', 'USED'),
(11, 14, 1, 1, 1, 24, 11000, 'QR_011', 'USED'),
(12, 15, 2, 1, 1, 20, 7000, 'QR_012', 'USED'),
(13, 16, 3, 1, 15, 24, 10000, 'QR_013', 'USED'),
(14, 17, 4, 1, 16, 21, 6000, 'QR_014', 'USED'),
(15, 18, 5, 1, 17, 23, 7000, 'QR_015', 'USED'),
(16, 19, 6, 1, 1, 24, 12000, 'QR_016', 'USED'),
(17, 20, 7, 4, 1, 24, 300000, 'QR_017', 'USED'),
(18, 21, 8, 3, 1, 24, 150000, 'QR_018', 'USED'),
(19, 22, 9, 1, 1, 22, 9000, 'QR_019', 'USED'),
(20, 23, 10, 1, 20, 24, 6000, 'QR_020', 'USED'),
(21, 24, 1, 1, 1, 14, 19000, 'QR_021', 'USED'), (22, 25, 2, 1, 1, 24, 11000, 'QR_022', 'USED'),
(23, 26, 3, 2, 1, 10, 40000, 'QR_023', 'USED'), (24, 27, 4, 1, 15, 22, 8000, 'QR_024', 'USED'),
(25, 28, 5, 1, 2, 12, 15000, 'QR_025', 'USED'), (26, 29, 6, 1, 1, 9, 9000, 'QR_026', 'USED'),
(27, 30, 7, 1, 17, 24, 8000, 'QR_027', 'USED'), (28, 31, 8, 4, 1, 14, 300000, 'QR_028', 'USED'),
(29, 32, 9, 1, 8, 14, 10000, 'QR_029', 'USED'), (30, 33, 10, 1, 1, 11, 13000, 'QR_030', 'USED'),
(31, 34, 1, 1, 1, 14, 19000, 'QR_031', 'USED'), (32, 35, 2, 1, 1, 24, 11000, 'QR_032', 'USED'),
(33, 36, 3, 2, 1, 10, 40000, 'QR_033', 'USED'), (34, 37, 4, 1, 15, 22, 8000, 'QR_034', 'USED'),
(35, 38, 5, 1, 2, 12, 15000, 'QR_035', 'USED'), (36, 39, 6, 1, 1, 9, 9000, 'QR_036', 'USED'),
(37, 40, 7, 1, 17, 24, 8000, 'QR_037', 'USED'), (38, 41, 8, 1, 1, 7, 6000, 'QR_038', 'USED'),
(39, 42, 9, 1, 8, 14, 10000, 'QR_039', 'USED'), (40, 43, 10, 1, 1, 11, 13000, 'QR_040', 'USED'),
(41, 44, 1, 1, 1, 14, 19000, 'QR_041', 'USED'), (42, 45, 2, 1, 1, 24, 11000, 'QR_042', 'USED'),
(43, 46, 3, 3, 1, 10, 150000, 'QR_043', 'USED'),(44, 47, 4, 1, 15, 22, 8000, 'QR_044', 'USED'),
(45, 48, 5, 1, 2, 12, 15000, 'QR_045', 'USED'), (46, 49, 6, 1, 1, 9, 9000, 'QR_046', 'USED'),
(47, 50, 7, 1, 17, 24, 8000, 'QR_047', 'USED'), (48, 4, 8, 1, 1, 13, 17000, 'QR_048', 'USED'),
(49, 5, 9, 1, 8, 14, 10000, 'QR_049', 'USED'), (50, 6, 10, 1, 1, 11, 13000, 'QR_050', 'USED'),
(51, 7, 1, 1, 1, 14, 19000, 'QR_051', 'UNUSED'), (52, 8, 2, 1, 1, 24, 11000, 'QR_052', 'UNUSED'),
(53, 9, 3, 2, 1, 14, 40000, 'QR_053', 'UNUSED'),
(54, 10, 4, 1, 1, 8, 8000, 'QR_054', 'EXPIRED'), (55, 11, 5, 1, 1, 22, 9000, 'QR_055', 'EXPIRED'),
(56, 12, 6, 1, 1, 14, 19000, 'QR_056', 'CANCELLED'), (57, 13, 7, 1, 1, 24, 11000, 'QR_057', 'CANCELLED'),
(58, 14, 8, 2, 1, 14, 40000, 'QR_058', 'CANCELLED'), (59, 15, 9, 1, 1, 8, 8000, 'QR_059', 'CANCELLED'),
(60, 16, 10, 1, 1, 22, 9000, 'QR_060', 'CANCELLED');