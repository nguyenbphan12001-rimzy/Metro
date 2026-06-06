-- =========================================================
-- NHÓM 1: TẠO BẢNG ĐỘC LẬP
-- =========================================================

CREATE TABLE ROUTES (
    route_id INT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE STATIONS (
    station_id INT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    location VARCHAR(150),
    status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE PAYMENT_METHODS (
    method_id INT PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE TICKET_TYPES (
    ticket_type_id INT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE USERS (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

-- =========================================================
-- NHÓM 1: CHÈN DỮ LIỆU MẪU
-- =========================================================

-- 1. ROUTES (2 dòng)
INSERT INTO ROUTES (route_id, route_name, status) VALUES
(101, 'Tuyến số 1 (Bến Thành - Suối Tiên)', 'Active'),
(102, 'Tuyến số 2 (Bến Thành - Tham Lương)', 'Active');

-- 2. STATIONS (25 dòng độc nhất - Ga Bến Thành ID=1 là ga chung)
INSERT INTO STATIONS (station_id, station_name, location, status) VALUES
(1, 'Ga Bến Thành', '10.7725, 106.6980', 'Active'),
(2, 'Ga Nhà hát Thành phố', '10.7761, 106.7032', 'Active'),
(3, 'Ga Ba Son', '10.7812, 106.7061', 'Active'),
(4, 'Ga Công viên Văn Thánh', '10.7951, 106.7135', 'Active'),
(5, 'Ga Tân Cảng', '10.7978, 106.7201', 'Active'),
(6, 'Ga Thảo Điền', '10.8015, 106.7324', 'Active'),
(7, 'Ga An Phú', '10.8038, 106.7410', 'Active'),
(8, 'Ga Rạch Chiếc', '10.8091, 106.7532', 'Active'),
(9, 'Ga Phước Long', '10.8164, 106.7645', 'Active'),
(10, 'Ga Bình Thái', '10.8245, 106.7721', 'Active'),
(11, 'Ga Thủ Đức', '10.8351, 106.7814', 'Active'),
(12, 'Ga Khu Công nghệ cao', '10.8502, 106.7932', 'Active'),
(13, 'Ga Đại học Quốc Gia', '10.8654, 106.8021', 'Active'),
(14, 'Ga Bến xe Suối Tiên', '10.8791, 106.8085', 'Active'),
(15, 'Ga Tao Đàn', '10.7750, 106.6912', 'Active'),
(16, 'Ga Dân Chủ', '10.7815, 106.6821', 'Active'),
(17, 'Ga Hòa Hưng', '10.7864, 106.6748', 'Active'),
(18, 'Ga Lê Thị Riêng', '10.7931, 106.6691', 'Active'),
(19, 'Ga Phạm Văn Hai', '10.7985, 106.6612', 'Active'),
(20, 'Ga Trường Chinh', '10.8041, 106.6521', 'Active'),
(21, 'Ga Bà Quẹo', '10.8095, 106.6432', 'Active'),
(22, 'Ga Đồng Đen', '10.8124, 106.6385', 'Active'),
(23, 'Ga Nguyễn Hồng Đào', '10.8172, 106.6312', 'Active'),
(24, 'Ga Tàu Trường Chinh', '10.8221, 106.6254', 'Active'),
(25, 'Ga Tham Lương', '10.8285, 106.6195', 'Active');

-- 3. PAYMENT_METHODS (4 dòng)
INSERT INTO PAYMENT_METHODS (method_id, method_name, status) VALUES
(1, 'Tiền mặt', 'Active'),
(2, 'Thẻ tín dụng', 'Active'),
(3, 'MoMo', 'Active'),
(4, 'VNPay', 'Active');

-- 4. TICKET_TYPES (4 loại chuẩn theo khung mẫu)
INSERT INTO TICKET_TYPES (ticket_type_id, type_name, description) VALUES
(1, 'Vé lượt', 'Vé sử dụng cho một lượt đi duy nhất'),
(2, 'Vé ngày', 'Vé sử dụng không giới hạn trong 24 giờ'),
(3, 'Vé tháng SV', 'Vé tháng ưu đãi dành cho Sinh viên'),
(4, 'Vé tháng PT', 'Vé tháng dành cho đối tượng Phổ thông');

-- 5. USERS (50 người dùng: ID 1-3 là Admin, còn lại là Customer)
INSERT INTO USERS (user_id, username, email, phone, role, status) VALUES
(1, 'admin_1', 'admin1@metro.com', '0911234501', 'Admin', 'Active'),
(2, 'admin_2', 'admin2@metro.com', '0911234502', 'Admin', 'Active'),
(3, 'admin_3', 'admin3@metro.com', '0911234503', 'Admin', 'Active'),
(4, 'user_4', 'customer4@gmail.com', '0901234504', 'Customer', 'Active'),
(5, 'user_5', 'customer5@gmail.com', '0901234505', 'Customer', 'Active'),
(6, 'user_6', 'customer6@gmail.com', '0901234506', 'Customer', 'Active'),
(7, 'user_7', 'customer7@gmail.com', '0901234507', 'Customer', 'Active'),
(8, 'user_8', 'customer8@gmail.com', '0901234508', 'Customer', 'Active'),
(9, 'user_9', 'customer9@gmail.com', '0901234509', 'Customer', 'Active'),
(10, 'user_10', 'customer10@gmail.com', '0901234510', 'Customer', 'Active'),
(11, 'user_11', 'customer11@gmail.com', '0901234511', 'Customer', 'Active'),
(12, 'user_12', 'customer12@gmail.com', '0901234512', 'Customer', 'Active'),
(13, 'user_13', 'customer13@gmail.com', '0901234513', 'Customer', 'Active'),
(14, 'user_14', 'customer14@gmail.com', '0901234514', 'Customer', 'Active'),
(15, 'user_15', 'customer15@gmail.com', '0901234515', 'Customer', 'Active'),
(16, 'user_16', 'customer16@gmail.com', '0901234516', 'Customer', 'Active'),
(17, 'user_17', 'customer17@gmail.com', '0901234517', 'Customer', 'Active'),
(18, 'user_18', 'customer18@gmail.com', '0901234518', 'Customer', 'Active'),
(19, 'user_19', 'customer19@gmail.com', '0901234519', 'Customer', 'Active'),
(20, 'user_20', 'customer20@gmail.com', '0901234520', 'Customer', 'Active'),
(21, 'user_21', 'customer21@gmail.com', '0901234521', 'Customer', 'Active'),
(22, 'user_22', 'customer22@gmail.com', '0901234522', 'Customer', 'Active'),
(23, 'user_23', 'customer23@gmail.com', '0901234523', 'Customer', 'Active'),
(24, 'user_24', 'customer24@gmail.com', '0901234524', 'Customer', 'Active'),
(25, 'user_25', 'customer25@gmail.com', '0901234525', 'Customer', 'Active'),
(26, 'user_26', 'customer26@gmail.com', '0901234526', 'Customer', 'Active'),
(27, 'user_27', 'customer27@gmail.com', '0901234527', 'Customer', 'Active'),
(28, 'user_28', 'customer28@gmail.com', '0901234528', 'Customer', 'Active'),
(29, 'user_29', 'customer29@gmail.com', '0901234529', 'Customer', 'Active'),
(30, 'user_30', 'customer30@gmail.com', '0901234530', 'Customer', 'Active'),
(31, 'user_31', 'customer31@gmail.com', '0901234531', 'Customer', 'Active'),
(32, 'user_32', 'customer32@gmail.com', '0901234532', 'Customer', 'Active'),
(33, 'user_33', 'customer33@gmail.com', '0901234533', 'Customer', 'Active'),
(34, 'user_34', 'customer34@gmail.com', '0901234534', 'Customer', 'Active'),
(35, 'user_35', 'customer35@gmail.com', '0901234535', 'Customer', 'Active'),
(36, 'user_36', 'customer36@gmail.com', '0901234536', 'Customer', 'Active'),
(37, 'user_37', 'customer37@gmail.com', '0901234537', 'Customer', 'Active'),
(38, 'user_38', 'customer38@gmail.com', '0901234538', 'Customer', 'Active'),
(39, 'user_39', 'customer39@gmail.com', '0901234539', 'Customer', 'Active'),
(40, 'user_40', 'customer40@gmail.com', '0901234540', 'Customer', 'Active'),
(41, 'user_41', 'customer41@gmail.com', '0901234541', 'Customer', 'Active'),
(42, 'user_42', 'customer42@gmail.com', '0901234542', 'Customer', 'Active'),
(43, 'user_43', 'customer43@gmail.com', '0901234543', 'Customer', 'Active'),
(44, 'user_44', 'customer44@gmail.com', '0901234544', 'Customer', 'Active'),
(45, 'user_45', 'customer45@gmail.com', '0901234545', 'Customer', 'Active'),
(46, 'user_46', 'customer46@gmail.com', '0901234546', 'Customer', 'Active'),
(47, 'user_47', 'customer47@gmail.com', '0901234547', 'Customer', 'Active'),
(48, 'user_48', 'customer48@gmail.com', '0901234548', 'Customer', 'Active'),
(49, 'user_49', 'customer49@gmail.com', '0901234549', 'Customer', 'Active'),
(50, 'user_50', 'customer50@gmail.com', '0901234550', 'Customer', 'Active');
