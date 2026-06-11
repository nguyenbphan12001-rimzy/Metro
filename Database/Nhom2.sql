-- =========================================================
-- FILE 2: Insert dữ liệu bảng lớp 1 (có FK đến nhóm 1)
-- Chạy sau file 01_insert_nhom1.sql
-- =========================================================
USE MetroDB;
GO

-- 6. ROUTESTATIONS
INSERT INTO ROUTESTATIONS (route_station_id, route_id, station_id, position) VALUES
(1,  101, 1,  1),  (2,  101, 2,  2),  (3,  101, 3,  3),  (4,  101, 4,  4),  (5,  101, 5,  5),
(6,  101, 6,  6),  (7,  101, 7,  7),  (8,  101, 8,  8),  (9,  101, 9,  9),  (10, 101, 10, 10),
(11, 101, 11, 11), (12, 101, 12, 12), (13, 101, 13, 13), (14, 101, 14, 14),
(15, 102, 1,  1),  (16, 102, 15, 2),  (17, 102, 16, 3),  (18, 102, 17, 4),  (19, 102, 18, 5),
(20, 102, 19, 6),  (21, 102, 20, 7),  (22, 102, 21, 8),  (23, 102, 22, 9),  (24, 102, 23, 10),
(25, 102, 24, 11), (26, 102, 25, 12);

-- 7. TRAINS
INSERT INTO TRAINS (train_id, route_id, departure_time, arrival_time, capacity) VALUES
(1,  101, '05:00', '06:00', 300),
(2,  101, '05:30', '06:30', 300),
(3,  101, '06:00', '07:00', 300),
(4,  101, '06:30', '07:30', 300),
(5,  101, '07:00', '08:00', 300),
(6,  102, '05:00', '06:10', 300),
(7,  102, '05:30', '06:40', 300),
(8,  102, '06:00', '07:10', 300),
(9,  102, '06:30', '07:40', 300),
(10, 102, '07:00', '08:10', 300);

-- 8. WALLETS (user_id 4-50 là customer, 1001-1003 là admin)
INSERT INTO WALLETS (wallet_id, user_id, balance, last_updated) VALUES
(1,    1,  450000.00, CURRENT_TIMESTAMP),
(2,    2,  120000.00, CURRENT_TIMESTAMP),
(3,    3,  350000.00, CURRENT_TIMESTAMP),
(4,    4,  20000.00,  CURRENT_TIMESTAMP),
(5,    5,  150000.00, CURRENT_TIMESTAMP),
(6,    6,  0.00,      CURRENT_TIMESTAMP),
(7,    7,  500000.00, CURRENT_TIMESTAMP),
(8,    8,  230000.00, CURRENT_TIMESTAMP),
(9,    9,  80000.00,  CURRENT_TIMESTAMP),
(10,   10, 110000.00, CURRENT_TIMESTAMP),
(11,   11, 420000.00, CURRENT_TIMESTAMP),
(12,   12, 310000.00, CURRENT_TIMESTAMP),
(13,   13, 60000.00,  CURRENT_TIMESTAMP),
(14,   14, 190000.00, CURRENT_TIMESTAMP),
(15,   15, 250000.00, CURRENT_TIMESTAMP),
(16,   16, 130000.00, CURRENT_TIMESTAMP),
(17,   17, 480000.00, CURRENT_TIMESTAMP),
(18,   18, 90000.00,  CURRENT_TIMESTAMP),
(19,   19, 170000.00, CURRENT_TIMESTAMP),
(20,   20, 220000.00, CURRENT_TIMESTAMP),
(21,   21, 350000.00, CURRENT_TIMESTAMP),
(22,   22, 40000.00,  CURRENT_TIMESTAMP),
(23,   23, 120000.00, CURRENT_TIMESTAMP),
(24,   24, 500000.00, CURRENT_TIMESTAMP),
(25,   25, 270000.00, CURRENT_TIMESTAMP),
(26,   26, 160000.00, CURRENT_TIMESTAMP),
(27,   27, 80000.00,  CURRENT_TIMESTAMP),
(28,   28, 330000.00, CURRENT_TIMESTAMP),
(29,   29, 210000.00, CURRENT_TIMESTAMP),
(30,   30, 140000.00, CURRENT_TIMESTAMP),
(31,   31, 460000.00, CURRENT_TIMESTAMP),
(32,   32, 50000.00,  CURRENT_TIMESTAMP),
(33,   33, 180000.00, CURRENT_TIMESTAMP),
(34,   34, 290000.00, CURRENT_TIMESTAMP),
(35,   35, 380000.00, CURRENT_TIMESTAMP),
(36,   36, 70000.00,  CURRENT_TIMESTAMP),
(37,   37, 240000.00, CURRENT_TIMESTAMP),
(38,   38, 410000.00, CURRENT_TIMESTAMP),
(39,   39, 100000.00, CURRENT_TIMESTAMP),
(40,   40, 150000.00, CURRENT_TIMESTAMP),
(41,   41, 260000.00, CURRENT_TIMESTAMP),
(42,   42, 320000.00, CURRENT_TIMESTAMP),
(43,   43, 490000.00, CURRENT_TIMESTAMP),
(44,   44, 110000.00, CURRENT_TIMESTAMP),
(45,   45, 30000.00,  CURRENT_TIMESTAMP),
(46,   46, 200000.00, CURRENT_TIMESTAMP),
(47,   47, 430000.00, CURRENT_TIMESTAMP),
(48,   48, 360000.00, CURRENT_TIMESTAMP),
(49,   49, 150000.00, CURRENT_TIMESTAMP),
(50,   50, 280000.00, CURRENT_TIMESTAMP);
-- ====================================================================
-- DỮ LIỆU BỔ SUNG CHO FILE 2: 02_insert_nhom2.sql
-- Thêm Ví tiền (WALLETS) tương ứng cho các tài khoản kiểm thử mới
-- ====================================================================

