import psycopg2
import pandas as pd

# 🔹 Database Connection
try:
    conn = psycopg2.connect(
        dbname="crime_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    print(" Connected to PostgreSQL!")
except Exception as e:
    print(" Error connecting to PostgreSQL:", e)
    exit()

# 🔹 Create Table (Schema Matches CSV)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS crime_data (
        crime_id SERIAL PRIMARY KEY,
        report_number INT,
        date_reported TIMESTAMP,
        date_occurred TIMESTAMP,
        time_occurred TIME,
        city TEXT,
        crime_code INT,
        crime_description TEXT,
        victim_age INT,
        victim_gender TEXT,
        weapon_used TEXT,
        crime_domain TEXT,
        police_deployed INT,
        case_closed TEXT,
        date_case_closed TIMESTAMP
    );
""")
conn.commit()
print(" Table 'crime_data' created successfully!")

# 🔹 Load CSV File
csv_file = "crime_data.csv"
crime_df = pd.read_csv(csv_file)

# 🔹 Debugging: Print Column Names
print("CSV Columns:", crime_df.columns)

# 🔹 Ensure Correct Column Names & Convert Data Types
crime_df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"), inplace=True)

# Convert date columns to proper datetime format
crime_df["date_reported"] = pd.to_datetime(crime_df["date_reported"], format="%d-%m-%Y %H:%M", errors='coerce')
crime_df["date_occurred"] = pd.to_datetime(crime_df["date_occurred"], format="%d-%m-%Y %H:%M", errors='coerce')

# Fix time_occurred column: Convert full datetime to time
crime_df["time_occurred"] = pd.to_datetime(crime_df["time_occurred"], format="%d-%m-%Y %H:%M", errors='coerce').dt.time

crime_df["date_case_closed"] = pd.to_datetime(crime_df["date_case_closed"], format="%d-%m-%Y %H:%M", errors='coerce')

# 🔹 Insert Data into PostgreSQL, handle NaT/NaN explicitly for each row
for _, row in crime_df.iterrows():
    # Replace NaT/NaN with None for each datetime column
    date_reported = row["date_reported"] if pd.notnull(row["date_reported"]) else None
    date_occurred = row["date_occurred"] if pd.notnull(row["date_occurred"]) else None
    time_occurred = row["time_occurred"] if pd.notnull(row["time_occurred"]) else None
    date_case_closed = row["date_case_closed"] if pd.notnull(row["date_case_closed"]) else None
    
    cursor.execute("""
        INSERT INTO crime_data (report_number, date_reported, date_occurred, time_occurred, city, crime_code, 
        crime_description, victim_age, victim_gender, weapon_used, crime_domain, police_deployed, case_closed, date_case_closed) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["crime_id"], date_reported, date_occurred, time_occurred, row["city"],
        row["crime_code"], row["crime_description"], row["victim_age"], row["victim_gender"],
        row["weapon_used"], row["crime_domain"], row["police_deployed"], row["case_closed"], date_case_closed
    ))

conn.commit()
print(" Data stored in PostgreSQL successfully!")

# 🔹 Close Connection
cursor.close()
conn.close()
print("🔒 Connection closed.")
