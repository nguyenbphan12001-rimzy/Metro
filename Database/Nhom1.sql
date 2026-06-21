USE Metro_Customer;
GO

-- =========================================================
-- 1. DỮ LIỆU BẢNG GỐC (ROUTES, STATIONS, PAYMENT_METHODS, TICKET_TYPES, USERS)
-- =========================================================
INSERT INTO ROUTE (route_id, route_name) VALUES
(101, 'Tuyến số 1 (Bến Thành - Suối Tiên)'),
(102, 'Tuyến số 2 (Bến Thành - Tham Lương)');

INSERT INTO STATION (station_id, station_name) VALUES
(1, 'Ga Bến Thành'), (2, 'Ga Nhà hát Thành phố'), (3, 'Ga Ba Son'),
(4, 'Ga Công viên Văn Thánh'), (5, 'Ga Tân Cảng'), (6, 'Ga Thảo Điền'),
(7, 'Ga An Phú'), (8, 'Ga Rạch Chiếc'), (9, 'Ga Phước Long'),
(10, 'Ga Bình Thái'), (11, 'Ga Thủ Đức'), (12, 'Ga Khu Công nghệ cao'),
(13, 'Ga Đại học Quốc Gia'), (14, 'Ga Bến xe Suối Tiên'), (15, 'Ga Tao Đàn'),
(16, 'Ga Dân Chủ'), (17, 'Ga Hòa Hưng'), (18, 'Ga Lê Thị Riêng'),
(19, 'Ga Phạm Văn Hai'), (20, 'Ga Trường Chinh'), (21, 'Ga Bà Quẹo'),
(22, 'Ga Đồng Đen'), (23, 'Ga Nguyễn Hồng Đào'), (24, 'Ga Tàu Trường Chinh'),
(25, 'Ga Tham Lương');

INSERT INTO PAYMENT_METHOD (method_id, method_name) VALUES
(1, 'Tiền mặt'), (2, 'Thẻ tín dụng'), (3, 'MoMo'), (4, 'VNPay');

INSERT INTO TICKET_TYPE (type_id, type_name, price, validity_days) VALUES
(1, 'Vé lượt',       NULL,      NULL),
(2, 'Vé ngày',       40000.00,  1),
(3, 'Vé tháng SV',   100000.00, 30),
(4, 'Vé tháng PT',   200000.00, 30);

-- Lưu ý: Đổi role của 3 user đầu tiên thành 'customer' và bọc [USER]
INSERT INTO [USER] (user_id, user_name, password, role, phone) VALUES
(1, 'user_1', 'hashed_pw', 'customer', '0911234501'), (2, 'user_2', 'hashed_pw', 'customer', '0911234502'),
(3, 'user_3', 'hashed_pw', 'customer', '0911234503'), (4, 'user_4', 'hashed_pw', 'customer', '0901234504'),
(5, 'user_5', 'hashed_pw', 'customer', '0901234505'), (6, 'user_6', 'hashed_pw', 'customer', '0901234506'),
(7, 'user_7', 'hashed_pw', 'customer', '0901234507'), (8, 'user_8', 'hashed_pw', 'customer', '0901234508'),
(9, 'user_9', 'hashed_pw', 'customer', '0901234509'), (10, 'user_10', 'hashed_pw', 'customer', '0901234510'),
(11, 'user_11', 'hashed_pw', 'customer', '0901234511'), (12, 'user_12', 'hashed_pw', 'customer', '0901234512'),
(13, 'user_13', 'hashed_pw', 'customer', '0901234513'), (14, 'user_14', 'hashed_pw', 'customer', '0901234514'),
(15, 'user_15', 'hashed_pw', 'customer', '0901234515'), (16, 'user_16', 'hashed_pw', 'customer', '0901234516'),
(17, 'user_17', 'hashed_pw', 'customer', '0901234517'), (18, 'user_18', 'hashed_pw', 'customer', '0901234518'),
(19, 'user_19', 'hashed_pw', 'customer', '0901234519'), (20, 'user_20', 'hashed_pw', 'customer', '0901234520'),
(21, 'user_21', 'hashed_pw', 'customer', '0901234521'), (22, 'user_22', 'hashed_pw', 'customer', '0901234522'),
(23, 'user_23', 'hashed_pw', 'customer', '0901234523'), (24, 'user_24', 'hashed_pw', 'customer', '0901234524'),
(25, 'user_25', 'hashed_pw', 'customer', '0901234525'), (26, 'user_26', 'hashed_pw', 'customer', '0901234526'),
(27, 'user_27', 'hashed_pw', 'customer', '0901234527'), (28, 'user_28', 'hashed_pw', 'customer', '0901234528'),
(29, 'user_29', 'hashed_pw', 'customer', '0901234529'), (30, 'user_30', 'hashed_pw', 'customer', '0901234530'),
(31, 'user_31', 'hashed_pw', 'customer', '0901234531'), (32, 'user_32', 'hashed_pw', 'customer', '0901234532'),
(33, 'user_33', 'hashed_pw', 'customer', '0901234533'), (34, 'user_34', 'hashed_pw', 'customer', '0901234534'),
(35, 'user_35', 'hashed_pw', 'customer', '0901234535'), (36, 'user_36', 'hashed_pw', 'customer', '0901234536'),
(37, 'user_37', 'hashed_pw', 'customer', '0901234537'), (38, 'user_38', 'hashed_pw', 'customer', '0901234538'),
(39, 'user_39', 'hashed_pw', 'customer', '0901234539'), (40, 'user_40', 'hashed_pw', 'customer', '0901234540'),
(41, 'user_41', 'hashed_pw', 'customer', '0901234541'), (42, 'user_42', 'hashed_pw', 'customer', '0901234542'),
(43, 'user_43', 'hashed_pw', 'customer', '0901234543'), (44, 'user_44', 'hashed_pw', 'customer', '0901234544'),
(45, 'user_45', 'hashed_pw', 'customer', '0901234545'), (46, 'user_46', 'hashed_pw', 'customer', '0901234546'),
(47, 'user_47', 'hashed_pw', 'customer', '0901234547'), (48, 'user_48', 'hashed_pw', 'customer', '0901234548'),
(49, 'user_49', 'hashed_pw', 'customer', '0901234549'), (50, 'user_50', 'hashed_pw', 'customer', '0901234550');

-- ====================================================================
-- DỮ LIỆU BỔ SUNG CHO FILE 1: 01_insert_nhom1.sql
-- Thêm Khách hàng mới cho các kịch bản Edge Cases & Temporal Data
-- ====================================================================

INSERT INTO [USER] (user_id, user_name, password, role, phone) VALUES
(51, 'user_edge_zero',   'hashed_password_default', 'customer', '0901234551'),
(52, 'user_temporal_apr', 'hashed_password_default', 'customer', '0901234552'),
(53, 'user_temporal_jul', 'hashed_password_default', 'customer', '0901234553'),
(54, 'user_stress_scan',  'hashed_password_default', 'customer', '0901234554'),
(55, 'user_refund_test',  'hashed_password_default', 'customer', '0901234555');
GO