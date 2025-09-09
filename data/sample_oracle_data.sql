-- Sample Oracle Database Schema and Data for Ed-Tech ETL Pipeline
-- This file contains the database schema and sample data for testing

-- Create tables
CREATE TABLE students (
    student_id VARCHAR2(10) PRIMARY KEY,
    first_name VARCHAR2(50) NOT NULL,
    last_name VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) UNIQUE NOT NULL,
    academic_program VARCHAR2(100) NOT NULL,
    enrollment_date DATE NOT NULL,
    graduation_date DATE,
    gpa NUMBER(3,2),
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    course_id VARCHAR2(10) PRIMARY KEY,
    course_name VARCHAR2(100) NOT NULL,
    course_code VARCHAR2(20) UNIQUE NOT NULL,
    department VARCHAR2(50) NOT NULL,
    credits NUMBER(2) NOT NULL,
    description CLOB,
    prerequisites VARCHAR2(500),
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enrollments (
    enrollment_id VARCHAR2(10) PRIMARY KEY,
    student_id VARCHAR2(10) NOT NULL,
    course_id VARCHAR2(10) NOT NULL,
    semester VARCHAR2(20) NOT NULL,
    year NUMBER(4) NOT NULL,
    grade VARCHAR2(2),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR2(20) DEFAULT 'ENROLLED',
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE academic_records (
    record_id VARCHAR2(10) PRIMARY KEY,
    student_id VARCHAR2(10) NOT NULL,
    semester VARCHAR2(20) NOT NULL,
    year NUMBER(4) NOT NULL,
    total_credits NUMBER(3) NOT NULL,
    gpa NUMBER(3,2) NOT NULL,
    academic_standing VARCHAR2(20) NOT NULL,
    honors VARCHAR2(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Insert sample students data
INSERT INTO students (student_id, first_name, last_name, email, academic_program, enrollment_date, graduation_date, gpa, status) VALUES
('STU001', 'John', 'Doe', 'john.doe@university.edu', 'Computer Science', DATE '2020-09-01', DATE '2024-05-15', 3.8, 'ACTIVE');
INSERT INTO students (student_id, first_name, last_name, email, academic_program, enrollment_date, graduation_date, gpa, status) VALUES
('STU002', 'Jane', 'Smith', 'jane.smith@university.edu', 'Data Science', DATE '2020-09-01', DATE '2024-05-15', 3.6, 'ACTIVE');
INSERT INTO students (student_id, first_name, last_name, email, academic_program, enrollment_date, graduation_date, gpa, status) VALUES
('STU003', 'Bob', 'Johnson', 'bob.johnson@university.edu', 'Business Administration', DATE '2020-09-01', DATE '2024-05-15', 3.9, 'ACTIVE');
INSERT INTO students (student_id, first_name, last_name, email, academic_program, enrollment_date, graduation_date, gpa, status) VALUES
('STU004', 'Alice', 'Williams', 'alice.williams@university.edu', 'Computer Science', DATE '2021-09-01', NULL, 3.7, 'ACTIVE');
INSERT INTO students (student_id, first_name, last_name, email, academic_program, enrollment_date, graduation_date, gpa, status) VALUES
('STU005', 'Charlie', 'Brown', 'charlie.brown@university.edu', 'Data Science', DATE '2021-09-01', NULL, 3.5, 'ACTIVE');

-- Insert sample courses data
INSERT INTO courses (course_id, course_name, course_code, department, credits, description, prerequisites) VALUES
('CS101', 'Introduction to Computer Science', 'CS-101', 'Computer Science', 3, 'Fundamental concepts of computer science and programming', NULL);
INSERT INTO courses (course_id, course_name, course_code, department, credits, description, prerequisites) VALUES
('CS201', 'Data Structures and Algorithms', 'CS-201', 'Computer Science', 4, 'Advanced programming concepts and algorithm design', 'CS101');
INSERT INTO courses (course_id, course_name, course_code, department, credits, description, prerequisites) VALUES
('DS101', 'Introduction to Data Science', 'DS-101', 'Data Science', 3, 'Fundamentals of data analysis and statistics', NULL);
INSERT INTO courses (course_id, course_name, course_code, department, credits, description, prerequisites) VALUES
('DS201', 'Machine Learning', 'DS-201', 'Data Science', 4, 'Introduction to machine learning algorithms', 'DS101');
INSERT INTO courses (course_id, course_name, course_code, department, credits, description, prerequisites) VALUES
('BA101', 'Business Fundamentals', 'BA-101', 'Business Administration', 3, 'Core business concepts and practices', NULL);
INSERT INTO courses (course_id, course_name, course_code, department, credits, description, prerequisites) VALUES
('BA201', 'Strategic Management', 'BA-201', 'Business Administration', 4, 'Advanced business strategy and management', 'BA101');

-- Insert sample enrollments data
INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, year, grade, enrollment_date) VALUES
('ENR001', 'STU001', 'CS101', 'Fall', 2020, 'A', DATE '2020-09-01');
INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, year, grade, enrollment_date) VALUES
('ENR002', 'STU001', 'CS201', 'Spring', 2021, 'A-', DATE '2021-01-15');
INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, year, grade, enrollment_date) VALUES
('ENR003', 'STU002', 'DS101', 'Fall', 2020, 'B+', DATE '2020-09-01');
INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, year, grade, enrollment_date) VALUES
('ENR004', 'STU002', 'DS201', 'Spring', 2021, 'A', DATE '2021-01-15');
INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, year, grade, enrollment_date) VALUES
('ENR005', 'STU003', 'BA101', 'Fall', 2020, 'A-', DATE '2020-09-01');
INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, year, grade, enrollment_date) VALUES
('ENR006', 'STU003', 'BA201', 'Spring', 2021, 'A', DATE '2021-01-15');

