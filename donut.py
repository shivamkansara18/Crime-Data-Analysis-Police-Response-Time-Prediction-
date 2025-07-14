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

# Load crime_domain data
query = """
SELECT crime_domain
FROM crime_data
WHERE crime_domain IS NOT NULL;
"""

df = pd.read_sql(query, conn)
conn.close()

# Count occurrences of each domain
crime_counts = df['crime_domain'].value_counts()
labels = crime_counts.index
sizes = crime_counts.values

# Plot Donut Chart
plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(
    sizes,
    labels=labels,
    autopct='%1.1f%%',
    startangle=140,
    textprops=dict(color="black"),
    wedgeprops=dict(width=0.3)
)

# Add a white circle to make it a donut
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.title('Distribution of Crime by Domain')
plt.axis('equal')
plt.tight_layout()
plt.show()
