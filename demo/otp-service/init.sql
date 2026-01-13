-- OTP Service Database Schema

CREATE DATABASE IF NOT EXISTS otp_db;
USE otp_db;

CREATE TABLE IF NOT EXISTS otp (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    otp_code VARCHAR(6) NOT NULL,
    transaction_id BIGINT UNIQUE NOT NULL,
    status ENUM('active', 'used', 'expired') DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_otp_code (otp_code),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_otp_code_status (otp_code, status),
    INDEX idx_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
