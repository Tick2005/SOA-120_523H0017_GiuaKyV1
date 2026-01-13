-- Create customer_db database
CREATE DATABASE IF NOT EXISTS customer_db;
USE customer_db;

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data (Admin created accounts with plain text passwords)
INSERT INTO customers (username, email, password, full_name, phone_number, balance) VALUES
('user123', 'tranduchuy2k5ne@gmail.com', 'password123', 'Nguyen Van User', '0901234567', 10000000),
('john_doe', 'phanduong19032023@gmail.com', 'john1234', 'John Doe', '0902345678', 5000000),
('jane_smith', 'jane@example.com', 'jane1234', 'Jane Smith', '0903456789', 15000000),
('admin', 'khangtrongclone@gmail.com', 'admin123', 'Administrator', '0904567890', 50000000);
