from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the PostgreSQL database
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/crime_db")

# Load data
query = """
SELECT report_number, victim_age, date_occurred
FROM crime_data
WHERE date_occurred IS NOT NULL AND victim_age IS NOT NULL;
"""
df = pd.read_sql(query, engine)

# Feature engineering
df["Time of Day"] = df["date_occurred"].dt.hour
df["Victim_age_group"] = pd.cut(df["victim_age"], bins=[0, 18, 35, 60, 100], labels=["Child", "Young", "Adult", "Senior"])

# Group by Time of Day and Victim_age_group
time_of_occ = df.groupby(['Time of Day', 'Victim_age_group'])[['report_number']].count().reset_index().sort_values(by='report_number', ascending=False)
time_of_occ.rename(columns={"report_number": "Cases_reported"}, inplace=True)

# Summarize by Victim_age_group
age_groups = time_of_occ.groupby('Victim_age_group')['Cases_reported'].sum()

# Plot a pie chart
plt.figure(figsize=(4, 4))
plt.pie(age_groups, labels=age_groups.index, autopct='%1.1f%%',
        colors=['#FF9999', '#66B3FF', '#99FF99', '#FFD700'])
plt.title("Crime Occurrence by Victim Age Group")
plt.tight_layout()
plt.show()
