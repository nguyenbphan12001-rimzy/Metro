USE MetroDB;
GO

-- 1. Xóa các bảng con chứa khóa ngoại trước để tránh lỗi ràng buộc (REFERENCE constraint)
DELETE FROM SCANNING_HISTORY;
DELETE FROM [TRANSACTION];

-- 2. Xóa các bảng trung gian sau khi bảng con đã sạch dữ liệu
DELETE FROM TICKET;

-- 3. Xóa các bảng hạ tầng và ví điện tử
DELETE FROM WALLET;
DELETE FROM PRICE_TABLE;
DELETE FROM TRAIN;
DELETE FROM ROUTESTATION;
GO