-- NHÓM 1: CÁC BẢNG GỐC 
CREATE TABLE USERS ( 
    user_id INT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(100) DEFAULT 'customer' CHECK (role IN ('customer','admin')),
    phone VARCHAR(200)
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
    price DECIMAL(10, 2),
    validity_days INT
);

-- NHÓM 2: CÁC BẢNG PHỤ THUỘC LỚP 1
CREATE TABLE ROUTESTATIONS (
    id INT PRIMARY KEY,
    route_id INT,
    station_id INT,
    position INT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);

CREATE TABLE TRAINS (
    train_id INT PRIMARY KEY,
    route_id INT,
    departure_time TIME,
    arrival_time TIME,
    capacity VARCHAR(200),
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id)
);

CREATE TABLE ADMIN_HISTORY (
    log_id INT PRIMARY KEY,                                   
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
    balance DECIMAL(15, 2) DEFAULT 0.00,                      
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE PRICE_TABLE (
    price_id INT PRIMARY KEY,
    route_id INT,
    from_station_id INT,
    to_station_id INT,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (route_id) REFERENCES ROUTES(route_id),
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id) REFERENCES STATIONS(station_id)
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

-- NHÓM 3: CÁC BẢNG PHỤ THUỘC LỚP 2
CREATE TABLE PRICE_HISTORY (
    history_id INT PRIMARY KEY,
    price_id INT,
    old_price DECIMAL(10, 2) NOT NULL,
    new_price DECIMAL(10, 2) NOT NULL,
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
    amount DECIMAL(15, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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
    price DECIMAL(10, 2) NOT NULL,
    qr_code VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'UNUSED' CHECK (status IN ('UNUSED', 'USED', 'EXPIRED', 'CANCELLED')),
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (train_id) REFERENCES TRAINS(train_id),
    FOREIGN KEY (type_id) REFERENCES TICKET_TYPES(type_id),
    FOREIGN KEY (from_station_id) REFERENCES STATIONS(station_id),
    FOREIGN KEY (to_station_id) REFERENCES STATIONS(station_id)
);

-- NHÓM 4: CÁC BẢNG NGHIỆP VỤ (Giao dịch, quét vé, hoàn tiền)
CREATE TABLE TRANSACTIONS (
    transaction_id INT PRIMARY KEY,
    user_id INT,
    wallet_id INT,
    ticket_id INT,
    amount DECIMAL(15, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (wallet_id) REFERENCES WALLETS(wallet_id),
    FOREIGN KEY (ticket_id) REFERENCES TICKETS(ticket_id)
);

CREATE TABLE SCANNING_HISTORY (
    scan_id INT PRIMARY KEY,
    ticket_id INT,
    staff_id INT,
    station_id INT,
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES TICKETS(ticket_id),
    FOREIGN KEY (staff_id) REFERENCES STAFFS(staff_id),
    FOREIGN KEY (station_id) REFERENCES STATIONS(station_id)
);

CREATE TABLE REFUNDS (
    refund_id INT PRIMARY KEY,
    ticket_id INT,
    wallet_id INT,
    amount DECIMAL(15, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES TICKETS(ticket_id),
    FOREIGN KEY (wallet_id) REFERENCES WALLETS(wallet_id)
);