-- Insert sample academic records data
INSERT INTO academic_records (record_id, student_id, semester, year, total_credits, gpa, academic_standing, honors) VALUES
('AR001', 'STU001', 'Fall', 2020, 3, 3.8, 'Good Standing', NULL);
INSERT INTO academic_records (record_id, student_id, semester, year, total_credits, gpa, academic_standing, honors) VALUES
('AR002', 'STU001', 'Spring', 2021, 4, 3.7, 'Good Standing', 'Dean''s List');
INSERT INTO academic_records (record_id, student_id, semester, year, total_credits, gpa, academic_standing, honors) VALUES
('AR003', 'STU002', 'Fall', 2020, 3, 3.6, 'Good Standing', NULL);
INSERT INTO academic_records (record_id, student_id, semester, year, total_credits, gpa, academic_standing, honors) VALUES
('AR004', 'STU002', 'Spring', 2021, 4, 3.8, 'Good Standing', 'Dean''s List');
INSERT INTO academic_records (record_id, student_id, semester, year, total_credits, gpa, academic_standing, honors) VALUES
('AR005', 'STU003', 'Fall', 2020, 3, 3.9, 'Good Standing', 'Dean''s List');
INSERT INTO academic_records (record_id, student_id, semester, year, total_credits, gpa, academic_standing, honors) VALUES
('AR006', 'STU003', 'Spring', 2021, 4, 3.8, 'Good Standing', 'Dean''s List');

-- Create indexes for better performance
CREATE INDEX idx_students_program ON students(academic_program);
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_academic_records_student ON academic_records(student_id);

-- Create views for common queries
CREATE VIEW student_enrollment_summary AS
SELECT 
    s.student_id,
    s.first_name,
    s.last_name,
    s.academic_program,
    s.gpa,
    COUNT(e.enrollment_id) as total_courses,
    AVG(CASE 
        WHEN e.grade = 'A' THEN 4.0
        WHEN e.grade = 'A-' THEN 3.7
        WHEN e.grade = 'B+' THEN 3.3
        WHEN e.grade = 'B' THEN 3.0
        WHEN e.grade = 'B-' THEN 2.7
        WHEN e.grade = 'C+' THEN 2.3
        WHEN e.grade = 'C' THEN 2.0
        ELSE 0
    END) as course_gpa
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
WHERE s.status = 'ACTIVE'
GROUP BY s.student_id, s.first_name, s.last_name, s.academic_program, s.gpa;

-- Grant necessary permissions
GRANT SELECT ON students TO etl_user;
GRANT SELECT ON courses TO etl_user;
GRANT SELECT ON enrollments TO etl_user;
GRANT SELECT ON academic_records TO etl_user;
GRANT SELECT ON student_enrollment_summary TO etl_user;

COMMIT;
