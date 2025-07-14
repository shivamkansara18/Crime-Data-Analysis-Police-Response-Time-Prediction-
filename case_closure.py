import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="crime_db",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

# SQL to fetch required data
query = """
SELECT crime_domain, date_reported, date_case_closed
FROM crime_data
WHERE case_closed ILIKE 'yes' 
  AND crime_domain IS NOT NULL 
  AND date_reported IS NOT NULL 
  AND date_case_closed IS NOT NULL;
"""

# Read data into DataFrame
df = pd.read_sql(query, conn)
conn.close()

# Date conversion
df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')
df['date_case_closed'] = pd.to_datetime(df['date_case_closed'], errors='coerce')

# Duration calculation
df['closure_duration_days'] = (df['date_case_closed'] - df['date_reported']).dt.days

# Drop nulls & invalids
df = df.dropna(subset=['closure_duration_days', 'crime_domain'])
df = df[df['closure_duration_days'] >= 0]

# Sort domains by median
ordered_domains = df.groupby('crime_domain')['closure_duration_days'].median().sort_values().index
df['crime_domain'] = pd.Categorical(df['crime_domain'], categories=ordered_domains, ordered=True)

# 🔹 Plot with y-axis ticks every 50
plt.figure(figsize=(14, 6))
df.boxplot(
    column='closure_duration_days',
    by='crime_domain',
    grid=False,
    patch_artist=True,
    boxprops=dict(facecolor='skyblue'),
    medianprops=dict(color='darkblue'),
)

# Custom Y-axis ticks
max_val = df['closure_duration_days'].max()
plt.yticks(np.arange(0, max_val + 50, 50))  #   Ticks at steps of 50

plt.title('Case Closure Time Distribution by Crime Domain')
plt.suptitle('')
plt.xlabel('Crime Domain')
plt.ylabel('Closure Duration (days)')
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()
