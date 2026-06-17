-- 1. Create the Database
CREATE DATABASE StudentMaksAnalyzerDB;


USE StudentAnalytics;


-- 2. Create Student Records Table
CREATE TABLE student_records (
    id INT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    class VARCHAR(50) NOT NULL,
    gender VARCHAR(15) NOT NULL,
    dob VARCHAR(20) NOT NULL -- Stored as VARCHAR to accommodate imported formats like '25-04-2017' before cleaning
);


-- 3. Create Subject Information Table
CREATE TABLE subject_info (
    SubjectID INT PRIMARY KEY,
    Sub_name VARCHAR(100) NOT NULL,
    teacher VARCHAR(150) NOT NULL,
    department VARCHAR(150) NOT NULL,
    highest_marks INT NOT NULL
);


-- 4. Create Student Marks Table
CREATE TABLE student_marks (
    student_id INT PRIMARY KEY, -- Primary Key if it's 1-to-1 per student row, otherwise remove PRIMARY KEY if a student has multiple rows
    maths INT DEFAULT 0,
    chemistry INT DEFAULT 0,
    physics INT DEFAULT 0,
    hindi INT DEFAULT 0,
    english INT DEFAULT 0,
    total_marks INT DEFAULT 0,
    percentage DECIMAL(5,2) DEFAULT 0.00,
    CONSTRAINT FK_Student_Marks FOREIGN KEY (student_id) REFERENCES student_records(id) ON DELETE CASCADE
);