INSERT INTO WALLETS (wallet_id, user_id, balance, last_updated) VALUES
(51, 51, 0.00,      '2026-04-15 10:00:00'), -- Số dư đúng bằng 0 để hệ thống chặn khi đặt mua vé lượt
(52, 52, 200000.00, '2026-04-01 07:00:00'), -- Tài khoản có tiền hoạt động từ Tháng 4
(53, 53, 300000.00, '2026-07-01 07:00:00'), -- Tài khoản có tiền hoạt động từ Tháng 7
(54, 54, 150000.00, '2026-06-10 08:00:00'), -- Tài khoản dùng để mua vé ngày di chuyển liên tục
(55, 55, 100000.00, '2026-06-10 09:00:00'); -- Tài khoản dùng để mua vé sau đó hủy/hoàn tiền
-- 9. STAFFS
-- Lưu ý: user_id 1-3 là admin, không dùng làm staff
-- Dùng employee_code để phân biệt
INSERT INTO STAFFS (staff_id, user_id, station_id, full_name, employee_code) VALUES
(501, NULL, 1,  'Nguyễn Văn Hùng',    'NV501'),
(502, NULL, 2,  'Trần Thị Mai',        'NV502'),
(503, NULL, 3,  'Lê Hoàng Long',       'NV503'),
(504, NULL, 4,  'Phạm Thành Nam',      'NV504'),
(505, NULL, 5,  'Đỗ Mỹ Linh',         'NV505'),
(506, NULL, 6,  'Nguyễn Tiến Dũng',   'NV506'),
(507, NULL, 7,  'Hoàng Hải Yến',      'NV507'),
(508, NULL, 8,  'Bùi Minh Tuấn',      'NV508'),
(509, NULL, 9,  'Vũ Phan Anh',        'NV509'),
(510, NULL, 10, 'Ngô Quốc Bảo',       'NV510'),
(511, NULL, 15, 'Đặng Thu Thảo',      'NV511'),
(512, NULL, 16, 'Lý Gia Hân',         'NV512'),
(513, NULL, 17, 'Trịnh Đình Quang',   'NV513'),
(514, NULL, 18, 'Võ Minh Trung',      'NV514'),
(515, NULL, 19, 'Phan Văn Đức',       'NV515'),
(516, NULL, 20, 'Lâm Thanh Hà',       'NV516'),
(517, NULL, 21, 'Mai Tiến Đạt',       'NV517'),
(518, NULL, 22, 'Đoàn Ngọc Hải',     'NV518'),
(519, NULL, 23, 'Nguyễn Minh Triết',  'NV519'),
(520, NULL, 25, 'Hà Thị Ngọc',       'NV520');

