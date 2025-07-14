from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

# Connect to PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/crime_db")

# Load data
query = """
SELECT report_number, date_occurred
FROM crime_data
WHERE date_occurred IS NOT NULL;
"""
df = pd.read_sql(query, engine)

# Extract hour and map to time categories
df["hour"] = df["date_occurred"].dt.hour

def categorize_time(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

df["time_category"] = df["hour"].apply(categorize_time)

# Count crimes by time category
time_counts = df["time_category"].value_counts().sort_index()

# Plot pie chart
plt.figure(figsize=(5, 5))
colors = ['#FFD700', '#FFA07A', '#20B2AA', '#778899']
plt.pie(time_counts, labels=time_counts.index, autopct='%1.1f%%', colors=colors)
plt.title("Crime Distribution by Time Category")
print(df["time_category"].value_counts())

plt.tight_layout()
plt.show()
