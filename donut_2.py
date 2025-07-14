import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="crime_db",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

# Fetch data from database
query = """
SELECT crime_description
FROM crime_data
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Count each crime type
crime_counts = df['crime_description'].value_counts()

# Create donut chart
plt.figure(figsize=(10, 8))
wedges, texts, autotexts = plt.pie(
    crime_counts,
    labels=crime_counts.index,
    autopct='%1.2f%%',
    startangle=140,
    pctdistance=0.85
)

# Draw center circle
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

# Final touches
plt.title('Distribution of Different Crime Types')
plt.axis('equal')
plt.tight_layout()
plt.show()