-- 10. PRICE_TABLE
INSERT INTO PRICE_TABLE (price_id, route_id, from_station_id, to_station_id, price) VALUES
(1,  101, 1,  2,  15000.00), (2,  101, 1,  3,  17000.00), (3,  101, 1,  5,  21000.00),
(4,  101, 1,  7,  25000.00), (5,  101, 1,  10, 31000.00), (6,  101, 1,  14, 41000.00),
(7,  101, 2,  3,  15000.00), (8,  101, 2,  6,  21000.00), (9,  101, 2,  11, 31000.00),
(10, 101, 3,  5,  17000.00), (11, 101, 3,  9,  25000.00), (12, 101, 4,  8,  21000.00),
(13, 101, 5,  6,  15000.00), (14, 101, 5,  10, 23000.00), (15, 101, 5,  14, 31000.00),
(16, 101, 6,  7,  15000.00), (17, 101, 6,  12, 25000.00), (18, 101, 7,  13, 25000.00),
(19, 101, 8,  14, 25000.00), (20, 101, 9,  11, 17000.00), (21, 101, 10, 14, 21000.00),
(22, 101, 11, 13, 17000.00), (23, 101, 12, 14, 17000.00), (24, 101, 13, 14, 15000.00),
(25, 101, 2,  14, 39000.00),
(26, 102, 1,  15, 15000.00), (27, 102, 1,  17, 19000.00), (28, 102, 1,  20, 25000.00),
(29, 102, 1,  22, 29000.00), (30, 102, 1,  25, 35000.00), (31, 102, 15, 16, 15000.00),
(32, 102, 15, 18, 19000.00), (33, 102, 15, 21, 25000.00), (34, 102, 16, 17, 15000.00),
(35, 102, 16, 20, 21000.00), (36, 102, 17, 19, 17000.00), (37, 102, 17, 23, 25000.00),
(38, 102, 18, 22, 21000.00), (39, 102, 18, 25, 27000.00), (40, 102, 19, 21, 17000.00),
(41, 102, 19, 24, 23000.00), (42, 102, 20, 22, 17000.00), (43, 102, 20, 25, 23000.00),
(44, 102, 21, 23, 17000.00), (45, 102, 22, 24, 17000.00), (46, 102, 23, 25, 17000.00),
(47, 102, 24, 25, 15000.00), (48, 102, 16, 25, 31000.00), (49, 102, 17, 25, 29000.00),
(50, 102, 15, 25, 33000.00);

-- 11. ADMIN_HISTORY
INSERT INTO ADMIN_HISTORY (ad_log_id, admin_id, action, target_table, target_id, description, created_at) VALUES
(801, 1, 'INSERT', 'STATIONS',     NULL, 'Thêm trạm mới vào Tuyến số 1',                               '2026-05-28 08:30:00'),
(802, 2, 'UPDATE', 'PRICE_TABLE',  6,    'Cập nhật giá vé chặng Bến Thành - Suối Tiên',                '2026-05-28 10:15:00'),
(803, 1, 'UPDATE', 'TRAINS',       4,    'Bảo trì hệ thống định vị tàu TRAIN_04',                      '2026-05-29 14:00:00'),
(804, 3, 'INSERT', 'PAYMENT_METHODS', NULL, 'Kích hoạt phương thức thanh toán VNPay',                  '2026-05-29 16:45:00'),
(805, 2, 'UPDATE', 'ROUTESTATIONS', 6,   'Điều chỉnh số thứ tự Ga Thảo Điền',                         '2026-05-30 09:10:00'),
(806, 1, 'INSERT', 'STAFFS',       NULL, 'Thêm nhân viên trực ca tại Ga Bến Thành',                    '2026-05-30 11:20:00'),
(807, 3, 'UPDATE', 'TICKET_TYPES', 3,    'Cập nhật mở rộng Vé Tháng trong bảng TICKET_TYPES',          '2026-05-31 13:05:00'),
(808, 2, 'SELECT', 'WALLETS',      NULL, 'Kiểm tra log hệ thống ví điện tử',                           '2026-06-01 15:40:00'),
(809, 1, 'UPDATE', 'TRAINS',       1,    'Thay đổi trạng thái đoàn tàu TRAIN_01 thành Operational',    '2026-06-02 08:00:00'),
(810, 3, 'UPDATE', 'PRICE_TABLE',  30,   'Cập nhật bảng giá Tuyến số 2 chặng Bến Thành - Tham Lương', '2026-06-02 10:30:00');
