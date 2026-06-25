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

-- 5 user đầu: người cao tuổi (>=60 tuổi tính theo năm 2026) -> test miễn phí vé
INSERT INTO [USER] (user_id, user_name, password, role, phone, DoB) VALUES
(1, 'user_1', 'hashed_pw', 'customer', '0911234501', '1960-03-15'),
(2, 'user_2', 'hashed_pw', 'customer', '0911234502', '1958-07-22'),
(3, 'user_3', 'hashed_pw', 'customer', '0911234503', '1962-11-05'),
(4, 'user_4', 'hashed_pw', 'customer', '0901234504', '1955-01-30'),
(5, 'user_5', 'hashed_pw', 'customer', '0901234505', '1964-09-18'),

-- 5 user kế: trẻ em (<6 tuổi tính theo năm 2026) -> test miễn phí vé
(6, 'user_6', 'hashed_pw', 'customer', '0901234506', '2021-04-12'),
(7, 'user_7', 'hashed_pw', 'customer', '0901234507', '2022-08-25'),
(8, 'user_8', 'hashed_pw', 'customer', '0901234508', '2020-12-03'),
(9, 'user_9', 'hashed_pw', 'customer', '0901234509', '2023-02-14'),
(10, 'user_10', 'hashed_pw', 'customer', '0901234510', '2021-06-30'),

-- Còn lại: người lớn bình thường (18-40 tuổi)
(11, 'user_11', 'hashed_pw', 'customer', '0901234511', '2003-05-10'),
(12, 'user_12', 'hashed_pw', 'customer', '0901234512', '1998-09-21'),
(13, 'user_13', 'hashed_pw', 'customer', '0901234513', '2000-01-15'),
(14, 'user_14', 'hashed_pw', 'customer', '0901234514', '1995-11-08'),
(15, 'user_15', 'hashed_pw', 'customer', '0901234515', '2002-03-25'),
(16, 'user_16', 'hashed_pw', 'customer', '0901234516', '1999-07-14'),
(17, 'user_17', 'hashed_pw', 'customer', '0901234517', '2001-12-02'),
(18, 'user_18', 'hashed_pw', 'customer', '0901234518', '1997-04-19'),
(19, 'user_19', 'hashed_pw', 'customer', '0901234519', '2004-08-27'),
(20, 'user_20', 'hashed_pw', 'customer', '0901234520', '1996-02-09'),
(21, 'user_21', 'hashed_pw', 'customer', '0901234521', '2003-10-16'),
(22, 'user_22', 'hashed_pw', 'customer', '0901234522', '1998-06-23'),
(23, 'user_23', 'hashed_pw', 'customer', '0901234523', '2000-09-04'),
(24, 'user_24', 'hashed_pw', 'customer', '0901234524', '1994-01-28'),
(25, 'user_25', 'hashed_pw', 'customer', '0901234525', '2002-05-17'),
(26, 'user_26', 'hashed_pw', 'customer', '0901234526', '1999-11-30'),
(27, 'user_27', 'hashed_pw', 'customer', '0901234527', '2001-07-08'),
(28, 'user_28', 'hashed_pw', 'customer', '0901234528', '1997-03-21'),
(29, 'user_29', 'hashed_pw', 'customer', '0901234529', '2004-09-12'),
(30, 'user_30', 'hashed_pw', 'customer', '0901234530', '1996-12-05'),
(31, 'user_31', 'hashed_pw', 'customer', '0901234531', '2003-02-19'),
(32, 'user_32', 'hashed_pw', 'customer', '0901234532', '1998-08-26'),
(33, 'user_33', 'hashed_pw', 'customer', '0901234533', '2000-04-13'),
(34, 'user_34', 'hashed_pw', 'customer', '0901234534', '1995-10-29'),
(35, 'user_35', 'hashed_pw', 'customer', '0901234535', '2002-06-07'),
(36, 'user_36', 'hashed_pw', 'customer', '0901234536', '1999-01-22'),
(37, 'user_37', 'hashed_pw', 'customer', '0901234537', '2001-09-15'),
(38, 'user_38', 'hashed_pw', 'customer', '0901234538', '1997-05-03'),
(39, 'user_39', 'hashed_pw', 'customer', '0901234539', '2004-11-20'),
(40, 'user_40', 'hashed_pw', 'customer', '0901234540', '1996-07-11'),
(41, 'user_41', 'hashed_pw', 'customer', '0901234541', '2003-03-28'),
(42, 'user_42', 'hashed_pw', 'customer', '0901234542', '1998-12-09'),
(43, 'user_43', 'hashed_pw', 'customer', '0901234543', '2000-08-16'),
(44, 'user_44', 'hashed_pw', 'customer', '0901234544', '1995-02-24'),
(45, 'user_45', 'hashed_pw', 'customer', '0901234545', '2002-10-01'),
(46, 'user_46', 'hashed_pw', 'customer', '0901234546', '1999-04-18'),
(47, 'user_47', 'hashed_pw', 'customer', '0901234547', '2001-06-25'),
(48, 'user_48', 'hashed_pw', 'customer', '0901234548', '1997-09-07'),
(49, 'user_49', 'hashed_pw', 'customer', '0901234549', '2004-01-14'),
(50, 'user_50', 'hashed_pw', 'customer', '0901234550', '1996-05-31');

-- ====================================================================
-- DỮ LIỆU BỔ SUNG: Khách hàng cho các kịch bản Edge Cases & Temporal Data
-- ====================================================================
INSERT INTO [USER] (user_id, user_name, password, role, phone, DoB) VALUES
(51, 'user_edge_zero',   'hashed_password_default', 'customer', '0901234551', '2000-01-01'),
(52, 'user_temporal_apr', 'hashed_password_default', 'customer', '0901234552', '1999-04-15'),
(53, 'user_temporal_jul', 'hashed_password_default', 'customer', '0901234553', '2001-07-20'),
(54, 'user_stress_scan',  'hashed_password_default', 'customer', '0901234554', '1998-11-11'),
(55, 'user_refund_test',  'hashed_password_default', 'customer', '0901234555', '2002-12-25');
GO