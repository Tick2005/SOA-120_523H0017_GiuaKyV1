CREATE DATABASE IF NOT EXISTS tuition_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE tuition_db;

CREATE TABLE IF NOT EXISTS tuitions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    student_email VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    fee DECIMAL(15,2) NOT NULL,
    status ENUM('unpaid', 'paid') DEFAULT 'unpaid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_student_email (student_email),
    INDEX idx_status (status),
    INDEX idx_student_year_semester (student_id, academic_year, semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed data
INSERT INTO tuitions (student_id, student_name, student_email, semester, academic_year, fee, status) VALUES
-- Student 52000123
('52000123', 'Nguyen Van A', '52000123@student.tdtu.edu.vn', 2, '2023-2024', 0, 'paid'),
('52000123', 'Nguyen Van A', '52000123@student.tdtu.edu.vn', 1, '2024-2025', 5000000, 'unpaid'),
('52000123', 'Nguyen Van A', '52000123@student.tdtu.edu.vn', 2, '2024-2025', 5000000, 'unpaid'),
('52000123', 'Nguyen Van A', '52000123@student.tdtu.edu.vn', 1, '2025-2026', 5500000, 'unpaid'),

-- Student 520H0696
('520H0696', 'Tran Thi B', '520H0696@student.tdtu.edu.vn', 1, '2023-2024', 0, 'paid'),
('520H0696', 'Tran Thi B', '520H0696@student.tdtu.edu.vn', 2, '2023-2024', 0, 'paid'),
('520H0696', 'Tran Thi B', '520H0696@student.tdtu.edu.vn', 1, '2024-2025', 5000000, 'unpaid'),
('520H0696', 'Tran Thi B', '520H0696@student.tdtu.edu.vn', 2, '2024-2025', 5000000, 'unpaid');
