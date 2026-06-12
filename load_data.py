import os
import pandas as pd
import pyodbc

print("--- STARTING MIGRATION ---")

# 1. READ YOUR CSV FILES
try:
    print("Reading CSV files...")
    records_df = pd.read_csv("student_records.csv")
    marks_df = pd.read_csv("student_marks.csv")
    subjects_df = pd.read_csv("subject_info.csv")
except FileNotFoundError as e:
    print(f"❌ Error: Could not find a CSV file. Make sure they are in the same folder! {e}")
    exit()

# Clean column headers
records_df.columns = [c.strip() for c in records_df.columns]
marks_df.columns = [c.strip() for c in marks_df.columns]
subjects_df.columns = [c.strip() for c in subjects_df.columns]

# Reformat dates from DD-MM-YYYY to SQL Server standard YYYY-MM-DD
records_df["dob"] = pd.to_datetime(records_df["dob"], format="%d-%m-%Y").dt.strftime("%Y-%m-%d")

# 2. DEFINE THE CONNECTION STRING (Pointing to your local Express server)
conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"  
    r"DATABASE=StudentMarksAnalyzerDB;"
    r"Trusted_Connection=yes;"
)

try:
    print("Connecting to SSMS (localhost\\SQLEXPRESS)...")
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    conn.autocommit = False
    
    # 3. INSERT DATA ROWS INTO TABLES
    print("Loading data into 'student_records'...")
    for _, row in records_df.iterrows():
        cursor.execute("INSERT INTO student_records VALUES (?, ?, ?, ?, ?)", 
                       int(row['id']), row['name'], row['class'], row['gender'], row['dob'])
                       
    print("Loading data into 'subject_info'...")
    for _, row in subjects_df.iterrows():
        cursor.execute("INSERT INTO subject_info VALUES (?, ?, ?, ?, ?)", 
                       int(row['SubjectID']), row['Sub_name'], row['teacher'], row['department'], int(row['highest_marks']))
                       
    print("Loading data into 'student_marks'...")
    for _, row in marks_df.iterrows():
        cursor.execute("INSERT INTO student_marks VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       int(row['student_id']), int(row['maths']), int(row['chemistry']), int(row['physics']), 
                       int(row['hindi']), int(row['english']), int(row['total marks']), float(row['percentage%']))
                       
    conn.commit()
    print("\n🚀 SUCCESS! All CSV records are now securely loaded into SSMS!")

except Exception as e:
    print(f"\n❌ Database Connection Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()