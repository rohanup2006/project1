USE StudentMarksAnalyzerDB;
GO

-- 1. Check a few rows from the student records
SELECT TOP 5 * FROM student_records;

-- 2. Check a few rows from the student marks
SELECT TOP 5 * FROM student_marks;

-- 3. See how many total rows were imported into each table
SELECT 'student_records' AS TableName, COUNT(*) AS TotalRows FROM student_records
UNION ALL
SELECT 'student_marks', COUNT(*) FROM student_marks
UNION ALL
SELECT 'subject_info', COUNT(*) FROM subject_info;