-- ==========================================================
-- Course Outcome Management System (COMS)
-- Database Script: database.sql
-- Description: Creates the database, tables, and sample data
-- ==========================================================

-- 1. Create and Select Database
CREATE DATABASE IF NOT EXISTS course_outcome_db;
USE course_outcome_db;

-- 2. Drop existing tables if they exist (in reverse order of foreign keys)
DROP TABLE IF EXISTS student_marks;
DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS course_outcomes;
DROP TABLE IF EXISTS courses;

-- 3. Table: courses
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL
);

-- 4. Table: course_outcomes
CREATE TABLE course_outcomes (
    co_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    co_number VARCHAR(10) NOT NULL,
    co_description VARCHAR(255) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- 5. Table: students
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    student_name VARCHAR(100) NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- 6. Table: assessments
CREATE TABLE assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    co_id INT NOT NULL,
    assessment_name VARCHAR(100) NOT NULL,
    max_marks DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (co_id) REFERENCES course_outcomes(co_id) ON DELETE CASCADE
);

-- 7. Table: student_marks
CREATE TABLE student_marks (
    marks_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    assessment_id INT NOT NULL,
    obtained_marks DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    CONSTRAINT unique_student_assessment UNIQUE (student_id, assessment_id)
);

-- ==========================================================
-- Sample Data for Demonstration and Viva Testing
-- ==========================================================

-- Insert Courses
INSERT INTO courses (course_id, course_code, course_name) VALUES
(1, 'CS301', 'Database Management Systems'),
(2, 'CS302', 'Computer Networks'),
(3, 'CS303', 'Operating Systems');

-- Insert Course Outcomes (for Course 1: DBMS)
INSERT INTO course_outcomes (co_id, course_id, co_number, co_description) VALUES
(1, 1, 'CO1', 'Understand relational database concepts and ER modeling'),
(2, 1, 'CO2', 'Formulate complex queries using Structured Query Language (SQL)'),
(3, 1, 'CO3', 'Apply database normalization to eliminate anomalies'),
(4, 1, 'CO4', 'Understand transaction processing, concurrency, and ACID properties');

-- Insert Course Outcomes (for Course 2: Computer Networks)
INSERT INTO course_outcomes (co_id, course_id, co_number, co_description) VALUES
(5, 2, 'CO1', 'Understand OSI and TCP/IP protocol stack layers'),
(6, 2, 'CO2', 'Analyze IP addressing, subnetting, and routing protocols');

-- Insert Students (Enrolled in Course 1: DBMS)
INSERT INTO students (student_id, roll_no, student_name, course_id) VALUES
(1, 'CS202401', 'Aarav Sharma', 1),
(2, 'CS202402', 'Neha Patil', 1),
(3, 'CS202403', 'Rohan Kulkarni', 1),
(4, 'CS202404', 'Pooja Iyer', 1),
(5, 'CS202405', 'Aniket Verma', 1),
(6, 'CS202406', 'Sneha Deshmukh', 1),
(7, 'CS202407', 'Aditya Joshi', 1),
(8, 'CS202408', 'Priya Nair', 1),
(9, 'CS202409', 'Vikram Shinde', 1),
(10, 'CS202410', 'Tanvi Mehta', 1);

-- Insert Assessments (Linked to Course 1 and respective COs)
INSERT INTO assessments (assessment_id, course_id, co_id, assessment_name, max_marks) VALUES
(1, 1, 1, 'Unit Test 1 (CO1)', 20.00),
(2, 1, 2, 'SQL Lab Test (CO2)', 25.00),
(3, 1, 3, 'Normalization Assignment (CO3)', 30.00),
(4, 1, 4, 'Unit Test 2 (CO4)', 20.00);

-- Insert Student Marks:
-- Target is 60% of Max Marks:
-- Assessment 1: Max 20, Target = 12. 8/10 students score >= 12 -> Attainment 80% (Level 3)
INSERT INTO student_marks (student_id, assessment_id, obtained_marks) VALUES
(1, 1, 16.00),
(2, 1, 14.50),
(3, 1, 18.00),
(4, 1, 15.00),
(5, 1, 13.00),
(6, 1, 11.00), -- below target
(7, 1, 17.50),
(8, 1, 10.00), -- below target
(9, 1, 15.50),
(10, 1, 14.00);

-- Assessment 2: Max 25, Target = 15. 7/10 students score >= 15 -> Attainment 70% (Level 3)
INSERT INTO student_marks (student_id, assessment_id, obtained_marks) VALUES
(1, 2, 22.00),
(2, 2, 19.00),
(3, 2, 24.00),
(4, 2, 17.00),
(5, 2, 12.00), -- below target
(6, 2, 16.00),
(7, 2, 20.00),
(8, 2, 11.50), -- below target
(9, 2, 13.00), -- below target
(10, 2, 18.50);

-- Assessment 3: Max 30, Target = 18. 6/10 students score >= 18 -> Attainment 60% (Level 2)
INSERT INTO student_marks (student_id, assessment_id, obtained_marks) VALUES
(1, 3, 25.00),
(2, 3, 21.00),
(3, 3, 27.00),
(4, 3, 16.00), -- below target
(5, 3, 14.00), -- below target
(6, 3, 19.50),
(7, 3, 22.00),
(8, 3, 15.00), -- below target
(9, 3, 12.50), -- below target
(10, 3, 20.00);

-- Assessment 4: Max 20, Target = 12. 5/10 students score >= 12 -> Attainment 50% (Level 1)
INSERT INTO student_marks (student_id, assessment_id, obtained_marks) VALUES
(1, 4, 15.00),
(2, 4, 13.00),
(3, 4, 16.50),
(4, 4, 10.00), -- below target
(5, 4, 11.00), -- below target
(6, 4, 14.00),
(7, 4, 12.50),
(8, 4, 9.00),  -- below target
(9, 4, 8.50),  -- below target
(10, 4, 11.50); -- below target
